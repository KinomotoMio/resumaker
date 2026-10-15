#!/usr/bin/env python3
"""Check that every resume bullet traces back to a confirmed achievement in the vault.

Usage:
  trace.py <application-dir> [--vault PATH]

Checks per bullet:
  - has a `from:` pointing at achievements/<id>.md            (else: unsourced)
  - the achievement exists and is `status: confirmed`          (drafts in inbox/ are errors)
  - confidentiality is not `secret`; `internal` needs a desensitisation review
  - every number in the bullet appears somewhere in its source files
  - metrics marked `verified: false` are flagged when their numbers are used

Exit code 1 when any error is found. Uses `typst eval` as the YAML parser.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "resumaker" / "config.json"
NUM = re.compile(r"\d+(?:[.,]\d+)?")


def resolve_vault(explicit):
    if explicit:
        return Path(explicit).expanduser()
    if os.environ.get("RESUMAKER_VAULT"):
        return Path(os.environ["RESUMAKER_VAULT"]).expanduser()
    try:
        return Path(json.loads(CONFIG.read_text())["vault"]).expanduser()
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        pass
    local = Path.cwd() / "career"
    return local if (local / "VAULT.md").exists() else None


def parse_yaml(text):
    res = subprocess.run(
        ["typst", "eval", "yaml(bytes(sys.inputs.src))", "--in", "-", "--input", f"src={text}"],
        input="", capture_output=True, text=True,
    )
    if res.returncode != 0:
        raise ValueError(res.stderr.strip())
    return json.loads(res.stdout)


def frontmatter(path):
    text = path.read_text()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    return parse_yaml(m.group(1)) or {}, text


def bullets(resume):
    for section in resume.get("sections") or []:
        for item in section.get("items") or []:
            if not isinstance(item, dict):
                continue
            for b in item.get("bullets") or []:
                if isinstance(b, dict):
                    src = b.get("from")
                    yield section.get("title", ""), b.get("text", ""), [src] if isinstance(src, str) else (src or [])
                else:
                    yield section.get("title", ""), str(b), []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("app_dir")
    ap.add_argument("--vault")
    args = ap.parse_args()

    app = Path(args.app_dir).expanduser().resolve()
    vault = resolve_vault(args.vault)
    if not vault or not (vault / "VAULT.md").exists():
        print(json.dumps({"ok": False, "error": "找不到履历库，先运行 resumaker-init"}, ensure_ascii=False))
        return 2

    resume = parse_yaml((app / "resume.yaml").read_text())
    cache = {}
    errors, warnings, unsourced = [], [], []
    total = 0

    for section, text, sources in bullets(resume):
        total += 1
        short = text[:40] + ("…" if len(text) > 40 else "")
        if not sources:
            unsourced.append(f"[{section}] {short}")
            continue

        corpus, unverified = "", []
        for sid in sources:
            if sid not in cache:
                path = vault / "achievements" / f"{sid}.md"
                draft = vault / "inbox" / f"{sid}.md"
                if path.exists():
                    cache[sid] = (path, *frontmatter(path))
                elif draft.exists():
                    cache[sid] = (draft, *frontmatter(draft))
                else:
                    cache[sid] = None
            entry = cache[sid]
            if entry is None:
                errors.append(f"[{section}] {short} → 成果 `{sid}` 不存在")
                continue
            path, fm, raw = entry
            corpus += raw
            if path.parent.name == "inbox" or fm.get("status") != "confirmed":
                errors.append(f"[{section}] {short} → `{sid}` 还是草稿，需先在 career-review 中确认")
            conf = fm.get("confidentiality", "internal")
            if conf == "secret":
                errors.append(f"[{section}] {short} → `{sid}` 标记为 secret，不能出现在简历里")
            elif conf == "internal":
                warnings.append(f"[{section}] {short} → `{sid}` 为 internal，确认已脱敏（内部系统名、客户名、未公开数据）")
            for m in fm.get("metrics") or []:
                if isinstance(m, dict) and m.get("verified") is False:
                    unverified += NUM.findall(str(m.get("text", "")))

        plain = text.replace("**", "")
        for n in NUM.findall(plain):
            if corpus and n not in corpus:
                warnings.append(f"[{section}] {short} → 数字 {n} 在来源成果里找不到出处")
            elif n in unverified:
                warnings.append(f"[{section}] {short} → 数字 {n} 来自未验证的指标（verified: false），面试前准备好佐证")

    report = {
        "ok": not errors,
        "bullets": total,
        "traced": total - len(unsourced),
        "errors": errors,
        "warnings": sorted(set(warnings), key=warnings.index),
        "unsourced": unsourced,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
