#!/usr/bin/env python3
"""quota_budget — the librarian's quota sense (1222 F1).

One call, one JSON result on stdout: for the subscription's five-hour and weekly
windows, how much is used, how fast it is being spent (velocity), and how fast it
may be spent (allowed rate) under the reserve the operator's intent sets; the
count of fresh librarian claims; and when to check again. The idle turn (F2)
maps these inputs to a mode and a concurrency cap; this script decides nothing.

Store (per subscription, because the config dir is what one subscription's
sandboxes share), `CFG` = ${CLAUDE_CONFIG_DIR:-~/.claude}:

    CFG/claude-kit/librarian/samples.jsonl    fallback history, one line per call
    CFG/claude-kit/librarian/intent.json      operator intent (read only here)
    CFG/claude-kit/librarian/claims/<repo>.json  one claim per repo (this repo's written)

The schema and the rules are in references/budget.md; the values (reserves,
TTLs) are owned by the agents repo's librarian-budget-policy series.

Reads: this session's sensor record CFG/statusline/sensor/<sid>.json (the
statusline-hub / statusline contract), this session's own registry file
CFG/sessions/<CLAUDE_PID>.json (identity fields only, and only when its
sessionId is ours), the store, and - when the claude-analytics sampler is
installed and live - its sink CFG/plugins/data/claude-analytics-*/samples/.
Never reads a settings file or the user-level Claude state file.

Stdlib only; never raises out of main(): a real error (a store write that
fails) exits 1 with a message on stderr, and still prints the JSON result.
"""
import argparse
import errno
import fcntl
import glob
import hashlib
import json
import math
import os
import re
import stat
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

V = 1
WINDOWS = ("five_hour", "seven_day")
# Reserves in percentage points per intent: (five_hour, seven_day). Defaults
# pending operator ratification; the agents librarian-budget-policy series owns
# them (away's five-hour reserve is 10, per its resolution of 1222's F1/F5 split).
RESERVES = {
    "present": (25.0, 15.0),
    "away": (10.0, 15.0),
    "done-for-the-day": (0.0, 15.0),
    "vacation": (5.0, 10.0),
}
DEFAULT_INTENT = "present"
IDLE_TTL_S = 2 * 3600          # a claim with nothing in flight is fresh this long
IN_FLIGHT_TTL_S = 4 * 3600     # a claim with items in flight is fresh this long
STALE_AFTER_S = 30 * 60        # a reading older than this is no signal
FUTURE_SKEW_S = 300            # a reading stamped further ahead than this is no signal
RESET_TOLERANCE_S = 60         # resets_at values this close name the same window
LOOKBACK_S = {"five_hour": 2 * 3600, "seven_day": 6 * 3600}
MIN_SPAN_S = 600               # velocity needs samples at least this far apart
NEXT_CHECK_MAX_S = 3600        # self-wake at most an hour out
NEXT_CHECK_MIN_S = 60
NEXT_CHECK_NO_SIGNAL_S = 900
RESET_GRACE_S = 60             # wake this long after a reset, so the new window shows
READ_MAX = 1 << 20             # bytes read from any JSON file
SAMPLES_TAIL = 2 << 20         # bytes of samples.jsonl read from its end
SAMPLES_PRUNE_AT = 1 << 20     # rewrite samples.jsonl above this size...
SAMPLES_KEEP_S = 8 * 86400     # ...keeping this much history
SINK_DAYS = 8                  # sink day-files read
_SAFE = re.compile(r"[A-Za-z0-9_-][A-Za-z0-9._-]{0,127}")
_DAYFILE = re.compile(r"(\d{4}-\d{2}-\d{2})\.jsonl")


# ---------------------------------------------------------------- basics

def cfg_dir(env=None):
    env = os.environ if env is None else env
    return os.path.expanduser(env.get("CLAUDE_CONFIG_DIR") or "~/.claude")


def store_dir(cfg):
    return os.path.join(cfg, "claude-kit", "librarian")


def safe_name(value, prefix="sid-"):
    """The sensor contract's safe_sid rule, reused for repo names: a safe token
    passes unchanged, anything else becomes prefix + a SHA-256 prefix."""
    if not value:
        return "unknown"
    if isinstance(value, str) and _SAFE.fullmatch(value):
        return value
    raw = value if isinstance(value, str) else repr(value)
    return prefix + hashlib.sha256(raw.encode("utf-8", "replace")).hexdigest()[:32]


def finite(x):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return None
    try:
        x = float(x)
    except OverflowError:
        return None
    return x if math.isfinite(x) else None


def epoch(x):
    """An epoch-seconds float from a number (seconds, or milliseconds when it is
    implausibly large) or an ISO 8601 string; None otherwise."""
    n = finite(x)
    if n is not None:
        return n / 1000.0 if n > 1e11 else n
    if isinstance(x, str) and x.strip():
        s = x.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            d = datetime.fromisoformat(s)
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
            return d.timestamp()
        except (ValueError, OverflowError, OSError):
            return None
    return None


def open_regular(path, flags, mode=0o600):
    """os.open(path, flags) that never blocks and yields only a regular file: the
    open is O_NONBLOCK (a FIFO with no peer would otherwise block it forever, and
    O_NOFOLLOW does not stop a FIFO), the fd is fstat'ed, anything but a regular
    file is closed and refused with OSError(EINVAL), and O_NONBLOCK is then
    cleared. A write-only open of a FIFO with no reader fails with ENXIO. The
    open is also O_NOCTTY, so a terminal reached through a followed symlink never
    becomes the controlling terminal before it is refused."""
    fd = os.open(path, flags | os.O_NONBLOCK | os.O_NOCTTY, mode)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise OSError(errno.EINVAL, "not a regular file", path)
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl & ~os.O_NONBLOCK)
    except BaseException:
        os.close(fd)
        raise
    return fd


def read_json(path):
    """A parsed JSON object from a regular file under READ_MAX bytes, else None."""
    try:
        with os.fdopen(open_regular(path, os.O_RDONLY), "rb") as f:
            if os.fstat(f.fileno()).st_size > READ_MAX:
                return None
            data = f.read(READ_MAX + 1)
        if len(data) > READ_MAX:
            return None
        d = json.loads(data.decode("utf-8"))
        return d if isinstance(d, dict) else None
    except (OSError, ValueError, UnicodeDecodeError, RecursionError, MemoryError):
        # RecursionError: deeply nested JSON. A poisoned file reads as absent.
        return None


def ensure_dir(path):
    """Create path and any missing parents 0700 (os.makedirs applies its mode to
    the leaf only), then tighten path itself to 0700. Existing parents are left
    as they are."""
    missing = []
    p = os.path.abspath(path)
    while not os.path.isdir(p):
        missing.append(p)
        parent = os.path.dirname(p)
        if parent == p:
            break
        p = parent
    for d in reversed(missing):
        try:
            os.mkdir(d, 0o700)
        except FileExistsError:
            pass
    os.chmod(path, 0o700)


def atomic_write_json(path, obj):
    """Write obj to path by a unique temp file in the same dir plus os.replace:
    a reader sees the old file or the new one, never a torn one. 0600."""
    d = os.path.dirname(path)
    ensure_dir(d)
    fd, tmp = tempfile.mkstemp(prefix="." + os.path.basename(path) + ".", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, sort_keys=True)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------- readings

def norm_windows(rl):
    """{window: {used, resets_at}} for the policy windows present in a
    rate_limits block with both fields finite."""
    out = {}
    if not isinstance(rl, dict):
        return out
    for w in WINDOWS:
        b = rl.get(w)
        if not isinstance(b, dict):
            continue
        used, reset = finite(b.get("used_percentage")), epoch(b.get("resets_at"))
        if used is None or reset is None:
            continue
        out[w] = {"used": min(max(used, 0.0), 100.0), "resets_at": reset}
    return out


def sensor_reading(cfg, session):
    """This session's sensor record as a sample {at, session, windows}, or
    (None, reason)."""
    if not session:
        return None, "no session id"
    rec = read_json(os.path.join(cfg, "statusline", "sensor", safe_name(session) + ".json"))
    if rec is None:
        return None, "no sensor record for this session"
    if type(rec.get("v")) is not int or rec["v"] != 1:
        return None, "sensor record version not understood"
    rl = rec.get("rate_limits")
    at = epoch(rl.get("at")) if isinstance(rl, dict) else None
    wins = norm_windows(rl)
    if at is None or not wins:
        return None, "sensor record has no rate limits (API-key session or not rendered yet)"
    return {"at": at, "session": session, "windows": wins}, None


def sample_line(s):
    """The samples.jsonl form of a sample."""
    d = {"v": V, "at": s["at"], "session": s.get("session")}
    for w, b in s["windows"].items():
        d[w] = {"used_percentage": b["used"], "resets_at": b["resets_at"]}
    return d


def parse_sample(d):
    """A sample from a samples.jsonl line, or None."""
    if not isinstance(d, dict):
        return None
    at = epoch(d.get("at"))
    wins = norm_windows({w: d.get(w) for w in WINDOWS})
    if at is None or not wins:
        return None
    return {"at": at, "session": d.get("session"), "windows": wins}


def parse_sink_sample(d):
    """A sample from a claude-analytics sampler line, as its design specifies
    (agent-telemetry 00, Collection): `ts`, `session_id`, and the payload's
    `rate_limits` block; other fields are ignored. None when unusable."""
    if not isinstance(d, dict):
        return None
    at = epoch(d.get("ts"))
    wins = norm_windows(d.get("rate_limits"))
    if at is None or not wins:
        return None
    return {"at": at, "session": d.get("session_id"), "windows": wins}


def read_jsonl(path, parse, tail=SAMPLES_TAIL):
    """The parsed samples of a .jsonl file's last `tail` bytes. A file that is
    missing, unreadable or not a regular file (a FIFO, a directory) reads as
    empty."""
    out = []
    try:
        with os.fdopen(open_regular(path, os.O_RDONLY), "rb") as f:
            size = os.fstat(f.fileno()).st_size
            if size > tail:
                f.seek(size - tail)
                f.readline()  # drop the partial first line
            data = f.read()
    except OSError:
        return out
    for raw in data.splitlines():
        try:
            d = json.loads(raw.decode("utf-8"))
        except (ValueError, RecursionError, MemoryError):
            # A poisoned line (bad UTF-8, bad JSON, an over-long integer, deep
            # nesting) is skipped. Nothing else is caught: a bug in `parse` or
            # anything but a parse failure is not a bad line.
            continue
        s = parse(d)
        if s is not None:
            out.append(s)
    return out


def sink_dirs(cfg, override=None):
    if override:
        return [override] if os.path.isdir(override) else []
    return sorted(p for p in glob.glob(os.path.join(cfg, "plugins", "data", "claude-analytics-*", "samples"))
                  if os.path.isdir(p))


def read_sink(dirs, now):
    """Samples from the sink's day files of the last SINK_DAYS days."""
    out = []
    cutoff = datetime.fromtimestamp(now - SINK_DAYS * 86400, timezone.utc).strftime("%Y-%m-%d")
    for d in dirs:
        try:
            names = os.listdir(d)
        except OSError:
            continue
        for n in sorted(names):
            m = _DAYFILE.fullmatch(n)
            if m and m.group(1) >= cutoff:
                out.extend(read_jsonl(os.path.join(d, n), parse_sink_sample))
    return out


def open_lock(path):
    """An fd on the lock file for flock. O_NOFOLLOW: a symlink planted at path
    fails with ELOOP (an OSError, reported as a store write error) and never
    creates or opens its target; a FIFO or other non-regular file is refused
    the same way (open_regular). A lock file this user may not write is opened
    read-only, which flock accepts."""
    try:
        return open_regular(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW)
    except PermissionError:
        return open_regular(path, os.O_RDONLY | os.O_NOFOLLOW)


def append_sample(path, s):
    """One O_APPEND write of one line; prune by a temp-and-rename rewrite once the
    file passes SAMPLES_PRUNE_AT. Append and prune both hold an exclusive flock
    on samples.lock beside it, so a prune never drops a concurrent append.
    Unparseable lines are dropped by the prune. Both opens are O_NOFOLLOW: a
    symlink planted at samples.jsonl or samples.lock fails as a store write
    error and never creates, opens or appends to its target; so does a FIFO or
    any other non-regular file there (open_regular), without blocking."""
    d = os.path.dirname(path)
    ensure_dir(d)
    line = (json.dumps(sample_line(s), sort_keys=True) + "\n").encode("utf-8")
    lk = open_lock(os.path.join(d, "samples.lock"))
    try:
        fcntl.flock(lk, fcntl.LOCK_EX)
        fd = open_regular(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW)
        try:
            os.write(fd, line)
        finally:
            os.close(fd)
        if os.path.getsize(path) > SAMPLES_PRUNE_AT:
            keep = [sample_line(x) for x in read_jsonl(path, parse_sample)
                    if x["at"] >= s["at"] - SAMPLES_KEEP_S]
            fd, tmp = tempfile.mkstemp(prefix=".samples.", suffix=".tmp", dir=d)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    for x in keep:
                        f.write(json.dumps(x, sort_keys=True) + "\n")
                    f.flush()
                    os.fsync(f.fileno())
                os.chmod(tmp, 0o600)
                os.replace(tmp, path)
            except BaseException:
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
                raise
    finally:
        os.close(lk)


# ---------------------------------------------------------------- arithmetic

def velocity(samples, window, current, now):
    """Spend rate of `window` in percentage points per hour, from the samples of
    the same window (resets_at within RESET_TOLERANCE_S of the current one): a
    reset boundary makes any cross-window rate garbage.

    The points are made monotone (a running maximum: a cumulative percentage
    cannot fall inside one window, so a lower reading is a stale payload); the
    rate runs from the newest point at least the lookback old (else the window's
    oldest) to the newest point. None with fewer than two points or a span under
    MIN_SPAN_S. Returns (rate, points_used, span_s)."""
    reset = current["resets_at"]
    pts = sorted((s["at"], s["windows"][window]["used"]) for s in samples
                 if window in s["windows"]
                 and abs(s["windows"][window]["resets_at"] - reset) <= RESET_TOLERANCE_S
                 and s["at"] <= now + FUTURE_SKEW_S)
    env, top = [], None
    for at, used in pts:
        top = used if top is None else max(top, used)
        env.append((at, top))
    if len(env) < 2:
        return None, len(env), 0.0
    last_at, last_used = env[-1]
    start = last_at - LOOKBACK_S.get(window, 7200)
    older = [p for p in env if p[0] <= start]
    first_at, first_used = older[-1] if older else env[0]
    span = last_at - first_at
    used_pts = sum(1 for p in env if p[0] >= first_at)
    if span < MIN_SPAN_S:
        return None, used_pts, span
    return (last_used - first_used) / (span / 3600.0), used_pts, span


def read_intent(store, now):
    """The operator's intent: the stored mode unless absent, unknown or past its
    `until`, in which case `present` (the most protective five-hour reserve)."""
    d = read_json(os.path.join(store, "intent.json"))
    out = {"mode": DEFAULT_INTENT, "source": "default", "stored": None,
           "until": None, "set_by": None, "at": None, "expired": False}
    if d is None:
        return out
    raw = d.get("mode")
    mode = re.sub(r"[\s_]+", "-", raw.strip().lower()) if isinstance(raw, str) else None
    until = epoch(d.get("until"))
    out.update(stored=raw if isinstance(raw, str) else None, until=until,
               set_by=d.get("set_by") if isinstance(d.get("set_by"), str) else None,
               at=epoch(d.get("at")))
    if mode not in RESERVES:
        out["source"] = "unknown-mode"
        return out
    if until is not None and until <= now:
        out.update(source="expired", expired=True)
        return out
    out.update(mode=mode, source="file")
    return out


def windows_result(current, history, reserves, now):
    res = {}
    for i, w in enumerate(WINDOWS):
        c = current["windows"][w]
        hours = (c["resets_at"] - now) / 3600.0
        reserve = reserves[i]
        headroom = 100.0 - c["used"] - reserve
        v, n, span = velocity(history, w, c, now)
        res[w] = {
            "used": round(c["used"], 3),
            "resets_at": c["resets_at"],
            "hours_to_reset": round(hours, 4),
            "reserve": reserve,
            "headroom": round(headroom, 3),
            "velocity": None if v is None else round(v, 4),
            "velocity_points": n,
            "velocity_span_s": round(span, 1),
            "allowed": round(max(headroom, 0.0) / hours, 4),
        }
    return res


# ---------------------------------------------------------------- claims

def registry_identity(cfg, session, env):
    """session_name, pid, pidDomain, procStart from this session's own registry
    file, only when its sessionId is ours; missing fields are None."""
    out = {"session_name": None, "pid": None, "pidDomain": None, "procStart": None}
    pid = env.get("CLAUDE_PID")
    if not pid or not str(pid).isdigit():
        return out
    d = read_json(os.path.join(cfg, "sessions", str(pid) + ".json"))
    if d is None or not session or d.get("sessionId") != session:
        return out
    out["session_name"] = d.get("name") if isinstance(d.get("name"), str) else None
    out["pid"] = d.get("pid") if isinstance(d.get("pid"), int) else None
    for k in ("pidDomain", "procStart"):
        out[k] = d.get(k) if isinstance(d.get(k), str) else None
    return out


def claim_fresh(c, now):
    """A claim is fresh while its heartbeat `at` is within the idle TTL (2 h), or
    the in-flight TTL (4 h) when `in_flight` is a non-empty list."""
    at = epoch(c.get("at")) if isinstance(c, dict) else None
    if at is None:
        return False
    inf = c.get("in_flight")
    ttl = IN_FLIGHT_TTL_S if isinstance(inf, list) and inf else IDLE_TTL_S
    return now - at <= ttl


def same_process(a, b):
    keys = ("pid", "pidDomain", "procStart")
    return all(a.get(k) is not None for k in keys) and all(a.get(k) == b.get(k) for k in keys)


def create_exclusive_json(path, obj):
    """Create path holding obj only if it does not exist: the temp file is
    written in full, then hard-linked into place (link fails on an existing
    name, so exactly one creator wins). True when this call created it."""
    d = os.path.dirname(path)
    ensure_dir(d)
    fd, tmp = tempfile.mkstemp(prefix="." + os.path.basename(path) + ".", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, sort_keys=True)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, 0o600)
        try:
            os.link(tmp, path)
            return True
        except FileExistsError:
            return False
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def claim_file_state(path):
    """How write_claim may treat a claim path read_json could not use: "absent";
    "garbled" only for a regular file of at most READ_MAX bytes, read in full,
    whose content does not parse as a JSON object (safe to replace); "ok" when
    it parses after all (it changed under us); "unusable" for anything else - not
    a regular file (a symlink, a directory, ...), oversized, or unreadable -
    which is never overwritten."""
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return "absent"
    except OSError:
        return "unusable"
    if not stat.S_ISREG(st.st_mode) or st.st_size > READ_MAX:
        return "unusable"
    try:
        fd = open_regular(path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as f:
            data = f.read(READ_MAX + 1)
    except OSError:
        return "unusable"
    if len(data) > READ_MAX:
        return "unusable"
    try:
        d = json.loads(data.decode("utf-8"))
    except (ValueError, RecursionError):  # UnicodeDecodeError is a ValueError
        return "garbled"
    except MemoryError:
        return "unusable"
    return "ok" if isinstance(d, dict) else "garbled"


IDENTITY_KEYS = ("session_name", "pid", "pidDomain", "procStart")


def _previous(old, now):
    return {"session_id": old.get("session_id"), "session_name": old.get("session_name"),
            "at": epoch(old.get("at")), "fresh": claim_fresh(old, now)}


def write_claim(store, repo, session, ident, now, takeover=False, attempts=3):
    """Write or refresh this repo's claim. Returns the claim report.

    - no claim: created by an exclusive create (one creator wins a race; the
      losers re-read and see a fresh foreign claim);
    - a claim file that does not parse (a regular file of at most READ_MAX
      bytes whose content is not a JSON object), or an expired claim: replaced,
      `in_flight: []`;
    - a claim path that is not a regular file, is oversized or cannot be read:
      never overwritten, reported as a conflict with `unusable: true`;
    - our own session's claim: refreshed, its other fields kept (an identity
      field this call could not read keeps its stored value);
    - a fresh claim of another session: taken over (`in_flight` reset, per the
      policy's takeover rule) only when it is this same process (pid, pidDomain
      and procStart all equal: a `/clear`) or `takeover` is set; otherwise left
      alone and reported as a conflict for the idle turn to judge.

    After every replace the file is re-read: if another session's claim is
    there, the report is a conflict (`lost_race: true`), not a write."""
    path = os.path.join(store, "claims", safe_name(repo, "repo-") + ".json")
    rep = {"repo": repo, "path": path, "written": False, "action": None, "previous": None}
    for _ in range(attempts):
        old = read_json(path)
        exists = os.path.lexists(path)
        claim = {"v": V, "repo": repo, "session_id": session, "at": now, "in_flight": []}
        claim.update(ident)
        rep["previous"] = None
        if old is None and not exists:
            if create_exclusive_json(path, claim):
                rep.update(action="created", written=True)
                return rep
            continue  # someone else created it first: judge their claim
        if old is None:
            state = claim_file_state(path)
            if state in ("absent", "ok"):
                continue  # it changed between the two looks: judge it again
            if state != "garbled":
                rep.update(action="conflict", unusable=True)
                return rep
            rep["action"] = "replaced-unreadable"
        elif old.get("session_id") == session:
            kept = dict(old)
            kept.update({k: v for k, v in claim.items()
                         if k != "in_flight" and not (k in IDENTITY_KEYS and v is None)})
            if not isinstance(kept.get("in_flight"), list):
                kept["in_flight"] = []
            claim, rep["action"] = kept, "refreshed"
        else:
            rep["previous"] = _previous(old, now)
            if not rep["previous"]["fresh"]:
                rep["action"] = "replaced-expired"
            elif same_process(ident, old):
                rep["action"] = "takeover-same-process"
            elif takeover:
                rep["action"] = "takeover"
            else:
                rep["action"] = "conflict"
                return rep
        atomic_write_json(path, claim)
        cur = read_json(path)
        if cur is not None and cur.get("session_id") != session:
            rep.update(action="conflict", written=False, lost_race=True,
                       previous=_previous(cur, now))
            return rep
        rep["written"] = True
        return rep
    cur = read_json(path) or {}
    rep.update(action="conflict", written=False, lost_race=True, previous=_previous(cur, now))
    return rep


def count_claims(store, now):
    """Fresh claims in claims/ (tombstones under claims/stale/ are not read), and
    the in-flight items they carry."""
    d = os.path.join(store, "claims")
    fresh = items = 0
    try:
        names = sorted(os.listdir(d))
    except OSError:
        return 0, 0
    for n in names:
        if not n.endswith(".json") or n.startswith("."):
            continue
        c = read_json(os.path.join(d, n))
        if c is not None and claim_fresh(c, now):
            fresh += 1
            inf = c.get("in_flight")
            items += len(inf) if isinstance(inf, list) else 0
    return fresh, items


def repo_name(cwd):
    """The basename of the main checkout (a worktree resolves to its main repo)."""
    try:
        p = subprocess.run(["git", "-C", cwd, "rev-parse", "--path-format=absolute",
                            "--git-common-dir"], capture_output=True, text=True, timeout=5)
        common = p.stdout.strip() if p.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        common = ""
    if common:
        common = os.path.normpath(common)
        if os.path.basename(common) == ".git":
            return os.path.basename(os.path.dirname(common))
        b = os.path.basename(common)
        return b[:-4] if b.endswith(".git") else b
    return os.path.basename(os.path.normpath(cwd))


# ---------------------------------------------------------------- main

def next_check(result, now):
    if result["signal"] != "ok":
        return NEXT_CHECK_NO_SIGNAL_S
    soonest = min(w["resets_at"] for w in result["windows"].values()) - now + RESET_GRACE_S
    return int(min(NEXT_CHECK_MAX_S, max(NEXT_CHECK_MIN_S, soonest)))


def compute(args, env, now):
    """The result dict and a list of error strings (store writes that failed)."""
    errors = []
    cfg = cfg_dir(env)
    store = store_dir(cfg)
    session = args.session or env.get("CLAUDE_CODE_SESSION_ID") or None
    result = {"v": V, "now": now, "session": session, "signal": "none", "reason": None,
              "source": None, "intent": None, "reserves": None, "windows": None,
              "binding": None, "allowed": None, "claims": None, "next_check": None}

    intent = read_intent(store, now)
    reserves = RESERVES[intent["mode"]]
    result["intent"] = intent
    result["reserves"] = {"five_hour": reserves[0], "seven_day": reserves[1]}

    # Current reading: this session's sensor record; the live sink when the
    # record is missing or stale. History: the live sink, else samples.jsonl.
    sdirs = sink_dirs(cfg, args.sink_dir)
    sink = [x for x in (read_sink(sdirs, now) if sdirs else [])
            if x["at"] <= now + FUTURE_SKEW_S]  # a future-stamped line is no evidence
    sink_live = any(now - s["at"] <= args.stale_after for s in sink)
    reading, reason = sensor_reading(cfg, session)
    if reading is not None and now - reading["at"] > args.stale_after:
        reading, reason = None, "sensor record is stale"
    src = "sensor"
    if reading is None and sink_live:
        cand = [s for s in sink if all(w in s["windows"] for w in WINDOWS)]
        if cand:
            reading, src = max(cand, key=lambda s: s["at"]), "sink"
    if reading is not None and reading["at"] - now > FUTURE_SKEW_S:
        reading, reason = None, "reading is stamped in the future (clock skew)"
    if reading is not None and not all(w in reading["windows"] for w in WINDOWS):
        reading, reason = None, "reading lacks the five-hour or weekly window"
    if reading is not None and any(reading["windows"][w]["resets_at"] <= now for w in WINDOWS):
        reading, reason = None, "a window has reset since the reading"

    history_src = "sink" if sink_live else "samples"
    samples_path = os.path.join(store, "samples.jsonl")
    if not sink_live and reading is not None and src == "sensor" and not args.read_only:
        try:
            append_sample(samples_path, reading)
        except OSError as e:
            errors.append("samples.jsonl append failed: %s" % e.strerror)
    result["source"] = {"reading": src if reading is not None else None, "history": history_src,
                        "sink_dirs": sdirs}

    if reading is not None:
        history = sink if sink_live else read_jsonl(samples_path, parse_sample)
        if not any(s["at"] == reading["at"] and s.get("session") == reading.get("session")
                   for s in history):
            history = history + [reading]
        wins = windows_result(reading, history, reserves, now)
        binding = min(WINDOWS, key=lambda w: wins[w]["allowed"])
        result.update(signal="ok", reading_at=reading["at"], windows=wins, binding=binding,
                      allowed=wins[binding]["allowed"])
    else:
        result["reason"] = reason or "no reading"

    claims = {"repo": None, "written": False, "action": "skipped"}
    if not args.read_only:
        repo = args.repo or repo_name(os.getcwd())
        if not session:
            claims.update(repo=repo, action="skipped-no-session")
        else:
            try:
                claims = write_claim(store, repo, session, registry_identity(cfg, session, env),
                                     now, args.takeover)
            except OSError as e:
                errors.append("claim write failed: %s" % e.strerror)
                claims.update(repo=repo, action="error")
    claims["fresh"], claims["fresh_in_flight"] = count_claims(store, now)
    result["claims"] = claims
    result["next_check"] = next_check(result, now)
    if errors:
        result["errors"] = errors
    return result, errors


def parser():
    p = argparse.ArgumentParser(description="The librarian's quota sense: prints one JSON result.")
    p.add_argument("--session", help="session id (default: $CLAUDE_CODE_SESSION_ID)")
    p.add_argument("--repo", help="repo name for the claim (default: basename of the main checkout)")
    p.add_argument("--read-only", action="store_true",
                   help="write nothing: no sample appended, no claim written")
    p.add_argument("--takeover", action="store_true",
                   help="overwrite a fresh claim of another session (the idle turn's call)")
    p.add_argument("--stale-after", type=float, default=STALE_AFTER_S,
                   help="seconds after which a reading is no signal (default %(default)s)")
    p.add_argument("--sink-dir", help="claude-analytics samples dir (default: discovered)")
    p.add_argument("--now", type=float, help=argparse.SUPPRESS)  # tests
    return p


def main(argv=None, env=None):
    env = os.environ if env is None else env
    try:
        args = parser().parse_args(argv)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 2
    try:
        now = args.now if args.now is not None else time.time()
        result, errors = compute(args, env, now)
    except Exception as e:  # never raise out
        sys.stderr.write("quota_budget: internal error: %s: %s\n" % (type(e).__name__, e))
        print(json.dumps({"v": V, "signal": "none", "reason": "internal error",
                          "next_check": NEXT_CHECK_NO_SIGNAL_S}))
        return 1
    print(json.dumps(result, sort_keys=True))
    for e in errors:
        sys.stderr.write("quota_budget: %s\n" % e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
