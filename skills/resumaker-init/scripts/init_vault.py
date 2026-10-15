#!/usr/bin/env python3
"""Create (or adopt) a Resumaker career vault and register it in the user config.

Usage:
  init_vault.py --path ~/career [--git] [--ignore-in /path/to/repo]
  init_vault.py --show            # print the currently resolved vault

Never overwrites existing files: an existing directory is "adopted" and only
missing skeleton files are added.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "vault"
CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "resumaker" / "config.json"


def load_config():
    try:
        return json.loads(CONFIG.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def resolve_vault():
    env = os.environ.get("RESUMAKER_VAULT")
    if env:
        return Path(env).expanduser(), "env RESUMAKER_VAULT"
    vault = load_config().get("vault")
    if vault:
        return Path(vault).expanduser(), str(CONFIG)
    local = Path.cwd() / "career"
    if (local / "VAULT.md").exists():
        return local, "./career"
    return None, None


def copy_skeleton(dest: Path):
    added = []
    for src in TEMPLATE.rglob("*"):
        rel = src.relative_to(TEMPLATE)
        target = dest / rel
        if src.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
            added.append(str(rel))
    (dest / ".resumaker").mkdir(exist_ok=True)
    return added


def ensure_ignored(repo: Path, vault: Path):
    try:
        rel = vault.resolve().relative_to(repo.resolve())
    except ValueError:
        return None
    gi = repo / ".gitignore"
    line = f"/{rel.as_posix()}/"
    existing = gi.read_text().splitlines() if gi.exists() else []
    if line in existing:
        return line
    with gi.open("a") as f:
        if existing and existing[-1].strip():
            f.write("\n")
        f.write(f"# Resumaker 履历库（个人数据，不提交）\n{line}\n")
    return line


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", help="vault directory to create or adopt")
    ap.add_argument("--git", action="store_true", help="git init the vault as its own repository")
    ap.add_argument("--ignore-in", help="add the vault to this repository's .gitignore")
    ap.add_argument("--no-config", action="store_true", help="do not write ~/.config/resumaker/config.json")
    ap.add_argument("--show", action="store_true", help="print the resolved vault and exit")
    args = ap.parse_args()

    if args.show:
        vault, via = resolve_vault()
        print(json.dumps({"vault": str(vault) if vault else None, "via": via, "config": str(CONFIG)}, ensure_ascii=False))
        return

    if not args.path:
        ap.error("--path is required")

    vault = Path(args.path).expanduser().resolve()
    adopted = vault.exists() and any(vault.iterdir())
    vault.mkdir(parents=True, exist_ok=True)
    added = copy_skeleton(vault)

    result = {"vault": str(vault), "adopted_existing": adopted, "added": added}

    if args.git and not (vault / ".git").exists():
        subprocess.run(["git", "init", "-q"], cwd=vault, check=True)
        result["git_init"] = True

    if args.ignore_in:
        result["gitignore_line"] = ensure_ignored(Path(args.ignore_in).expanduser(), vault)

    if not args.no_config:
        cfg = load_config()
        cfg["vault"] = str(vault)
        CONFIG.parent.mkdir(parents=True, exist_ok=True)
        CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
        result["config"] = str(CONFIG)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
