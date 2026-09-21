"""Parity with the statusline plugin's own writer of the sensor record.

The tee carries a vendored copy of that writer (a plugin may not import
another plugin's code). This suite holds the copy to its source, two ways:

- Drift: every vendored definition in tee.py is compared, as parsed code,
  with the definition of the same name in statusline's hooks/sensor.py or
  hooks/statusline.py, and sensor_blocks() with the statements of
  statusline.py's main() it restates. An edit to either side that the other
  does not get fails here.
- Records: statusline's record cases (its test_statusline_state.py and
  test_sensor.py) run through statusline.py and through tee.py, each in its
  own config dir, and the two resulting records must be identical (the `at`
  stamp of the render itself aside, which is the clock).

Runs only in the source repo, where the statusline plugin sits beside this one
(plugins/statusline/hooks/); an installed copy of this plugin skips it. The
statusline modules are read from their files, sensor.py loaded under a private
name, statusline.py only parsed and run as a subprocess."""
import ast, importlib.util, json, os, tempfile, time, unittest

import helpers
import tee as T

SL_HOOKS = os.path.join(os.path.dirname(helpers.PLUGIN), "statusline", "hooks")
SENSOR = os.path.join(SL_HOOKS, "sensor.py")
STATUSLINE = os.path.join(SL_HOOKS, "statusline.py")
BESIDE = os.path.isfile(SENSOR) and os.path.isfile(STATUSLINE)

FROM_SENSOR = ("SENSOR_V", "READ_MAX", "FUTURE_SLACK_S", "_SAFE_SID", "base_dir",
               "safe_sid", "sensor_dir", "sensor_path", "_load", "_is_v", "_at",
               "read_sensor", "_mkstemp", "_mkdir_private", "write_sensor")
FROM_STATUSLINE = ("MAX_AHEAD", "num", "_WINDOW_KEY", "LIMIT_FIELDS", "WINDOWS_MAX",
                   "limits_record", "obj")


def top_level(path):
    """{name: ast.dump} of the module-level functions and single-name
    assignments in the file at path (comments and layout do not count;
    docstrings do)."""
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    out = {}
    for n in tree.body:
        if isinstance(n, ast.FunctionDef):
            out[n.name] = ast.dump(n)
        elif isinstance(n, ast.Assign) and len(n.targets) == 1 and \
                isinstance(n.targets[0], ast.Name):
            out[n.targets[0].id] = ast.dump(n)
    return out


def function(path, name):
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)


def load_sensor():
    spec = importlib.util.spec_from_file_location("statusline_sensor_under_test", SENSOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@unittest.skipUnless(BESIDE, "statusline plugin not beside this one")
class Drift(unittest.TestCase):
    def test_vendored_definitions_match_their_source(self):
        mine = top_level(helpers.TEE)
        for src, names in ((SENSOR, FROM_SENSOR), (STATUSLINE, FROM_STATUSLINE)):
            theirs = top_level(src)
            for name in names:
                with self.subTest(name=name):
                    self.assertIn(name, theirs, f"{name} is gone from {src}")
                    self.assertEqual(mine[name], theirs[name],
                                     f"{name} drifted from {os.path.basename(src)}")

    def test_everything_the_writer_uses_is_vendored(self):
        """Every module-level name the vendored functions reach, transitively,
        in their source file is in the copy: a new helper there that the copy
        lacks fails here, not at a user's render."""
        for src, names in ((SENSOR, FROM_SENSOR), (STATUSLINE, FROM_STATUSLINE)):
            with open(src, encoding="utf-8") as f:
                tree = ast.parse(f.read())
            defs = {}
            for n in tree.body:
                if isinstance(n, ast.FunctionDef):
                    defs[n.name] = n
                elif isinstance(n, ast.Assign) and len(n.targets) == 1 and \
                        isinstance(n.targets[0], ast.Name):
                    defs[n.targets[0].id] = n
            todo = [x for x in names if isinstance(defs.get(x), ast.FunctionDef)]
            reached = set()
            while todo:
                for n in ast.walk(defs[todo.pop()]):
                    if isinstance(n, ast.Name) and n.id in defs and n.id not in reached:
                        reached.add(n.id)
                        todo.append(n.id)
            with self.subTest(src=os.path.basename(src)):
                self.assertEqual(sorted(reached - set(names)), [])

    def test_sensor_blocks_restates_main(self):
        """The statements of statusline.py's main() that build the two blocks
        - from `cw = ...` to the session-id check, then the `exact` expression
        and the write call's arguments - equal sensor_blocks()'s."""
        main = function(STATUSLINE, "main")
        body = main.body
        start = next(i for i, s in enumerate(body)
                     if isinstance(s, ast.Assign) and ast.unparse(s.targets[0]) == "cw")
        guard = next(i for i, s in enumerate(body) if isinstance(s, ast.If) and
                     ast.unparse(s.test) == "sid")
        theirs = [ast.unparse(s) for s in body[start:guard]]
        write_try = body[guard].body[0]
        theirs_exact = ast.unparse(write_try.body[0])
        call = write_try.body[1].value
        self.assertEqual(ast.unparse(call),
                         "S.write_sensor(sid, exact, limits_record(d.get('rate_limits'), now), now)")

        blocks = function(helpers.TEE, "sensor_blocks").body[1]  # the try
        mine = [ast.unparse(s) for s in blocks.body]
        self.assertEqual(mine[0], "d = obj(d)")
        self.assertEqual(mine[1:1 + len(theirs)], theirs)
        self.assertEqual(mine[1 + len(theirs)], theirs_exact)
        self.assertEqual(mine[2 + len(theirs)],
                         "return (sid, exact, limits_record(d.get('rate_limits'), now))")


def cases(now):
    """(name, seed, sid, renders): `seed` is raw text or a record to put at the
    session's path first (or None), and each render is a payload dict (the
    usual fields filled in) or raw stdin text. Built once per case so both
    writers see the same numbers."""
    five, seven = now + 3600, now + 3 * 86400
    out = [
        ("shape", None, "s", [{"rate_limits": {
            "five_hour": {"used_percentage": 23.5, "resets_at": five},
            "seven_day": {"used_percentage": 91, "resets_at": int(seven)}}}]),
        ("every window", None, "s", [{"rate_limits": {
            "five_hour": {"used_percentage": 1, "resets_at": now + 60},
            "seven_day_opus": {"used_percentage": 99, "resets_at": now + 86400},
            "spend_limit": {"used_percentage": 5, "resets_at": now + 7200}}}]),
        ("numeric fields and safe names", None, "s", [{"rate_limits": {
            "five_hour": {"used_percentage": 10, "resets_at": now + 60,
                          "label": "free text", "extra": {"x": 1}},
            "Bad Name\n": {"used_percentage": 1, "resets_at": now + 60},
            "x" * 41: {"used_percentage": 1, "resets_at": now + 60},
            "at": {"used_percentage": 1, "resets_at": now + 60},
            "seven_day": {"used_percentage": "abc", "resets_at": now + 60},
            "spend_limit": {"used_percentage": True, "resets_at": "soon"},
            "ms_window": {"used_percentage": 3, "resets_at": (now + 60) * 1000}}}]),
        ("past reset kept", None, "s", [{"rate_limits": {
            "five_hour": {"used_percentage": 100, "resets_at": now - 60}}}]),
        ("bad limits leave exact", None, "s", [{"rate_limits": {"five_hour": "x"}}]),
        ("exact kept when only limits arrive",
         {"v": 1, "exact": {"pct": 12.0, "tokens": 120_000, "window": 1_000_000, "at": 1.0}},
         "s", [{"context_window": {}, "rate_limits": {
             "five_hour": {"used_percentage": 50, "resets_at": now + 60}}}]),
        ("stored limits survive", None, "s", [
            {"rate_limits": {"five_hour": {"used_percentage": 50, "resets_at": now + 60}}},
            {}]),
        ("numeric string pct", None, "s", [{"context_window": dict(helpers.CTX,
                                                                   used_percentage="42")}]),
        ("unknown keys not carried", {"v": 1, "junk": "x" * 100}, "s", [{}]),
        ("newer record not regressed",
         {"v": 1, "exact": {"pct": 1.0, "tokens": 10_000, "window": 1_000_000,
                            "at": now + 30}}, "s", [{}]),
        ("far future does not block",
         {"v": 1, "exact": {"pct": 1.0, "tokens": 1, "window": 1_000_000,
                            "at": now + 86400}}, "s", [{}]),
        ("three renders", None, "s", [{}, {}, {}]),
        ("unparsable stdin", None, "s", ["{not json"]),
        ("empty stdin", None, "s", [""]),
        ("not an object", None, "s", ["[1, 2]", "7", "null"]),
        ("nan pct", None, "s", ['{"session_id": "s", "context_window": {"used_percentage":'
                                ' NaN, "context_window_size": 1000000,'
                                ' "total_input_tokens": 1}}']),
    ]
    bads = [None, [], "x", 5, True, {}, {"five_hour": None}, {"five_hour": "90%"},
            {"five_hour": {}}, {"five_hour": {"used_percentage": "abc", "resets_at": None}},
            {"five_hour": {"used_percentage": float("nan")}},
            {"seven_day": {"resets_at": "Infinity"}}]
    for i, bad in enumerate(bads):
        p = {"context_window": None}
        if bad is not None:
            p["rate_limits"] = bad
        out.append((f"bad limits {i}", None, "s", [p]))
    for sid in (None, 7, ["s"]):
        out.append((f"no sid {sid!r}", None, "s", [{"session_id": sid, "rate_limits": {
            "five_hour": {"used_percentage": 1, "resets_at": now + 60}}}]))
    for bad in ("abc", True, [], {}, "NaN", "inf"):
        out.append((f"bad pct {bad!r}", None, "s", [{
            "context_window": dict(helpers.CTX, used_percentage=bad),
            "rate_limits": {"five_hour": {"used_percentage": 20, "resets_at": now + 3600}}}]))
    for field in ("context_window_size", "total_input_tokens"):
        out.append((f"bad {field}", None, "s", [{"context_window": dict(helpers.CTX,
                                                                          **{field: "lots"})}]))
    for raw in ("{garbage", "[]", json.dumps({"v": 2, "exact": {"at": 9e99}}),
                json.dumps({"exact": {"pct": 1}})):
        out.append((f"record on disk {raw[:12]!r}", raw, "s", [{}]))
    limits = {}
    for i in range(100):
        v = "bad" if i % 10 == 0 else i
        limits[f"w{i:03d}"] = {"used_percentage": v,
                               "resets_at": "x" if v == "bad" else now + 60}
    out.append(("window cap", None, "s", [{"rate_limits": limits}] * 2))
    n = float(int(now))
    huge = "9" * 400
    out.append(("huge integer", None, "s", [
        '{"session_id": "s", "model": {"display_name": "Fable"},'
        ' "context_window": {"used_percentage": %s, "context_window_size": 1000000,'
        ' "total_input_tokens": 1},'
        ' "rate_limits": {"five_hour": {"used_percentage": %s, "resets_at": %f},'
        ' "seven_day": {"used_percentage": 50, "resets_at": %s},'
        ' "spend_limit": {"used_percentage": 5, "resets_at": %f}}}'
        % (huge, huge, n + 3600, huge, n + 7200)]))
    for pct in (1e300, -5):
        out.append((f"pct clamp {pct}", None, "s",
                    [{"context_window": dict(helpers.CTX, used_percentage=pct)}]))
    for size in (0, -5, -1e9, 0.5, 0.999, 1, 1.5):
        out.append((f"size {size}", None, "s",
                    [{"context_window": dict(helpers.CTX, context_window_size=size)}]))
    for tok in (-7, 2_000_000, 1.9):
        out.append((f"tokens {tok}", None, "s",
                    [{"context_window": dict(helpers.CTX, total_input_tokens=tok)}]))
    for sid in ("../../evil", "..", "a/b", ".hidden", "x" * 128, "x" * 129, "中",
                "0c7eafc7-18dc-4274-9add-93aa21324fb3"):
        out.append((f"sid {sid[:12]!r}", None, sid, [{"session_id": sid}]))
    return out


@unittest.skipUnless(BESIDE, "statusline plugin not beside this one")
class Records(unittest.TestCase):
    def outcome(self, script, seed, sid, renders):
        """(files under the config dir, their parsed contents) after running
        `renders` through `script` in a fresh config dir; `at` stamps taken
        during the run read as "NOW"."""
        with tempfile.TemporaryDirectory() as cfg:
            env = dict(os.environ, CLAUDE_CONFIG_DIR=cfg, HOME=cfg)
            for k in helpers.DROP:
                env.pop(k, None)
            path = os.path.join(cfg, "statusline", "sensor", T.safe_sid(sid) + ".json")
            if seed is not None:
                os.makedirs(os.path.dirname(path))
                with open(path, "w") as f:
                    f.write(seed if isinstance(seed, str) else json.dumps(seed))
            t0 = time.time()
            for r in renders:
                if isinstance(r, str):
                    rc, _, err = helpers.run(script, raw=r, env=env)
                else:
                    rc, _, err = helpers.run(script, helpers.with_defaults(r), env=env)
                self.assertEqual((rc, err), (0, ""), script)
            t1 = time.time()
            files = {}
            for root, _, names in os.walk(cfg):
                for n in names:
                    p = os.path.join(root, n)
                    with open(p) as f:
                        raw = f.read()
                    try:
                        rec = json.loads(raw)
                    except ValueError:
                        rec = raw
                    if isinstance(rec, dict):
                        for block in rec.values():
                            if isinstance(block, dict) and isinstance(block.get("at"), float) \
                                    and t0 <= block["at"] <= t1:
                                block["at"] = "NOW"
                    files[os.path.relpath(p, cfg)] = rec
            return files

    def test_same_records_as_statusline(self):
        for name, seed, sid, renders in cases(time.time()):
            with self.subTest(case=name):
                theirs = self.outcome(STATUSLINE, seed, sid, renders)
                mine = self.outcome(helpers.TEE, seed, sid, renders)
                self.assertEqual(mine, theirs)

    def test_cases_exercise_both_blocks(self):
        """The corpus is not vacuous: some cases end with each block written,
        and some with no record at all."""
        seen = set()
        for name, seed, sid, renders in cases(time.time()):
            if seed is not None:
                continue
            files = self.outcome(helpers.TEE, seed, sid, renders)
            recs = [r for r in files.values() if isinstance(r, dict)]
            seen.add("none" if not recs else "record")
            for r in recs:
                seen |= {k for k in ("exact", "rate_limits") if k in r}
        self.assertEqual(seen, {"none", "record", "exact", "rate_limits"})

    def test_unwritable_sensor_dir(self):
        """A file where the sensor dir should be: neither writes, neither fails."""
        for script in (STATUSLINE, helpers.TEE):
            with tempfile.TemporaryDirectory() as cfg:
                os.makedirs(os.path.join(cfg, "statusline"))
                with open(os.path.join(cfg, "statusline", "sensor"), "w") as f:
                    f.write("not a dir")
                env = dict(os.environ, CLAUDE_CONFIG_DIR=cfg, HOME=cfg)
                rc, _, err = helpers.run(script, helpers.with_defaults({}), env=env)
                self.assertEqual((rc, err), (0, ""))
                with open(os.path.join(cfg, "statusline", "sensor")) as f:
                    self.assertEqual(f.read(), "not a dir")


@unittest.skipUnless(BESIDE, "statusline plugin not beside this one")
class Writer(helpers.Hermetic):
    """statusline's test_sensor.py write cases, in-process, against both
    write_sensor()s: the same return values and the same record."""
    EX = {"pct": 1.0, "tokens": 1, "window": 100, "at": 5.0}

    @classmethod
    def setUpClass(cls):
        cls.S = load_sensor()

    def both(self, steps):
        """Run `steps` (a list of (sid, kwargs)) through each module in a fresh
        sensor dir; return [(results, record)] per module."""
        out = []
        for mod in (self.S, T):
            d = os.path.join(self.cfg, "statusline")
            if os.path.isdir(d):
                for root, dirs, files in os.walk(d, topdown=False):
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for x in dirs:
                        os.rmdir(os.path.join(root, x))
            res = [mod.write_sensor(sid, **kw) for sid, kw in steps]
            out.append((res, self.read_sensor(), sorted(
                os.listdir(os.path.join(d, "sensor"))) if os.path.isdir(
                os.path.join(d, "sensor")) else None))
        return out

    def check(self, steps):
        theirs, mine = self.both(steps)
        self.assertEqual(mine, theirs)

    def test_nothing_to_write(self):
        self.check([("s", {}), (None, {"exact": self.EX}), ("", {"exact": self.EX})])

    def test_merge_both_ways(self):
        rl = {"five_hour": {"used_percentage": 1.0}, "at": 6.0}
        self.check([("s", {"exact": self.EX, "now": 5.0}),
                    ("s", {"rate_limits": rl, "now": 6.0}),
                    ("s", {"exact": dict(self.EX, at=7.0), "now": 7.0})])

    def test_older_render_skips(self):
        self.check([("s", {"exact": dict(self.EX, at=100.0), "now": 100.0}),
                    ("s", {"exact": dict(self.EX, at=99.0), "now": 99.0}),
                    ("s", {"exact": dict(self.EX, at=30.0), "now": 30.0})])

    def test_future_slack_edge(self):
        self.check([("s", {"exact": dict(self.EX, at=160.0), "now": 160.0}),
                    ("s", {"exact": dict(self.EX, at=100.0), "now": 100.0}),
                    ("s", {"exact": dict(self.EX, at=99.0), "now": 99.0})])

    def test_read_ignores_other_versions(self):
        for rec in ({"v": 2}, {"v": "1"}, {"v": True}, {}, [1], {"v": 1, "x": 1}):
            with self.subTest(rec=rec):
                self.write_json(T.sensor_path("s"), rec)
                self.assertEqual(T.read_sensor("s"), self.S.read_sensor("s"))

    def test_paths_and_sids_agree(self):
        corpus = ["0c7eafc7-18dc-4274-9add-93aa21324fb3", "s", "..", ".", "../../evil",
                  "a/b", ".hidden", "-lead", "x" * 128, "x" * 129, "", None, 0, 123,
                  1.5, ["s"], {"a": 1}, b"s", "été", "中", "a\nb", "\ud800", "sid-abc"]
        for cfg in (self.cfg, "", None):
            if cfg is None:
                os.environ.pop("CLAUDE_CONFIG_DIR", None)
            else:
                os.environ["CLAUDE_CONFIG_DIR"] = cfg
            self.assertEqual(T.base_dir(), self.S.base_dir())
            for sid in corpus:
                self.assertEqual(T.safe_sid(sid), self.S.safe_sid(sid), repr(sid))
                self.assertEqual(T.sensor_path(sid), self.S.sensor_path(sid), repr(sid))


if __name__ == "__main__":
    unittest.main()
