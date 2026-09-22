#!/usr/bin/env python3
"""Stand the context gate down: record that a checkpoint completed this epoch.

Run by the checkpoint skill (Step 4b), right after it writes the manifest:
    python3 mark_checkpoint.py "$CLAUDE_CODE_SESSION_ID"
DUE stops re-firing, HARD stops blocking, and a deferred auto-compaction is
allowed to proceed on its next attempt. Refuses (exit 1, nothing written)
when the session has no state file: a live session always has one, so that
means a mistyped id, not a session to create.

First it stamps the manifest's machine fields (stamp_manifest), so the model
never types them. The manifest it stamps is THIS SESSION'S OWN, at
${CLAUDE_CONFIG_DIR:-~/.claude}/claude-kit/handoff/<safe_sid>/HANDOFF.md,
when that file exists; otherwise - transitionally, while the checkpoint skill
still writes the repo file - the legacy repo manifest the rehydration hook
reads from the current directory (8cc2-F3b-2). In it the frontmatter lines
`written:` (UTC now), `head:` (git rev-parse --short HEAD of the manifest's
repo), `branch:`, `top:` (that repo's toplevel, else the cwd - the manifest
no longer lives in the repo it describes, so it records it) and `session:`
(this session's id: $CLAUDE_CODE_SESSION_ID, else the id given) are
rewritten, or added before the closing `---` when absent. Nothing else in the
file changes, byte for byte; the new file replaces the old atomically, and
not at all if the file changed while it was being stamped. Stamping makes a
new manifest VERSION (its sha changes) owned by this session through
`session:`, so it runs before anything can pin a version - the
SessionEnd(clear) link, a Read adoption - and a link made after it pins the
stamped version.

It stamps only a manifest this checkpoint plausibly just wrote:
  - modified within STAMP_WINDOW_S (an older file was not written by this
    checkpoint's Step 4b; stamping it would pass stale memory off as fresh);
  - with frontmatter;
  - and, on the LEGACY repo manifest only - a file every session in the
    checkout shares, so another may own it - whose `session:`
    - is empty, or not a session-id token (a placeholder such as
      `<stamped>`), or this session - $CLAUDE_CODE_SESSION_ID when set (an id
      given that differs from it grants nothing), else the id given;
    - or names a session in its lineage (the /clear predecessor or fork
      parent) or the author of the version it adopted by a full Read, AND the
      file is no longer the version that link pinned or that Read adopted: it
      was rewritten since, with the id copied. Untouched, it is still that
      session's (a fork parent may be live) and is left alone.
    Any other session's id may be a concurrent peer's manifest: that is left
    untouched, and the warning below names it.
On the store path that claim test collapses: the file is this session's by
path, so no other session can be writing it, and a `session:` copied from a
predecessor's manifest is simply corrected. The path is built from
this_session(sid, environ) - $CLAUDE_CODE_SESSION_ID first - so an argv id
that differs from the env's still names nothing. Ownership by path is only
as good as the path, so it is checked by realpath (own_store_manifest): a
symlink planted at that file, or at the <sid>/ directory above it, resolves
out of the store, is not this session's manifest, and is left to the legacy
arm's claim test rather than rewritten as ours.
A manifest this session already stamped and nobody rewrote since (the same
head, branch, top and session, and an mtime within STAMP_TOUCH_S of its
`written:`) is left as it is, so repeated marks do not re-date it.
Stamping never fails the checkpoint: every problem is a warning, and the gate
record (L.mark_checkpoint) is exactly what it would be without a manifest.

Then checks the author id (session_warnings: stderr, exit still 0 - the
checkpoint is recorded either way, and a HARD-blocked session must be able
to stand the gate down): the id given should be $CLAUDE_CODE_SESSION_ID when
that is set, and the manifest resolved the same way the stamp resolves it -
this session's own file, else the legacy repo one - should carry it in
`session:`. The manifest's `session:` is the
key rehydrate.py re-injects by, so an id copied from the manifest being
replaced (the predecessor's, after /clear or a handoff) makes this session's
own manifest foreign to it and hands its goal to the other session.
"""
import glob, os, re, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_context as L

STAMP_WINDOW_S = 30 * 60
STAMP_TOUCH_S = 3
WRITE_BUDGET = 6000
STAMP_KEYS = ("written", "head", "branch", "top", "session")
_KEY_LINE = re.compile(rb"(written|head|branch|top|session)[ \t]*:")


def this_session(sid, environ=None):
    env = os.environ if environ is None else environ
    return env.get("CLAUDE_CODE_SESSION_ID") or sid


def store_manifest_path(sid):
    """`sid`'s own rehydration manifest,
    ${CLAUDE_CONFIG_DIR:-~/.claude}/claude-kit/handoff/<safe_sid>/HANDOFF.md.
    Named through safe_sid, so a garbled or hostile id cannot name a path
    outside the store; the directory is created by the writer, never here.

    L.manifest_path once 8cc2-F3b-1 has landed, and the same path computed
    from the same pieces until it does - this feature is built on a main that
    does not yet carry the store helper. Delete the fallback with that merge."""
    fn = getattr(L, "manifest_path", None)
    if fn is not None:
        return fn(sid)
    return os.path.join(L._base_dir(), "claude-kit", "handoff",
                        L.safe_sid(sid), "HANDOFF.md")


def own_store_manifest(path, sid):
    """Whether `path` really IS `sid`'s own manifest in the store, and not a
    symlink - at the file, or at the <sid>/ directory above it - pointing at
    something else. The store directory is shared by every session that reads
    this config dir, so the path existing is not the same as it being ours,
    and it is ownership by path that collapses the claim test: without this,
    a planted link would make an arbitrary file "ours" and have it rewritten
    with no warning. Decided on realpath, so a link out of the store resolves
    out of the store and fails. A path that fails is not this session's
    manifest and falls through to the legacy arm and its claim test.

    L.manifest_sid once 8cc2-F3b-1 has landed, and the same comparison until
    it does; delete the fallback with that merge (store_manifest_path)."""
    try:
        fn = getattr(L, "manifest_sid", None)
        if fn is not None:
            return fn(path) == L.safe_sid(sid)
        root = os.path.realpath(os.path.join(L._base_dir(), "claude-kit",
                                             "handoff"))
        return os.path.realpath(path) == os.path.join(root, L.safe_sid(sid),
                                                      "HANDOFF.md")
    except Exception:
        return False


class TargetUnreadable(Exception):
    """A manifest that was found but could not be read, carrying its path so
    the warning can name it: the target is not interchangeable, so a read
    failure is reported against that file and nothing else is stamped."""
    def __init__(self, path, exc):
        super().__init__(path, exc)
        self.path, self.exc = path, exc


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


def _claimable(owner, sha, want, st):
    """Whether this checkpoint may put `want` over `session: owner` on the
    version with hash `sha`. Only the LEGACY repo manifest reaches this test:
    it is the one manifest several sessions share. This session's own store
    file is ours by path, so the test collapses there (8cc2-F3b-2).

    `want` is this session ($CLAUDE_CODE_SESSION_ID,
    else the id given): an id given that is not the env's grants nothing. A
    lineage session or the author of the adopted version is claimable only
    when the file is no longer the version that link pinned or that Read
    adopted - it was rewritten since; untouched, it is still that session's
    (and already this one's through the pin), so it is left alone."""
    if not isinstance(owner, str) or not owner or not L._SAFE_SID.fullmatch(owner):
        return True                     # none, or a placeholder
    if owner == want:
        return True
    for e in L.lineage_of(st):
        if e["sid"] == owner and e["manifest"] and e["manifest"]["sha"] != sha:
            return True
    ad = st.get("manifest_adopted") if isinstance(st, dict) else None
    return isinstance(ad, dict) and ad.get("owner") == owner \
        and isinstance(ad.get("sha"), str) and ad["sha"] != sha


def _own_stamp(fm, fields, mtime):
    """Whether the file already carries this stamp, untouched since: `head`,
    `branch`, `top` and `session` are what it would write, and the mtime is
    within STAMP_TOUCH_S after `written:` (the mark step writes both at once; a
    rewrite moves the mtime, and a copied stamp is older). Then a repeated
    mark leaves it as it is instead of re-dating it."""
    import rehydrate as R
    t = R.stamp_epoch(fm.get("written"))
    return t is not None and 0 <= mtime - t < STAMP_TOUCH_S and all(
        fm.get(k) == fields[k]
        for k in ("head", "branch", "top", "session") if k in fields)


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


def stamp_target(want, cwd):
    """The manifest this session stamps, and reports on: (path, top, raw text,
    is_store). `want` is this session (this_session), so the store file is the
    one no other session can name.

    This session's own store manifest when that file exists AND is really
    ours (own_store_manifest: a link planted at that path is not), else the
    legacy repo manifest, read exactly as it is today - the transitional
    fallback that keeps checkpoints working end to end while the checkpoint
    skill still writes the repo file (8cc2-F3b-2; it goes away with the legacy
    read). `top` is the repo the stamp records: the cwd's git toplevel, else
    the cwd. (None, top, None, False) when neither manifest exists; raises
    TargetUnreadable when this session's own manifest cannot be read - no
    other file stands in for it."""
    import rehydrate as R
    p = store_manifest_path(want)
    if os.path.exists(p) and own_store_manifest(p, want):
        try:
            with open(p, errors="replace") as fh:
                text = fh.read()
        except OSError as e:
            raise TargetUnreadable(p, e)
        return p, (R.git(cwd, "rev-parse", "--show-toplevel") or cwd), text, True
    path, top, text = R.read_manifest(cwd)
    return path, top, text, False


def stamp_manifest(sid, cwd=None, environ=None, now=None):
    """(stdout lines, warning lines). Never raises."""
    out, warn = [], []
    try:
        import rehydrate as R
        want = this_session(sid, environ)
        path, top, text, is_store = stamp_target(want, cwd or os.getcwd())
        if not path:
            out.append(f"no rehydration manifest to stamp "
                       f"({store_manifest_path(want)}, else .claude-sandbox/"
                       f"HANDOFF.md or HANDOFF.md at the repo root)")
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
        fm = R.front_matter(text)
        v = R.manifest_version(text, fm)
        # The store file is ours by path - no other session can be named by
        # it - so only the shared legacy repo manifest is claim-tested.
        if not is_store and \
                not _claimable(v["owner"], v["sha"], want, L.load_state(want)):
            warn.append(f"mark_checkpoint.py: not stamped: {path} names another "
                        f"session in `session:` and was not rewritten by this one "
                        f"(see below).")
            return out, warn
        head = R.git(top, "rev-parse", "--short", "HEAD")
        fields = {"written": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
                  "top": top, "session": want}
        if head:
            fields["head"] = head
            branch = R.git(top, "rev-parse", "--abbrev-ref", "HEAD")
            if branch:
                fields["branch"] = branch
        if _own_stamp(fm, fields, fst.st_mtime):
            out.append(f"{path} already stamped (written {fm.get('written')}); "
                       f"not rewritten since, so left as it is")
            return out, warn
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
                   f"top {top}, session {want})")
    except TargetUnreadable as e:
        warn.append(f"mark_checkpoint.py: not stamped: {e.path}, this session's "
                    f"own manifest and the file Step 4b writes, could not be "
                    f"read ({type(e.exc).__name__}); nothing else was stamped "
                    f"in its place. Fix the file, then run this again.")
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
        # The same manifest the stamp step targets, so the warning is about
        # the file that is actually this session's (8cc2-F3b-2).
        want = this_session(sid, environ)
        path, _top, text, _is_store = stamp_target(want, cwd or os.getcwd())
        if path:
            owner = R.manifest_version(text)["owner"]
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
