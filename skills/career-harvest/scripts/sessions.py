#!/usr/bin/env python3
"""Find agent sessions worth harvesting and condense them into readable digests.

Usage:
  sessions.py pending [--scan] [--since 14d] [--agents claude,codex,gemini]
      List sessions not harvested yet: everything queued by the SessionEnd hook,
      plus (with --scan) transcripts found on disk modified within --since.
  sessions.py digest <transcript_path> [--agent claude|codex|gemini] [--max-chars 24000]
      Print a compact, secret-redacted digest: what the user asked, what the agent
      said, which tools ran, which files changed, which commits were made.
  sessions.py mark <session_id> [<session_id> ...] [--skip]
      Record sessions as harvested (or skipped) so they are not offered again.

State lives in <vault>/.resumaker/: harvest-queue.jsonl (written by enqueue.py)
and harvest-state.json (processed session ids).
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "resumaker" / "config.json"
HOME = Path.home()
LOCATIONS = {
    "claude": (Path(os.environ.get("CLAUDE_CONFIG_DIR", HOME / ".claude")) / "projects", "*/*.jsonl"),
    "codex": (Path(os.environ.get("CODEX_HOME", HOME / ".codex")) / "sessions", "**/rollout-*.jsonl"),
    "gemini": (HOME / ".gemini" / "tmp", "*/chats/session-*.json"),
}
SECRET = re.compile(
    r"(sk-[A-Za-z0-9_\-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9\-]{10,}"
    r"|eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"
    r"|(?i:(?:password|passwd|secret|token|api[_-]?key)\s*[:=]\s*)\S+)"
)
NOISE = re.compile(
    r"^\s*(<(system-reminder|command-|local-command|environment_context|user_instructions|recommended_plugins"
    r"|app-context|permissions|turn_aborted|INSTRUCTIONS)|# AGENTS\.md instructions|Caveat: The messages below)", re.I)
COMMIT_M = re.compile(r"git commit[^\n]*?-m\s+(['\"])(.+?)\1")
COMMIT_HEREDOC = re.compile(r"git commit[^\n]*<<-?\s*'?(\w+)'?\s*\n\s*(.+)")


# ── vault & state ───────────────────────────────────────
def resolve_vault():
    if os.environ.get("RESUMAKER_VAULT"):
        return Path(os.environ["RESUMAKER_VAULT"]).expanduser()
    try:
        return Path(json.loads(CONFIG.read_text())["vault"]).expanduser()
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        pass
    local = Path.cwd() / "career"
    return local if (local / "VAULT.md").exists() else None


def state_dir():
    vault = resolve_vault()
    if not vault:
        sys.exit(json.dumps({"error": "找不到履历库，先运行 resumaker-init"}, ensure_ascii=False))
    d = vault / ".resumaker"
    d.mkdir(parents=True, exist_ok=True)
    return vault, d


def load_state(d):
    try:
        return json.loads((d / "harvest-state.json").read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {"done": {}, "last_scan": None}


def save_state(d, state):
    (d / "harvest-state.json").write_text(json.dumps(state, ensure_ascii=False, indent=1))


# ── transcript parsing ──────────────────────────────────
def guess_agent(path):
    p = str(path)
    if "/.codex/" in p or Path(p).name.startswith("rollout-"):
        return "codex"
    if "/.gemini/" in p or p.endswith(".json"):
        return "gemini"
    return "claude"


def blocks_text(content):
    if isinstance(content, str):
        return [content]
    out = []
    for b in content or []:
        if isinstance(b, dict) and b.get("type") in ("text", "input_text", "output_text") or (isinstance(b, dict) and "text" in b and "type" not in b):
            out.append(b.get("text", ""))
    return out


def events_claude(path):
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("isSidechain"):
            continue
        t, msg = d.get("type"), d.get("message") or {}
        if t == "user":
            content = msg.get("content")
            if isinstance(content, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
                continue
            for s in blocks_text(content):
                yield "user", s, d.get("timestamp")
        elif t == "assistant":
            for b in msg.get("content") or []:
                if b.get("type") == "text":
                    yield "agent", b.get("text", ""), d.get("timestamp")
                elif b.get("type") == "tool_use":
                    yield "tool", (b.get("name", ""), b.get("input") or {}), d.get("timestamp")


def events_codex(path):
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") != "response_item":
            continue
        p = d.get("payload") or {}
        if p.get("type") == "message" and p.get("role") in ("user", "assistant"):
            for s in blocks_text(p.get("content")):
                yield ("user" if p["role"] == "user" else "agent"), s, d.get("timestamp")
        elif p.get("type") in ("function_call", "custom_tool_call", "local_shell_call"):
            args = p.get("arguments") or p.get("input") or p.get("action") or ""
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {"input": args}
            yield "tool", (p.get("name", p.get("type")), args), d.get("timestamp")


def events_gemini(path):
    data = json.load(open(path, encoding="utf-8", errors="replace"))
    for m in data.get("messages", []):
        t = m.get("type")
        if t == "user":
            for s in blocks_text(m.get("content")):
                yield "user", s, m.get("timestamp")
        elif t in ("gemini", "model", "assistant"):
            for s in blocks_text(m.get("content")):
                yield "agent", s, m.get("timestamp")
            for tc in m.get("toolCalls") or []:
                yield "tool", (tc.get("name", ""), tc.get("args") or {}), m.get("timestamp")


PARSERS = {"claude": events_claude, "codex": events_codex, "gemini": events_gemini}


def tool_summary(name, args):
    """One short line per tool call; collect edited files and commit messages."""
    if not isinstance(args, dict):
        args = {"input": str(args)}
    cmd = args.get("command") or args.get("cmd") or args.get("input") or ""
    if isinstance(cmd, list):
        cmd = " ".join(map(str, cmd))
    path = args.get("file_path") or args.get("path") or args.get("absolute_path") or ""
    if cmd:
        return f"{name}: {str(cmd).splitlines()[0][:160]}", path, str(cmd)
    return f"{name}: {path}"[:200], path, ""


def digest(path, agent, max_chars):
    agent = agent or guess_agent(path)
    lines, files, commits, tools = [], [], [], {}
    first_ts = last_ts = None
    for kind, payload, ts in PARSERS[agent](path):
        first_ts = first_ts or ts
        last_ts = ts or last_ts
        if kind == "tool":
            summary, fpath, cmd = tool_summary(*payload)
            name = payload[0]
            tools[name] = tools.get(name, 0) + 1
            if fpath and fpath not in files and any(k in name.lower() for k in ("edit", "write", "replace", "patch", "create")):
                files.append(fpath)
            if "git commit" in cmd:
                m = COMMIT_HEREDOC.search(cmd) or COMMIT_M.search(cmd)
                if m and not m.group(2).startswith("$("):
                    commits.append(m.group(2).strip()[:160])
            if "apply_patch" in name or "*** Begin Patch" in cmd:
                for f in re.findall(r"\*\*\* (?:Update|Add) File: ([^\n\\]+)", cmd):
                    if f not in files:
                        files.append(f)
            continue
        text = payload.strip()
        if not text or NOISE.match(text):
            continue
        limit = 1500 if kind == "user" else 900
        if len(text) > limit:
            text = text[:limit] + " …[截断]"
        lines.append(f"[{'用户' if kind == 'user' else 'Agent'}] {text}")

    head = [
        f"# 会话摘要 · {agent} · {Path(path).name}",
        f"时间：{first_ts} → {last_ts}",
        f"工具调用：{', '.join(f'{k}×{v}' for k, v in sorted(tools.items(), key=lambda x: -x[1])[:12]) or '无'}",
        f"改动文件：{', '.join(files[:30]) or '无'}",
        f"提交：{' | '.join(commits[:10]) or '无'}",
        "",
    ]
    body = "\n\n".join(lines)
    if len(body) > max_chars:  # 保留开头（需求）和结尾（结果），中间省略
        half = max_chars // 2
        body = body[:half] + "\n\n…[中间省略]…\n\n" + body[-half:]
    return SECRET.sub("[已脱敏]", "\n".join(head) + body)


def session_cwd(path, agent):
    """Working directory of a session, read from the transcript head (claude/codex)."""
    if agent == "gemini":
        return None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for _, line in zip(range(40), f):
                d = json.loads(line)
                cwd = d.get("cwd") or (d.get("payload") or {}).get("cwd")
                if cwd:
                    return cwd
    except (OSError, json.JSONDecodeError):
        pass
    return None


def peek(path, agent):
    """First meaningful user request, for cheap triage before a full digest."""
    try:
        for kind, payload, _ in PARSERS[agent](path):
            if kind == "user" and payload.strip() and not NOISE.match(payload):
                return " ".join(payload.split())[:100]
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        pass
    return ""


# ── commands ────────────────────────────────────────────
def parse_since(s):
    m = re.fullmatch(r"(\d+)([dh])", s)
    if not m:
        raise SystemExit("--since 格式如 14d 或 12h")
    return int(m.group(1)) * (86400 if m.group(2) == "d" else 3600)


def cmd_pending(args):
    vault, d = state_dir()
    state = load_state(d)
    done = state["done"]
    agents = args.agents.split(",")
    found = {}

    q = d / "harvest-queue.jsonl"
    if q.exists():
        for line in q.read_text().splitlines():
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            sid = e.get("session_id")
            if sid and sid not in done and e.get("transcript_path") and Path(e["transcript_path"]).exists():
                found[sid] = {"agent": e.get("agent"), "session_id": sid, "transcript_path": e["transcript_path"],
                              "cwd": e.get("cwd"), "via": "hook"}

    if args.scan:
        cutoff = time.time() - parse_since(args.since)
        for agent in agents:
            root, pattern = LOCATIONS[agent]
            if not root.exists():
                continue
            for p in root.glob(pattern):
                try:
                    mtime = p.stat().st_mtime
                except OSError:
                    continue
                sid = p.stem.split("rollout-")[-1] if agent == "codex" else p.stem
                if agent == "codex":
                    sid = sid[-36:]
                if mtime < cutoff or sid in done or sid in found:
                    continue
                if time.time() - mtime < 600:  # 可能还在进行中
                    continue
                found[sid] = {"agent": agent, "session_id": sid, "transcript_path": str(p), "via": "scan",
                              "cwd": session_cwd(p, agent),
                              "modified": time.strftime("%Y-%m-%d %H:%M", time.localtime(mtime)), "size_kb": p.stat().st_size // 1024}
        state["last_scan"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save_state(d, state)

    items = [x for x in found.values() if not str(x.get("cwd") or x["transcript_path"]).startswith(str(vault))]
    for x in items:
        x["first_request"] = peek(x["transcript_path"], x.get("agent") or guess_agent(x["transcript_path"]))
    print(json.dumps({"vault": str(vault), "pending": items}, ensure_ascii=False, indent=2))


def cmd_mark(args):
    _, d = state_dir()
    state = load_state(d)
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    for sid in args.ids:
        state["done"][sid] = {"at": now, "result": "skipped" if args.skip else "harvested"}
    save_state(d, state)
    print(json.dumps({"marked": args.ids}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pending")
    p.add_argument("--scan", action="store_true")
    p.add_argument("--since", default="14d")
    p.add_argument("--agents", default="claude,codex,gemini")
    g = sub.add_parser("digest")
    g.add_argument("path")
    g.add_argument("--agent", choices=list(PARSERS))
    g.add_argument("--max-chars", type=int, default=24000)
    m = sub.add_parser("mark")
    m.add_argument("ids", nargs="+")
    m.add_argument("--skip", action="store_true")
    args = ap.parse_args()

    if args.cmd == "pending":
        cmd_pending(args)
    elif args.cmd == "digest":
        print(digest(args.path, args.agent, args.max_chars))
    else:
        cmd_mark(args)


if __name__ == "__main__":
    main()
