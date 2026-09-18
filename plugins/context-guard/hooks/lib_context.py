"""Shared state and depth accounting for the context-guard context-gate hooks.

Depth sources, in order of preference:
1. EXACT - written by the status line (the statusline plugin; its data
   contract is that plugin's install-statusline references/sensor-contract.md),
   which receives
   context_window.used_percentage and context_window_size from Claude Code on
   every render. Hooks never get those fields in their own input, so the status
   line doubles as the sensor. Two records are read (sensor()): the statusline
   plugin's neutral sensor file,
   ${CLAUDE_CONFIG_DIR:-~/.claude}/statusline/sensor/<safe_sid>.json (v1:
   `exact`, `rate_limits`; a record whose `v` is not 1 is treated as absent),
   and the legacy `exact` block in this plugin's own state file (written by
   context-guard's deprecated statusline.py until the compat release). The
   one with the larger `exact.at` wins; ties go to the sensor file. The
   sensor file is read only when it is a regular file (opened O_NONBLOCK, so
   a FIFO planted at the path cannot hang a hook), and an `exact.at` more than
   FUTURE_SKEW_S in the future is rejected: it would otherwise read as fresh,
   and gate as exact, until the clock caught up.
2. INFERRED - from the transcript's per-message `usage` blocks (the numbers the
   API charged), window guessed from the session's peak. A guess can be wrong
   in either direction (live-fired 2026-09-16: a 1M session with a stale exact
   record was scored against 200K and HARD-blocked), so an inferred depth may
   warn but never block; context_warn.py requires source "exact" to exit 2.
   An exact record that has gone stale (older than EXACT_MAX_AGE_S) still
   pins the window - a session's window never shrinks with time - and its
   token count is a floor for the re-derived one. A new epoch (reset_epoch)
   demotes the record to window-only: a fresh record written seconds before
   a compaction or /clear describes the OLD fill and must not gate the new
   epoch, and the status line may not have re-rendered yet. context-guard
   never writes the sensor file: _reset stamps `epoch_at` in its own state,
   and any record with `at <= epoch_at` (from either path) is read as
   window-only - which also covers a render whose payload predates the
   compaction but whose write lands after it.

State is per session under $CLAUDE_CONFIG_DIR/claude-kit/context-gate/, and is
EPOCH-aware: a compaction (PostCompact) or /clear starts a new epoch, resetting
advisories, DUE/HARD accounting and the deferred-compaction flag. The v1 hooks
latched once per session, which is why a session's second fill got no warning.

Writers never load-modify-save the file bare: update_state(sid, fn) runs the
read-modify-write under a per-session advisory lock (fcntl.flock, bounded by
LOCK_TIMEOUT_S; on timeout, error, or a platform without fcntl it proceeds
unlocked - today's behaviour - rather than block a session). save_state writes
a unique temp file in the same dir (created O_EXCL, as tempfile.mkstemp does,
without the ~5 ms tempfile import on every status-line render) and
os.replace()s it, so a racing writer can never install a torn file. A session
id becomes a file name only when it is a safe token; anything else is hashed,
so no id escapes the dir. The lock file is opened O_NOFOLLOW, so a planted
symlink cannot make it create a file outside the dir.

publish_gauge() (called by the SessionStart rehydrate hook) writes
claude-kit/context-gate/gauge.json (v1): the threshold ANCHORS and the gauge
labels, for the statusline plugin to colour and label its gauge by the same
policy the gate enforces. It is generated from ANCHORS, the constant
thresholds() interpolates, so the two can never disagree.

sweep_stale() (called by the SessionStart rehydrate hook) removes the dotfiles
a killed writer leaves behind: temp files older than a day, and lock files of
sessions whose state file is over 30 days old or gone. At most once a day.
"""
import json, math, os, re, stat, time
try:
    import fcntl
except ImportError:  # not POSIX: no lock, unique temp names still hold
    fcntl = None

DEFAULTS = (200_000, 1_000_000)
EXACT_MAX_AGE_S = 600

# The gate's threshold policy, in REMAINING tokens: (window, due, hard)
# anchors, sorted by window; linear between, clamped outside. thresholds()
# interpolates it and publish_gauge() serialises it - the single source.
ANCHORS = ((200_000, 70_000, 40_000), (1_000_000, 150_000, 60_000))
# The words the status line shows beside its gauge under `due` and `hard`.
GAUGE_LABELS = {"due": "checkpoint DUE", "hard": "HARD gate"}
GAUGE_V = 1
SENSOR_V = 1
# A sensor `exact.at` further ahead of now than this is a bad clock or a bad
# record, never a fresh reading.
FUTURE_SKEW_S = 60


def _base_dir():
    """${CLAUDE_CONFIG_DIR:-~/.claude}: an empty value counts as unset."""
    return os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR") or "~/.claude")


def _state_dir():
    d = os.path.join(_base_dir(), "claude-kit", "context-gate")
    os.makedirs(d, exist_ok=True)
    return d


LOCK_TIMEOUT_S = 0.2
_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_NONBLOCK = getattr(os, "O_NONBLOCK", 0)
_SAFE_SID = re.compile(r"[A-Za-z0-9_-][A-Za-z0-9._-]{0,127}")


def safe_sid(session_id):
    """The file-name form of a session id. A safe token (the UUIDs Claude Code
    issues) passes unchanged; anything else - a path separator, a leading dot,
    '..', over 128 chars, a non-string - becomes 'sid-<sha256 prefix>', so a
    hostile or garbled id can never name a path outside the state dir."""
    if not session_id:
        return "unknown"
    if isinstance(session_id, str) and _SAFE_SID.fullmatch(session_id):
        return session_id
    import hashlib  # lazily: only a malformed id pays for it
    raw = session_id if isinstance(session_id, str) else repr(session_id)
    return "sid-" + hashlib.sha256(raw.encode("utf-8", "replace")).hexdigest()[:32]


def state_path(session_id):
    return os.path.join(_state_dir(), safe_sid(session_id) + ".json")


def sensor_path(session_id):
    """The statusline plugin's sensor record for this session (read-only here;
    the status line is its only writer). The dir is not created."""
    return os.path.join(_base_dir(), "statusline", "sensor",
                        safe_sid(session_id) + ".json")


def gauge_path():
    return os.path.join(_state_dir(), "gauge.json")


def ledger_path(session_id):
    d = os.path.join(_base_dir(), "claude-kit", "ledger")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, safe_sid(session_id) + ".md")


def load_state(session_id):
    try:
        with open(state_path(session_id)) as f:
            st = json.load(f)
        return st if isinstance(st, dict) else {}
    except Exception:
        return {}


def _mkstemp(d, prefix):
    """tempfile.mkstemp's contract (a new file no other writer can share,
    mode 0600) at os-module cost."""
    for _ in range(100):
        name = os.path.join(d, f"{prefix}{os.getpid()}.{os.urandom(6).hex()}.tmp")
        try:
            return os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), name
        except FileExistsError:
            continue
    raise FileExistsError("no unique temp name")


def save_state(session_id, data):
    """Atomic write: a unique temp file in the same dir, then os.replace.
    Callers that modify existing state go through update_state instead."""
    tmp = None
    try:
        path = state_path(session_id)
        fd, tmp = _mkstemp(os.path.dirname(path), "." + safe_sid(session_id) + ".")
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=1)
        os.replace(tmp, path)
        tmp = None
    except Exception:
        pass
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except Exception:
                pass


def _acquire(session_id):
    """Take the session's advisory lock, waiting at most LOCK_TIMEOUT_S.
    Returns the locked fd, or None (no fcntl, timeout, any error): the caller
    then proceeds unlocked. Never raises. A lock won on an inode no longer at
    the path (sweep_stale unlinked it while this call waited) guards nothing,
    since the next opener creates a fresh file: it is dropped and the path is
    re-opened, within the same deadline."""
    if fcntl is None:
        return None
    fd = None
    try:
        path = os.path.join(_state_dir(), "." + safe_sid(session_id) + ".lock")
        deadline = time.monotonic() + LOCK_TIMEOUT_S
        while True:
            if fd is None:
                fd = os.open(path, os.O_RDWR | os.O_CREAT | _NOFOLLOW, 0o600)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                if _same_file(fd, path):
                    return fd
                os.close(fd)             # orphaned inode: its lock is void
                fd = None
                if time.monotonic() >= deadline:
                    break
            except (BlockingIOError, InterruptedError):
                if time.monotonic() >= deadline:
                    break
                time.sleep(0.002)
    except Exception:
        pass
    if fd is not None:
        try:
            os.close(fd)
        except Exception:
            pass
    return None


def _same_file(fd, path):
    """Whether the open fd is still the file at path (same device and inode)."""
    try:
        a, b = os.fstat(fd), os.stat(path)
        return (a.st_dev, a.st_ino) == (b.st_dev, b.st_ino)
    except OSError:
        return False


def _release(fd):
    if fd is None:
        return
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    except Exception:
        pass
    try:
        os.close(fd)
    except Exception:
        pass


def update_state(session_id, fn):
    """Read-modify-write the session's state under its lock: load, fn(state)
    mutates it in place, save. Returns the saved state. Every writer uses this
    so a concurrent writer's keys are never overwritten with a stale copy.
    The lock wait is bounded; on timeout the update runs unlocked."""
    fd = _acquire(session_id)
    try:
        st = load_state(session_id)
        fn(st)
        save_state(session_id, st)
        return st
    finally:
        _release(fd)


TMP_MAX_AGE_S = 24 * 3600
LOCK_MAX_AGE_S = 30 * 24 * 3600
SWEEP_EVERY_S = 24 * 3600
_TMP_RE = re.compile(r"\.(.+)\.\d+\.[0-9a-f]+\.tmp")
_LOCK_RE = re.compile(r"\.(.+)\.lock")


def sweep_stale(keep=None, now=None):
    """Best-effort removal of orphaned dotfiles in the state dir: temp files
    (`.<sid>.<pid>.<hex>.tmp`, which a writer killed mid-save leaks) older than
    TMP_MAX_AGE_S, and lock files (`.<sid>.lock`) whose session's state file is
    older than LOCK_MAX_AGE_S - or gone, with the lock itself that old. The
    session `keep` is never touched, and a lock someone holds is skipped: it is
    removed only while this call holds it. Runs at most once per SWEEP_EVERY_S
    (a `.swept` stamp). Returns the names removed; never raises."""
    removed = []
    try:
        now = time.time() if now is None else now
        d = _state_dir()
        stamp = os.path.join(d, ".swept")
        try:
            if now - os.lstat(stamp).st_mtime < SWEEP_EVERY_S:
                return removed
        except OSError:
            pass
        _touch_stamp(stamp, now)
        skip = safe_sid(keep) if keep else None

        def age(p):
            try:
                return now - os.lstat(p).st_mtime
            except OSError:
                return None

        for name in os.listdir(d):
            if not name.startswith("."):
                continue
            p = os.path.join(d, name)
            try:
                m = _TMP_RE.fullmatch(name)
                if m:
                    a = age(p)
                    if m.group(1) != skip and a is not None and a > TMP_MAX_AGE_S:
                        os.unlink(p)
                        removed.append(name)
                    continue
                m = _LOCK_RE.fullmatch(name)
                if not m or m.group(1) == skip:
                    continue
                sa = age(os.path.join(d, m.group(1) + ".json"))
                if sa is None:
                    sa = age(p)
                if sa is None or sa <= LOCK_MAX_AGE_S:
                    continue
                if _unlink_unheld_lock(p):
                    removed.append(name)
            except Exception:
                continue
    except Exception:
        pass
    return removed


def _touch_stamp(stamp, now):
    """Create or re-date a stamp file without truncating and without
    following a symlink or blocking (O_NOFOLLOW, O_NONBLOCK: a planted link or
    a FIFO without a reader fails the open and the stamp is silently skipped). Returns True when the stamp was dated. Never
    raises."""
    fd = None
    try:
        fd = os.open(stamp, os.O_WRONLY | os.O_CREAT | _NOFOLLOW | _NONBLOCK,
                     0o600)
        os.utime(fd, (now, now))
        return True
    except Exception:
        return False
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except Exception:
                pass


def _unlink_unheld_lock(p):
    """Unlink lock file p only if its lock is free, holding it meanwhile."""
    if fcntl is None:
        return False
    fd = None
    try:
        fd = os.open(p, os.O_RDWR | _NOFOLLOW)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        os.unlink(p)
        return True
    except Exception:
        return False
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except Exception:
                pass


def epoch(state):
    return int(state.get("epoch", 0))


def reset_epoch(session_id, compact_summary=None):
    """New epoch: advisories and DUE/HARD accounting start over; the deferred
    flag clears; the checkpoint requirement re-arms. The ledger survives."""
    return update_state(session_id,
                        lambda st: _reset(st, compact_summary, session_id))


def _reset(st, compact_summary, session_id=None):
    # The fill the ending epoch reached, read under the lock before the demote
    # below drops it (postcompact_epoch logs it in the ledger's epoch header).
    # The status line's exact record (the fresher of the sensor file and the
    # legacy in-state block) is the source; the top-level `tokens` that
    # context_warn.decide() stores on every prompt (the depth it last scored,
    # exact or inferred) is the fallback. Read before epoch_at moves, which
    # would demote it.
    try:
        end = sensor(session_id, st) if session_id else (st.get("exact") or {})
        st["epoch_end_tokens"] = int(end.get("tokens") or st.get("tokens") or 0)
    except (TypeError, ValueError, AttributeError):
        st["epoch_end_tokens"] = 0
    st["epoch"] = epoch(st) + 1
    st.pop("compact_deferred", None)
    st.pop("due", None)
    st["prompt_n"] = 0
    # Any exact record stamped at or before this instant describes the old
    # epoch (sensor() demotes it): the sensor file, which context-guard never
    # writes, and a legacy block written back by a render that raced this reset.
    st["epoch_at"] = time.time()
    ex = st.get("exact") or {}
    if ex.get("window"):
        # Demote, don't stamp: the record's tokens/pct describe the epoch that
        # just ended, so a still-fresh one would HARD-block a 3% session until
        # the status line re-renders. With `at` zeroed and the tokens dropped,
        # depth() takes its existing stale path - the window survives as the
        # floor (a compaction never shrinks the model's window) and the count
        # comes from the post-boundary transcript alone, boundary line or not
        # (/clear starts a transcript with no compact_boundary). The next
        # status-line render overwrites the block with a fresh exact record.
        st["exact"] = {"window": int(ex["window"]), "at": 0}
    if compact_summary is not None:
        st["compact_summary"] = compact_summary[:20000]


def mark_checkpoint(session_id):
    def mark(st):
        st["checkpoint_epoch"] = epoch(st)
        st["checkpoint_at"] = time.strftime("%F %T")
    return update_state(session_id, mark)


def checkpointed_this_epoch(state):
    return state.get("checkpoint_epoch") == epoch(state)


def thresholds(window):
    """Action thresholds in REMAINING tokens, per threads/A-checkpoint-timing.md.

    Interpolated over ANCHORS - (200K -> due 70K, hard 40K) and (1M -> due
    150K, hard 60K) - linear between, clamped outside. A full checkpoint costs
    ~16-60K in the live window and one operator exchange is p90 ~20K, so
    `hard` is the floor below which only /checkpoint itself is affordable.
    """
    w = max(int(window or 0), 1)
    lo_w, lo_d, lo_h = ANCHORS[0]
    if w <= lo_w:
        return {"due": lo_d, "hard": lo_h}
    for hi_w, hi_d, hi_h in ANCHORS[1:]:
        if w < hi_w:
            f = (w - lo_w) / (hi_w - lo_w)
            return {"due": int(lo_d + f * (hi_d - lo_d)),
                    "hard": int(lo_h + f * (hi_h - lo_h))}
        lo_w, lo_d, lo_h = hi_w, hi_d, hi_h
    return {"due": lo_d, "hard": lo_h}


def gauge_record():
    """The gauge.json (v1) content, generated from ANCHORS and GAUGE_LABELS."""
    return {"v": GAUGE_V, "writer": "context-guard",
            "thresholds": {"unit": "tokens_remaining", "interp": "linear_clamped",
                           "anchors": [{"window": w, "due": d, "hard": h}
                                       for w, d, h in ANCHORS]},
            "labels": dict(GAUGE_LABELS)}


def publish_gauge():
    """Write gauge.json when it is missing, unreadable or differs from
    gauge_record(): a unique temp file, then os.replace, so a reader never
    sees a torn file. Returns True when it wrote. Never raises."""
    tmp = None
    try:
        want = gauge_record()
        path = gauge_path()
        try:
            with open(path) as f:
                if json.load(f) == want:
                    return False
        except Exception:
            pass
        fd, tmp = _mkstemp(os.path.dirname(path), ".gauge.")
        with os.fdopen(fd, "w") as f:
            json.dump(want, f, indent=1)
        os.replace(tmp, path)
        tmp = None
        return True
    except Exception:
        return False
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except Exception:
                pass


def read_usage(transcript_path):
    """Return (current_tokens, peak_tokens) from the transcript. Zero when unknown."""
    cur, peak, _ = scan_usage(transcript_path)
    return cur, peak


def scan_usage(transcript_path):
    """Return (current_tokens, peak_tokens, saw_boundary). `saw_boundary` is
    True when a compact_boundary was read: the current count then describes a
    new window and older state (a stale exact record) must not floor it."""
    if not transcript_path or not os.path.exists(transcript_path):
        return 0, 0, False
    cur = peak = 0
    boundary = False
    try:
        with open(transcript_path, errors="replace") as fh:
            for line in fh:
                if '"compact_boundary"' in line:
                    # Bug A (live-fired 2026-08-31): pre-boundary usage records
                    # described the OLD window; reading them after a compaction
                    # reported 62% used on a ~2% session. Keep peak (the model
                    # window did not change); reset current.
                    cur = 0
                    boundary = True
                    continue
                if '"usage"' not in line:
                    continue
                try:
                    u = (json.loads(line).get("message") or {}).get("usage")
                except Exception:
                    continue
                if not u:
                    continue
                t = sum(u.get(k) or 0 for k in
                        ("input_tokens", "cache_read_input_tokens",
                         "cache_creation_input_tokens"))
                if t:
                    cur = t
                    peak = max(peak, t)
    except Exception:
        return 0, 0, False
    return cur, peak, boundary


def window(peak, floor=0):
    """Guess the window from the session's peak usage. `floor` is a window that
    was once reported exactly (by the status line): the guess never returns
    less than it. CLAUDE_KIT_CONTEXT_WINDOW pins the window outright."""
    env = os.environ.get("CLAUDE_KIT_CONTEXT_WINDOW")
    if env and env.isdigit():
        return int(env)
    small, large = DEFAULTS
    guess = large if peak > small * 0.95 else small
    return max(guess, int(floor or 0))


def _finite(x):
    """x as a float when it is a real finite number (not a bool), else None."""
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return None
    x = float(x)
    return x if math.isfinite(x) else None


def read_json_file(path):
    """The JSON value in the regular file at path, or None when it is absent,
    unreadable, not JSON, or not a regular file. The open is O_NONBLOCK and the
    type is checked on the open fd before any read, so a FIFO, socket or
    device at the path can neither hang nor feed the caller. Never raises."""
    fd = None
    try:
        fd = os.open(path, os.O_RDONLY | _NONBLOCK)
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            return None
        with os.fdopen(fd, encoding="utf-8", errors="replace") as f:
            fd = None
            return json.load(f)
    except Exception:
        return None
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except Exception:
                pass


def sensor_record(session_id):
    """The status line's sensor record (the whole v1 dict: `exact`,
    `rate_limits`), or {} when it is absent, unreadable, not a regular file,
    not an object, or its `v` is not 1 - a newer version is never misread.
    Never raises."""
    rec = read_json_file(sensor_path(session_id))
    if not isinstance(rec, dict) or type(rec.get("v")) is not int \
            or rec["v"] != SENSOR_V:
        return {}
    return rec


def _sensor_exact(session_id):
    """The sensor record's `exact` block, normalised, or {} unless it carries
    a window >= 1 and finite pct, tokens and at, with `at` no more than
    FUTURE_SKEW_S ahead of now."""
    ex = sensor_record(session_id).get("exact")
    if not isinstance(ex, dict):
        return {}
    win, tok, pct, at = (_finite(ex.get(k)) for k in ("window", "tokens", "pct", "at"))
    if win is None or win < 1 or tok is None or pct is None or at is None:
        return {}
    if at > time.time() + FUTURE_SKEW_S:
        return {}
    return {"pct": min(max(pct, 0.0), 100.0), "tokens": max(int(tok), 0),
            "window": int(win), "at": at}


def sensor(session_id, state=None):
    """The exact block depth() uses: the fresher (larger `at`; a tie goes to the
    sensor file) of the statusline plugin's sensor record and the legacy
    `exact` in this session's state (`state`, else loaded). A block stamped
    at or before the state's `epoch_at` describes an earlier epoch and is
    demoted to window-only ({"window", "at": 0}). Returns {} when neither
    exists. Never raises."""
    try:
        st = state if state is not None else load_state(session_id)
        legacy = st.get("exact") or {}
        if not isinstance(legacy, dict):
            legacy = {}
        new = _sensor_exact(session_id)
        if new and (not legacy or new["at"] >= (_finite(legacy.get("at")) or 0.0)):
            ex = new
        else:
            ex = legacy
        cut = _finite(st.get("epoch_at"))
        at = _finite(ex.get("at"))
        if cut is not None and at and at <= cut and ex.get("window"):
            return {"window": int(ex["window"]), "at": 0}
        return ex
    except Exception:
        return {}


def depth(transcript_path, session_id=None):
    """Return (tokens, window, pct_full, source).

    source is "exact" when the status line's record is fresh; otherwise it
    starts with "inferred" - the tokens are a guess and must not hard-block.
    A stale exact record still contributes its window (as the floor of the
    guess) and its tokens (as the floor of the transcript-derived count).
    """
    ex = {}
    if session_id:
        ex = sensor(session_id)
        if ex.get("window") and time.time() - ex.get("at", 0) < EXACT_MAX_AGE_S:
            return ex["tokens"], ex["window"], ex["pct"], "exact"
    cur, peak, boundary = scan_usage(transcript_path)
    known = int(ex.get("window") or 0)
    w = window(peak, floor=known)
    src = "inferred"
    if known:
        if not boundary:
            # After a compaction the stale record describes the OLD epoch's
            # fill; only its window still holds.
            cur = max(cur, int(ex.get("tokens") or 0))
        src = "inferred, window from status line"
    return cur, w, (100.0 * cur / w if w else 0.0), src
