"""Shared fixtures. Hermetic: CLAUDE_CONFIG_DIR and HOME both point at a temp
dir (so an expanduser fallback cannot reach the real ~/.claude), and the
plugin env vars are removed. The tee runs as a subprocess, the way a
status-line renderer runs it."""
import json, os, subprocess, sys, tempfile, unittest

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.dirname(HOOKS)
TEE = os.path.join(HOOKS, "tee.py")
if HOOKS not in sys.path:
    sys.path.insert(0, HOOKS)

CTX = {"used_percentage": 42.0, "context_window_size": 1_000_000,
       "total_input_tokens": 420_000}
DROP = ("CLAUDE_PLUGIN_DATA", "CLAUDE_PLUGIN_ROOT")


def run(script, payload=None, raw=None, env=None, args=()):
    """(returncode, stdout, stderr) of one run of `script` with a payload on
    stdin: `raw` text as is, else `payload` as JSON."""
    text = raw if raw is not None else json.dumps(payload)
    p = subprocess.run([sys.executable, script, *args], input=text, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=env, timeout=30)
    return p.returncode, p.stdout, p.stderr


def with_defaults(payload):
    """A copy of `payload` with the fields a real render always carries."""
    p = dict(payload)
    p.setdefault("session_id", "s")
    p.setdefault("context_window", dict(CTX))
    p.setdefault("model", {"display_name": "Fable"})
    return p


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

    def tee(self, payload=None, raw=None, args=()):
        """Run the tee on a payload (defaults filled in); assert it printed
        nothing and exited 0."""
        if payload is not None:
            payload = with_defaults(payload)
        rc, out, err = run(TEE, payload, raw=raw, env=self.env, args=args)
        self.assertEqual((rc, out, err), (0, "", ""))

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

    def all_files(self):
        out = []
        for root, _, files in os.walk(self.cfg):
            out += [os.path.join(root, f) for f in files]
        return out
