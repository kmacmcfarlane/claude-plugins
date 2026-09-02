"""Reasoning-ledger helpers. The ledger is session-addressed (never in a repo):
an append-only markdown file of one-line entries the live session writes as it
works, so an end-of-window checkpoint is a delta rather than a reconstruction.

Line grammar:  - <D|X|C|U|R|Q|P> <text> [-> path]
  D decided  X rejected  C corrected  U unverified  R refused  Q open question
  P pointer (machine-written: commits, investigation writes)
"""
import os, time
import lib_context as L

KINDS = "DXCURQP"


def append(session_id, kind, text, ref=None):
    if kind not in KINDS or not text:
        return False
    line = f"- {kind} {text.strip()}"
    if ref:
        line += f" -> {ref}"
    try:
        p = L.ledger_path(session_id)
        new = not os.path.exists(p) or os.path.getsize(p) == 0
        with open(p, "a") as fh:
            if new:
                fh.write(f"# ledger {session_id}\n")
            fh.write(line + "\n")
        return True
    except Exception:
        return False


def epoch_header(session_id, epoch_n, tokens):
    try:
        with open(L.ledger_path(session_id), "a") as fh:
            fh.write(f"\n## epoch {epoch_n} — {time.strftime('%F %T')} — {tokens:,} tok\n")
    except Exception:
        pass


def tail(session_id, max_chars=4000):
    """Newest-first bounded read for re-injection after compaction."""
    try:
        lines = open(L.ledger_path(session_id), errors="replace").read().splitlines()
    except Exception:
        return ""
    out, size = [], 0
    for ln in reversed(lines):
        if size + len(ln) > max_chars:
            break
        out.append(ln)
        size += len(ln) + 1
    return "\n".join(reversed(out))
