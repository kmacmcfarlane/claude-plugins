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
   the render) that runs each record hook under its timeout. The render never
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
6. Print the segments joined by the configured separator, in order.

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
GLYPH = "⚠"          # a record hook's health file says it is failing


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
                if not chunk or len(st[2]) >= OUT_MAX:
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

def dispatch_records(hooks, data):
    """Hand the payload to one detached runner for the record hooks; returns
    at once. Never raises."""
    try:
        spec = json.dumps([{k: h[k] for k in ("name", "kind", "argv", "timeout_ms")}
                           for h in hooks])
        fd = payload_fd(data)
        try:
            subprocess.Popen([sys.executable, os.path.abspath(__file__), "--run-records", spec],
                             stdin=fd, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, cwd=workdir(), close_fds=True,
                             start_new_session=True)
        finally:
            os.close(fd)
    except Exception:
        pass


def run_records(spec):
    """The detached runner: start every record hook with the payload read from
    stdin, byte for byte, then kill any still running at its timeout."""
    data = sys.stdin.buffer.read(READ_MAX + 1)
    if len(data) > READ_MAX:
        return
    procs = []
    t0 = time.monotonic()
    for h in json.loads(spec):
        try:
            procs.append((spawn(h, data, subprocess.DEVNULL), t0 + h["timeout_ms"] / 1000.0))
        except Exception:
            continue
    for p, deadline in procs:
        try:
            p.wait(timeout=max(deadline - time.monotonic(), 0))
        except subprocess.TimeoutExpired:
            kill(p)
            try:
                p.wait(timeout=1)
            except Exception:
                pass
        except Exception:
            pass


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
        if records:
            dispatch_records(records, data)
        segs = run_displays(displays, data, sid, now) if displays else {}
        line = cfg["separator"].join(segs[h["name"]] for h in displays if segs.get(h["name"]))
        if any(R.health(h["health_path"], now, cfg["health_stale_min"])
               for h in hooks if h.get("health_path")):
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
    return 0


def main(argv):
    if len(argv) >= 3 and argv[1] == "--run-records":
        try:
            run_records(argv[2])
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
