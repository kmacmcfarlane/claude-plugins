"""statusline-hub housekeeping, run from the SessionStart hook - never from a render.

- prune() / prune_tmp(): sensor records untouched for PRUNE_DAYS, and temp
  files a killed writer left behind. VENDORED verbatim from the statusline
  plugin's hooks/sensor.py (a plugin may not import another's code), so a
  record the hub's tee wrote is pruned by the same rule whether or not the
  statusline plugin is installed; both share the one PRUNE_STAMP, so on a
  machine with both the pass runs once a day, whichever gets there first.
  tests/test_parity.py fails when the copy drifts.
- prune_hub(): the hub's own dirs - hooks.d manifests not refreshed for
  registry.STALE_DAYS (a plugin that stopped refreshing its manifest was
  uninstalled or disabled: its hook is dead; a manifest that says
  "pinned": true is kept), last-good cache entries older
  than CACHE_DAYS, logs older than LOG_DAYS, segment files no render will
  show again (past expires_at, or untouched for registry.SEGMENT_AGE_MAX_S;
  never one a producer replaced or touched mid-pass), orphaned temp files
  (in the segment dirs, any dot-file an hour old). The wrap
  record (wrap.json) is never pruned: it holds the user's own entry.

Nothing here raises.
"""
import json, os, re, stat, time

import registry
from tee import safe_sid, sensor_dir

# -- VENDORED from statusline hooks/sensor.py (verbatim) --

PRUNE_DAYS = 30             # a sensor record untouched this long is deleted
PRUNE_EVERY_S = 86400       # prune at most this often (the PRUNE_STAMP mtime)
TMP_STALE_S = 3600          # an orphaned temp file older than this is deleted
PRUNE_STAMP = ".pruned"
_TMP = re.compile(r"\..+\.\d+\.[0-9a-f]{12}\.tmp")  # _mkstemp's names


def prune_tmp(d, now=None, max_age=TMP_STALE_S):
    """Delete the orphaned temp files _mkstemp names (.<name>.<pid>.<hex>.tmp)
    in dir d older than max_age - a writer killed between create and
    replace. Regular files only; a live write is milliseconds old. Returns
    how many went. Never raises."""
    n = 0
    now = time.time() if now is None else now
    try:
        with os.scandir(d) as it:
            for e in it:
                try:
                    if _TMP.fullmatch(e.name) and e.is_file(follow_symlinks=False) and \
                            now - e.stat(follow_symlinks=False).st_mtime > max_age:
                        os.unlink(e.path)
                        n += 1
                except OSError:
                    continue
    except OSError:
        pass
    return n


def prune(keep=None, now=None, days=PRUNE_DAYS):
    """Delete sensor records not modified for `days` and stale temp files in
    the sensor dir, except `keep`'s (the current session's) record. Runs at
    most once per PRUNE_EVERY_S: the PRUNE_STAMP file's mtime says when it
    last ran (a stamp that is not a regular file - a planted symlink, say -
    is removed and replaced, never followed). Returns how many files went,
    or None when it was not yet due. Never raises."""
    try:
        now = time.time() if now is None else now
        d = sensor_dir()
        if os.path.islink(d) or not os.path.isdir(d):
            return 0
        stamp = os.path.join(d, PRUNE_STAMP)
        try:
            st = os.lstat(stamp)
            if not stat.S_ISREG(st.st_mode):
                os.unlink(stamp)
            elif 0 <= now - st.st_mtime < PRUNE_EVERY_S:
                return None
        except FileNotFoundError:
            pass
        keep_name = safe_sid(keep) + ".json" if keep else None
        n = prune_tmp(d, now)
        with os.scandir(d) as it:
            for e in it:
                try:
                    if not e.name.endswith(".json") or e.name == keep_name or \
                            not e.is_file(follow_symlinks=False):
                        continue
                    if now - e.stat(follow_symlinks=False).st_mtime > days * 86400:
                        os.unlink(e.path)
                        n += 1
                except OSError:
                    continue
        fd = os.open(stamp, os.O_WRONLY | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
        try:
            os.utime(fd if os.utime in os.supports_fd else stamp, (now, now))
        finally:
            os.close(fd)
        return n
    except Exception:
        return 0

# -- end VENDORED --

CACHE_DAYS = 1      # a last-good entry is shown for 60 s at most; a day-old one is litter
LOG_DAYS = 14


def _prune_files(d, older_than, now, suffixes, recurse=False):
    """Delete regular files (never following a symlink) in dir d whose name
    ends in one of `suffixes` and whose mtime is more than `older_than`
    seconds ago; with `recurse`, one level of subdirs too, removing a subdir
    left empty. Returns how many files went. Never raises."""
    n = 0
    try:
        if os.path.islink(d) or not os.path.isdir(d):
            return 0
        n += prune_tmp(d, now)
        with os.scandir(d) as it:
            for e in it:
                try:
                    if recurse and e.is_dir(follow_symlinks=False):
                        n += _prune_files(e.path, older_than, now, suffixes)
                        try:
                            os.rmdir(e.path)  # only succeeds when empty
                        except OSError:
                            pass
                        continue
                    if e.name.endswith(suffixes) and e.is_file(follow_symlinks=False) and \
                            now - e.stat(follow_symlinks=False).st_mtime > older_than:
                        os.unlink(e.path)
                        n += 1
                except OSError:
                    continue
    except OSError:
        pass
    return n


def _pinned(path):
    """Whether the manifest at path says "pinned": true (a capped read that
    never follows a symlink). Never raises."""
    try:
        raw, _ = registry._read_capped(path, registry.MANIFEST_MAX)
        d = json.loads(raw.decode("utf-8")) if raw is not None else None
        return isinstance(d, dict) and d.get("pinned") is True
    except Exception:
        return False


def prune_manifests(now=None):
    """Delete hooks.d manifests not modified for registry.STALE_DAYS, except
    pinned ones, plus orphaned temp files. Returns how many went. Never
    raises."""
    n = 0
    try:
        now = time.time() if now is None else now
        d = registry.hooks_dir()
        if registry.private_dir_problem(d):
            return 0
        n += prune_tmp(d, now)
        with os.scandir(d) as it:
            for e in it:
                try:
                    if e.name.endswith(".json") and e.is_file(follow_symlinks=False) and \
                            now - e.stat(follow_symlinks=False).st_mtime > \
                            registry.STALE_DAYS * 86400 and not _pinned(e.path):
                        os.unlink(e.path)
                        n += 1
                except OSError:
                    continue
    except Exception:
        pass
    return n


def _dead_segment(path, now):
    """The stat of the segment file at path when it is one no render will
    show again - untouched for registry.SEGMENT_AGE_MAX_S, or past its
    expires_at - else None. A file that cannot be read or parsed is judged by
    its age alone; one replaced while it was being judged is not judged.
    Never raises."""
    try:
        st = os.lstat(path)
        if not stat.S_ISREG(st.st_mode):
            return None
        if now - st.st_mtime > registry.SEGMENT_AGE_MAX_S:
            return st
        raw, rst = registry._read_capped(path, registry.SEGMENT_MAX)
        if _ident(rst) != _ident(st):
            return None
        d = json.loads(raw.decode("utf-8")) if raw is not None else None
        exp = registry._number(d.get("expires_at")) if isinstance(d, dict) else None
        return st if exp is not None and now >= exp else None
    except Exception:
        return None


def _ident(st):
    """What says a file is still the one judged: the same inode (a producer's
    os.replace makes a new one) with the same mtime (its os.utime keep-up)."""
    return (st.st_dev, st.st_ino, st.st_mtime_ns)


def _unlink_if_same(path, st):
    """Delete path only when it is still the file `st` describes, so a
    producer's write that landed after the judgment survives. Raises
    OSError."""
    if _ident(os.lstat(path)) != _ident(st):
        return False
    os.unlink(path)
    return True


def _prune_dot_temps(d, now, max_age=TMP_STALE_S):
    """Delete the regular dot-files in dir d older than max_age: the temp
    files a producer's tempfile.mkstemp left when it was killed between
    create and replace (hook-contract.md § 11 has producers name them with
    a leading dot, in any shape - prune_tmp's _TMP shape is only the hub's
    own). The age gate spares a live producer's temp, which is milliseconds
    old. Returns how many went. Never raises."""
    n = 0
    try:
        with os.scandir(d) as it:
            for e in it:
                try:
                    if e.name.startswith(".") and e.is_file(follow_symlinks=False) and \
                            now - e.stat(follow_symlinks=False).st_mtime > max_age:
                        os.unlink(e.path)
                        n += 1
                except OSError:
                    continue
    except OSError:
        pass
    return n


def prune_segments(now=None):
    """Delete segment files no render will show again (see _dead_segment),
    in the drop dir and one level of provider dirs, removing a provider dir
    left empty, plus orphaned temp files (any dot-file over TMP_STALE_S old).
    A file is deleted only while it is still the one judged dead (same
    inode and mtime), so a producer's rewrite racing the pass survives. A
    dir that fails the trust check is left alone. Returns how many files
    went. Never raises."""
    n = 0
    try:
        now = time.time() if now is None else now
        d = registry.segments_dir()
        if registry.private_dir_problem(d):
            return 0
        with os.scandir(d) as it:
            subs = [e.path for e in it
                    if e.is_dir(follow_symlinks=False) and not e.name.startswith(".")]
        for sub in [d] + subs:
            if sub != d and registry.private_dir_problem(sub):
                continue
            n += _prune_dot_temps(sub, now)
            with os.scandir(sub) as it:
                for e in it:
                    try:
                        if e.name.endswith(".json") and not e.name.startswith("."):
                            st = _dead_segment(e.path, now)
                            if st is not None and _unlink_if_same(e.path, st):
                                n += 1
                    except OSError:
                        continue
            if sub != d:
                try:
                    # only succeeds when empty; a producer that loses its dir
                    # here retries (hook-contract.md § 11)
                    os.rmdir(sub)
                except OSError:
                    pass
    except Exception:
        pass
    return n


def prune_hub(now=None):
    """Prune the hub's dirs (see the module doc). Does nothing to a dir that
    fails the registry's trust check (a symlink, someone else's). Returns how
    many files went. Never raises."""
    n = 0
    try:
        now = time.time() if now is None else now
        if registry.private_dir_problem(registry.hub_dir()):
            return 0
        n += prune_manifests(now)
        n += prune_tmp(registry.hub_dir(), now)   # a killed wrap-record write
        n += _prune_files(registry.cache_dir(), CACHE_DAYS * 86400, now, (".json",),
                          recurse=True)
        n += _prune_files(registry.log_dir(), LOG_DAYS * 86400, now, (".log",))
        n += _prune_files(registry.run_dir(), TMP_STALE_S, now, (".tmp",))
        n += prune_segments(now)
    except Exception:
        pass
    return n
