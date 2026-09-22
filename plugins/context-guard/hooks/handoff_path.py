#!/usr/bin/env python3
"""Print this session's own rehydration manifest path, and nothing else:

    python3 handoff_path.py --path ["$CLAUDE_CODE_SESSION_ID"]

The manifest is one file per session, at
${CLAUDE_CONFIG_DIR:-~/.claude}/claude-kit/handoff/<safe_sid>/HANDOFF.md
(8cc2-F3b), so its path can no longer be guessed from the repo: the checkpoint
skill writes it at that path (Step 4b) and prints it, and a successor reads it
there. This is what answers "where do I write it?" and "where is it?".

It is a lookup, not a hook: it writes nothing, creates no directory, reads no
state and never records a checkpoint - `mark_checkpoint.py` alone stands the
gate down, and its argv contract is untouched. `--path` is required so the
command says what it does at the call site. The session id is optional:
$CLAUDE_CODE_SESSION_ID wins whenever it is set, exactly as the mark step
resolves it, so an id passed that differs from the env's names nothing.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Two pure functions: the path rule and the env-first session id. Importing
# this module runs no hook and touches no state.
from mark_checkpoint import store_manifest_path, this_session

USAGE = "usage: handoff_path.py --path [<session_id>]"


def main(argv):
    if not 2 <= len(argv) <= 3 or argv[1] != "--path":
        sys.exit(USAGE)
    want = this_session(argv[2] if len(argv) == 3 else "")
    if not want:
        sys.exit("handoff_path.py: no session id: pass one, or set "
                 "$CLAUDE_CODE_SESSION_ID.")
    print(store_manifest_path(want))


if __name__ == "__main__":
    main(sys.argv)
