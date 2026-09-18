#!/usr/bin/env python3
"""Stand the context gate down: record that a checkpoint completed this epoch.

Run by the checkpoint skill (Step 4b):  python3 mark_checkpoint.py <session_id>
DUE stops re-firing, HARD stops blocking, and a deferred auto-compaction is
allowed to proceed on its next attempt. Refuses (exit 1, nothing written)
when the session has no state file: a live session always has one, so that
means a mistyped id, not a session to create.
"""
import os, sys
import lib_context as L

if len(sys.argv) != 2:
    sys.exit("usage: mark_checkpoint.py <session_id>")
if not os.path.exists(L.state_path(sys.argv[1])):
    # A live session always has state (every prompt's gate hook writes it), so
    # a missing file means a mistyped id: refuse rather than stand down nothing.
    sys.exit(f"mark_checkpoint.py: no context-gate state for session "
             f"{sys.argv[1]!r} (expected {L.state_path(sys.argv[1])}); "
             f"check the session id — nothing recorded.")
st = L.mark_checkpoint(sys.argv[1])
print(f"checkpoint recorded for epoch {L.epoch(st)}")
