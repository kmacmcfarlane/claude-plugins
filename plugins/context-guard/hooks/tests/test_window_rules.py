"""window_rules: the window rules, one test per truth-table row (plan d63e
section 2, re-cited to the docs and observations by e347) plus the
auto-compact window (decision 34). Pure: envs are dicts, nothing touches
os.environ."""
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
        # model-config § Extended context, plus Opus/Sonnet 5.5 observed with -p.
        for m in ("claude-opus-5", "claude-opus-5-5", "claude-opus-4-7", "claude-opus-4-8",
                  "claude-sonnet-5", "claude-sonnet-5-5", "claude-fable-5", "claude-fable-5-1",
                  "claude-haiku-5-5"):
            with self.subTest(m=m):
                self.check(derive(m), M1, True, "native_1m")

    def test_row01b_models_no_claude_code_source_covers_are_unresolved(self):
        # Answer 168 (a): only the Claude Code docs or a -p observation
        # resolve a window. Mythos was not runnable here, so it only warns.
        for m in ("claude-mythos-5", "claude-mythos-5-1", "claude-mythos-preview",
                  "claude-opus-4-1", "claude-opus-4-0", "claude-3-7-sonnet"):
            with self.subTest(m=m):
                self.check(derive(m), K200, False, "unknown_model")

    def test_row02_suffix(self):
        self.check(derive("claude-opus-5[1m]"), M1, True, "suffix_1m")
        self.check(derive("claude-opus-5[1M]"), M1, True, "suffix_1m")

    def test_row03_observed_200k_and_first_party_ids(self):
        for m in ("claude-haiku-4-5-20251001", "claude-haiku-4-5", "claude-opus-4-5",
                  "claude-opus-4-5-20251101"):
            with self.subTest(m=m):
                self.check(derive(m), K200, True, "cited_200k")

    def test_row04_suffix_on_a_model_not_documented_as_1m_capable(self):
        self.check(derive("claude-haiku-4-5[1m]"), M1, False, "suffix_1m_unsupported")
        # The 4.6 pair reach 1M through the suffix (model-config).
        for m in ("claude-opus-4-6[1m]", "claude-sonnet-4-6[1m]"):
            self.check(derive(m), M1, True, "suffix_1m")

    def test_row05_disable_1m(self):
        self.check(derive("claude-opus-5", env(CLAUDE_CODE_DISABLE_1M_CONTEXT=1)),
                   K200, True, "disable_1m")

    def test_row06_disable_1m_beats_suffix(self):
        for v in ("true", " TRUE ", "yes", "on"):
            with self.subTest(v=v):
                self.check(derive("claude-opus-5[1m]", env(CLAUDE_CODE_DISABLE_1M_CONTEXT=v)),
                           K200, True)
        # A documented off spelling: 1M stands.
        self.check(derive("claude-opus-5[1m]", env(CLAUDE_CODE_DISABLE_1M_CONTEXT="0")), M1, True)
        # An undocumented spelling: the window cannot be known.
        for v in ("2", "enable"):
            with self.subTest(v=v):
                self.check(derive("claude-opus-5[1m]", env(CLAUDE_CODE_DISABLE_1M_CONTEXT=v)),
                           M1, False, "flag_unparsed")
                self.check(derive("claude-opus-5", env(CLAUDE_CODE_DISABLE_1M_CONTEXT=v)),
                           M1, False, "flag_unparsed")

    def test_row07_disable_compact_plus_max_context_tokens(self):
        e = env(DISABLE_COMPACT=1, CLAUDE_CODE_MAX_CONTEXT_TOKENS=500000)
        for m in ("claude-opus-5", "claude-haiku-4-5", "claude-opus-5[1m]", "my-gw-model"):
            with self.subTest(m=m):
                self.check(derive(m, e), 500_000, True, "max_context_tokens")
        # DISABLE_AUTO_COMPACT is not DISABLE_COMPACT.
        e = env(DISABLE_AUTO_COMPACT=1, CLAUDE_CODE_MAX_CONTEXT_TOKENS=500000)
        self.check(derive("claude-opus-5", e), M1, True, "native_1m")
        # Documented numeric spellings (env-vars § Variables).
        for v in ("5e5", "500_000"):
            with self.subTest(v=v):
                e = env(DISABLE_COMPACT=1, CLAUDE_CODE_MAX_CONTEXT_TOKENS=v)
                self.check(derive("claude-opus-5", e), 500_000, True, "max_context_tokens")
        # Undocumented spellings, zero or negative: the window cannot be known.
        for v in ("500,000", " 500000 ", "900k", "abc", "0", "-5"):
            with self.subTest(v=v):
                e = env(DISABLE_COMPACT=1, CLAUDE_CODE_MAX_CONTEXT_TOKENS=v)
                self.assertFalse(derive("claude-opus-5", e)["resolved"])
                self.assertEqual(derive("claude-opus-5", e)["rule"],
                                 "max_context_tokens_unparsed")
        # An undocumented DISABLE_COMPACT spelling leaves the override unknown.
        e = env(DISABLE_COMPACT="enable", CLAUDE_CODE_MAX_CONTEXT_TOKENS=500000)
        self.check(derive("claude-opus-5", e), 500_000, False, "max_context_tokens_unparsed")

    def test_row07b_unrecognized_id_with_suffix(self):
        # model-config: an unrecognized ID with [1m] is assumed 1M and the
        # variable "doesn't apply on its own"; whether Claude Code recognizes
        # a spelling is not observable, so the result only warns.
        e = env(DISABLE_COMPACT=1, CLAUDE_CODE_MAX_CONTEXT_TOKENS=500000)
        self.check(derive("my-gw-model[1m]", e), M1, False, "suffix_1m_unrecognized")
        self.check(derive("my-gw-model[1m]"), M1, False, "suffix_1m_unrecognized")
        # With CLAUDE_CODE_DISABLE_1M_CONTEXT the ID is sized as if untagged.
        e = env(DISABLE_COMPACT=1, CLAUDE_CODE_MAX_CONTEXT_TOKENS=500000,
                CLAUDE_CODE_DISABLE_1M_CONTEXT=1)
        self.check(derive("my-gw-model[1m]", e), 500_000, True, "max_context_tokens")

    def test_row08_max_context_tokens_ignored_for_catalog_models(self):
        e = env(CLAUDE_CODE_MAX_CONTEXT_TOKENS=500000)
        self.check(derive("claude-opus-5", e), M1, True, "native_1m")
        self.check(derive("claude-haiku-4-5", e), K200, True)

    def test_row09_custom_model_with_max_context_tokens(self):
        self.check(derive("my-gw-model", env(CLAUDE_CODE_MAX_CONTEXT_TOKENS=300000)),
                   300_000, False, "max_context_tokens_custom")

    def test_row10_credits_message_only_warns(self):
        # Answer 167 (a): after the credits error, 200K warns, never blocks.
        self.check(derive("claude-opus-5", latch=True, latch_known=True),
                   K200, False, "credits_message")
        self.check(derive("claude-opus-5[1m]", latch=True, latch_known=True),
                   K200, False, "credits_message")
        # Never raises a 200K window.
        self.check(derive("claude-haiku-4-5", latch=True), K200, True, "cited_200k")

    def test_row11_latch_under_max_context_override(self):
        e = env(DISABLE_COMPACT=1, CLAUDE_CODE_MAX_CONTEXT_TOKENS=800000)
        self.check(derive("claude-opus-5", e, latch=True), 800_000, True, "max_context_tokens")

    def test_row12_latch_without_process_marker(self):
        self.check(derive("claude-opus-5", latch=True, latch_known=False),
                   K200, False, "credits_message")

    def test_row13_third_party_or_foreign_base_url(self):
        for e in (env(CLAUDE_CODE_USE_BEDROCK=1), env(CLAUDE_CODE_USE_VERTEX="true"),
                  env(ANTHROPIC_BASE_URL="https://gw.example.com/v1")):
            with self.subTest(e=e["provider"]):
                self.check(derive("claude-opus-5", e), M1, False, "native_1m_3p")
        # The Anthropic API host itself is direct.
        self.check(derive("claude-opus-5", env(ANTHROPIC_BASE_URL="https://api.anthropic.com")),
                   M1, True)
        # A documented off spelling, or empty, is unset (env-vars).
        for v in ("off", "0", ""):
            with self.subTest(v=v):
                self.check(derive("claude-opus-5", env(CLAUDE_CODE_USE_BEDROCK=v)), M1, True,
                           "native_1m")

    def test_row13b_host_managed_or_undocumented_provider_spelling(self):
        self.check(derive("claude-opus-5", env(CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST=1)),
                   M1, False, "native_1m_3p")
        e = env(CLAUDE_CODE_USE_VERTEX="enable")
        self.assertEqual(e["provider"], "unknown")
        self.check(derive("claude-opus-5", e), M1, False, "native_1m_3p")

    def test_row14_sonnet_4_6(self):
        self.check(derive("claude-sonnet-4-6"), K200, False, "beta_unobservable")
        # CLAUDE_CODE_DISABLE_1M_CONTEXT rules the [1m] variant out.
        self.check(derive("claude-sonnet-4-6", env(CLAUDE_CODE_DISABLE_1M_CONTEXT=1)),
                   K200, True, "cited_200k")

    def test_row15_beta_capable_200k(self):
        for m in ("claude-opus-4-6", "claude-sonnet-4-6"):
            with self.subTest(m=m):
                self.check(derive(m), K200, False, "beta_unobservable")
        # No Claude Code source covers these: unresolved either way.
        for m in ("claude-sonnet-4-5-20250929", "claude-sonnet-4-20250514"):
            with self.subTest(m=m):
                self.check(derive(m), K200, False, "unknown_model")

    def test_row17_no_model(self):
        for m in (None, "", "  "):
            self.check(derive(m), None, False, "no_model")

    def test_row18_unknown_claude_id(self):
        self.check(derive("claude-opus-6"), K200, False, "unknown_model")
        self.check(derive("claude-3-opus-20240229"), K200, False, "unknown_model")

    def test_doc_int_takes_only_documented_spellings(self):
        # env-vars § Variables: plain digits, scientific notation, `_` separators.
        cases = {"500000": 500000, "5e5": 500000, "1.5e5": 150000, "2e3": 2000,
                 "64_000": 64000, "1_000_000": 1000000,
                 "1.23456e2": None, "1,000,000": None, " 42 ": None, "900k": None,
                 "0x10": None, "+7": None, "-3": None, "0": None, "abc": None, "": None}
        for raw, want in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(R.doc_int(raw), want)
        self.assertIsNone(R.doc_int(None))

    def test_acw_int_reads_the_leading_integer(self):
        # env-vars, CLAUDE_CODE_AUTO_COMPACT_WINDOW: plain integer; "500k" reads as 500.
        self.assertEqual(R.acw_int("500000"), (500000, True))
        self.assertEqual(R.acw_int("500k"), (500, True))
        for raw in ("5e5", "500_000", "500,000"):
            with self.subTest(raw=raw):
                self.assertFalse(R.acw_int(raw)[1])
        self.assertEqual(R.acw_int("abc"), (None, False))

    def test_flag_spellings(self):
        for v in ("1", "true", "YES", "On"):
            self.assertIs(R.flag(v), True, v)
        for v in (None, "", "0", "false", "No", "OFF"):
            self.assertIs(R.flag(v), False, v)
        for v in ("2", "enable", "y"):
            self.assertIsNone(R.flag(v), v)

    def test_env_inputs_carry_no_env_strings(self):
        e = R.env_inputs({"ANTHROPIC_BASE_URL": "https://user:secret@gw.example.com",
                          "CLAUDE_CODE_MAX_CONTEXT_TOKENS": "123456"})
        blob = json.dumps(e)
        self.assertNotIn("secret", blob)
        self.assertNotIn("gw.example.com", blob)
        self.assertEqual(e["mct"], 123456)
        self.assertFalse(e["first_party_direct"])

    def test_provider_ambiguity_is_not_first_party(self):
        e = env(CLAUDE_CODE_USE_BEDROCK=1, CLAUDE_CODE_USE_VERTEX=1)
        self.assertEqual(e["provider"], "ambiguous")
        self.assertFalse(derive("claude-opus-5", e)["resolved"])


class TestAutoCompact(unittest.TestCase):
    NONE = {"window": None, "enabled": None, "unsure": False, "policy": False,
            "remote_ruled_out": True}
    # Every hidden layer ruled out - a state the real settings reader never
    # reports, since server-managed settings can never be ruled out
    # (REMOTE_POLICY_RULED_OUT), kept to test the rule.
    ON = dict(NONE, enabled=True)

    def acw(self, model="claude-opus-5", mw=M1, e=None, s=None, observable=True, **kw):
        return R.autocompact(model, mw, e if e is not None else env(), s or self.ON,
                             observable=observable, **kw)

    def test_env_window_resolved_only_when_everything_is_seen(self):
        e = env(CLAUDE_CODE_AUTO_COMPACT_WINDOW=500000)
        self.assertEqual(self.acw(e=e), {"window": 500_000, "resolved": True, "source": "env"})
        # autoCompactEnabled not set in a settings layer the hook reads: a
        # managed layer may set it, so an explicit true is required.
        self.assertEqual(self.acw(e=e, s=self.NONE)["resolved"], False)
        # A flag layer could be in play (or the cmdline was not read).
        self.assertEqual(self.acw(e=e, observable=False)["resolved"], False)
        # An undocumented spelling of the window or of a compaction switch.
        for e2 in (env(CLAUDE_CODE_AUTO_COMPACT_WINDOW="5e5"),
                   env(CLAUDE_CODE_AUTO_COMPACT_WINDOW=500000, DISABLE_AUTO_COMPACT="maybe")):
            self.assertEqual(self.acw(e=e2)["resolved"], False)
        # An unreadable policy file; any policy tier present; server-managed
        # settings not ruled out (what the reader always reports).
        self.assertEqual(self.acw(e=e, s=dict(self.ON, unsure=True))["resolved"], False)
        self.assertEqual(self.acw(e=e, s=dict(self.ON, policy=True))["resolved"], False)
        self.assertEqual(self.acw(e=e, s=dict(self.ON, remote_ruled_out=False))["resolved"],
                         False)
        self.assertEqual(self.acw(e=e, s={k: v for k, v in self.ON.items()
                                          if k != "policy"})["resolved"], False)

    def test_env_clamp(self):
        self.assertEqual(self.acw(e=env(CLAUDE_CODE_AUTO_COMPACT_WINDOW=50000))["window"], 100_000)
        self.assertIsNone(self.acw(e=env(CLAUDE_CODE_AUTO_COMPACT_WINDOW=5000000))["window"])
        self.assertIsNone(self.acw(mw=K200, e=env(CLAUDE_CODE_AUTO_COMPACT_WINDOW=500000))["window"])

    def test_env_beats_settings(self):
        a = self.acw(e=env(CLAUDE_CODE_AUTO_COMPACT_WINDOW=600000),
                     s=dict(self.ON, window=300_000))
        self.assertEqual((a["window"], a["source"]), (600_000, "env"))

    def test_env_invalid_falls_through(self):
        s = dict(self.ON, window=300_000)
        for v in ("0", "-1", "abc"):
            self.assertEqual(self.acw(e=env(CLAUDE_CODE_AUTO_COMPACT_WINDOW=v), s=s)["source"],
                             "settings", v)
        # doc: env-vars - "500k" reads as 500 and clamps to the 100K minimum.
        a = self.acw(e=env(CLAUDE_CODE_AUTO_COMPACT_WINDOW="500k"))
        self.assertEqual(a, {"window": 100_000, "resolved": True, "source": "env"})

    def test_settings_window(self):
        a = self.acw(s=dict(self.ON, window=300_000))
        self.assertEqual(a, {"window": 300_000, "resolved": True, "source": "settings"})
        a = self.acw(s=dict(self.NONE, window=300_000))
        self.assertEqual(a, {"window": 300_000, "resolved": False, "source": "settings"})

    def test_disabled(self):
        for e in (env(DISABLE_AUTO_COMPACT=1), env(DISABLE_COMPACT=1)):
            a = self.acw(e=e, s=dict(self.ON, window=300_000))
            self.assertEqual((a["source"], a["window"]), ("disabled", None))
        a = self.acw(e=env(CLAUDE_CODE_AUTO_COMPACT_WINDOW=500000),
                     s={"window": None, "enabled": False, "unsure": False})
        self.assertEqual((a["source"], a["window"]), ("disabled_setting", None))

    def test_model_defaults(self):
        # Nothing configured: Claude Code's window tuned for the model is not
        # modelled, whatever the model.
        for model in ("claude-sonnet-5", "claude-sonnet-4-6", "claude-opus-5"):
            with self.subTest(model=model):
                self.assertEqual(self.acw(model),
                                 {"window": None, "resolved": False, "source": "auto"})

    def settings_dirs(self, d):
        cfg, proj = os.path.join(d, "cfg"), os.path.join(d, "proj")
        os.makedirs(cfg)
        os.makedirs(os.path.join(proj, ".claude"))
        managed = os.path.join(d, "managed.json")
        dropins = os.path.join(d, "managed.d")
        os.makedirs(dropins)

        def put(p, obj):
            with open(p, "w") as f:
                json.dump(obj, f) if not isinstance(obj, str) else f.write(obj)

        def read():
            return R.settings_autocompact(cfg, proj, L.read_json_file, (managed,), (dropins,))
        return cfg, proj, managed, dropins, put, read

    def test_settings_precedence(self):
        with tempfile.TemporaryDirectory() as d:
            cfg, proj, managed, dropins, put, read = self.settings_dirs(d)
            self.assertEqual(read(), dict(self.NONE, remote_ruled_out=False))
            put(os.path.join(cfg, "settings.json"), {"autoCompactWindow": 300000,
                                                     "env": {"X": "not read"}})
            self.assertEqual(read()["window"], 300_000)
            put(os.path.join(proj, ".claude", "settings.json"), {"autoCompactWindow": 400000})
            self.assertEqual(read()["window"], 400_000)
            put(os.path.join(proj, ".claude", "settings.local.json"),
                {"autoCompactWindow": 450000, "autoCompactEnabled": True})
            self.assertEqual(read(), {"window": 450_000, "enabled": True, "unsure": False,
                                      "policy": False, "remote_ruled_out": False})
            put(os.path.join(dropins, "10-org.json"), {"autoCompactWindow": 600000})
            self.assertEqual((read()["window"], read()["policy"]), (600_000, True))
            put(managed, {"autoCompactEnabled": False})
            self.assertEqual(read(), {"window": 600_000, "enabled": False, "unsure": False,
                                      "policy": True, "remote_ruled_out": False})
            put(os.path.join(cfg, R.REMOTE_SETTINGS), {"autoCompactWindow": 700000})
            self.assertEqual(read()["window"], 700_000)

    def test_out_of_range_settings_fall_through(self):
        # doc: settings-reference - autoCompactWindow is 100000 to 1000000.
        # Treating a value outside that as absent, so the lower layer's wins,
        # is our own handling (window_rules._valid_acw), not documented.
        with tempfile.TemporaryDirectory() as d:
            cfg, proj, managed, dropins, put, read = self.settings_dirs(d)
            put(os.path.join(proj, ".claude", "settings.json"), {"autoCompactWindow": 50000})
            self.assertEqual(read()["window"], None)
            put(os.path.join(cfg, "settings.json"), {"autoCompactWindow": 300000})
            self.assertEqual(read()["window"], 300_000)
            for bad in (1_000_001, "500k", 300000.5, True, None):
                put(os.path.join(proj, ".claude", "settings.json"), {"autoCompactWindow": bad})
                self.assertEqual(read()["window"], 300_000, bad)

    def test_unreadable_policy_or_odd_enabled_is_unsure(self):
        with tempfile.TemporaryDirectory() as d:
            cfg, proj, managed, dropins, put, read = self.settings_dirs(d)
            put(managed, "{not json")
            self.assertTrue(read()["unsure"])
            os.unlink(managed)
            put(os.path.join(cfg, "settings.json"), {"autoCompactEnabled": "yes"})
            self.assertEqual((read()["enabled"], read()["unsure"]), (None, True))


class TestPolicyPresence(unittest.TestCase):
    """Any policy tier present makes a settings-derived window unresolved,
    whatever keys it holds (managedSourcesBehavior, documented on the
    managed-settings page, chooses among tiers; the rules do not model that)."""
    ON = TestAutoCompact.ON
    acw = TestAutoCompact.acw
    settings_dirs = TestAutoCompact.settings_dirs
    def test_any_tier_counts_even_without_the_keys(self):
        with tempfile.TemporaryDirectory() as d:
            cfg, proj, managed, dropins, put, read = self.settings_dirs(d)
            put(os.path.join(cfg, "settings.json"),
                {"autoCompactWindow": 300000, "autoCompactEnabled": True})
            self.assertFalse(read()["policy"])
            for tier, path in (("managed file", managed),
                               ("drop-in", os.path.join(dropins, "a.json")),
                               ("remote cache", os.path.join(cfg, R.REMOTE_SETTINGS))):
                with self.subTest(tier):
                    put(path, {"permissions": {}})
                    got = read()
                    self.assertTrue(got["policy"])
                    self.assertFalse(self.acw(s=got)["resolved"])
                    os.unlink(path)

    def test_remote_policy_is_never_ruled_out_in_this_version(self):
        self.assertIs(R.REMOTE_POLICY_RULED_OUT, False)
        with tempfile.TemporaryDirectory() as d:
            cfg, proj, managed, dropins, put, read = self.settings_dirs(d)
            put(os.path.join(cfg, "settings.json"),
                {"autoCompactWindow": 300000, "autoCompactEnabled": True})
            a = self.acw(s=read(), e=env(CLAUDE_CODE_AUTO_COMPACT_WINDOW=400000))
            self.assertEqual((a["window"], a["resolved"]), (400_000, False))


class TestProviderAndUrl(unittest.TestCase):
    def test_url_host_keeps_a_non_default_port(self):
        self.assertEqual(R.url_host("https://api.anthropic.com"), "api.anthropic.com")
        self.assertEqual(R.url_host("https://api.anthropic.com:443/v1"), "api.anthropic.com")
        self.assertEqual(R.url_host("https://API.anthropic.com:8443"), "api.anthropic.com:8443")
        self.assertEqual(R.url_host("http://api.anthropic.com:443"), "api.anthropic.com:443")
        self.assertIsNone(R.url_host("not a url"))

    def test_port_8443_is_not_first_party(self):
        e = env(ANTHROPIC_BASE_URL="https://api.anthropic.com:8443")
        self.assertFalse(e["first_party_direct"])
        d = derive("claude-opus-5", e)
        self.assertEqual((d["window"], d["resolved"]), (M1, False))

    def test_beta_models_are_unresolved_on_every_provider(self):
        for extra in ({}, {"CLAUDE_CODE_USE_VERTEX": 1}, {"CLAUDE_CODE_USE_BEDROCK": 1}):
            for m in ("claude-opus-4-6", "claude-sonnet-4-6"):
                with self.subTest(m=m, extra=extra):
                    d = derive(m, env(**extra))
                    self.assertEqual((d["window"], d["resolved"], d["rule"]),
                                     (K200, False, "beta_unobservable"))

    def test_unknown_latch_unresolves_windows_above_200k_only(self):
        d = derive("claude-opus-5", latch=False, latch_known=False)
        self.assertEqual((d["window"], d["resolved"], d["rule"]), (M1, False, "latch_unknown"))
        d = derive("claude-haiku-4-5", latch=False, latch_known=False)
        self.assertEqual((d["window"], d["resolved"]), (K200, True))


if __name__ == "__main__":
    unittest.main()
