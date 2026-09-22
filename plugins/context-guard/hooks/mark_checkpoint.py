#!/usr/bin/env python3
"""Stand the context gate down: record that a checkpoint completed this epoch.

Run by the checkpoint skill (Step 4b):
    python3 mark_checkpoint.py "$CLAUDE_CODE_SESSION_ID"
DUE stops re-firing, HARD stops blocking, and a deferred auto-compaction is
allowed to proceed on its next attempt. Refuses (exit 1, nothing written)
when the session has no state file: a live session always has one, so that
means a mistyped id, not a session to create.

Then checks the author id (session_warnings: stderr, exit still 0 - the
checkpoint is recorded either way, and a HARD-blocked session must be able
to stand the gate down): the id given should be $CLAUDE_CODE_SESSION_ID when
that is set, and the manifest the rehydration hook reads from the current
directory should carry it in `session:`. The manifest's `session:` is the
key rehydrate.py re-injects by, so an id copied from the manifest being
replaced (the predecessor's, after /clear or a handoff) makes this session's
own manifest foreign to it and hands its goal to the other session.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L


def session_warnings(sid, cwd=None, environ=None):
    """Lines to warn with (empty when all is well). Never raises."""
    out = []
    try:
        env = os.environ if environ is None else environ
        cur = env.get("CLAUDE_CODE_SESSION_ID") or ""
        if cur and cur != sid:
            out.append(f"mark_checkpoint.py: warning: the id given ({sid}) is not "
                       f"$CLAUDE_CODE_SESSION_ID ({cur}), this session's id.")
        import rehydrate as R
        path, _top, text = R.read_manifest(cwd or os.getcwd())
        if path:
            owner = R.manifest_version(text)["owner"]
            want = cur or sid
            if owner and owner != want:
                shown = owner if L._SAFE_SID.fullmatch(owner) else "another id"
                out.append(
                    f"mark_checkpoint.py: warning: {path} has `session: {shown}`, "
                    f"not this session ({want}). If this checkpoint wrote that "
                    f"manifest, set `session:` to $CLAUDE_CODE_SESSION_ID - never "
                    f"the id of the manifest it replaced - or the rehydration hook "
                    f"treats it as another session's.")
    except Exception:
        pass
    return out


def main(argv):
    if len(argv) != 2:
        sys.exit("usage: mark_checkpoint.py <session_id>")
    sid = argv[1]
    if not os.path.exists(L.state_path(sid)):
        # A live session always has state (every prompt's gate hook writes it), so
        # a missing file means a mistyped id: refuse rather than stand down nothing.
        sys.exit(f"mark_checkpoint.py: no context-gate state for session "
                 f"{sid!r} (expected {L.state_path(sid)}); "
                 f"check the session id — nothing recorded.")
    st = L.mark_checkpoint(sid)
    print(f"checkpoint recorded for epoch {L.epoch(st)}")
    for w in session_warnings(sid):
        print(w, file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv)
