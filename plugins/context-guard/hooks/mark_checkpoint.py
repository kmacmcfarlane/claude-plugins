#!/usr/bin/env python3
"""Stand the context gate down: record that a checkpoint completed this epoch.

Run by the checkpoint skill (Step 4b), right after it drafts the manifest:
    python3 mark_checkpoint.py --from <draft> "$CLAUDE_CODE_SESSION_ID"
    python3 mark_checkpoint.py "$CLAUDE_CODE_SESSION_ID"   (no draft: stamp only)
DUE stops re-firing, HARD stops blocking, and a deferred auto-compaction is
allowed to proceed on its next attempt. Refuses (exit 1, nothing written)
when the session has no state file: a live session always has one, so that
means a mistyped id, not a session to create.

With `--from <draft>` it first INSTALLS the draft (install_draft): the
skill writes the manifest with the Write tool into its session scratchpad,
which the harness allows without a prompt, and this script - a plain Bash
command - copies it to the session's own store path. The Write tool never
targets the store: that path is in the config dir, outside the project and
inside a protected directory, so writing it there prompts in default and
acceptEdits modes and is denied in dontAsk, which stalls an unattended
checkpoint (8cc2-F3b-4 r1). The copy uses the same id resolution and the same
ownership-by-realpath guard as the stamp, creates the store directories 0700,
and replaces the file atomically; a failed install stamps nothing and leaves
the draft as it was. handoff_path.py stays a lookup that writes nothing.

Then it stamps the manifest's machine fields (stamp_manifest), so the model
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
as good as the path, so it is checked by realpath (L.own_store_manifest): a
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
    outside the store; the directory is created by the writer, never here."""
    return L.manifest_path(sid)


def own_store_manifest(path, sid):
    """L.own_store_manifest, the store's ownership-by-path test, shared with
    rehydrate's read path so both sides of the store answer "ours?" the same
    way (0836). Kept under this name for the docstrings above that cite it."""
    return L.own_store_manifest(path, sid)


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


DRAFT_MAX = 256 * 1024


class InstallRefused(Exception):
    """A draft that was not installed; the message says why."""


def install_draft(draft, sid, environ=None, now=None):
    """Copy the manifest drafted at `draft` to this session's own store path,
    L.manifest_path(this_session(sid, environ)), and return that path. Raises
    InstallRefused, having written nothing to the store, when the draft is
    missing or unreadable, older than STAMP_WINDOW_S (the stamp's own "this
    checkpoint wrote it" rule, judged by the DRAFT: the installed copy is
    always new, so without this a previous checkpoint's draft - a Write that
    failed or was skipped - would be sealed as this one's), the id is not a
    plain one, or the store path (the
    file, or the <sid>/ directory above it) is not really ours - a link
    planted there resolves out of place and is refused, never written
    through. The store directories are created 0700; the file is written to a
    temp file in its own directory and os.replace'd in, 0600. The draft is
    only read."""
    want = this_session(sid, environ)
    if not L._SAFE_SID.fullmatch(want or ""):
        raise InstallRefused("the session id is not a plain id")
    try:
        if not os.path.isfile(draft):
            raise InstallRefused(f"no draft manifest at {draft}")
        if os.path.getsize(draft) > DRAFT_MAX:
            raise InstallRefused(f"the draft {draft} is over {DRAFT_MAX:,} bytes")
        age = (time.time() if now is None else now) - os.path.getmtime(draft)
        if age > STAMP_WINDOW_S:
            raise InstallRefused(f"the draft {draft} was last written "
                                 f"{int(age // 60)} min ago, so this checkpoint "
                                 f"did not write it; rewrite it (Step 4b)")
        with open(draft, "rb") as fh:
            data = fh.read(DRAFT_MAX + 1)
    except InstallRefused:
        raise
    except OSError as e:
        raise InstallRefused(f"the draft {draft} could not be read "
                             f"({type(e).__name__})")
    target = store_manifest_path(want)
    root = os.path.realpath(L.handoff_root())
    home = os.path.join(root, L.safe_sid(want))
    try:
        os.makedirs(root, mode=0o700, exist_ok=True)
        if not os.path.lexists(os.path.dirname(target)):
            os.mkdir(os.path.dirname(target), 0o700)
    except OSError as e:
        raise InstallRefused(f"the store directory for {target} could not be "
                             f"created ({type(e).__name__})")
    if os.path.realpath(os.path.dirname(target)) != home or \
            (os.path.lexists(target) and not own_store_manifest(target, want)):
        raise InstallRefused(f"{target} is not this session's own manifest "
                             f"(a link resolves out of place); nothing written")
    if os.path.lexists(target) and os.path.realpath(draft) == os.path.realpath(target):
        return target                  # already in place
    fd, tmp = tempfile.mkstemp(dir=home, prefix=".HANDOFF.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp, 0o600)
        os.replace(tmp, os.path.join(home, L.MANIFEST_NAME))
        tmp = None
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except OSError:
                pass
    if not own_store_manifest(target, want):
        raise InstallRefused(f"{target} is not this session's own manifest "
                             f"after the copy")
    return target


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
                            f"install it with `mark_checkpoint.py --from {p} "
                            f"<session_id>` (Step 4b).")
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
    draft = None
    usage = "usage: mark_checkpoint.py [--from <draft>] <session_id>"
    if len(argv) >= 2 and argv[1] == "--from":
        if len(argv) != 4:
            sys.exit(usage)
        draft, argv = argv[2], [argv[0], argv[3]]
    if len(argv) != 2 or argv[1].startswith("-"):
        # an id never starts with "-": that is a mistyped flag
        sys.exit(usage)
    sid = argv[1]
    if not os.path.exists(L.state_path(sid)):
        # A live session always has state (every prompt's gate hook writes it), so
        # a missing file means a mistyped id: refuse rather than stand down nothing.
        sys.exit(f"mark_checkpoint.py: no context-gate state for session "
                 f"{sid!r} (expected {L.state_path(sid)}); "
                 f"check the session id — nothing recorded.")
    # Stamp first, in its own guard: it must precede anything that pins a
    # version, and nothing it does may keep the gate from standing down.
    installed, refused = [], []
    if draft is not None:
        try:
            target = install_draft(draft, sid)
            installed.append(f"installed {draft} as {target}")
            try:
                # The ledger's pointer to the manifest: the Write that used to
                # record it (ledger_pointer.py) now writes only the draft.
                import ledger
                ledger.append(this_session(sid), "P", "installed HANDOFF.md",
                              ref=target)
            except Exception:
                pass
        except InstallRefused as e:
            refused.append(f"mark_checkpoint.py: not installed, so not stamped: "
                           f"{e}. Fix it and run this again.")
        except Exception as e:
            refused.append(f"mark_checkpoint.py: not installed, so not stamped: "
                           f"{type(e).__name__}. Run this again.")
    try:
        # A draft that did not install stamps nothing: whatever store file is
        # there is an older one, not what this checkpoint wrote.
        stamped, warns = stamp_manifest(sid) if not refused else ([], refused)
    except Exception:
        stamped, warns = [], []
    stamped = installed + stamped
    st = L.mark_checkpoint(sid)
    print(f"checkpoint recorded for epoch {L.epoch(st)}")
    for s in stamped:
        print(s)
    for w in warns + session_warnings(sid):
        print(w, file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv)
