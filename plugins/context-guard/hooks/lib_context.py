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
2. DERIVED - the window mirrored from Claude Code's own selection logic
   (window_rules.py: the transcript's `attachment.type:"model"` line, the
   native-1M table, `[1m]`, the CLAUDE_CODE_* window env vars, the credits
   latch), the tokens from the transcript's post-boundary `usage` blocks
   (the same sum the status line reports). A RESOLVED derived depth (every
   input observed, the Claude Code version not distrusted) is source
   "derived" and may hard-block like "exact". An UNRESOLVED one never
   changes the depth: the inferred path below runs as before and the
   derived candidate is only named in the advisory (measure()'s `note`).
   With a fresh exact record the derived window is a cross-check
   (cross_check): a disagreement is logged to window-mismatch.jsonl and
   distrusts that Claude Code version, so its derived depth warns only.
   CONTEXT_GUARD_DERIVE=off turns the mirror off (and the auto-compact
   window below): the gate is then exactly exact-or-inferred.
3. INFERRED - from the transcript's per-message `usage` blocks (the numbers the
   API charged), window guessed from the session's peak. A guess can be wrong
   in either direction (live-fired 2026-09-16: a 1M session with a stale exact
   record was scored against 200K and HARD-blocked), so an inferred depth may
   warn but never block; context_warn.py requires a source in
   BLOCKING_SOURCES ("exact", "derived") to exit 2.
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

The GATE window (measure()'s `window`) is the model window above lowered to
the auto-compact window when one is configured below it
(window_rules.autocompact: CLAUDE_CODE_AUTO_COMPACT_WINDOW, the
autoCompactWindow setting, the model defaults): Claude Code compacts there.
A resolved auto-compact window may bound a hard block; an unresolved one only
warns, and a hard stop is then still measured against the model window.
depth() returns the MODEL window: precompact_gate proves a compaction
proactive against it.

The mirror's state, all written through update_state: per session `proc`
(window_events.py at SessionStart: this Claude Code process's start offset in
the transcript, its pid key, when), `model_switch` (PostModelSwitch's
to_model), `derived` (the last derived result, with the Claude Code version
it was read on and RULES_CC_VERSION) and `window_mismatch`; the pseudo
sessions `_proc-<pid>-<starttime>` (a credits latch seen in that process,
which outlives a /clear) and `_window-rules` (the distrusted versions).

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
    r = scan_transcript(transcript_path)
    return r["cur"], r["peak"], r["boundary"]


LATCH_KEEP = 16


def _scan_empty():
    return {"cur": 0, "peak": 0, "boundary": False, "model_id": None,
            "model_off": -1, "model_at": None, "cc_version": None,
            "latches": [], "size": 0}


def _iso_ts(v):
    """An ISO-8601 transcript timestamp as epoch seconds, or None."""
    if not isinstance(v, str) or not v:
        return None
    try:
        from datetime import datetime, timezone
        d = datetime.fromisoformat(v.replace("Z", "+00:00"))
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d.timestamp()
    except Exception:
        return None


_VERSION_RE = re.compile(rb'"version":\s*"([0-9A-Za-z.+-]{1,32})"')
VERSION_TAIL = 64 * 1024


def _tail_version(fh, size):
    """The `version` of the last transcript line carrying one, from the last
    VERSION_TAIL bytes (every Claude Code line carries it), or None."""
    try:
        fh.seek(max(0, size - VERSION_TAIL))
        found = _VERSION_RE.findall(fh.read(VERSION_TAIL))
        return found[-1].decode("ascii") if found else None
    except Exception:
        return None


def scan_transcript(transcript_path, usage=True):
    """One pass over the transcript. Returns a dict:
    cur, peak, boundary - as scan_usage (zero with usage=False, which skips
      parsing the usage lines: the exact path needs only the model line);
    model_id, model_off, model_at - the last `attachment.type:"model"` line's
      identity.modelId, its byte offset and timestamp (epoch);
    cc_version - the `version` of the last line that carries one;
    latches - [(byte offset, epoch)] of the last LATCH_KEEP API-error lines
      that set Claude Code's long-context-credits latch;
    size - bytes read.
    Lines are only parsed when a cheap substring test says they matter.
    Any error yields the empty result, as scan_usage always has."""
    out = _scan_empty()
    if not transcript_path or not os.path.exists(transcript_path):
        return out
    R = _rules()
    phrases = tuple(p.encode() for p in R.NUE_PHRASES)
    try:
        with open(transcript_path, "rb") as fh:
            off = 0
            for line in fh:
                start = off
                off += len(line)
                if b'"compact_boundary"' in line:
                    # Bug A (live-fired 2026-08-31): pre-boundary usage records
                    # described the OLD window; reading them after a compaction
                    # reported 62% used on a ~2% session. Keep peak (the model
                    # window did not change); reset current.
                    out["cur"] = 0
                    out["boundary"] = True
                    continue
                has_u = usage and b'"usage"' in line
                if not has_u and b"isApiErrorMessage" not in line and not (
                        b'"attachment"' in line and b'"model"' in line):
                    continue
                try:
                    obj = json.loads(line.decode("utf-8", "replace"))
                except Exception:
                    continue
                if not isinstance(obj, dict):
                    continue
                v = obj.get("version")
                if isinstance(v, str) and v:
                    out["cc_version"] = v[:32]     # fallback for the tail read
                if has_u:
                    msg = obj.get("message")
                    u = msg.get("usage") if isinstance(msg, dict) else None
                    if isinstance(u, dict):
                        try:
                            t = sum(u.get(k) or 0 for k in
                                    ("input_tokens", "cache_read_input_tokens",
                                     "cache_creation_input_tokens"))
                        except TypeError:
                            t = 0
                        if t:
                            out["cur"] = t
                            out["peak"] = max(out["peak"], t)
                if obj.get("type") == "attachment":
                    att = obj.get("attachment")
                    ident = att.get("identity") if isinstance(att, dict) \
                        and att.get("type") == "model" else None
                    mid = ident.get("modelId") if isinstance(ident, dict) else None
                    if isinstance(mid, str) and mid.strip():
                        out["model_id"] = mid.strip()[:200]
                        out["model_off"] = start
                        out["model_at"] = _iso_ts(obj.get("timestamp"))
                if obj.get("isApiErrorMessage") is True and (
                        obj.get("apiError") == R.LATCH_API_ERROR
                        or any(p in line for p in phrases)):
                    out["latches"] = (out["latches"] + [
                        (start, _iso_ts(obj.get("timestamp")))])[-LATCH_KEEP:]
            out["size"] = off
            out["cc_version"] = _tail_version(fh, off) or out["cc_version"]
    except Exception:
        return _scan_empty()
    return out


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


BLOCKING_SOURCES = ("exact", "derived")
DERIVE_ENV = "CONTEXT_GUARD_DERIVE"
# Pseudo session ids (a leading "_" never starts a Claude Code session id):
# the Claude Code process record (keyed pid-starttime) that carries the
# credits latch across /clear, and the mirror's distrust list.
PROC_PREFIX = "_proc-"
RULES_SID = "_window-rules"
MISMATCH_LOG = "window-mismatch.jsonl"
MISMATCH_KEEP = 200
ANCESTORS = 8


def _rules():
    """window_rules, imported from this file's own directory - a caller may
    load lib_context by path (the statusline plugin's contract test) without
    that directory on sys.path."""
    try:
        import window_rules
    except ImportError:
        import sys
        here = os.path.dirname(os.path.abspath(__file__))
        if here not in sys.path:
            sys.path.insert(0, here)
        import window_rules
    return window_rules


def derive_off(environ=None):
    """CONTEXT_GUARD_DERIVE=off (or 0/false/no): the window mirror is off."""
    v = (environ if environ is not None else os.environ).get(DERIVE_ENV) or ""
    return v.strip().lower() in ("off", "0", "false", "no")


def proc_key():
    """'<pid>-<starttime>' of the Claude Code process this hook runs under,
    or None. Walks at most ANCESTORS parents through /proc and takes the
    first whose pid has an entry in Claude Code's session registry
    (<config>/sessions/<pid>.json - only its existence is checked, it is
    never opened); the /proc start time guards against pid reuse. Without
    /proc (non-Linux) or a registry entry: None. Never raises."""
    try:
        reg = os.path.join(_base_dir(), "sessions")
        pid, seen = os.getppid(), set()
        for _ in range(ANCESTORS):
            if not pid or pid <= 1 or pid in seen:
                return None
            seen.add(pid)
            if os.path.isfile(os.path.join(reg, f"{pid}.json")):
                with open(f"/proc/{pid}/stat") as f:
                    fields = f.read().rsplit(")", 1)[1].split()
                return f"{pid}-{int(fields[19])}"
            with open(f"/proc/{pid}/status") as f:
                pid = next((int(ln.split()[1]) for ln in f if ln.startswith("PPid:")), 0)
    except Exception:
        return None
    return None


def distrusted_versions():
    """{cc_version: first_seen_epoch} of the versions a mismatch demoted."""
    d = load_state(RULES_SID).get("distrust")
    return d if isinstance(d, dict) else {}


def _latch(scan, st):
    """(latch, latch_known, latch_at): whether this Claude Code process has
    its long-context-credits latch set. With a SessionStart marker
    (state `proc`) only API-error lines at or after the process's start
    offset count, and the pid-keyed process record carries a latch set
    before a /clear; without one every such line counts and the answer is
    not known (a line may come from an earlier process)."""
    proc = st.get("proc") if isinstance(st.get("proc"), dict) else None
    lines = scan.get("latches") or []
    if proc is None or not isinstance(proc.get("offset"), int):
        return bool(lines), False, (lines[-1][1] if lines else None)
    mine = [(o, t) for o, t in lines if o >= proc["offset"]]
    key = proc.get("key") if isinstance(proc.get("key"), str) else None
    if mine:
        if key and not load_state(PROC_PREFIX + key).get("latch"):
            update_state(PROC_PREFIX + key,
                         lambda p: p.setdefault("latch", time.time()))
        return True, True, mine[-1][1]
    if key:
        at = _finite(load_state(PROC_PREFIX + key).get("latch"))
        if at:
            return True, True, at
    return False, True, None


def derived_window(scan, st, environ=None):
    """window_rules.derive() on this session's inputs, then the trust gate:
    a PostModelSwitch newer than the last model line replaces the model (or,
    when it named only an alias, leaves the result unresolved), and a
    distrusted Claude Code version is unresolved. The returned dict adds
    model, cc_version, rules_version, latch, changed_at (the epoch at which
    the last input changed: model line, switch or latch) and distrusted."""
    R = _rules()
    environ = os.environ if environ is None else environ
    env = R.env_inputs(environ)
    model, changed = scan.get("model_id"), scan.get("model_at")
    alias = False
    sw = st.get("model_switch")
    if isinstance(sw, dict) and isinstance(sw.get("to_model"), str) \
            and isinstance(sw.get("size"), int) and sw["size"] > scan.get("model_off", -1):
        tm = sw["to_model"].strip()
        if tm.lower().startswith("claude-"):
            model = tm
        else:
            alias = True
        changed = max(changed or 0.0, _finite(sw.get("at")) or 0.0) or None
    latch, known, latch_at = _latch(scan, st)
    if latch and latch_at:
        changed = max(changed or 0.0, latch_at)
    served = R.served_declared(_base_dir(), R.canonical(model), read_json_file)
    d = R.derive(model, env, latch=latch, latch_known=known, served=served)
    ver = scan.get("cc_version")
    d.update(model=model, cc_version=ver, rules_version=R.RULES_CC_VERSION,
             latch=latch, changed_at=changed, distrusted=False, served=served)
    if alias:
        d.update(resolved=False, rule="model_switch_alias")
    if d["resolved"] and (ver or "unknown") in distrusted_versions():
        d.update(resolved=False, distrusted=True)
    return d, env


def cross_check(session_id, ex, d, st):
    """Compare a status-line record's window with a resolved derived one.
    Only a record written by this Claude Code process (at >= the SessionStart
    marker) after the derived inputs last changed can disagree; then one
    line goes to window-mismatch.jsonl (the last MISMATCH_KEEP kept), the
    Claude Code version joins the distrust list and the session records
    `window_mismatch` (context_warn tells the operator once). Returns True
    on a mismatch (the caller demotes the derived result). Never raises."""
    try:
        win, at = _finite(ex.get("window")), _finite(ex.get("at"))
        proc = st.get("proc") if isinstance(st.get("proc"), dict) else {}
        started = _finite(proc.get("at"))
        if not (d.get("resolved") and d.get("window") and win and at) \
                or int(win) == int(d["window"]):
            return False
        if started is None or at < started or d.get("changed_at") is None \
                or at < d["changed_at"]:
            return False
        ver = d.get("cc_version") or "unknown"
        rec = {"at": round(time.time(), 3), "session": safe_sid(session_id),
               "cc_version": ver, "rules_version": d.get("rules_version"),
               "model": d.get("model"), "rule": d.get("rule"),
               "derived": int(d["window"]), "exact": int(win)}

        def log(rs):
            dist = rs.get("distrust") if isinstance(rs.get("distrust"), dict) else {}
            dist.setdefault(ver, rec["at"])
            rs["distrust"] = dist
            _append_capped(os.path.join(_state_dir(), MISMATCH_LOG),
                           json.dumps(rec, sort_keys=True), MISMATCH_KEEP)
        update_state(RULES_SID, log)
        update_state(session_id, lambda s: s.setdefault(
            "window_mismatch", {"cc_version": ver, "at": rec["at"],
                                "derived": rec["derived"], "exact": rec["exact"],
                                "notified": False}))
        return True
    except Exception:
        return False


def _append_capped(path, line, keep):
    """Append one line to a regular file (never through a symlink, never
    blocking on a FIFO); past `keep` lines, rewrite the last `keep` through a
    temp file and os.replace. Callers hold the RULES_SID lock."""
    fd = None
    try:
        fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT | _NOFOLLOW | _NONBLOCK,
                     0o600)
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            return
        os.write(fd, (line + "\n").encode("utf-8"))
    except Exception:
        return
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except Exception:
                pass
    tmp = None
    try:
        with open(path, "rb") as f:
            lines = f.read().splitlines(keepends=True)
        if len(lines) <= keep:
            return
        tfd, tmp = _mkstemp(os.path.dirname(path), ".window-mismatch.")
        with os.fdopen(tfd, "wb") as f:
            f.writelines(lines[-keep:])
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


def measure(transcript_path, session_id=None, cwd=None, environ=None):
    """The depth the gate scores, as a dict:

    tokens, window, pct - the GATE window: the model window, lowered to a
      configured auto-compact window below it;
    source - "exact", "derived", or a string starting "inferred";
    block_window - the window a hard stop may be measured against (None when
      the source may not block; the model window when only an unresolved
      auto-compact window lowered `window`);
    model_window, model_pct - the model window and the fill against it;
    derived - derived_window()'s dict (None with the mirror off);
    acw - window_rules.autocompact()'s dict;
    note - words for the advisory (an unresolved derived window, the
      auto-compact window), "" when there is nothing to add.

    Precedence: a fresh exact record; a resolved derived window; the
    inferred guess (an unresolved derived window only adds its note). Never
    raises for a missing or malformed transcript."""
    R = _rules()
    environ = os.environ if environ is None else environ
    off = derive_off(environ)
    st = load_state(session_id) if session_id else {}
    ex = sensor(session_id, st) if session_id else {}
    fresh = bool(ex.get("window")) and time.time() - (ex.get("at") or 0) < EXACT_MAX_AGE_S
    res = {"derived": None, "acw": {"window": None, "resolved": False, "source": "off"},
           "note": ""}
    if fresh and off:
        res.update(tokens=ex["tokens"], model_window=ex["window"], model_pct=ex["pct"],
                   source="exact")
        return _gate(res, True)
    scan = scan_transcript(transcript_path, usage=not fresh)
    d = env = None
    if not off:
        try:
            d, env = derived_window(scan, st, environ)
        except Exception:
            d = env = None
    if fresh:
        if d and session_id and cross_check(session_id, ex, d, st):
            d.update(resolved=False, distrusted=True)
        res.update(tokens=ex["tokens"], model_window=ex["window"], model_pct=ex["pct"],
                   source="exact")
        blocking = True
    else:
        if d and d["resolved"] and ex.get("window") and session_id \
                and cross_check(session_id, ex, d, st):
            # A stale record from this process disagrees with nothing changed
            # since: the status line wins, as the inferred path below does.
            d.update(resolved=False, distrusted=True)
        if d and d["resolved"]:
            cur = scan["cur"]
            w = int(d["window"])
            res.update(tokens=cur, model_window=w, model_pct=100.0 * cur / w,
                       source="derived")
            blocking = True
        else:
            cur, peak, boundary = scan["cur"], scan["peak"], scan["boundary"]
            known = int(ex.get("window") or 0)
            w = window(peak, floor=known)
            src = "inferred"
            if known:
                if not boundary:
                    # After a compaction the stale record describes the OLD
                    # epoch's fill; only its window still holds.
                    cur = max(cur, int(ex.get("tokens") or 0))
                src = "inferred, window from status line"
            res.update(tokens=cur, model_window=w,
                       model_pct=(100.0 * cur / w if w else 0.0), source=src)
            blocking = False
            if d and d.get("window"):
                res["note"] = (f"derived window {int(d['window']):,} unresolved "
                               f"({d['rule']}{', CC ' + str(d['cc_version']) + ' distrusted' if d.get('distrusted') else ''})")
    res["derived"] = d
    if not off and env is not None:
        try:
            proj = environ.get("CLAUDE_PROJECT_DIR") or cwd
            res["acw"] = R.autocompact(d.get("model") if d else None, res["model_window"],
                                       env, R.settings_autocompact(_base_dir(), proj, read_json_file),
                                       latch=bool(d and d.get("latch")),
                                       served=d.get("served") if d else None)
        except Exception:
            pass
    return _gate(res, blocking)


def _gate(res, blocking):
    """Fill window/pct/block_window from model_window and the acw result."""
    mw, tok = res["model_window"], res["tokens"]
    acw = res["acw"] or {}
    aw = acw.get("window")
    if aw and aw < mw:
        res["window"], res["pct"] = aw, 100.0 * tok / aw
        res["note"] = "; ".join(x for x in (res["note"], (
            f"auto-compact window {aw:,} ({acw.get('source')}"
            f"{'' if acw.get('resolved') else ', unresolved'})")) if x)
        block = aw if acw.get("resolved") else mw
    else:
        res["window"], res["pct"] = mw, res["model_pct"]
        block = mw
    res["block_window"] = block if blocking else None
    return res


def derived_record(m):
    """The `derived` block context_warn keeps in state (the plan's shape)."""
    d = m.get("derived")
    if not d:
        return None
    return {"window": d.get("window"), "model": d.get("model"), "rule": d.get("rule"),
            "resolved": bool(d.get("resolved")), "cc_version": d.get("cc_version"),
            "rules_version": d.get("rules_version"), "at": round(time.time(), 3)}


def depth(transcript_path, session_id=None, cwd=None):
    """Return (tokens, window, pct_full, source) against the MODEL window.

    source is "exact" when the status line's record is fresh, "derived" when
    the mirrored window resolved; otherwise it starts with "inferred" - the
    tokens are a guess and must not hard-block. A stale exact record still
    contributes its window (as the floor of the guess) and its tokens (as the
    floor of the transcript-derived count). See measure() for the gate window.
    """
    m = measure(transcript_path, session_id, cwd=cwd)
    return m["tokens"], m["model_window"], m["model_pct"], m["source"]
