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
ELL = "…"
BIDI_AND_ZERO_WIDTH = ([chr(c) for c in range(0x200B, 0x2010)] +
                       [chr(c) for c in range(0x202A, 0x202F)] +
                       [chr(c) for c in range(0x2060, 0x2065)] +
                       [chr(c) for c in range(0x2066, 0x206A)] + ["﻿"])
CODER = "\U0001F469‍\U0001F4BB"  # woman technologist: woman ZWJ laptop
FAMILY = "\U0001F468‍\U0001F469‍\U0001F467"
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
        self.assertEqual(clean("‮evil‬ name"), "evil name")
        self.assertEqual(clean("x⁧⁦y⁩⁩"), "xy")

    def test_name_of_only_stripped_characters_is_empty(self):
        for raw in ("‮", "​​", "".join(BIDI_AND_ZERO_WIDTH),
                    "‍", "‍‍", " ​ ‮\n", "﻿‍﻿",
                    "\U000E0067\U000E007F", "​" * 1000, "\ud800"):
            self.assertEqual(clean(raw), "", repr(raw))

    def test_stripping_does_not_leave_double_spaces(self):
        self.assertEqual(clean("a ​ b"), "a b")
        self.assertEqual(clean("​ a ‮"), "a")

    def test_lone_surrogates_are_dropped(self):
        self.assertEqual(clean("a\ud800b\udfffc"), "abc")


class KeptSequences(unittest.TestCase):
    def test_combining_marks_survive(self):
        for s in ("café", "ño", "कि",  # Devanagari ki
                  "a⃝"):  # enclosing circle (Me)
            self.assertEqual(clean(s), s, repr(s))

    def test_emoji_zwj_sequences_survive(self):
        for s in (CODER, FAMILY, "\U0001F3F3️‍\U0001F308",  # rainbow flag
                  f"dev {CODER} work", ENGLAND):
            self.assertEqual(clean(s), s, repr(s))

    def test_zwj_in_indic_text_survives(self):
        s = "क्‍ष"  # half-form ka ZWJ ssa
        self.assertEqual(clean(s), s)

    def test_dangling_zwj_is_dropped(self):
        for raw, want in (("a‍b", "ab"), ("‍\U0001F469", "\U0001F469"),
                          ("\U0001F469‍", "\U0001F469"),
                          ("\U0001F469‍ \U0001F4BB", "\U0001F469 \U0001F4BB"),
                          ("\U0001F469‍‍\U0001F4BB", "\U0001F469\U0001F4BB")):
            self.assertEqual(clean(raw), want, repr(raw))

    def test_tag_characters_outside_a_flag_are_dropped(self):
        self.assertEqual(clean("a\U000E0067\U000E007Fb"), "ab")


class ColumnCap(unittest.TestCase):
    def test_columns(self):
        self.assertEqual(S.columns("a"), 1)
        self.assertEqual(S.columns("中"), 2)        # CJK
        self.assertEqual(S.columns("Ａ"), 2)        # fullwidth A
        self.assertEqual(S.columns("\U0001F469"), 2)    # emoji
        self.assertEqual(S.columns("́"), 0)        # combining acute
        self.assertEqual(S.columns("⃝"), 0)        # enclosing mark
        self.assertEqual(S.columns("‍"), 0)        # ZWJ

    def test_cjk_is_capped_at_sixty_columns(self):
        out = clean("中" * 60)  # 120 columns
        self.assertTrue(out.endswith(ELL), out)
        self.assertEqual(out, "中" * 29 + ELL)
        self.assertLessEqual(width(out), S.NAME_MAX)

    def test_thirty_cjk_fit_exactly(self):
        self.assertEqual(clean("中" * 30), "中" * 30)

    def test_odd_boundary_does_not_split_a_wide_character(self):
        out = clean("a" + "中" * 40)
        self.assertEqual(out, "a" + "中" * 29 + ELL)
        self.assertEqual(width(out[:-1]), 59)

    def test_combining_marks_do_not_count(self):
        s = "é" * 60  # 60 columns, 120 code points
        self.assertEqual(clean(s), s)
        out = clean("é" * 61)
        self.assertEqual(out, "é" * 59 + ELL)  # marks stay with their base

    def test_ascii_cap_unchanged(self):
        self.assertEqual(clean("n" * 60), "n" * 60)
        self.assertEqual(clean("n" * 100), "n" * 59 + ELL)

    def test_cut_never_ends_on_a_zwj(self):
        out = clean("n" * 57 + CODER * 3)
        self.assertTrue(out.endswith(ELL), out)
        self.assertNotIn("‍" + ELL, out)
        self.assertLessEqual(width(out), S.NAME_MAX)

    def test_emoji_names_are_capped(self):
        out = clean(CODER * 40)
        self.assertTrue(out.endswith(ELL))
        self.assertLessEqual(width(out), S.NAME_MAX)

    def test_zero_width_flood_is_bounded(self):
        out = clean("a" + "́" * 100000)
        self.assertTrue(out.startswith("á") and out.endswith(ELL))
        self.assertLessEqual(len(out), S.SCAN_MAX + 1)

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
        rc, line, err = self.line("‮ab​中文 " + CODER)
        self.assertEqual((rc, err), (0, ""))
        self.assertIn(f"  (ab中文 {CODER})  ", line)
        for ch in BIDI_AND_ZERO_WIDTH:
            if ch != "‍":
                self.assertNotIn(ch, line, f"U+{ord(ch):04X}")

    def test_only_format_characters_shows_no_name(self):
        rc, line, err = self.line("‮​﻿")
        self.assertEqual((rc, err), (0, ""))
        self.assertNotIn("(", line)
        self.assertIn("42%  580k left", line)

    def test_lone_surrogate_does_not_crash(self):
        rc, line, err = self.line("a\ud800b")
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("  (ab)  ", line)


if __name__ == "__main__":
    unittest.main()
