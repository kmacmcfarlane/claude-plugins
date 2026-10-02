"""Property test: no compiled pattern in scan-findings.py stalls on hostile input.

Stalls were found one review at a time (overlapping quantifiers, unbounded spans); a
timeout holds the whole run with no line to strip. This test enumerates every compiled
pattern the scanner uses - each rule's regex and every module-level re.Pattern, so a new
pattern is covered automatically (the scanner keeps no inline regex) - and times search
(finditer), match and fullmatch on a standard set of hostile shapes at 30 KB and 120 KB.
A case fails when its time grows more than RATIO-fold over that 4x step and the larger
time is above FLOOR (linear growth is about 4x, quadratic about 16x), or when it takes
more than STALL seconds at all. The shapes: long runs of spaces and separators, unclosed
openers, each word as a tag opener with attributes, each pattern's own literal words
repeated with separators, and pairs of its words mixed with separators (an option chain
re-walked from every separator). Each
pattern runs in its own child process under a timeout, so one stall cannot hang the suite,
and the child reports the case it was on.
"""
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scan-findings.py"
RATIO = 8.0          # growth over a 4x size step: linear is ~4, quadratic ~16
FLOOR = 0.05         # seconds: below this at 120 KB, growth is not judged (timer noise)
STALL = 10.0         # seconds: any single case slower than this fails outright
CHILD_TIMEOUT = 180  # seconds per pattern, all cases

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
SIZES = (30000, 120000)
RATIO, FLOOR = float(sys.argv[3]), float(sys.argv[4])
def rep(unit):
    """A shape is (prefix, unit, suffix); build() repeats the unit to each size."""
    return ("", unit)
shapes = {}
for unit in [" ", "\t ", "<", "<!--", "<!-- ", "[", "[x](", "(", "\"", "'", "`", "|", "| ",
             "- ", "-", "/", "\\", "=", "a=", "a =", ": ", ". ", "a ", "a,", "a, ", "+ ",
             "*", "_", "~", "&#", "\"a\" ", "'a' + ", "> "]:
    shapes["rep(%r)" % unit] = rep(unit) + ("!",)
words = []
for w in re.findall(r"[A-Za-z_]{2,}", p.pattern):
    if w not in words:
        words.append(w)
words = words[:40]
for w in words:
    for sep in ("", " ", "|", "/", " -"):
        shapes["rep(%r)" % (w + sep)] = rep(w + sep) + ("!",)
    shapes["<%s + spaces" % w] = ("<" + w, " ", "!")
    for unit in ("<%s a=b\"" % w, "<%s a=\"" % w, "<%s a=\"x\" " % w, "<%s a " % w):
        shapes["rep(%r)" % unit] = rep(unit) + ("!",)
# The pattern's words mixed with separators: adjacent pairs in pattern order and the
# first word with each other word (the shape of an option chain re-walked from every
# separator), and all words in one unit.
pairs = list(zip(words, words[1:] + words[:1])) + [(words[0], w) for w in words[1:]]
for a, b in pairs:
    for unit in ("-%s|%s " % (a, b), "-%s|%s " % (b, a), "%s/%s" % (a, b)):
        shapes["rep(%r)" % unit] = rep(unit) + ("!",)
for unit in ("".join("-" + w + "|" for w in words), "".join(w + " -" for w in words),
             "|".join(words) + " "):
    shapes["rep(all words %r)" % unit[:20]] = rep(unit) + ("!",)
def build(shape, n):
    prefix, unit, suffix = shape
    return prefix + (unit * (n // max(1, len(unit)) + 1))[:n] + suffix
def timed(how, text):
    t0 = time.perf_counter()
    if how == "finditer":
        for _ in p.finditer(text):
            pass
    else:
        getattr(p, how)(text)
    return time.perf_counter() - t0
for label, shape in shapes.items():
    small, big = build(shape, SIZES[0]), build(shape, SIZES[1])
    for how in ("finditer", "match", "fullmatch"):
        print("START", label, how, flush=True)
        t1, t2 = timed(how, small), timed(how, big)
        if t2 > FLOOR and t2 / max(t1, 1e-6) > RATIO:      # re-measure once: noise
            t1, t2 = min(t1, timed(how, small)), min(t2, timed(how, big))
        print("TIME %.4f %.4f %s %s" % (t1, t2, label, how), flush=True)
'''


def patterns():
    out = subprocess.run([sys.executable, "-c", CHILD, str(SCRIPT), "list"],
                         capture_output=True, text=True, timeout=60)
    return out.stdout.split()


class NoPatternStalls(unittest.TestCase):
    def test_patterns_are_enumerated(self):
        names = patterns()
        self.assertGreaterEqual(len([n for n in names if n.startswith("rule:")]), 19)
        for n in ("_LINK", "_TAG", "_IN_WORD", "_CONCAT_GAP", "_FENCE", "_CLOSER",
                  "_BACKTICKS", "_DIGITS"):
            self.assertIn(n, names)

    def test_every_pattern_on_hostile_shapes(self):
        slow = []
        for name in patterns():
            with self.subTest(pattern=name):
                try:
                    out = subprocess.run([sys.executable, "-c", CHILD, str(SCRIPT), name,
                                          str(RATIO), str(FLOOR)],
                                         capture_output=True, text=True,
                                         timeout=CHILD_TIMEOUT).stdout
                except subprocess.TimeoutExpired as e:
                    last = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
                    started = [ln for ln in last.splitlines() if ln.startswith("START")]
                    slow.append("%s: stalled at %s" % (name, started[-1] if started else "?"))
                    continue
                for ln in out.splitlines():
                    if ln.startswith("TIME "):
                        _, t1, t2, rest = ln.split(" ", 3)
                        t1, t2 = float(t1), float(t2)
                        if t2 > STALL or (t2 > FLOOR and t2 / max(t1, 1e-6) > RATIO):
                            slow.append("%s: %.3f s -> %.3f s (30 KB -> 120 KB) on %s"
                                        % (name, t1, t2, rest))
        self.assertEqual(slow, [], "\n".join(slow))


if __name__ == "__main__":
    unittest.main()
