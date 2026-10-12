"""Shell snippets that run Python inline run it isolated (python3 -I).

`python3 -c '...'` and `python3 - <<EOF` put the current directory first on the module
search path, so a json.py (or any module name) in the repo the user is in is imported and
runs. `-I` (isolated mode) stops that. Every skill, reference, agent and README under
plugins/ that shows an inline python3 / python snippet must pass -I: -c, - or a bare
python3 reading stdin (`<<`, `<`, or the end of a pipe), and -m (also cwd first; `-m unittest`
is exempt, it runs our own tests from their own directory). A path before the name
(/usr/bin/python3) and inline-code prose (`python3 -c`) count.

Python files run as `python3 path/to/script.py` are not inline snippets: their own directory,
not the cwd, is first on the path. Test code (tests/ directories) is not scanned.

The repo scan runs only in the source repo (it reads every plugin); in an isolated copy of
kit-dev it skips. Standard library only. Run from plugins/kit-dev:

    python3 -m unittest discover -s tests -q
"""
import re
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
REPO = KIT.parent.parent
PLUGINS = REPO / "plugins"
IN_REPO = (REPO / ".claude-plugin" / "marketplace.json").is_file() and PLUGINS.is_dir()

# python / python3 (optionally python3.12), other short flags, then -c or a lone - (stdin).
INLINE = re.compile(r"(?<![\w.-])python3?(?:\.\d+)?((?:\s+-[A-Za-z]+)*)\s+(-c|-|-m\s+[\w.]+)(?=[\s'\"`]|$)")
# -m puts the cwd first too; unittest discover is exempt: it runs our own tests from their own dir.
# Bare stdin forms: python3 <<EOF, python3 < f, x | python3.
STDIN = re.compile(r"(?<![\w.-])python3?(?:\.\d+)?((?:\s+-[A-Za-z]+)*)\s*<(?:<|\s)|\|\s*python3?(?:\.\d+)?((?:\s+-[A-Za-z]+)*)\s*$")
EXEMPT = re.compile(r"-m\s+unittest$")
SUFFIXES = {".md", ".json", ".sh"}


def unisolated(text):
    """Yield (line number, line) for each inline snippet whose flags lack -I."""
    for n, line in enumerate(text.splitlines(), 1):
        for m in INLINE.finditer(line):
            if EXEMPT.match(m.group(2)):
                continue
            flags = m.group(1) + " " + m.group(2)
            if not re.search(r"(^|\s)-[A-Za-z]*I", flags):
                yield n, line.strip()
        for m in STDIN.finditer(line):
            flags = (m.group(1) or "") + (m.group(2) or "")
            if not re.search(r"(^|\s)-[A-Za-z]*I", flags):
                yield n, line.strip()


@unittest.skipUnless(IN_REPO, "needs the source repo's plugins/")
class IsolatedPython(unittest.TestCase):
    def test_every_inline_snippet_runs_isolated(self):
        bad = []
        for p in sorted(PLUGINS.rglob("*")):
            if p.suffix not in SUFFIXES or not p.is_file() or "tests" in p.relative_to(PLUGINS).parts:
                continue
            for n, line in unisolated(p.read_text(encoding="utf-8", errors="replace")):
                bad.append(f"{p.relative_to(REPO)}:{n}: {line[:100]}")
        self.assertEqual(bad, [], "inline python without -I:\n" + "\n".join(bad))


class Matcher(unittest.TestCase):
    """The scan itself, proved on strings, so it runs in an isolated copy too."""

    def hits(self, s):
        return [n for n, _ in unisolated(s)]

    def test_flags_missing_i(self):
        self.assertEqual(self.hits("x | python3 -c 'pass'"), [1])
        self.assertEqual(self.hits("python3 - a <<'PY'"), [1])
        self.assertEqual(self.hits('python -c "pass"'), [1])
        self.assertEqual(self.hits("python3 -u -c 'pass'"), [1])
        self.assertEqual(self.hits("python3 <<'PY'"), [1])
        self.assertEqual(self.hits("cat f | python3"), [1])
        self.assertEqual(self.hits("python3 -m json.tool f"), [1])
        self.assertEqual(self.hits("or `python3 -c`; the shape"), [1])
        self.assertEqual(self.hits("/usr/bin/python3 -c 'pass'"), [1])

    def test_accepts_isolated_and_files(self):
        self.assertEqual(self.hits("python3 -I -c 'pass'"), [])
        self.assertEqual(self.hits("python3 -I - a <<'PY'"), [])
        self.assertEqual(self.hits("python3 path/to/script.py --x"), [])
        self.assertEqual(self.hits("python3 -m unittest discover"), [])
        self.assertEqual(self.hits("python3 -I -m py_compile f"), [])
        self.assertEqual(self.hits("python3 -I <<'PY'"), [])


if __name__ == "__main__":
    unittest.main()
