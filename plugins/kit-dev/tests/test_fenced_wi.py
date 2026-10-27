"""No fenced command in plugins/**/*.md runs a bare `wi` (CLAUDE.md § Conventions).

A fenced command runs the resolved `$WI`, the absolute command the lookup printed, never
a bare `wi`: a bare `wi` runs the first `wi` on PATH, which in most sessions does not
exist and, where a person put one there, may be another tool or another install. Prose
outside fences keeps `wi <verb>` as the name of the verb.

A line in a fence is a hit when `wi <verb>` starts a command: at the start of the line,
or after `;`, `&&`, `||`, `|`, `$(`, an opening backtick, the keywords `then`, `do`,
`else`, or `!` (each followed by whitespace), or `{` or `(`; and after any environment
assignments (`NAME=value wi ls`) in any of those places. Comment lines (first non-space
character `#`) are exempt by rule. ALLOWED lists any other line that may stay, keyed
relative to plugins/ with a substring of the line, each with its reason; an entry that
no longer matches fails, so the list only shrinks.

No fenced command greps the store for `^decision [0-9]` to find a decision number either
(work item 03ab F8, answer 309 (b)): a number comes from `$WI raise`, the last one from
`$WI counter`. COUNTER_ALLOWED keeps the older-`wi` fallbacks (an installed `wi` with no
`raise` or `counter` exits 2 with `invalid choice`), under the same only-shrinks rule. The
checkpoint SKILL.md holds its fallback, checked here because context-guard's own suites
test no skill text.

Runs only in the source repo (it reads every plugin); in an isolated copy of kit-dev it
skips. Standard library only. Run from plugins/kit-dev:

    python3 -m unittest discover -s tests -q
"""
import re
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
REPO = KIT.parent.parent
PLUGINS = REPO / "plugins"
IN_REPO = ((REPO / "README.md").is_file()
           and (REPO / ".claude-plugin" / "marketplace.json").is_file())

# (file relative to plugins/, a substring of the line) -> why it may stay. Each is prose
# inside a fence (a brief template, a sample file, a directory map) that names a verb in an
# inline code span, which the opening-backtick form cannot tell from a substitution.
_PROSE = "prose in a fence naming the verb in a code span, not a command"
ALLOWED = {
    ("context-guard/skills/checkpoint/references/handoff-format.md",
     "Work-item IDs (`wi show <id>`)"): _PROSE,
    ("dev-flow/skills/dev-cycle/references/agent-brief.md",
     "Do not run `wi done`, `wi claim` or `wi release`"): _PROSE,
    ("dev-flow/skills/dev-cycle/references/review-brief.md",
     "Do not run `wi claim`, `wi done`, `wi handoff`"): _PROSE,
    ("kit-dev/skills/update-kit/references/repo-map.md",
     "(wi CLI incl. `wi estate`"): _PROSE,
    ("kit-dev/skills/update-kit/references/repo-map.md",
     "written from `wi estate`)"): _PROSE,
    ("work-items/skills/work-items/references/format.md",
     "closed items moved by `wi archive`"): _PROSE,
}

# (file relative to plugins/, a substring of the line) -> why that counter grep may stay.
_FALLBACK = "the older-wi fallback: an installed wi with no counter or raise exits 2"
COUNTER_ALLOWED = {
    ("dev-flow/skills/librarian-mode/references/rehydrate.md",
     "$WI counter || grep -rh '^decision [0-9]'"): _FALLBACK,
    ("context-guard/skills/checkpoint/SKILL.md",
     "grep -rhoE '^decision [0-9]+' <store>"): _FALLBACK,
}
COUNTER_GREP = re.compile(r"\bgrep\b.*\^decision \[0-9\]")
CHECKPOINT = "context-guard/skills/checkpoint/SKILL.md"

_SEP = (r"(?:^\s*"                      # start of the line
        r"|(?:;|&&|\|\||\|)\s*"         # ; && || |
        r"|\$\(\s*|`\s*"                # $( and an opening backtick
        r"|\b(?:then|do|else)\s+"       # shell keywords
        r"|!\s+"                        # negation
        r"|[{(]\s*)")                   # a group or subshell
_ASSIGN = r"(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*"
BARE_WI = re.compile(_SEP + _ASSIGN + r"wi\s+[a-z][a-z-]*\b")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")


def bare_wi(line):
    """True when the fenced line runs a bare `wi <verb>`."""
    if line.lstrip().startswith("#"):
        return False
    return bool(BARE_WI.search(line))


def fenced_lines(text):
    """(line number, line) for every line inside a fence."""
    opener = None
    for n, line in enumerate(text.splitlines(), 1):
        m = FENCE.match(line)
        if opener is None:
            if m:
                opener = m.group(1)
            continue
        if m and m.group(1)[0] == opener[0] and len(m.group(1)) >= len(opener) \
                and not line.strip()[len(m.group(1)):].strip():
            opener = None
            continue
        yield n, line


def counter_grep(line):
    """True when the fenced line greps for `^decision [0-9]` to find a decision number."""
    if line.lstrip().startswith("#"):
        return False
    return bool(COUNTER_GREP.search(line))


def scan(text, test):
    """(line number, line) for every fenced line of `text` that `test` reports."""
    return [(n, line) for n, line in fenced_lines(text) if test(line)]


def hits(test=bare_wi):
    out = []
    for path in sorted(PLUGINS.rglob("*.md")):
        rel = str(path.relative_to(PLUGINS))
        for n, line in scan(path.read_text(encoding="utf-8"), test):
            out.append((rel, n, line))
    return out


def allowed(rel, line, table=ALLOWED):
    return any(f == rel and sub in line for (f, sub) in table)


def checkpoint_problems(text):
    """The checkpoint SKILL.md raises with `$WI raise` and keeps the older-wi fallback."""
    flat = " ".join(text.split())
    fenced = [line.strip() for _, line in fenced_lines(text)]
    out = []
    if "$WI raise <id> -- '<question>'" not in fenced:
        out.append("no fenced `$WI raise`")
    if "with `wi raise <id> -- '<question>'`, which gives out N from the store's counter" \
            not in flat:
        out.append("no `wi raise` in the prose")
    if "An older `wi` has no `raise` (exit 2, `invalid choice: 'raise'`)" not in flat \
            or not any(x.startswith("# an older wi (exit 2, invalid choice: 'raise')")
                       for x in fenced):
        out.append("no older-wi fallback")
    if "N one more than the store's highest" in flat:
        out.append("the old grep-first text")
    return out


class TestScanForms(unittest.TestCase):
    REPORTED = [
        "wi ls",
        "cd x; wi ls",
        "true && wi ls",
        "false || wi ls",
        "echo x | wi note abc -- y",
        "X=$(wi show abc)",
        "X=`wi show abc`",
        "if true; then wi ls; fi",
        "for i in 1; do wi ls; done",
        "if false; then :; else wi ls; fi",
        "! wi lint",
        "{ wi ls; }",
        "(wi ls)",
        "WORK_ITEMS_ROOT=x wi ls",
        "cd x && WORK_ITEMS_ROOT=x WORK_ITEMS_OWNER=y wi ls",
    ]
    NOT_REPORTED = [
        "$WI ls",
        "# a wi comment",
        "  # wi prime first",
        "python3 /x/scripts/wi.py ls",
        "items: abc  # optional: wi ids you expect",
        "command -v wi",
    ]

    def test_reported(self):
        for line in self.REPORTED:
            self.assertTrue(bare_wi(line), line)

    def test_not_reported(self):
        for line in self.NOT_REPORTED:
            self.assertFalse(bare_wi(line), line)

    COUNTER_REPORTED = [
        "grep -rh '^decision [0-9]' \"$WORK_ITEMS_ROOT\" | sort -k2 -n | tail -1",
        "grep -rhoE '^decision [0-9]+' <store> | sort -k2 -n | tail -1",
        "N=$(grep -rh '^decision [0-9]' x | wc -l)",
        "$WI counter || grep -rh '^decision [0-9]' x",
    ]
    COUNTER_NOT_REPORTED = [
        "$WI counter",
        "$WI raise <id> -- '<question>'",
        "# the old grep '^decision [0-9]', for an older wi",
        "grep -rh '^answer [0-9]' x",
    ]

    def test_counter_grep_reported(self):
        for line in self.COUNTER_REPORTED:
            self.assertTrue(counter_grep(line), line)
        for line in self.COUNTER_NOT_REPORTED:
            self.assertFalse(counter_grep(line), line)

    def test_counter_grep_fixture(self):
        # mutant: the old grep inserted into a copy of a fixture file, fenced and in prose
        fixture = ("Find the next number:\n\n```bash\n$WI counter\n```\n\n"
                   "Never `grep -rh '^decision [0-9]'` the store.\n")
        self.assertEqual(scan(fixture, counter_grep), [])
        mutant = fixture.replace("$WI counter\n",
                                 "$WI counter\ngrep -rh '^decision [0-9]' x | tail -1\n")
        self.assertEqual([n for n, _ in scan(mutant, counter_grep)], [5])

    def test_only_fenced_lines(self):
        text = "wi ls in prose\n```bash\n$WI ls\nwi ls\n```\nwi ls after\n"
        self.assertEqual([n for n, _ in fenced_lines(text)], [3, 4])
        text = "````md\n```bash\nwi ls\n```\nwi ls\n````\nwi ls\n"
        self.assertEqual([n for n, _ in fenced_lines(text)], [2, 3, 4, 5])


@unittest.skipUnless(IN_REPO, "runs in the source repo only")
class TestFencedWi(unittest.TestCase):
    def test_no_bare_wi_in_fences(self):
        bad = [f"plugins/{rel}:{n}: {line.strip()}" for rel, n, line in hits()
               if not allowed(rel, line)]
        self.assertEqual(bad, [], "fenced commands run $WI, never a bare wi "
                                  "(CLAUDE.md § Conventions)")

    def test_allowed_entries_still_match(self):
        found = hits()
        stale = [k for k in ALLOWED
                 if not any(rel == k[0] and k[1] in line for rel, _, line in found)]
        self.assertEqual(stale, [])

    def test_no_counter_grep_in_fences(self):
        bad = [f"plugins/{rel}:{n}: {line.strip()}" for rel, n, line in hits(counter_grep)
               if not allowed(rel, line, COUNTER_ALLOWED)]
        self.assertEqual(bad, [], "a decision number comes from $WI raise and $WI counter, "
                                  "never a grep of the store (03ab F8)")

    def test_counter_allowed_entries_still_match(self):
        found = hits(counter_grep)
        stale = [k for k in COUNTER_ALLOWED
                 if not any(rel == k[0] and k[1] in line for rel, _, line in found)]
        self.assertEqual(stale, [])

    def test_checkpoint_raises_through_the_counter(self):
        text = (PLUGINS / CHECKPOINT).read_text(encoding="utf-8")
        self.assertEqual(checkpoint_problems(text), [])
        # mutants: the fenced raise, the prose, the fallback comment and sentence deleted
        self.assertIn("no fenced `$WI raise`", checkpoint_problems(
            text.replace("$WI raise <id> -- '<question>'\n", "")))
        self.assertIn("no `wi raise` in the prose", checkpoint_problems(
            re.sub(r"`wi raise <id> -- '<question>'`,\s+which", "a grep, which", text)))
        self.assertIn("no older-wi fallback", checkpoint_problems(
            "\n".join(x for x in text.splitlines()
                      if not x.startswith("# an older wi (exit 2"))))
        self.assertIn("no older-wi fallback", checkpoint_problems(
            re.sub(r"An older `wi` has no\s+`raise`", "A `wi`", text)))


if __name__ == "__main__":
    unittest.main()
