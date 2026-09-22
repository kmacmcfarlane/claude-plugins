#!/usr/bin/env python3
"""statusline-hub owner mode: the `statusLine` command when the hub owns the slot.

    python3 hub.py              render: payload on stdin, one line on stdout
    python3 hub.py --status     list the registered hooks, why any is skipped,
                                and their health (for a person, not a render)

Each render, in this order:

1. Read stdin once, as bytes (at most READ_MAX; a larger payload is not one
   Claude Code sends: nothing runs and the line is empty).
2. Tee: write the sensor record (tee.py), before anything that can be slow,
   so a render Claude Code cancels still leaves the record fresh.
3. Record hooks: hand the payload, byte for byte, to one detached runner
   (`hub.py --run-records`, its own session, no stdout or stderr shared with
   the render) that runs each record hook under its timeout. A record hook
   whose previous instance is still running is skipped for this render (a
   per-hook lock), so a hung hook costs one process, not one per render. The render never
   waits for it; a record hook that crashes or hangs cannot touch the line or
   the sensor record.
4. Display hooks: spawn all at once, each with the payload on stdin (its own
   copy), the hub dir as working directory, STATUSLINE_HUB=1 in its env, and
   stderr to log/<name>.log. Collect stdout (capped) until each hook's
   timeout_ms, all inside DISPLAY_BUDGET_MS. On time with exit 0: its first
   line, sanitised (registry.sanitise), becomes its segment and its last-good
   text; empty output means "show nothing". Timeout, non-zero exit or a
   failed start: its last-good text when younger than LAST_GOOD_S, else no
   segment. A hook still running at its deadline is killed with its process
   group.
5. Health: for each hook with a health_path, one capped read; any "warn"
   appends GLYPH once.
6. Segments: read the drop dir (registry.scan_segments; files other tools
   write, no code runs), each file capped, stale or expired ones dropped.
7. Print the display hooks' segments and the drop-dir segments joined by
   the configured separator, in order; when COLUMNS says the line is too
   wide (the health glyph's width counted), drop-dir segments go first,
   lowest priority first. With COLUMNS unset nothing is dropped or cut.

Wrap mode (the user consented, with install-statusline-hub --wrap, to the hub
running the statusLine command their user settings held before it): when the
wrap record (registry.read_wrap) is trusted, running and from the user
settings file (registry.wrap_applies - never a project's), step 3 also hands the payload to
one detached inner runner (`hub.py --run-inner <sid>`), started before the
display hooks so it runs beside them. The runner runs the kept command
exactly as written, through `/bin/sh -c` as Claude Code runs a statusLine
command, in the render's own working directory and environment, with the
payload byte for byte on stdin; it kills the command's process group at
INNER_MAX_MS, and on exit 0 stores its stdout (at most INNER_OUT_MAX bytes,
every line, verbatim: it is the user's own renderer, which drew straight to
the slot before the wrap) as this session's last-good output.
CLAUDE_CODE_SHELL_PREFIX, which Claude Code puts in front of the commands it
runs, is not applied: the command runs as written. At most one
runner lives at a time (a lock), so a hung command costs one process. The
render waits for the runner only until DISPLAY_BUDGET_MS, then shows the
last-good output if it is younger than INNER_LAST_GOOD_S - fresh when the
command finished in time; for a command slower than the budget, the output
of the one before. The command's output comes first; the display segments
follow on its last line, after a colour reset when it used escapes. A command that fails or hangs costs only its own
output: the sensor record, the record hooks and the display hooks are not
touched.

The hub never raises: whatever fails, it prints the best line it has, or "".
"""
import json, os, selectors, signal, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import registry as R  # noqa: E402
import tee as T  # noqa: E402

READ_MAX = T.READ_MAX
DISPLAY_BUDGET_MS = 250   # every display hook is done or dropped by then
OUT_MAX = 4096            # stdout bytes read from one display hook
LAST_GOOD_S = 60
LOG_MAX = 65536           # a hook's log is emptied once it grows past this
GLYPH = "\u26a0"          # a record hook's health file says it is failing
INNER = "_wrapped"        # cache/lock/log name of the wrapped command; never a hook name
INNER_MAX_MS = 5000       # the wrapped command is killed after this
INNER_OUT_MAX = 16384     # stdout bytes kept from the wrapped command
INNER_LAST_GOOD_S = 600   # its last output shows this long when a render misses it


def _obj(v):
    return v if isinstance(v, dict) else {}


def project_dirs(d):
    """The session's project and working dirs, from the payload and the env."""
    ws = _obj(d.get("workspace"))
    return [ws.get("project_dir"), ws.get("current_dir"), d.get("cwd"),
            os.environ.get("CLAUDE_PROJECT_DIR")]


def payload_fd(data):
    """A readable fd holding `data` at offset 0, private to one child: a
    memfd where the OS has them, else an unlinked temp file in the hub's run
    dir. A file, not a pipe, so no child can block the writer."""
    if hasattr(os, "memfd_create"):
        fd = os.memfd_create("statusline-hub", getattr(os, "MFD_CLOEXEC", 0))
    else:
        R.mkdirs_private(R.run_dir())
        fd, name = T._mkstemp(R.run_dir(), ".payload.")
        os.unlink(name)
    try:
        view = memoryview(data)
        while view:
            view = view[os.write(fd, view):]
        os.lseek(fd, 0, os.SEEK_SET)
        return fd
    except BaseException:
        os.close(fd)
        raise


def log_fd(name):
    """An append fd on log/<name>.log (0600, emptied once over LOG_MAX), or
    DEVNULL when the log cannot be opened."""
    try:
        if not R.mkdirs_private(R.log_dir()):
            return subprocess.DEVNULL
        path = os.path.join(R.log_dir(), name + ".log")
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0) | \
            getattr(os, "O_CLOEXEC", 0)
        try:
            if os.lstat(path).st_size > LOG_MAX:
                flags |= os.O_TRUNC
        except FileNotFoundError:
            pass
        return os.open(path, flags, 0o600)
    except Exception:
        return subprocess.DEVNULL


def workdir():
    d = R.hub_dir()
    return d if R.mkdirs_private(d) else "/"


def spawn(hook, data, stdout):
    """Start one hook with `data` on its stdin; returns the Popen. Raises on a
    failed start."""
    env = dict(os.environ, STATUSLINE_HUB="1", STATUSLINE_HUB_KIND=hook["kind"],
               STATUSLINE_HUB_HOOK=hook["name"])
    fd = payload_fd(data)
    err = log_fd(hook["name"])
    try:
        return subprocess.Popen(hook["argv"], stdin=fd, stdout=stdout, stderr=err,
                                cwd=workdir(), env=env, close_fds=True,
                                start_new_session=True)
    finally:
        os.close(fd)
        if isinstance(err, int) and err >= 0:
            os.close(err)


def kill(p):
    """SIGKILL a hook's whole process group (it leads its own session)."""
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except Exception:
        try:
            p.kill()
        except Exception:
            pass


# -- last-good cache ---------------------------------------------------------

def _cache_path(name, sid):
    return os.path.join(R.cache_dir(), name, T.safe_sid(sid or "unknown") + ".json")


def cache_put(name, sid, text, now):
    tmp = None
    try:
        path = _cache_path(name, sid)
        d = os.path.dirname(path)
        if not R.mkdirs_private(d):
            return
        fd, tmp = T._mkstemp(d, "." + name + ".")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"at": now, "text": text}, f, ensure_ascii=False)
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


def cache_get(name, sid, now):
    """The last good text of hook `name` for this session when younger than
    LAST_GOOD_S, else None."""
    try:
        raw, _ = R._read_capped(_cache_path(name, sid), OUT_MAX * 4)
        d = json.loads(raw.decode("utf-8")) if raw is not None else None
        at = T._at(d)
        if isinstance(d, dict) and isinstance(d.get("text"), str) and \
                0 <= now - at <= LAST_GOOD_S:
            return R.sanitise(d["text"])
    except Exception:
        pass
    return None


# -- display hooks -----------------------------------------------------------

def run_displays(hooks, data, sid, now):
    """{name: segment text} for the display hooks, run in parallel under
    their timeouts (see the module doc). Never raises."""
    out = {}
    t0 = time.monotonic()
    budget = t0 + DISPLAY_BUDGET_MS / 1000.0
    live = {}  # name -> [hook, popen, buffer, deadline, timed_out]
    for h in hooks:
        try:
            p = spawn(h, data, subprocess.PIPE)
            live[h["name"]] = [h, p, bytearray(), min(t0 + h["timeout_ms"] / 1000.0, budget),
                               False]
        except Exception:
            out[h["name"]] = cache_get(h["name"], sid, now)
    sel = selectors.DefaultSelector()
    try:
        for name, st in live.items():
            os.set_blocking(st[1].stdout.fileno(), False)
            sel.register(st[1].stdout, selectors.EVENT_READ, name)
        reading = set(live)
        while reading:
            t = time.monotonic()
            for name in [n for n in reading if t >= live[n][3]]:
                live[name][4] = True
                sel.unregister(live[name][1].stdout)
                reading.discard(name)
            if not reading:
                break
            wait = min(live[n][3] for n in reading) - t
            for key, _ in sel.select(max(wait, 0)):
                name = key.data
                st = live[name]
                try:
                    chunk = os.read(key.fd, 4096)
                except BlockingIOError:
                    continue
                except OSError:
                    chunk = b""
                st[2] += chunk[:OUT_MAX - len(st[2])]
                # the first line is all that shows: stop reading at its end, so
                # a grandchild that keeps stdout open cannot hold the hook
                if not chunk or len(st[2]) >= OUT_MAX or b"\n" in st[2]:
                    sel.unregister(st[1].stdout)
                    reading.discard(name)
        for name, (h, p, buf, deadline, timed_out) in live.items():
            ok = False
            if not timed_out:
                try:
                    ok = p.wait(timeout=max(deadline - time.monotonic(), 0)) == 0
                except subprocess.TimeoutExpired:
                    ok = False
            if p.poll() is None:
                kill(p)
            if ok:
                text = R.sanitise(bytes(buf).decode("utf-8", "replace"))
                cache_put(name, sid, text, now)
                out[name] = text
            else:
                out[name] = cache_get(name, sid, now)
    except Exception:
        for name, st in live.items():
            if st[1].poll() is None:
                kill(st[1])
            out.setdefault(name, cache_get(name, sid, now))
    finally:
        sel.close()
        for st in live.values():
            try:
                st[1].stdout.close()
            except Exception:
                pass
    return out


# -- record hooks ------------------------------------------------------------

def _lock(name):
    """An fd holding an exclusive, non-blocking flock on run/<name>.lock - the
    one live instance of record hook `name` - or None when another instance
    holds it or the lock cannot be taken. Never raises."""
    fd = None
    try:
        import fcntl
        if not R.mkdirs_private(R.run_dir()):
            return None
        fd = os.open(os.path.join(R.run_dir(), name + ".lock"),
                     os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0) |
                     getattr(os, "O_CLOEXEC", 0), 0o600)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except Exception:
        if fd is not None:
            os.close(fd)
        return None


def _free(hook):
    """Whether no instance of record hook `hook` is running now (a probe: the
    runner takes the lock for real)."""
    fd = _lock(hook["name"])
    if fd is None:
        return False
    os.close(fd)
    return True


def dispatch_records(hooks, data):
    """Hand the payload to one detached runner for the record hooks that are
    not still running from an earlier render; returns at once. The runner's
    stdin is `<spec length>\\n<spec JSON><payload>`, so neither the spec's
    size nor the payload's is bound by the argument-length limit. Never
    raises."""
    try:
        free = [h for h in hooks if _free(h)]
        if not free:
            return
        spec = json.dumps([{k: h[k] for k in ("name", "kind", "argv", "timeout_ms")}
                           for h in free]).encode("utf-8")
        fd = payload_fd(b"%d\n" % len(spec) + spec + data)
        try:
            subprocess.Popen([sys.executable, os.path.abspath(__file__), "--run-records"],
                             stdin=fd, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, cwd=workdir(), close_fds=True,
                             start_new_session=True)
        finally:
            os.close(fd)
    except Exception:
        pass


SPEC_MAX = 1 << 22


def run_records():
    """The detached runner: read the spec and the payload from stdin, start
    each record hook whose lock it gets (at most one live instance per hook:
    one still running from an earlier render is skipped this time) with the
    payload byte for byte, release each lock as its hook exits, and kill any
    hook still running at its timeout."""
    head = sys.stdin.buffer.readline(24)
    n = int(head)
    if not 0 <= n <= SPEC_MAX:
        return
    spec = json.loads(sys.stdin.buffer.read(n).decode("utf-8"))
    data = sys.stdin.buffer.read(READ_MAX + 1)
    if len(data) > READ_MAX:
        return
    live = []
    t0 = time.monotonic()
    for h in spec:
        lock = _lock(h["name"])
        if lock is None:
            continue
        try:
            live.append((spawn(h, data, subprocess.DEVNULL),
                         t0 + h["timeout_ms"] / 1000.0, lock))
        except Exception:
            os.close(lock)
    while live:
        t = time.monotonic()
        for item in list(live):
            p, deadline, lock = item
            try:
                if p.poll() is None and t >= deadline:
                    kill(p)
                    p.wait(timeout=1)
            except Exception:
                pass
            if p.poll() is not None or t >= deadline:
                os.close(lock)
                live.remove(item)
        if live:
            time.sleep(0.02)


# -- wrap mode: the inner command ------------------------------------------

def inner_put(sid, text, now):
    """Store the wrapped command's output as this session's last good."""
    tmp = None
    try:
        path = _cache_path(INNER, sid)
        d = os.path.dirname(path)
        if not R.mkdirs_private(d):
            return
        fd, tmp = T._mkstemp(d, "." + INNER + ".")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"at": now, "text": text}, f, ensure_ascii=False)
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


def inner_get(sid, now):
    """The wrapped command's last output for this session when younger than
    INNER_LAST_GOOD_S, else None."""
    try:
        raw, _ = R._read_capped(_cache_path(INNER, sid), INNER_OUT_MAX * 8)
        d = json.loads(raw.decode("utf-8")) if raw is not None else None
        if isinstance(d, dict) and isinstance(d.get("text"), str) and \
                0 <= now - T._at(d) <= INNER_LAST_GOOD_S:
            return d["text"]
    except Exception:
        pass
    return None


def dispatch_inner(data, sid):
    """Start the inner runner with the payload on stdin, in this process's
    working directory and environment; its Popen, or None when one is still
    running from an earlier render or it cannot start. Never raises."""
    try:
        if not _free({"name": INNER}):
            return None
        fd = payload_fd(data)
        try:
            return subprocess.Popen([sys.executable, os.path.abspath(__file__), "--run-inner",
                                     T.safe_sid(sid or "unknown")],
                                    stdin=fd, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL, close_fds=True,
                                    start_new_session=True)
        finally:
            os.close(fd)
    except Exception:
        return None


def run_inner(sid):
    """The inner runner: run the wrapped command once (see the module doc).
    stdin is the payload, handed to the command untouched."""
    lock = _lock(INNER)
    if lock is None:
        return
    try:
        rec, _ = R.read_wrap([os.getcwd(), os.environ.get("CLAUDE_PROJECT_DIR")])
        if not rec or not rec["running"] or not R.wrap_applies(rec):
            return
        now = time.time()
        err = log_fd(INNER)
        try:
            p = subprocess.Popen(["/bin/sh", "-c", rec["command"]], stdin=0,
                                 stdout=subprocess.PIPE, stderr=err, close_fds=True,
                                 start_new_session=True)
        finally:
            if isinstance(err, int) and err >= 0:
                os.close(err)
        deadline = time.monotonic() + INNER_MAX_MS / 1000.0
        buf, ok = bytearray(), False
        fd = p.stdout.fileno()
        sel = selectors.DefaultSelector()
        sel.register(fd, selectors.EVENT_READ)
        try:
            while True:
                left = deadline - time.monotonic()
                if left <= 0:
                    break
                if sel.select(min(left, 0.05)):
                    chunk = os.read(fd, 65536)
                    if not chunk:
                        break           # EOF: every writer has closed stdout
                    buf += chunk[:INNER_OUT_MAX - len(buf)]
                elif p.poll() is not None:
                    break               # exited; a grandchild may hold stdout open
            if time.monotonic() < deadline:
                try:
                    ok = p.wait(timeout=max(deadline - time.monotonic(), 0)) == 0
                except subprocess.TimeoutExpired:
                    ok = False
        finally:
            sel.close()
            if p.poll() is None:
                kill(p)
            p.stdout.close()
        if ok:
            inner_put(sid, bytes(buf).decode("utf-8", "replace").rstrip("\r\n"), now)
    finally:
        os.close(lock)


# -- composing the line ------------------------------------------------------

def arrange_parts(displays, texts, drops, cfg):
    """[(text, priority)] in display order: the display hooks' texts (priority
    None: never dropped for width) and the segment drop dir's segments, sorted
    together by the user's `order`, then each one's `order` hint, then name
    (a display hook before a segment of the same name). `displays` is already
    in that order (registry.arrange); the sort keeps it."""
    rank = {n: i for i, n in enumerate(cfg["order"])}
    keyed = [((rank.get(h["name"], len(rank)), h["order"], h["name"], 0), texts[h["name"]], None)
             for h in displays if texts.get(h["name"])]
    keyed += [((rank.get(s["name"], len(rank)), s["order"], s["name"], 1), s["text"],
               s["priority"]) for s in drops]
    keyed.sort(key=lambda k: k[0])
    return [(text, prio) for _, text, prio in keyed]


def term_columns():
    """The terminal width from COLUMNS, or None when it is not set to a
    positive integer."""
    try:
        n = int(os.environ.get("COLUMNS", ""))
        return n if n > 0 else None
    except Exception:
        return None


def join_line(parts, inner, sep):
    line = sep.join(text for text, _ in parts)
    if inner:
        if line and "\x1b" in inner:
            inner += R.RESET  # its colour must not bleed into the segments
        line = f"{inner}{sep}{line}" if line else inner
    return line


def fit_line(parts, inner, sep, cols, reserve=0):
    """The line: the wrapped command's output (when there is one) first, the
    parts after it on its last line. With `cols` known and the last line
    wider than `cols` less `reserve` (the columns something appended after
    it will take: the health glyph), drop-dir segments go one at a time -
    the lowest priority first, and of equal ones the last shown - until it
    fits or none is left. A display hook's text and the wrapped output are
    never dropped."""
    parts = list(parts)
    line = join_line(parts, inner, sep)
    while cols and R.columns(line.rsplit("\n", 1)[-1]) + reserve > cols:
        drop = [i for i, (_, prio) in enumerate(parts) if prio is not None]
        if not drop:
            break
        del parts[min(drop, key=lambda i: (parts[i][1], -i))]
        line = join_line(parts, inner, sep)
    return line


# -- render ------------------------------------------------------------------

def render(data, now=None):
    """The status line for one payload (bytes). Never raises."""
    line = ""
    try:
        now = time.time() if now is None else now
        if len(data) > READ_MAX:
            return ""
        text = data.decode("utf-8", "replace")
        T.tee(text, now)
        try:
            d = _obj(json.loads(text))
        except Exception:
            d = {}
        sid = d.get("session_id") if isinstance(d.get("session_id"), str) else None
        cfg = R.config()
        hooks = R.load(now, project_dirs(d), cfg)
        records = [h for h in hooks if h["kind"] == "record"]
        displays = [h for h in hooks if h["kind"] == "display"]
        t0 = time.monotonic()
        wrap, _ = R.read_wrap(project_dirs(d))
        wrapped = bool(wrap and wrap["running"] and R.wrap_applies(wrap))
        runner = dispatch_inner(data, sid) if wrapped else None
        if records:
            dispatch_records(records, data)
        segs = run_displays(displays, data, sid, now) if displays else {}
        parts = arrange_parts(displays, segs, R.segments(sid, now, project_dirs(d), cfg), cfg)
        inner = None
        if wrapped:
            if runner is not None:
                try:
                    runner.wait(timeout=max(t0 + DISPLAY_BUDGET_MS / 1000.0 -
                                            time.monotonic(), 0))
                except subprocess.TimeoutExpired:
                    pass
            inner = inner_get(sid, time.time())  # the runner stamps it after `now`
        failing = any(R.health(h["health_path"], now, cfg["health_stale_min"])
                      for h in hooks if h.get("health_path"))
        line = fit_line(parts, inner, cfg["separator"], term_columns(),
                        R.columns(" " + GLYPH) if failing else 0)
        if failing:
            line = f"{line} {GLYPH}" if line else GLYPH
    except Exception:
        pass
    return line


def status():
    """Print the registry for a person: each hook, or why it is skipped."""
    now = time.time()
    cfg = R.config()
    hooks, problems = R.scan(now, [os.getcwd(), os.environ.get("CLAUDE_PROJECT_DIR")])
    print(f"registry: {R.hooks_dir()}")
    if not hooks and not problems:
        print("  no hooks registered")
    for h in R.arrange(hooks, dict(cfg, disabled=set())):
        state = "disabled in config.json" if h["name"] in cfg["disabled"] else "active"
        health = ""
        if h.get("health_path"):
            health = "  health: " + (R.health(h["health_path"], now, cfg["health_stale_min"])
                                     or "ok or unknown")
        print(f"  {h['name']}: {h['kind']}, {state}, timeout {h['timeout_ms']} ms, "
              f"runs {os.path.basename(h['argv'][0])}{health}")
    for name, why in problems:
        print(f"  {name}: skipped ({why})")
    segs, problems = R.scan_segments(None, now, [os.getcwd(), os.environ.get("CLAUDE_PROJECT_DIR")])
    if segs or problems:
        print(f"segments: {R.segments_dir()} (session files are read per render)")
    for sg in segs:
        state = "disabled in config.json" if sg["name"] in cfg["disabled"] else \
            ("shows" if sg["text"] else "empty")
        print(f"  {sg['name']}: all sessions, {state}, priority {sg['priority']}")
    for name, why in problems:
        print(f"  {name}: skipped ({why})")
    rec, why = R.read_wrap([os.getcwd(), os.environ.get("CLAUDE_PROJECT_DIR")])
    if rec:
        if not R.wrap_applies(rec):  # run_inner refuses it; never claim it runs
            state = "kept, not run (not the user settings file)"
        else:
            state = "running" if rec["running"] else "kept, not running"
        print(f"wrap: {state} - the "
              f"statusLine that was in {rec['settings']} (timeout {INNER_MAX_MS} ms, "
              f"stderr in {os.path.join(R.log_dir(), INNER + '.log')})")
    elif why != "missing":
        print(f"wrap: {R.wrap_path()} skipped ({why})")
    return 0


def main(argv):
    if len(argv) >= 2 and argv[1] == "--run-records":
        try:
            run_records()
        except BaseException:
            pass
        return 0
    if len(argv) >= 3 and argv[1] == "--run-inner":
        try:
            run_inner(argv[2])
        except BaseException:
            pass
        return 0
    if len(argv) >= 2 and argv[1] == "--status":
        return status()
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    try:
        data = sys.stdin.buffer.read(READ_MAX + 1)
    except Exception:
        data = b""
    line = render(data)
    try:
        print(line)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    try:
        code = main(sys.argv)
    except BaseException:  # the status line never raises
        code = 0
    sys.exit(code)
