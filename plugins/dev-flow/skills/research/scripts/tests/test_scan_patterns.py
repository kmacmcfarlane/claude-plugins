"""Property test: no compiled pattern in scan-findings.py stalls on hostile input.

Stalls were found one review at a time (overlapping quantifiers, unbounded spans); a
timeout holds the whole run with no line to strip. This test enumerates every compiled
pattern the scanner uses - each rule's regex and every module-level re.Pattern, so a new
pattern is covered automatically - and times search (finditer), match and fullmatch on a
standard set of hostile shapes of about 60 KB (a quadratic pattern takes seconds there):
long runs of spaces and separators, unclosed openers, each word as a tag opener with
attributes, each pattern's own literal words repeated with separators, and pairs of its
words mixed with separators (an option chain re-walked from every separator). Each
pattern runs in its own child process under a timeout, so one stall cannot hang the suite,
and the child reports the case it was on.
"""
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scan-findings.py"
LIMIT = 1.0          # seconds per case
CHILD_TIMEOUT = 60   # seconds per pattern, all cases

CHILD = r'''
import importlib.util, re, sys, time
spec = importlib.util.spec_from_file_location("scan_findings", sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
pats = [("rule:" + r.name, r.rx) for r in mod.RULES]
pats += sorted((n, v) for n, v in vars(mod).items() if isinstance(v, re.Pattern))
if sys.argv[2] == "list":
    print("\n".join(n for n, _ in pats))
    sys.exit()
name, p = next(x for x in pats if x[0] == sys.argv[2])
N = 60000
def rep(unit):
    return (unit * (N // max(1, len(unit)) + 1))[:N]
shapes = {}
for unit in [" ", "\t ", "<", "<!--", "<!-- ", "[", "[x](", "(", "\"", "'", "`", "|", "| ",
             "- ", "-", "/", "\\", "=", "a=", "a =", ": ", ". ", "a ", "a,", "a, ", "+ ",
             "*", "_", "~", "&#", "\"a\" ", "'a' + ", "> "]:
    shapes["rep(%r)" % unit] = rep(unit) + "!"
words = []
for w in re.findall(r"[A-Za-z_]{2,}", p.pattern):
    if w not in words:
        words.append(w)
words = words[:40]
for w in words:
    for sep in ("", " ", "|", "/", " -"):
        shapes["rep(%r)" % (w + sep)] = rep(w + sep) + "!"
    shapes["<%s + spaces" % w] = "<" + w + " " * N + "!"
    for unit in ("<%s a=b\"" % w, "<%s a=\"" % w, "<%s a=\"x\" " % w, "<%s a " % w):
        shapes["rep(%r)" % unit] = rep(unit) + "!"
# The pattern's words mixed with separators: adjacent pairs in pattern order and the
# first word with each other word (the shape of an option chain re-walked from every
# separator), and all words in one unit.
pairs = list(zip(words, words[1:] + words[:1])) + [(words[0], w) for w in words[1:]]
for a, b in pairs:
    for unit in ("-%s|%s " % (a, b), "-%s|%s " % (b, a), "%s/%s" % (a, b)):
        shapes["rep(%r)" % unit] = rep(unit) + "!"
for unit in ("".join("-" + w + "|" for w in words), "".join(w + " -" for w in words),
             "|".join(words) + " "):
    shapes["rep(all words %r)" % unit[:20]] = rep(unit) + "!"
for label, text in shapes.items():
    for how in ("finditer", "match", "fullmatch"):
        print("START", label, how, flush=True)
        t0 = time.perf_counter()
        if how == "finditer":
            for _ in p.finditer(text):
                pass
        else:
            getattr(p, how)(text)
        print("TIME %.4f %s %s" % (time.perf_counter() - t0, label, how), flush=True)
'''


def patterns():
    out = subprocess.run([sys.executable, "-c", CHILD, str(SCRIPT), "list"],
                         capture_output=True, text=True, timeout=60)
    return out.stdout.split()


class NoPatternStalls(unittest.TestCase):
    def test_patterns_are_enumerated(self):
        names = patterns()
        self.assertGreaterEqual(len([n for n in names if n.startswith("rule:")]), 19)
        for n in ("_LINK", "_TAG", "_IN_WORD", "_CONCAT_GAP", "_FENCE", "_CLOSER"):
            self.assertIn(n, names)

    def test_every_pattern_on_hostile_shapes(self):
        slow = []
        for name in patterns():
            with self.subTest(pattern=name):
                try:
                    out = subprocess.run([sys.executable, "-c", CHILD, str(SCRIPT), name],
                                         capture_output=True, text=True,
                                         timeout=CHILD_TIMEOUT).stdout
                except subprocess.TimeoutExpired as e:
                    last = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
                    started = [ln for ln in last.splitlines() if ln.startswith("START")]
                    slow.append("%s: stalled at %s" % (name, started[-1] if started else "?"))
                    continue
                for ln in out.splitlines():
                    if ln.startswith("TIME "):
                        _, secs, rest = ln.split(" ", 2)
                        if float(secs) >= LIMIT:
                            slow.append("%s: %s s on %s" % (name, secs, rest))
        self.assertEqual(slow, [], "\n".join(slow))


if __name__ == "__main__":
    unittest.main()
