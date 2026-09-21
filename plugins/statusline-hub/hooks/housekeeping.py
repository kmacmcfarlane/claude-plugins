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
  than CACHE_DAYS, logs older than LOG_DAYS, orphaned temp files.

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
        n += _prune_files(registry.cache_dir(), CACHE_DAYS * 86400, now, (".json",),
                          recurse=True)
        n += _prune_files(registry.log_dir(), LOG_DAYS * 86400, now, (".log",))
        n += _prune_files(registry.run_dir(), TMP_STALE_S, now, (".tmp",))
    except Exception:
        pass
    return n
