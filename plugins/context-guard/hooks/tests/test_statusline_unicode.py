"""Unicode handling of the status line's session name: format characters are
dropped, combining marks and emoji ZWJ sequences survive, and the NAME_MAX cap
counts terminal columns rather than code points.

clean() is exercised directly (statusline.py runs main() on import, so it is
loaded with an empty stdin and its one line of output swallowed), and the whole
hook end to end as a subprocess, the way Claude Code runs it."""
import contextlib, importlib.util, io, json, os, subprocess, sys, tempfile, unittest
import unicodedata

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HOOKS)


def load_statusline():
    spec = importlib.util.spec_from_file_location(
        "statusline_under_test", os.path.join(HOOKS, "statusline.py"))
    mod = importlib.util.module_from_spec(spec)
    old_stdin = sys.stdin
    sys.stdin = io.StringIO("")
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            spec.loader.exec_module(mod)
    finally:
        sys.stdin = old_stdin
    return mod


S = load_statusline()
clean = S.clean
ELL = "\u2026"
BIDI_AND_ZERO_WIDTH = ([chr(c) for c in range(0x200B, 0x2010)] +
                       [chr(c) for c in range(0x202A, 0x202F)] +
                       [chr(c) for c in range(0x2060, 0x2065)] +
                       [chr(c) for c in range(0x2066, 0x206A)] + ["\ufeff"])
CODER = "\U0001F469\u200d\U0001F4BB"  # woman technologist: woman ZWJ laptop
FAMILY = "\U0001F468\u200d\U0001F469\u200d\U0001F467"
ENGLAND = "\U0001F3F4\U000E0067\U000E0062\U000E0065\U000E006E\U000E0067\U000E007F"


def width(s):
    return sum(S.columns(ch) for ch in s)


class FormatCharacters(unittest.TestCase):
    def test_each_listed_character_is_dropped(self):
        for ch in BIDI_AND_ZERO_WIDTH:
            self.assertEqual(clean(f"ab{ch}cd"), "abcd", f"U+{ord(ch):04X}")

    def test_every_format_character_is_dropped(self):
        # Whatever Unicode version this Python carries: no Cf survives
        # between ASCII letters (the tag and ZWJ exceptions need emoji).
        for c in range(0x110000):
            ch = chr(c)
            if unicodedata.category(ch) == "Cf":
                self.assertEqual(clean(f"a{ch}b"), "ab", f"U+{c:04X}")

    def test_bidi_override_cannot_reverse_the_name(self):
        self.assertEqual(clean("\u202eevil\u202c name"), "evil name")
        self.assertEqual(clean("x\u2067\u2066y\u2069\u2069"), "xy")

    def test_name_of_only_stripped_characters_is_empty(self):
        for raw in ("\u202e", "\u200b\u200b", "".join(BIDI_AND_ZERO_WIDTH),
                    "\u200d", "\u200d\u200d", " \u200b \u202e\n", "\ufeff\u200d\ufeff",
                    "\U000E0067\U000E007F", "\u200b" * 1000, "\ud800"):
            self.assertEqual(clean(raw), "", repr(raw))

    def test_stripping_does_not_leave_double_spaces(self):
        self.assertEqual(clean("a \u200b b"), "a b")
        self.assertEqual(clean("\u200b a \u202e"), "a")

    def test_lone_surrogates_are_dropped(self):
        self.assertEqual(clean("a\ud800b\udfffc"), "abc")


class KeptSequences(unittest.TestCase):
    def test_combining_marks_survive(self):
        for s in ("cafe\u0301", "n\u0303o", "\u0915\u093f",  # Devanagari ki
                  "a\u20dd"):  # enclosing circle (Me)
            self.assertEqual(clean(s), s, repr(s))

    def test_emoji_zwj_sequences_survive(self):
        for s in (CODER, FAMILY, "\U0001F3F3\ufe0f\u200d\U0001F308",  # rainbow flag
                  f"dev {CODER} work", ENGLAND):
            self.assertEqual(clean(s), s, repr(s))

    def test_zwj_in_indic_text_survives(self):
        s = "\u0915\u094d\u200d\u0937"  # half-form ka ZWJ ssa
        self.assertEqual(clean(s), s)

    def test_dangling_zwj_is_dropped(self):
        for raw, want in (("a\u200db", "ab"), ("\u200d\U0001F469", "\U0001F469"),
                          ("\U0001F469\u200d", "\U0001F469"),
                          ("\U0001F469\u200d \U0001F4BB", "\U0001F469 \U0001F4BB"),
                          ("\U0001F469\u200d\u200d\U0001F4BB", CODER)):  # one joiner is enough
            self.assertEqual(clean(raw), want, repr(raw))

    def test_tag_characters_outside_a_flag_are_dropped(self):
        self.assertEqual(clean("a\U000E0067\U000E007Fb"), "ab")

    def test_only_a_real_subdivision_flag_keeps_its_tags(self):
        black = "\U0001F3F4"
        for raw, want in (
                (black + "\U000E0061" * 1000, black),               # no terminator
                (black + "\U000E0061" * 8 + "\U000E007F", black),   # too long
                (black + "\U000E0061" + "\U000E007F", black),       # too short
                (black + "\U000E007F", black),                      # bare terminator
                (ENGLAND + "\U000E0061" * 50, ENGLAND),             # padding after
                (ENGLAND + "\U000E007F", ENGLAND),                  # second terminator
                ("x\U000E0067\U000E0062" + ENGLAND[1:], "x"),       # tags without base
                (ENGLAND + " " + ENGLAND, ENGLAND + " " + ENGLAND)):
            self.assertEqual(clean(raw), want, repr(raw))

    def test_zwj_after_marks_cannot_pad(self):
        out = clean("\u00e9" + "\u0301\u200d" * 300)
        self.assertNotIn("\u200d", out)
        out = clean("\u00e9" + "\u0301\u200d" * 300 + "\u4e2d")
        self.assertLessEqual(out.count("\u200d"), 1)
        # A joiner after an emoji variation selector still joins (rainbow flag).
        self.assertEqual(clean("\U0001F3F3\ufe0f\u200d\U0001F308").count("\u200d"), 1)


class ColumnCap(unittest.TestCase):
    def test_columns(self):
        self.assertEqual(S.columns("a"), 1)
        self.assertEqual(S.columns("\u4e2d"), 2)        # CJK
        self.assertEqual(S.columns("\uff21"), 2)        # fullwidth A
        self.assertEqual(S.columns("\U0001F469"), 2)    # emoji
        self.assertEqual(S.columns("\u0301"), 0)        # combining acute
        self.assertEqual(S.columns("\u20dd"), 0)        # enclosing mark
        self.assertEqual(S.columns("\u200d"), 0)        # ZWJ

    def test_cjk_is_capped_at_sixty_columns(self):
        out = clean("\u4e2d" * 60)  # 120 columns
        self.assertTrue(out.endswith(ELL), out)
        self.assertEqual(out, "\u4e2d" * 29 + ELL)
        self.assertLessEqual(width(out), S.NAME_MAX)

    def test_thirty_cjk_fit_exactly(self):
        self.assertEqual(clean("\u4e2d" * 30), "\u4e2d" * 30)

    def test_odd_boundary_does_not_split_a_wide_character(self):
        out = clean("a" + "\u4e2d" * 40)
        self.assertEqual(out, "a" + "\u4e2d" * 29 + ELL)
        self.assertEqual(width(out[:-1]), 59)

    def test_combining_marks_do_not_count(self):
        s = "e\u0301" * 60  # 60 columns, 120 code points
        self.assertEqual(clean(s), s)
        out = clean("e\u0301" * 61)
        self.assertEqual(out, "e\u0301" * 59 + ELL)  # marks stay with their base

    def test_ascii_cap_unchanged(self):
        self.assertEqual(clean("n" * 60), "n" * 60)
        self.assertEqual(clean("n" * 100), "n" * 59 + ELL)

    def test_cut_never_ends_on_a_zwj(self):
        out = clean("n" * 57 + CODER * 3)
        self.assertTrue(out.endswith(ELL), out)
        self.assertNotIn("\u200d" + ELL, out)
        self.assertLessEqual(width(out), S.NAME_MAX)

    def test_vs16_makes_a_text_default_character_wide(self):
        heart = "\u2764\ufe0f"
        self.assertEqual(S.widths(heart), [2, 0])
        self.assertEqual(S.widths("\u2764"), [1])
        for base in ("\u2764", "\u2600", "\u270c", "\u263a"):
            out = clean((base + "\ufe0f") * 40)
            self.assertEqual(out, (base + "\ufe0f") * 29 + ELL, repr(base))
        self.assertEqual(clean(heart * 30), heart * 30)  # exactly 60 columns

    def test_emoji_names_are_capped(self):
        out = clean(CODER * 40)
        self.assertTrue(out.endswith(ELL))
        self.assertLessEqual(width(out), S.NAME_MAX)

    def test_zero_width_flood_is_bounded(self):
        out = clean("a" + "\u0301" * 100000)
        self.assertTrue(out.startswith("a\u0301") and out.endswith(ELL))
        self.assertLessEqual(len(out), S.SCAN_MAX + 1)

    def test_name_behind_a_long_format_run_is_found(self):
        # More format characters than SCAN_MAX no longer hide the name ...
        self.assertEqual(clean("\u200b" * (S.SCAN_MAX * 4) + "real"), "real")
        # ... up to the SCAN_HARD bound, which is the documented trade-off.
        self.assertEqual(clean("\u200b" * (S.SCAN_HARD + 10) + "real"), "")
        self.assertEqual(clean("ab" + "\u200b" * S.SCAN_HARD), "ab" + ELL)

    def test_whitespace_flood_is_not_a_long_name(self):
        self.assertEqual(clean("abc" + " " * 10000 + "d"), "abc d")

    def test_non_strings(self):
        for v in (None, 7, ["x"], {"a": 1}, b"\xe2\x80\xae"):
            self.assertEqual(clean(v), "")


class EndToEnd(unittest.TestCase):
    CTX = {"used_percentage": 42.0, "context_window_size": 1_000_000,
           "total_input_tokens": 420_000}

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def line(self, name):
        payload = {"session_id": "s", "context_window": dict(self.CTX),
                   "model": {"display_name": "Fable"}, "session_name": name}
        e = dict(os.environ)
        e["CLAUDE_CONFIG_DIR"] = self.tmp.name
        p = subprocess.run([sys.executable, os.path.join(HOOKS, "statusline.py")],
                           input=json.dumps(payload), capture_output=True,
                           text=True, encoding="utf-8", env=e, timeout=30)
        return p.returncode, p.stdout, p.stderr

    def test_hostile_unicode_name(self):
        rc, line, err = self.line("\u202eab\u200b\u4e2d\u6587 " + CODER)
        self.assertEqual((rc, err), (0, ""))
        self.assertIn(f"  (ab\u4e2d\u6587 {CODER})  ", line)
        for ch in BIDI_AND_ZERO_WIDTH:
            if ch != "\u200d":
                self.assertNotIn(ch, line, f"U+{ord(ch):04X}")

    def test_only_format_characters_shows_no_name(self):
        rc, line, err = self.line("\u202e\u200b\ufeff")
        self.assertEqual((rc, err), (0, ""))
        self.assertNotIn("(", line)
        self.assertIn("42%  580k left", line)

    def test_lone_surrogate_does_not_crash(self):
        rc, line, err = self.line("a\ud800b")
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("  (ab)  ", line)

    def run_raw(self, payload):
        e = dict(os.environ)
        e["CLAUDE_CONFIG_DIR"] = self.tmp.name
        p = subprocess.run([sys.executable, os.path.join(HOOKS, "statusline.py")],
                           input=json.dumps(payload), capture_output=True,
                           text=True, encoding="utf-8", errors="replace",
                           env=e, timeout=30)
        return p.returncode, p.stdout, p.stderr

    def test_surrogates_in_other_fields_do_not_crash(self):
        rc, line, err = self.run_raw({
            "session_id": "s", "context_window": dict(self.CTX),
            "model": {"display_name": "Fa\ud800ble"},
            "workspace": {"current_dir": "/x/re\udfffpo"}})
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("[Fa?ble] re?po", line)
        self.assertIn("42%  580k left", line)

    def test_non_object_payloads_do_not_crash(self):
        for payload in ([], None, 7, "x", [{"session_id": "s"}]):
            rc, line, err = self.run_raw(payload)
            self.assertEqual((rc, err), (0, ""), repr(payload))
            self.assertIn("ctx --", line, repr(payload))

    def test_wrong_typed_blocks_do_not_crash(self):
        rc, line, err = self.run_raw({
            "session_id": "s", "context_window": [], "model": "Fable",
            "workspace": ["x"], "effort": 3, "cwd": 7, "rate_limits": []})
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("ctx --", line)


if __name__ == "__main__":
    unittest.main()
