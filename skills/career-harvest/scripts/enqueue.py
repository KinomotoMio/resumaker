#!/usr/bin/env python3
"""SessionEnd hook: queue the finished session for career-harvest. Never blocks, never fails.

Claude Code, Codex and Gemini CLI all pass a JSON object on stdin with
`session_id`, `transcript_path` and `cwd`. We only append one line to
<vault>/.resumaker/harvest-queue.jsonl — reading and judging the transcript
happens later in career-harvest, outside the hook's time budget.
"""
import json
import os
import sys
import time
from pathlib import Path


def main():
    agent = sys.argv[sys.argv.index("--agent") + 1] if "--agent" in sys.argv else "unknown"
    try:
        event = json.load(sys.stdin)
    except Exception:
        return
    if not event.get("transcript_path"):
        return

    vault = os.environ.get("RESUMAKER_VAULT")
    if not vault:
        cfg = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "resumaker" / "config.json"
        try:
            vault = json.loads(cfg.read_text()).get("vault")
        except Exception:
            return
    if not vault:
        return

    state = Path(vault).expanduser() / ".resumaker"
    if not state.parent.exists():
        return
    state.mkdir(exist_ok=True)
    line = {
        "agent": agent,
        "session_id": event.get("session_id"),
        "transcript_path": event.get("transcript_path"),
        "cwd": event.get("cwd"),
        "reason": event.get("reason"),
        "queued_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    with open(state / "harvest-queue.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
