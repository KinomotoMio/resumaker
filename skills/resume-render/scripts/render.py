#!/usr/bin/env python3
"""Render resume.yaml → resume.pdf with Typst, then self-check the layout.

Usage:
  render.py <application-dir | resume.yaml> [--template clean] [--reset-template] [--ppi 110]

Writes next to resume.yaml:
  resume.typ          copied from the template on first run (edit freely per application)
  resume.pdf
  .preview/page-N.png page images for visual review

Prints a JSON report: pages, how full the last page is, text-layer check, and hints.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL / "assets" / "templates"
CJK_FONTS = [
    "Noto Sans CJK SC", "Source Han Sans SC", "Noto Sans SC", "PingFang SC",
    "Hiragino Sans GB", "Microsoft YaHei", "Heiti SC", "WenQuanYi Micro Hei",
]
INSTALL_HINT = (
    "未找到 typst。安装：macOS `brew install typst`；Windows `winget install --id Typst.Typst`；"
    "Linux 用发行版包管理器或 `cargo install --locked typst-cli`；也可从 https://github.com/typst/typst/releases 下载。"
)


def font_paths():
    cands = [os.environ.get("RESUMAKER_FONTS"),
             str(Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "resumaker" / "fonts")]
    return [p for p in cands if p and Path(p).expanduser().is_dir()]


def typst(args, cwd, fonts):
    cmd = ["typst", *args]
    for fp in fonts:
        cmd += ["--font-path", str(Path(fp).expanduser())]
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def clean_warnings(stderr):
    """Drop the noisy per-family 'unknown font' warnings; fallbacks are intentional."""
    blocks = re.split(r"\n(?=warning:|error:)", stderr.strip())
    return [b for b in blocks if b and "unknown font family" not in b]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--template", default=None, help="template name in assets/templates (default: meta.template or clean)")
    ap.add_argument("--reset-template", action="store_true", help="overwrite resume.typ with a fresh template copy")
    ap.add_argument("--ppi", type=int, default=110)
    args = ap.parse_args()

    if not shutil.which("typst"):
        print(json.dumps({"ok": False, "error": INSTALL_HINT}, ensure_ascii=False))
        return 2

    target = Path(args.target).expanduser().resolve()
    workdir = target if target.is_dir() else target.parent
    data = workdir / "resume.yaml"
    if not data.exists():
        print(json.dumps({"ok": False, "error": f"缺少 {data}"}, ensure_ascii=False))
        return 2

    name = args.template
    if not name:
        m = re.search(r"^\s*template:\s*([\w-]+)", data.read_text(), re.M)
        name = m.group(1) if m else "clean"
    template = TEMPLATES / f"{name}.typ"
    if not template.exists():
        avail = sorted(p.stem for p in TEMPLATES.glob("*.typ"))
        print(json.dumps({"ok": False, "error": f"模板 {name} 不存在，可选：{avail}"}, ensure_ascii=False))
        return 2

    typ = workdir / "resume.typ"
    if args.reset_template or not typ.exists():
        shutil.copy2(template, typ)

    fonts = font_paths()
    report = {"ok": True, "pdf": str(workdir / "resume.pdf"), "template": name, "hints": []}

    res = typst(["compile", "resume.typ", "resume.pdf"], workdir, fonts)
    if res.returncode != 0:
        report.update(ok=False, error=res.stderr.strip())
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1
    warnings = clean_warnings(res.stderr)
    if warnings:
        report["warnings"] = warnings

    preview = workdir / ".preview"
    shutil.rmtree(preview, ignore_errors=True)
    preview.mkdir()
    typst(["compile", "resume.typ", str(preview / "page-{p}.png"), "--ppi", str(args.ppi)], workdir, fonts)
    report["previews"] = sorted(str(p) for p in preview.glob("page-*.png"))

    # 版面：内容在哪一页、哪个高度结束
    ev = typst(["eval", "query(<resume-end>).first().value", "--in", "resume.typ"], workdir, fonts)
    try:
        end = json.loads(ev.stdout)
        usable = end["height"] - end["top"] - end["bottom"]
        fill = max(0.0, min(1.0, (end["y"] - end["top"]) / usable))
        pages = end["page"]
        m = re.search(r"^\s*density:\s*(\w+)", data.read_text(), re.M)
        density = m.group(1) if m else "normal"
        report["pages"] = pages
        report["last_page_fill"] = round(fill, 2)
        if pages > 1 and fill < 0.4:
            alt = "" if density == "compact" else "，或设 meta.density: compact"
            report["hints"].append(f"第 {pages} 页只用了 {fill:.0%}：精简内容压回 {pages - 1} 页{alt}。")
        elif pages == 1 and fill < 0.75:
            alt = "" if density == "airy" else "，或设 meta.density: airy"
            report["hints"].append(f"一页只填了 {fill:.0%}：可以补充与 JD 相关的成果{alt}。")
        elif pages > 2:
            report["hints"].append(f"共 {pages} 页：除非是学术 CV，一般应控制在 1～2 页。")
    except (json.JSONDecodeError, KeyError):
        report["hints"].append("模板里没有 <resume-end> 标记，无法检查版面占用。")

    # 字体：是否有可用的中文字体
    listed = typst(["fonts"], workdir, fonts).stdout.splitlines()
    cjk = [f for f in CJK_FONTS if f in listed]
    report["cjk_font"] = cjk[0] if cjk else None
    if not cjk:
        report["hints"].append("没有找到中文字体，中文可能显示为方块。安装 Noto Sans CJK SC，或把字体文件放到 ~/.config/resumaker/fonts/。")

    # 文本层：ATS 能否按顺序读出文字
    if shutil.which("pdftotext"):
        txt = subprocess.run(["pdftotext", "-layout", "resume.pdf", "-"], cwd=workdir, capture_output=True, text=True).stdout
        m = re.search(r"^\s*name:\s*(.+)$", data.read_text(), re.M)
        person = m.group(1).strip().strip("\"'") if m else ""
        report["text_layer"] = {"chars": len(txt), "name_found": bool(person) and person in txt}
        if person and person not in txt:
            report["hints"].append("PDF 文本层里找不到姓名，ATS 可能无法正确解析。")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
