"""Shared fixtures. Hermetic: CLAUDE_CONFIG_DIR and HOME both point at a temp
dir (so an expanduser fallback cannot reach the real ~/.claude), and the
plugin env vars are removed. Scripts run as subprocesses, the way Claude Code
runs them."""
import json, os, subprocess, sys, tempfile, unittest

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.dirname(HOOKS)
SKILL = os.path.join(PLUGIN, "skills", "install-statusline")
STATUSLINE = os.path.join(HOOKS, "statusline.py")
if HOOKS not in sys.path:
    sys.path.insert(0, HOOKS)

CTX = {"used_percentage": 42.0, "context_window_size": 1_000_000,
       "total_input_tokens": 420_000}
PUB = ("claude-kit", "context-gate")  # the publisher's dir, as a fixture
DEFAULT_GAUGE = {
    "v": 1, "writer": "context-guard",
    "thresholds": {"unit": "tokens_remaining", "interp": "linear_clamped",
                   "anchors": [{"window": 200000, "due": 70000, "hard": 40000},
                               {"window": 1000000, "due": 150000, "hard": 60000}]},
    "labels": {"due": "checkpoint DUE", "hard": "HARD gate"}}
DROP = ("CLAUDE_PLUGIN_DATA", "CLAUDE_PLUGIN_ROOT",
        "CONTEXT_GUARD_CONTEXT_WINDOW", "CLAUDE_KIT_CONTEXT_WINDOW")


class Hermetic(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cfg = self.tmp.name
        self.env = dict(os.environ, CLAUDE_CONFIG_DIR=self.cfg, HOME=self.cfg)
        for k in DROP:
            self.env.pop(k, None)
        self._saved = {k: os.environ.get(k) for k in ("CLAUDE_CONFIG_DIR", "HOME") + DROP}
        os.environ["CLAUDE_CONFIG_DIR"] = self.cfg
        os.environ["HOME"] = self.cfg
        for k in DROP:
            os.environ.pop(k, None)

    def tearDown(self):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self.tmp.cleanup()

    # -- running ---------------------------------------------------------

    def render(self, payload=None, raw=None, env=None):
        """(returncode, stdout, stderr) of one status-line render."""
        if payload is not None:
            payload.setdefault("session_id", "s")
            payload.setdefault("context_window", dict(CTX))
            payload.setdefault("model", {"display_name": "Fable"})
        e = dict(self.env, **(env or {}))
        p = subprocess.run([sys.executable, STATUSLINE],
                           input=raw if raw is not None else json.dumps(payload),
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", env=e, timeout=30)
        return p.returncode, p.stdout, p.stderr

    def line(self, payload=None, **kw):
        rc, out, err = self.render(payload if payload is not None else {}, **kw)
        self.assertEqual((rc, err), (0, ""))
        return out

    # -- files -----------------------------------------------------------

    def sensor_file(self, sid="s"):
        return os.path.join(self.cfg, "statusline", "sensor", sid + ".json")

    def read_sensor(self, sid="s"):
        p = self.sensor_file(sid)
        if not os.path.exists(p):
            return None
        with open(p) as f:
            return json.load(f)

    def write_json(self, path, obj=None, raw=None):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(raw if raw is not None else json.dumps(obj))
        return path

    def publish(self, sid="s", gauge=None, state=None, raw_gauge=None):
        """Seed the publisher side: gauge.json and this session's state."""
        d = os.path.join(self.cfg, *PUB)
        if gauge is not False:
            self.write_json(os.path.join(d, "gauge.json"),
                            DEFAULT_GAUGE if gauge is None else gauge, raw=raw_gauge)
        if state is not False:
            self.write_json(os.path.join(d, sid + ".json"),
                            {"epoch": 0} if state is None else state)

    def all_files(self):
        out = []
        for root, _, files in os.walk(self.cfg):
            out += [os.path.join(root, f) for f in files]
        return out
