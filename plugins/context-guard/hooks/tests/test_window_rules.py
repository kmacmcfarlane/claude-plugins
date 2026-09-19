"""window_rules: the mirrored window selection, one test per truth-table row
(plan d63e section 2) plus the auto-compact window (decision 34). Pure: envs are
dicts, nothing touches os.environ."""
import json, os, sys, tempfile, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import window_rules as R
import lib_context as L

M1, K200 = 1_000_000, 200_000


def env(**kw):
    return R.env_inputs({k: str(v) for k, v in kw.items()})


def derive(model, e=None, **kw):
    return R.derive(model, e if e is not None else env(), **kw)


class TestTruthTable(unittest.TestCase):
    def check(self, d, window, resolved, rule=None):
        self.assertEqual((d["window"], d["resolved"]), (window, resolved), d)
        if rule:
            self.assertEqual(d["rule"], rule)

    def test_row01_native_1m(self):
        for m in ("claude-opus-5", "claude-opus-4-7", "claude-opus-4-8", "claude-sonnet-5",
                  "claude-fable-5", "claude-fable-5-1", "claude-mythos-5",
                  "claude-mythos-5-1", "claude-mythos-preview"):
            with self.subTest(m=m):
                self.check(derive(m), M1, True, "native_1m")

    def test_row02_suffix(self):
        self.check(derive("claude-opus-5[1m]"), M1, True, "suffix_1m")
        self.check(derive("claude-opus-5[1M]"), M1, True, "suffix_1m")

    def test_row03_haiku_first_party_id(self):
        self.check(derive("claude-haiku-4-5-20251001"), K200, True, "catalog_200k")
        self.check(derive("claude-haiku-4-5"), K200, True, "catalog_200k")

    def test_row04_suffix_has_no_support_check(self):
        self.check(derive("claude-haiku-4-5[1m]"), M1, True, "suffix_1m")

    def test_row05_disable_1m(self):
        self.check(derive("claude-opus-5", env(CLAUDE_CODE_DISABLE_1M_CONTEXT=1)),
                   K200, True, "disable_1m")

    def test_row06_disable_1m_beats_suffix(self):
        for v in ("true", " TRUE ", "yes", "on"):
            with self.subTest(v=v):
                self.check(derive("claude-opus-5[1m]", env(CLAUDE_CODE_DISABLE_1M_CONTEXT=v)),
                           K200, True)
        # Not a truthy spelling: 1M stands.
        self.check(derive("claude-opus-5[1m]", env(CLAUDE_CODE_DISABLE_1M_CONTEXT="0")), M1, True)

    def test_row07_disable_compact_plus_max_context_tokens(self):
        e = env(DISABLE_COMPACT=1, CLAUDE_CODE_MAX_CONTEXT_TOKENS=500000)
        for m in ("claude-opus-5", "claude-haiku-4-5", "claude-opus-5[1m]", "my-gw-model"):
            with self.subTest(m=m):
                self.check(derive(m, e), 500_000, True, "max_context_tokens")
        # DISABLE_AUTO_COMPACT is not DISABLE_COMPACT.
        e = env(DISABLE_AUTO_COMPACT=1, CLAUDE_CODE_MAX_CONTEXT_TOKENS=500000)
        self.check(derive("claude-opus-5", e), M1, True, "native_1m")
        # Claude Code's own integer parse: 5e5 and 500,000 are 500000.
        for v in ("5e5", "500,000", " 500000 "):
            e = env(DISABLE_COMPACT=1, CLAUDE_CODE_MAX_CONTEXT_TOKENS=v)
            self.check(derive("claude-opus-5", e), 500_000, True, "max_context_tokens")
        # NaN or <= 0 is no override at all.
        for v in ("abc", "0", "-5"):
            e = env(DISABLE_COMPACT=1, CLAUDE_CODE_MAX_CONTEXT_TOKENS=v)
            self.check(derive("claude-opus-5", e), M1, True, "native_1m")

    def test_row08_max_context_tokens_ignored_for_catalog_models(self):
        e = env(CLAUDE_CODE_MAX_CONTEXT_TOKENS=500000)
        self.check(derive("claude-opus-5", e), M1, True, "native_1m")
        self.check(derive("claude-haiku-4-5", e), K200, True)

    def test_row09_custom_model_with_max_context_tokens(self):
        self.check(derive("my-gw-model", env(CLAUDE_CODE_MAX_CONTEXT_TOKENS=300000)),
                   300_000, False, "max_context_tokens_custom")

    def test_row10_credits_latch(self):
        self.check(derive("claude-opus-5", latch=True, latch_known=True),
                   K200, True, "credits_latch")
        # Never raises a 200K window.
        self.check(derive("claude-haiku-4-5", latch=True), K200, True, "catalog_200k")

    def test_row11_latch_under_max_context_override(self):
        e = env(DISABLE_COMPACT=1, CLAUDE_CODE_MAX_CONTEXT_TOKENS=800000)
        self.check(derive("claude-opus-5", e, latch=True), 800_000, True, "max_context_tokens")

    def test_row12_latch_without_process_marker(self):
        self.check(derive("claude-opus-5", latch=True, latch_known=False),
                   K200, False, "credits_latch")

    def test_row13_third_party_or_foreign_base_url(self):
        for e in (env(CLAUDE_CODE_USE_BEDROCK=1), env(CLAUDE_CODE_USE_VERTEX="true"),
                  env(ANTHROPIC_BASE_URL="https://gw.example.com/v1")):
            with self.subTest(e=e["provider"]):
                self.check(derive("claude-opus-5", e), M1, False, "native_1m_3p")
        # The Anthropic API host itself, or the assume flag, is direct.
        self.check(derive("claude-opus-5", env(ANTHROPIC_BASE_URL="https://api.anthropic.com")),
                   M1, True)
        self.check(derive("claude-opus-5", env(ANTHROPIC_BASE_URL="https://gw.example.com",
                                               _CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL=1)),
                   M1, True)

    def test_row14_sonnet_4_6(self):
        d = derive("claude-sonnet-4-6")
        self.check(d, K200, False)
        self.assertIn(d["rule"], ("beta_unobservable", "experiment"))

    def test_row15_beta_capable_200k(self):
        for m in ("claude-sonnet-4-5-20250929", "claude-opus-4-6", "claude-sonnet-4-20250514"):
            with self.subTest(m=m):
                self.check(derive(m), K200, False, "beta_unobservable")

    def test_row16_served_catalog(self):
        self.check(derive("claude-haiku-4-5", served=150_000), 150_000, False, "served_catalog")
        self.check(derive("claude-opus-5", served=900_000), 900_000, False, "served_catalog")
        # Not native: a declared 1M is believed as 200K.
        self.check(derive("claude-opus-4-5", served=M1), K200, False, "served_catalog")

    def test_row17_no_model(self):
        for m in (None, "", "  "):
            self.check(derive(m), None, False, "no_model")

    def test_row18_unknown_claude_id(self):
        self.check(derive("claude-opus-6"), K200, False, "unknown_model")
        self.check(derive("claude-3-opus-20240229"), K200, False, "unknown_model")

    def test_js_int_mirrors_yl(self):
        cases = {"500000": 500000, " 42 ": 42, "5e5": 500000, "1.5e5": 150000,
                 "1.23456e2": None, "1,000,000": 1000000, "1_000": 1000, "900k": 900,
                 "0x10": 0, "+7": 7, "-3": -3, "abc": None, "": None, "1,00": 1}
        for raw, want in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(R.js_int(raw), want)
        self.assertIsNone(R.js_int(None))

    def test_env_inputs_carry_no_env_strings(self):
        e = R.env_inputs({"ANTHROPIC_BASE_URL": "https://user:secret@gw.example.com",
                          "CLAUDE_CODE_MAX_CONTEXT_TOKENS": "123456",
                          "CLAUDE_CODE_ENTRYPOINT": "cli"})
        blob = json.dumps(e)
        self.assertNotIn("secret", blob)
        self.assertNotIn("gw.example.com", blob)
        self.assertEqual(e["mct"], 123456)
        self.assertFalse(e["first_party_direct"])

    def test_provider_ambiguity_is_not_first_party(self):
        e = env(CLAUDE_CODE_USE_BEDROCK=1, CLAUDE_CODE_USE_VERTEX=1)
        self.assertEqual(e["provider"], "ambiguous")
        self.assertFalse(derive("claude-opus-5", e)["resolved"])


class TestServedCatalog(unittest.TestCase):
    def test_reads_only_model_rows(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "cache", "model-catalog")
            os.makedirs(p)
            with open(os.path.join(p, "acct-org-cc.json"), "w") as f:
                json.dump({"version": 2, "fetchedAt": 1, "catalog": {"config": {"models": [
                    {"id": "claude-opus-5"},
                    {"id": "claude-haiku-4-5", "context_window": 150000},
                    {"id": "claude-sonnet-5", "runtime": {"max_input_tokens": 600000},
                     "context_window": 900000}]}}}, f)
            self.assertIsNone(R.served_declared(d, "claude-opus-5", L.read_json_file))
            self.assertEqual(R.served_declared(d, "claude-haiku-4-5", L.read_json_file), 150_000)
            self.assertEqual(R.served_declared(d, "claude-sonnet-5", L.read_json_file), 600_000)
            self.assertIsNone(R.served_declared(d, None, L.read_json_file))


class TestAutoCompact(unittest.TestCase):
    NONE = {"window": None, "unparsed": False, "enabled": None}

    def acw(self, model="claude-opus-5", mw=M1, e=None, s=None, **kw):
        return R.autocompact(model, mw, e if e is not None else env(), s or self.NONE, **kw)

    def test_env_window(self):
        a = self.acw(e=env(CLAUDE_CODE_AUTO_COMPACT_WINDOW=500000))
        self.assertEqual(a, {"window": 500_000, "resolved": True, "source": "env"})
        # Clamped to [100K, 1M]; at or above the model window it lowers nothing.
        self.assertEqual(self.acw(e=env(CLAUDE_CODE_AUTO_COMPACT_WINDOW=50000))["window"], 100_000)
        self.assertIsNone(self.acw(e=env(CLAUDE_CODE_AUTO_COMPACT_WINDOW=5000000))["window"])
        self.assertIsNone(self.acw(mw=K200, e=env(CLAUDE_CODE_AUTO_COMPACT_WINDOW=500000))["window"])

    def test_env_beats_settings(self):
        a = self.acw(e=env(CLAUDE_CODE_AUTO_COMPACT_WINDOW=600000),
                     s={"window": 300_000, "unparsed": False, "enabled": None})
        self.assertEqual((a["window"], a["source"]), (600_000, "env"))

    def test_env_invalid_falls_through(self):
        s = {"window": 300_000, "unparsed": False, "enabled": None}
        for v in ("0", "-1", "abc"):
            self.assertEqual(self.acw(e=env(CLAUDE_CODE_AUTO_COMPACT_WINDOW=v), s=s)["source"],
                             "settings", v)
        # parseInt semantics, as in Claude Code: "500k" is 500, clamped up to 100K.
        a = self.acw(e=env(CLAUDE_CODE_AUTO_COMPACT_WINDOW="500k"))
        self.assertEqual(a, {"window": 100_000, "resolved": True, "source": "env"})

    def test_settings_window(self):
        a = self.acw(s={"window": 300_000, "unparsed": False, "enabled": None})
        self.assertEqual(a, {"window": 300_000, "resolved": True, "source": "settings"})
        a = self.acw(s={"window": None, "unparsed": True, "enabled": None})
        self.assertEqual((a["window"], a["resolved"]), (None, False))

    def test_disabled(self):
        for e in (env(DISABLE_AUTO_COMPACT=1), env(DISABLE_COMPACT=1)):
            a = self.acw(e=e, s={"window": 300_000, "unparsed": False, "enabled": None})
            self.assertEqual(a["source"], "disabled")
            self.assertIsNone(a["window"])
        a = self.acw(e=env(CLAUDE_CODE_AUTO_COMPACT_WINDOW=500000),
                     s={"window": None, "unparsed": False, "enabled": False})
        self.assertEqual(a["source"], "disabled")

    def test_model_defaults(self):
        # claude-sonnet-5's per-entrypoint default, unresolved (client data may replace it).
        a = self.acw("claude-sonnet-5", e=env(CLAUDE_CODE_ENTRYPOINT="local-agent"))
        self.assertEqual(a, {"window": 500_000, "resolved": False,
                             "source": "model_default_surface"})
        self.assertIsNone(self.acw("claude-sonnet-5", e=env(CLAUDE_CODE_ENTRYPOINT="cli"))["window"])
        # Nothing configured: server client data / experiments cannot be ruled out.
        self.assertEqual(self.acw(), {"window": None, "resolved": False, "source": "auto"})

    def test_settings_precedence(self):
        with tempfile.TemporaryDirectory() as d:
            cfg, proj = os.path.join(d, "cfg"), os.path.join(d, "proj")
            os.makedirs(cfg)
            os.makedirs(os.path.join(proj, ".claude"))
            managed = os.path.join(d, "managed.json")

            def put(p, obj):
                with open(p, "w") as f:
                    json.dump(obj, f)

            def read():
                return R.settings_autocompact(cfg, proj, L.read_json_file, (managed,))
            self.assertEqual(read(), self.NONE)
            put(os.path.join(cfg, "settings.json"), {"autoCompactWindow": 300000,
                                                     "env": {"X": "not read"}})
            self.assertEqual(read()["window"], 300_000)
            put(os.path.join(proj, ".claude", "settings.json"), {"autoCompactWindow": 400000})
            self.assertEqual(read()["window"], 400_000)
            put(os.path.join(proj, ".claude", "settings.local.json"),
                {"autoCompactWindow": 450000, "autoCompactEnabled": True})
            self.assertEqual(read(), {"window": 450_000, "unparsed": False, "enabled": True})
            put(managed, {"autoCompactWindow": "500k", "autoCompactEnabled": False})
            self.assertEqual(read(), {"window": None, "unparsed": True, "enabled": False})


if __name__ == "__main__":
    unittest.main()
