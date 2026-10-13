"""The scrub of Claude Code internals (e347) does not regress: no hook source
or test names a short function label in a comment or a string, the shape a
minified identifier takes (CLAUDE.md § Claude Code source material, rule 1).

A short name (four characters or fewer) called like a function, inside a
comment or a string literal, must be a Python builtin or a name this
directory defines itself. A comment may not hold a letter-dollar name either.
Nor may a comment or a string hold a short mangled-looking name written
without a call (cc_scan's mixed-case, digit-inside and dollar shapes), unless
it is a name defined here, an escape or format sequence (`\x1b`, `%dT`), a
four-hex work-item id, or a feature label such as F3b.
"""
import builtins, glob, os, re, tokenize, unittest

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHORT = re.compile(r"(?<![A-Za-z0-9_.$])([A-Za-z_$][A-Za-z0-9_$]{0,3})\(")
DOLLAR = re.compile(r"[A-Za-z0-9_]\$[A-Za-z0-9_]|[A-Za-z]\$")
# Parameter names used as calls in docstrings ("fn(state)", "run()").
LOCAL = {"fn", "run"}
# The unparenthesised short-label shapes of CLAUDE.md's cc_scan.
MANGLED = re.compile(r"(?<![A-Za-z0-9_$])([A-Za-z]+\$[A-Za-z0-9]*|[A-Za-z0-9]?[a-z][A-Z][A-Za-z0-9]?"
                     r"|[A-Za-z][0-9][A-Za-z][A-Za-z0-9]?)(?![A-Za-z0-9_$])")
ORDINARY = {"NaN", "eE"}
BENIGN = re.compile(r"[0-9a-f]{4}|[A-Z][0-9][a-z]{1,2}")


def sources():
    return sorted(glob.glob(os.path.join(HOOKS, "*.py"))
                  + glob.glob(os.path.join(HOOKS, "tests", "*.py")))


def defined_names(paths):
    names = set(dir(builtins)) | LOCAL
    for p in paths:
        with open(p, encoding="utf-8") as f:
            src = f.read()
        names |= set(re.findall(r"\bdef\s+([A-Za-z_]\w*)", src))
        names |= set(re.findall(r"\bclass\s+([A-Za-z_]\w*)", src))
        names |= set(re.findall(r"\bimport\s+(?:\w+\s+as\s+)?([A-Za-z_]\w*)", src))
        names |= set(re.findall(r"\b([A-Za-z_]\w*)\s*=", src))
    return names


def hits(paths):
    names, out = defined_names(paths), []
    for p in paths:
        with open(p, "rb") as f:
            for tok in tokenize.tokenize(f.readline):
                if tok.type not in (tokenize.COMMENT, tokenize.STRING):
                    continue
                for m in SHORT.finditer(tok.string):
                    if m.group(1) not in names:
                        out.append(f"{os.path.relpath(p, HOOKS)}:{tok.start[0]}")
                if tok.type == tokenize.COMMENT and DOLLAR.search(tok.string):
                    out.append(f"{os.path.relpath(p, HOOKS)}:{tok.start[0]}")
                for m in MANGLED.finditer(tok.string):
                    w, before = m.group(1), tok.string[m.start(1) - 1:m.start(1)]
                    if before in ("\\", "%") or w in names or w in ORDINARY \
                            or BENIGN.fullmatch(w):
                        continue
                    out.append(f"{os.path.relpath(p, HOOKS)}:{tok.start[0]}")
    return out


class TestNoInternalLabels(unittest.TestCase):
    def test_no_short_call_shaped_labels_in_comments_or_strings(self):
        # Locations only: the message never repeats what it found.
        self.assertEqual(hits(sources()), [])

    def test_the_scan_sees_a_planted_label(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "planted.py")
            with open(p, "w") as f:
                f.write("x = 1\n# mirrors " + "Qz" + "9() upstream\n")
            self.assertEqual(len(hits([p])), 1)

    def test_the_scan_sees_a_planted_constant_without_a_call(self):
        import tempfile
        for label in ("a" + "Bc", "q" + "7z", "k" + "$r"):
            with self.subTest(label=label), tempfile.TemporaryDirectory() as d:
                p = os.path.join(d, "planted.py")
                with open(p, "w") as f:
                    f.write(f"x = 1\n# the {label} constant upstream\n")
                self.assertTrue(hits([p]))


if __name__ == "__main__":
    unittest.main()
