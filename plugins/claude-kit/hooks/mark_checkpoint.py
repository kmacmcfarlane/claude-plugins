#!/usr/bin/env python3
"""Stand the context gate down: record that a checkpoint completed this epoch.

Run by the checkpoint skill (Step 4b):  python3 mark_checkpoint.py <session_id>
DUE stops re-firing, HARD stops blocking, and a deferred auto-compaction is
allowed to proceed on its next attempt.
"""
import sys
import lib_context as L

if len(sys.argv) != 2:
    sys.exit("usage: mark_checkpoint.py <session_id>")
st = L.mark_checkpoint(sys.argv[1])
print(f"checkpoint recorded for epoch {L.epoch(st)}")
