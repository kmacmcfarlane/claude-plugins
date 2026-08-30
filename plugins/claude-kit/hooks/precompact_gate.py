#!/usr/bin/env python3
"""PreCompact (auto): convert the first automatic compaction into a decision.

Blocks at most ONCE per session. Per the hooks reference, blocking a compaction
that fired *proactively* is free -- the conversation simply continues
uncompacted -- but blocking one that fired to recover from a context-limit
error the API already returned makes the in-flight request FAIL. Hook input
cannot distinguish the two, so we never block twice: the second attempt always
proceeds. One decision point, no wedged session.

Manual /compact is never blocked; that is already the operator deciding.
"""
import json, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L


def git(cwd, *args):
    try:
        return subprocess.run(("git", "-C", cwd) + args, capture_output=True,
                              text=True, timeout=5).stdout.strip()
    except Exception:
        return ""


def main():
    try:
        inp = json.load(sys.stdin)
    except Exception:
        print(json.dumps({})); return

    sid = inp.get("session_id", "unknown")
    cwd = inp.get("cwd") or os.getcwd()
    st = L.load_state(sid)

    dirty = git(cwd, "status", "--porcelain")
    head = git(cwd, "log", "--oneline", "-1")
    tok, win, pct = L.depth(inp.get("transcript_path", ""))

    st.update(last_compact_trigger=inp.get("trigger"), at=time.strftime("%F %T"),
              cwd=cwd, head=head, uncommitted=dirty.splitlines(),
              tokens=tok, pct=round(pct, 1))

    if inp.get("trigger") != "auto" or st.get("compact_blocked"):
        L.save_state(sid, st)
        print(json.dumps({})); return

    st["compact_blocked"] = True
    L.save_state(sid, st)

    n = len(dirty.splitlines())
    sys.stderr.write(
        "AUTO-COMPACT DEFERRED ONCE by the claude-kit context gate.\n\n"
        "STOP. Do not start or continue new work. Invoke the `checkpoint` skill now\n"
        "and follow it. Facts for that walkthrough:\n"
        f"  context : {pct:.0f}% full ({tok:,} of {win:,} tokens)\n"
        f"  cwd     : {cwd}\n"
        f"  HEAD    : {head or '(none)'}\n"
        f"  dirty   : {n} uncommitted file(s)\n\n"
        "The NEXT auto-compact will NOT be blocked, so treat this as the last\n"
        "cheap moment to get state onto disk.\n")
    sys.exit(2)


main()
