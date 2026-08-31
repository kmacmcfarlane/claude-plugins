#!/usr/bin/env python3
"""PostToolUse(Bash|Write|Edit): free ledger pointers.

A commit or an investigation write is already durable; the ledger records
WHERE, so the checkpoint's inventory is a lookup rather than a recall. Fires
in subagents and forks too (PostToolUse reaches them), so it returns {} when
agent_id/agent_type is present — a subagent's actions are not this session's
reasoning trail.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ledger

COMMIT = re.compile(r"\bgit\b[^|;&]*\bcommit\b")
SHA = re.compile(r"\[[\w./-]+ ([0-9a-f]{7,40})\]")


def main():
    try:
        inp = json.load(sys.stdin)
    except Exception:
        print(json.dumps({})); return
    if inp.get("agent_id") or inp.get("agent_type"):
        print(json.dumps({})); return

    sid = inp.get("session_id", "unknown")
    tool = inp.get("tool_name")
    ti = inp.get("tool_input") or {}

    if tool == "Bash" and COMMIT.search(ti.get("command") or ""):
        resp = inp.get("tool_response") or {}
        out = resp.get("stdout") if isinstance(resp, dict) else str(resp)
        m = SHA.search(out or "")
        first = next((l for l in (out or "").splitlines() if l.strip()), "")[:120]
        ledger.append(sid, "P", f"commit {m.group(1) if m else '?'}: {first}",
                      ref=inp.get("cwd"))
    elif tool in ("Write", "Edit"):
        path = ti.get("file_path") or ""
        if "/investigations/" in path or path.endswith(("HANDOFF.md", "INDEX.md")):
            ledger.append(sid, "P", f"wrote {os.path.basename(path)}", ref=path)
    print(json.dumps({}))


main()
