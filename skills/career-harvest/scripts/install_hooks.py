#!/usr/bin/env python3
"""Install (or remove) the career-harvest SessionEnd hook for Claude Code, Codex and Gemini CLI.

Usage:
  install_hooks.py --agent claude --agent codex [--dry-run]
  install_hooks.py --agent gemini --uninstall

The hook script is copied to ~/.config/resumaker/bin/enqueue.py so it keeps
working even if the skill is reinstalled elsewhere. Each settings file is backed
up to <file>.bak before it is changed. Entries are recognised by the marker
"resumaker" in the command, so re-running is idempotent.
"""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "resumaker"
BIN = CONFIG_DIR / "bin" / "enqueue.py"

TARGETS = {
    # agent: (settings file, handler extras, note)
    "claude": (Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude")) / "settings.json", {}, None),
    "codex": (Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "hooks.json", {"timeout": 3},
              "Codex 需要在 CLI 里运行 /hooks 审核并信任这个新 hook，之后才会生效。"),
    "gemini": (Path.home() / ".gemini" / "settings.json", {"name": "resumaker-harvest", "timeout": 3000}, None),
}


def command(agent):
    return f'python3 "{BIN}" --agent {agent}'


def is_ours(group):
    return any("resumaker" in h.get("command", "") for h in group.get("hooks", []))


def apply(agent, uninstall, dry_run):
    path, extras, note = TARGETS[agent]
    try:
        settings = json.loads(path.read_text()) if path.exists() else {}
    except json.JSONDecodeError as e:
        return {"agent": agent, "ok": False, "error": f"{path} 不是纯 JSON（{e}），请手动添加",
                "snippet": {"hooks": {"SessionEnd": [{"hooks": [{"type": "command", "command": command(agent), **extras}]}]}}}

    hooks = settings.setdefault("hooks", {})
    groups = [g for g in hooks.get("SessionEnd", []) if not is_ours(g)]
    removed = len(hooks.get("SessionEnd", [])) - len(groups)
    if not uninstall:
        groups.append({"hooks": [{"type": "command", "command": command(agent), **extras}]})
    if groups:
        hooks["SessionEnd"] = groups
    else:
        hooks.pop("SessionEnd", None)
        if not hooks:
            settings.pop("hooks")

    result = {"agent": agent, "ok": True, "file": str(path),
              "action": "uninstall" if uninstall else ("update" if removed else "install")}
    if note and not uninstall:
        result["note"] = note
    if dry_run:
        result["dry_run"] = True
        result["SessionEnd"] = hooks.get("SessionEnd", [])
        return result

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))
    path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n")
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", action="append", choices=list(TARGETS), required=True)
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not args.uninstall and not args.dry_run:
        BIN.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HERE / "enqueue.py", BIN)

    results = [apply(a, args.uninstall, args.dry_run) for a in args.agent]
    print(json.dumps({"hook_script": str(BIN), "results": results}, ensure_ascii=False, indent=2))
    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
