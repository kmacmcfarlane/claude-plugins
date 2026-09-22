#!/usr/bin/env python3
"""Stand the context gate down: record that a checkpoint completed this epoch.

Run by the checkpoint skill (Step 4b), right after it writes the manifest:
    python3 mark_checkpoint.py "$CLAUDE_CODE_SESSION_ID"
DUE stops re-firing, HARD stops blocking, and a deferred auto-compaction is
allowed to proceed on its next attempt. Refuses (exit 1, nothing written)
when the session has no state file: a live session always has one, so that
means a mistyped id, not a session to create.

First it stamps the manifest's machine fields (stamp_manifest), so the model
never types them: in the manifest the rehydration hook reads from the current
directory, the frontmatter lines `written:` (UTC now), `head:` (git rev-parse
--short HEAD of the manifest's repo), `branch:` and `session:` (this
session's id: $CLAUDE_CODE_SESSION_ID, else the id given) are rewritten, or
added before the closing `---` when absent. Nothing else in the file changes,
byte for byte; the new file replaces the old atomically, and not at all if
the file changed while it was being stamped. Stamping makes a new manifest
VERSION (its sha changes) owned by this session through `session:`, so it
runs before anything can pin a version - the SessionEnd(clear) link, a Read
adoption - and a link made after it pins the stamped version.

It stamps only a manifest this checkpoint plausibly just wrote:
  - modified within STAMP_WINDOW_S (an older file was not written by this
    checkpoint's Step 4b; stamping it would pass stale memory off as fresh);
  - with frontmatter;
  - whose `session:` is empty, not a session-id token (a placeholder such as
    `<stamped>`), this session, a session in its lineage (the /clear
    predecessor or fork parent whose manifest it replaced) or the author of
    the version it adopted by a full Read. Any other session's id may be a
    concurrent peer's manifest: that is left untouched, and the warning below
    names it.
Stamping never fails the checkpoint: every problem is a warning, and the gate
record (L.mark_checkpoint) is exactly what it would be without a manifest.

Then checks the author id (session_warnings: stderr, exit still 0 - the
checkpoint is recorded either way, and a HARD-blocked session must be able
to stand the gate down): the id given should be $CLAUDE_CODE_SESSION_ID when
that is set, and the manifest the rehydration hook reads from the current
directory should carry it in `session:`. The manifest's `session:` is the
key rehydrate.py re-injects by, so an id copied from the manifest being
replaced (the predecessor's, after /clear or a handoff) makes this session's
own manifest foreign to it and hands its goal to the other session.
"""
import glob, os, re, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L

STAMP_WINDOW_S = 30 * 60
WRITE_BUDGET = 6000
STAMP_KEYS = ("written", "head", "branch", "session")
_KEY_LINE = re.compile(rb"(written|head|branch|session)[ \t]*:")


def this_session(sid, environ=None):
    env = os.environ if environ is None else environ
    return env.get("CLAUDE_CODE_SESSION_ID") or sid


def restamp(raw, fields):
    """`raw` (bytes) with each frontmatter line `key: ...` for a key in
    `fields` replaced by `key: value`, and any key not present added before
    the closing `---`; every other byte unchanged (line endings kept). None
    when there is no frontmatter (same delimiters as rehydrate.front_matter)."""
    lines = raw.splitlines(keepends=True)
    if not lines or lines[0].strip() != b"---":
        return None
    close = next((i for i in range(1, len(lines)) if lines[i].strip() == b"---"),
                 None)
    if close is None:
        return None
    first_eol = lines[0][len(lines[0].rstrip(b"\r\n")):] or b"\n"
    seen, out = set(), [lines[0]]
    for ln in lines[1:close]:
        m = _KEY_LINE.match(ln)
        key = m.group(1).decode() if m else None
        if key in fields:
            eol = ln[len(ln.rstrip(b"\r\n")):]
            out.append(f"{key}: {fields[key]}".encode() + eol)
            seen.add(key)
        else:
            out.append(ln)
    out += [f"{k}: {fields[k]}".encode() + first_eol
            for k in STAMP_KEYS if k in fields and k not in seen]
    return b"".join(out + lines[close:])


def _claimable(owner, sid, want, st):
    """Whether this checkpoint may put its own id over `session: owner`."""
    if not isinstance(owner, str) or not owner or not L._SAFE_SID.fullmatch(owner):
        return True                     # none, or a placeholder
    if owner in (sid, want):
        return True
    if any(e["sid"] == owner for e in L.lineage_of(st)):
        return True
    ad = st.get("manifest_adopted") if isinstance(st, dict) else None
    return isinstance(ad, dict) and ad.get("owner") == owner


def _write_atomic(real, raw, new, mode):
    """Replace `real` with `new` unless it no longer holds `raw`. -> bool."""
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(real), prefix=".HANDOFF.",
                               suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(new)
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp, mode)
        with open(real, "rb") as fh:
            if fh.read() != raw:
                return False
        os.replace(tmp, real)
        tmp = None
        return True
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except OSError:
                pass


def _scratchpad_manifests(want):
    """A HANDOFF.md at the top of this session's scratchpad (the wrong place:
    the rehydration hook never reads it). Not deeper: scratch repos and test
    fixtures live below it. Never raises."""
    try:
        base = os.environ.get("CLAUDE_CODE_TMPDIR") or tempfile.gettempdir()
        return sorted(glob.glob(os.path.join(
            glob.escape(base), "claude-*", "*", glob.escape(L.safe_sid(want)),
            "scratchpad", "HANDOFF.md")))[:3]
    except Exception:
        return []


def stamp_manifest(sid, cwd=None, environ=None, now=None):
    """(stdout lines, warning lines). Never raises."""
    out, warn = [], []
    try:
        import rehydrate as R
        want = this_session(sid, environ)
        path, top, text = R.read_manifest(cwd or os.getcwd())
        if not path:
            out.append("no rehydration manifest to stamp (.claude-sandbox/"
                       "HANDOFF.md, else HANDOFF.md at the repo root)")
            for p in _scratchpad_manifests(want):
                warn.append(f"mark_checkpoint.py: warning: {p} is in the session "
                            f"scratchpad, where the rehydration hook never looks; "
                            f"write the manifest per Step 4b instead.")
            return out, warn
        body = text.split("\n---", 1)[-1] if text.startswith("---") else text
        if len(body) > WRITE_BUDGET:
            warn.append(f"mark_checkpoint.py: warning: {path} body is {len(body)} "
                        f"chars, over the {WRITE_BUDGET:,}-char write budget; the "
                        f"hook will trim it.")
        if not L._SAFE_SID.fullmatch(want or ""):
            warn.append("mark_checkpoint.py: not stamped: the session id is not "
                        "a plain id.")
            return out, warn
        real = os.path.realpath(path)
        with open(real, "rb") as fh:
            raw = fh.read()
        fst = os.stat(real)
        now = time.time() if now is None else now
        age = now - fst.st_mtime
        if age > STAMP_WINDOW_S:
            warn.append(f"mark_checkpoint.py: not stamped: {path} was last written "
                        f"{int(age // 60)} min ago, so this checkpoint did not write "
                        f"it; rewrite it (Step 4b), then run this again.")
            return out, warn
        owner = R.manifest_version(text)["owner"]
        if not _claimable(owner, sid, want, L.load_state(want)):
            warn.append(f"mark_checkpoint.py: not stamped: {path} names another "
                        f"session in `session:` (see below).")
            return out, warn
        head = R.git(top, "rev-parse", "--short", "HEAD")
        fields = {"written": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
                  "session": want}
        if head:
            fields["head"] = head
            branch = R.git(top, "rev-parse", "--abbrev-ref", "HEAD")
            if branch:
                fields["branch"] = branch
        new = restamp(raw, fields)
        if new is None:
            warn.append(f"mark_checkpoint.py: not stamped: {path} has no "
                        f"frontmatter (see references/handoff-format.md).")
            return out, warn
        if new != raw and not _write_atomic(real, raw, new, fst.st_mode & 0o7777):
            warn.append(f"mark_checkpoint.py: not stamped: {path} changed while "
                        f"being stamped; run this again.")
            return out, warn
        out.append(f"stamped {path} (written {fields['written']}, head "
                   f"{fields.get('head', '?')}, branch {fields.get('branch', '?')}, "
                   f"session {want})")
    except Exception as e:
        warn.append(f"mark_checkpoint.py: not stamped: {type(e).__name__}.")
    return out, warn


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
                    f"the id of the manifest it replaced - and run this again, or "
                    f"the rehydration hook treats it as another session's.")
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
    # Stamp first, in its own guard: it must precede anything that pins a
    # version, and nothing it does may keep the gate from standing down.
    try:
        stamped, warns = stamp_manifest(sid)
    except Exception:
        stamped, warns = [], []
    st = L.mark_checkpoint(sid)
    print(f"checkpoint recorded for epoch {L.epoch(st)}")
    for s in stamped:
        print(s)
    for w in warns + session_warnings(sid):
        print(w, file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv)
