"""5039 H3: the `## Holds` section — in every tier of an owned manifest, never
trimmed, a past end time flagged `expired? confirm`, never in a foreign header.
Every test runs against a temp CLAUDE_CONFIG_DIR and a temp git repo."""
import json, os, subprocess, sys, tempfile, time, unittest

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HOOKS)

MANIFEST = """---
handoff: 1
repo: demo
session: {session}
written: {written}
head: {head}
mode: continue
---
## Doing
Building the thing.

## Goal
mode: continue — operator: "finish phase 2"
{holds}
## In flight
- implementer — thing-1a2b — agent a1b2c3 — round 2 — waiting on review

## Read in full
a/plan.md — the plan

## Copy forward
- /tmp/scratch/brief.md — the brief, copy to the series dir

## Aware of
- CORRECTION the cache is per session, not per repo
- REFUSED sudo for dd
{aware}
## Next
wi show thing-1a2b

## Scrolls
{scrolls}
"""

PAST = "2020-01-02T03:04Z"
FUTURE = "2999-01-01T00:00Z"
HOLDS = f"""
## Holds
- HOLD no push to origin — operator reviewing the log — until decision 52
- HOLD dispatch small (one agent) — quota — until {FUTURE}
- HOLD pause the loop — operator asleep — until {PAST}
"""


def run_hook(payload, env):
    p = subprocess.run([sys.executable, os.path.join(HOOKS, "rehydrate.py")],
                       input=json.dumps(payload), capture_output=True,
                       text=True, env=env, timeout=30)
    return p.returncode, json.loads(p.stdout) if p.stdout.strip() else {}


class TestHolds(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cfg = tempfile.TemporaryDirectory()
        self.env = dict(os.environ, CLAUDE_CONFIG_DIR=self.cfg.name)
        os.environ["CLAUDE_CONFIG_DIR"] = self.cfg.name
        global rh
        import rehydrate as rh
        self.repo = self.tmp.name
        for c in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "x"]):
            subprocess.run(["git", "-C", self.repo, "-c", "user.email=t@t",
                            "-c", "user.name=t"] + c, check=True, capture_output=True)
        self.head = subprocess.run(["git", "-C", self.repo, "rev-parse", "--short", "HEAD"],
                                   capture_output=True, text=True).stdout.strip()

    def tearDown(self):
        self.tmp.cleanup(); self.cfg.cleanup()
        os.environ.pop("CLAUDE_CONFIG_DIR", None)

    def write(self, holds=HOLDS, session="s", aware="", scrolls="- x.md — notes"):
        text = MANIFEST.format(
            session=session, head=self.head, holds=holds, aware=aware, scrolls=scrolls,
            written=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        with open(os.path.join(self.repo, "HANDOFF.md"), "w") as fh:
            fh.write(text)
        return text

    def ctx(self, source, sid="s"):
        rc, out = run_hook({"session_id": sid, "source": source, "cwd": self.repo},
                           self.env)
        self.assertEqual(rc, 0)
        return (out.get("hookSpecificOutput") or {}).get("additionalContext", "")

    # ── every tier ─────────────────────────────────────────────────────────
    def test_header_only_tiers_carry_the_hold_lines(self):
        self.write()
        for source in ("startup", "clear"):
            c = self.ctx(source)
            self.assertNotIn("## Doing", c, source)                 # header only
            self.assertIn("Holds this manifest records", c, source)
            self.assertIn("- HOLD no push to origin — operator reviewing the log — "
                          "until decision 52", c, source)
            self.assertIn(f"until {FUTURE}", c, source)
            self.assertIn(f"until {PAST} [expired? confirm", c, source)

    def test_resume_header_carries_holds_too(self):
        self.write()
        self.assertIn("## Holds", self.ctx("resume"))              # first sight: full
        c = self.ctx("resume")                                     # unchanged: header
        self.assertNotIn("## Doing", c)
        self.assertIn("HOLD no push to origin", c)

    def test_full_tier_carries_the_section_with_expiry_marked(self):
        self.write()
        c = self.ctx("compact")
        self.assertIn("## Holds\n- HOLD no push to origin", c)
        self.assertIn(f"until {PAST} [expired? confirm: its end time has passed]", c)
        self.assertNotIn(f"until {FUTURE} [expired", c)
        self.assertNotIn("decision 52 [expired", c)
        self.assertNotIn("Holds this manifest records", c)          # no duplicate block

    def test_foreign_header_carries_no_holds(self):
        self.write(session="other-session")
        for source in ("startup", "clear", "compact", "resume"):
            c = self.ctx(source)
            self.assertIn("not this session", c, source)
            self.assertNotIn("HOLD", c, source)
            self.assertNotIn("Holds this manifest records", c, source)

    def test_no_holds_section_or_none_behaves_as_before(self):
        for holds in ("", "\n## Holds\nNone\n", "\n## Holds\n- None.\n"):
            self.write(holds=holds)
            for source in ("startup", "compact"):
                c = self.ctx(source)
                self.assertNotIn("Holds this manifest records", c, repr(holds))
                self.assertNotIn("expired?", c, repr(holds))

    # ── expiry ─────────────────────────────────────────────────────────────
    def test_hold_expired_reads_only_the_end_condition(self):
        now = rh.stamp_epoch("2026-09-22T12:00Z")
        cases = {
            "HOLD x — why — until 2026-09-22T11:59Z": True,
            "HOLD x — why — until 2026-09-22T12:30Z": False,
            "HOLD x — why — until 2026-09-22 13:00 +02:00": True,     # 11:00 UTC
            "HOLD x — why — until 2026-09-21": True,                  # the day ended
            "HOLD x — why — until 2026-09-22": False,                 # still today
            "HOLD x — why — until decision 52": False,
            "HOLD x — why — until bedtime": False,                    # an event
            "HOLD x — filed 2020-01-01 — until decision 52": False,   # why, not end
            "HOLD x — why — 2026-09-20T00:00Z": True,                 # no `until`
            "HOLD x — why — until decision 52 (filed 2020-01-01)": False,
            "HOLD x — why — until the 2020-01-01 build ships": False,  # an event
            "HOLD x — why — until 2026-09-21 or decision 5": True,     # leads: a time
            "HOLD x — why — until: 2026-09-21": True,                  # `until:`
            "HOLD x — why — Until 2026-09-21": True,
        }
        for line, want in cases.items():
            self.assertEqual(rh.hold_expired(line, now), want, line)

    # ── never trimmed ──────────────────────────────────────────────────────
    PROTECTED = ("## Doing\nBuilding the thing.",
                 'mode: continue — operator: "finish phase 2"',
                 "- HOLD no push to origin — operator reviewing the log — until decision 52",
                 "- HOLD dispatch small (one agent)",
                 "- implementer — thing-1a2b — agent a1b2c3 — round 2 — waiting on review",
                 "a/plan.md — the plan",
                 "- /tmp/scratch/brief.md — the brief, copy to the series dir")

    def test_trim_never_touches_protected_sections(self):
        aware = "".join(f"- DECIDED choice {i} — {'d' * 80}\n" for i in range(40))
        scrolls = "\n".join(f"- f{i}.md — {'z' * 200}" for i in range(60))
        text = self.write(aware=aware, scrolls=scrolls)
        out = rh.trim(text, 3000)
        self.assertLessEqual(len(out), 3000)
        for keep in self.PROTECTED:
            self.assertIn(keep, out)
        self.assertIn("## Scrolls\n(trimmed — read the manifest file)", out)
        # Aware of keeps CORRECTION/REFUSED, loses the rest
        self.assertIn("- CORRECTION the cache is per session", out)
        self.assertIn("- REFUSED sudo for dd", out)
        self.assertNotIn("DECIDED choice", out)

    def test_trim_order_scrolls_before_next_before_aware_of(self):
        scrolls = "\n".join(f"- f{i}.md — {'z' * 100}" for i in range(10))
        text = self.write(aware="- DECIDED keep me\n", scrolls=scrolls)
        out = rh.trim(text, len(text) - 200)             # Scrolls alone is enough
        self.assertIn("## Scrolls\n(trimmed", out)
        self.assertIn("wi show thing-1a2b", out)
        self.assertIn("DECIDED keep me", out)

    def test_trim_keeps_the_next_withheld_line(self):
        text = self.write(scrolls="\n".join(f"- f{i}.md — {'z' * 200}" for i in range(30)))
        text = rh.withhold_next(text, "Next withheld: head moved 2 commits since this "
                                      "manifest (a..b); run wi prime and git log.")
        text = text.replace("run wi prime and git log.\n",
                            "run wi prime and git log.\n" + "extra\n" * 200)
        out = rh.trim(text, 1800)
        self.assertIn("Next withheld: head moved 2 commits", out)

    def test_full_injection_over_budget_keeps_holds_in_flight_copy_forward(self):
        aware = "".join(f"- DECIDED choice {i} — {'d' * 80}\n" for i in range(40))
        scrolls = "\n".join(f"- f{i}.md — {'z' * 200}" for i in range(60))
        self.write(aware=aware, scrolls=scrolls)
        c = self.ctx("compact")
        self.assertLess(len(c), 10_000)
        self.assertIn("trimmed", c)
        for keep in self.PROTECTED:
            self.assertIn(keep, c)
        self.assertIn(f"until {PAST} [expired? confirm", c)

    def test_final_pass_keeps_what_the_steps_kept(self):
        # review r1: an early extra section must go before a stepped one loses
        # its CORRECTION/REFUSED or Next-withheld line.
        text = self.write(aware="".join(f"- DECIDED d{i} — {'d' * 80}\n" for i in range(10)))
        text = text.replace("Building the thing.\n", "Building the thing.\n" + "b" * 3000 + "\n")
        text = text.replace("\n## Holds\n", "\n## Context\n" + "c" * 1500 + "\n\n## Holds\n")
        text = rh.withhold_next(text, "Next withheld: head moved 2 commits since this "
                                      "manifest (a..b); run wi prime and git log.")
        out = rh.trim(text, 4400)
        self.assertLessEqual(len(out), 4400)
        self.assertIn("## Context\n(trimmed — read the manifest file)", out)
        for keep in ("- CORRECTION the cache is per session", "- REFUSED sudo for dd",
                     "Next withheld: head moved 2 commits") + self.PROTECTED:
            self.assertIn(keep, out)
        self.assertNotIn("DECIDED d1", out)

    def test_heading_variants_and_prose_lines(self):
        for head in ("## Holds:", "## Holds (1)", "## Holds"):
            holds = (f"\n{head}\nOne line per standing hold, ≤8; `None` when there are "
                     f"none.\n- HOLD no push — why — until decision 52\n")
            text = self.write(holds=holds)
            c = self.ctx("startup")
            self.assertIn("- HOLD no push — why — until decision 52", c, head)
            self.assertNotIn("One line per standing hold", c, head)
            out = rh.trim(text.replace("- x.md — notes", "x" * 5000), 1500)
            self.assertIn(head + "\nOne line per standing hold", out, head)

    def test_hold_line_shapes(self):
        holds = ("\n## Holds\n- **HOLD** bold push — why — until decision 1\n"
                 "- hold lower dispatch — why — until decision 2\n"
                 "- a prose note, not a hold\n")
        self.assertEqual(rh.hold_lines(self.write(holds=holds)),
                         ["**HOLD** bold push — why — until decision 1",
                          "hold lower dispatch — why — until decision 2"])
        c = self.ctx("startup")
        self.assertIn("- **HOLD** bold push", c)
        self.assertNotIn("a prose note", c)

    def test_crlf_manifest(self):
        # review r2: CRLF headings end in \r; they must still name their sections.
        aware = "".join(f"- DECIDED d{i} — {'d' * 80}\n" for i in range(20))
        scrolls = "\n".join(f"- f{i}.md — {'z' * 100}" for i in range(20))
        lf = self.write(aware=aware, scrolls=scrolls)
        crlf = lf.replace("\n", "\r\n")
        with open(os.path.join(self.repo, "HANDOFF.md"), "w", newline="") as fh:
            fh.write(crlf)
        names = [n for n, _ in rh._sections(crlf)]
        for want in ("doing", "goal", "holds", "in flight", "read in full",
                     "copy forward", "aware of", "next", "scrolls"):
            self.assertIn(want, names)
        self.assertEqual(len(rh.hold_lines(crlf)), 3)
        out = rh.trim(crlf, 2000)
        self.assertLessEqual(len(out), 2000)
        for keep in ("a/plan.md — the plan", "- REFUSED sudo for dd",
                     "- CORRECTION the cache is per session", "- HOLD no push to origin",
                     "- implementer — thing-1a2b — agent a1b2c3"):
            self.assertIn(keep, out)
        self.assertNotIn("DECIDED d1", out)
        self.assertIn(f"until {PAST} [expired? confirm: its end time has passed]\r\n",
                      rh.annotate_holds(crlf))
        c = self.ctx("startup")
        self.assertIn("- HOLD no push to origin", c)
        self.assertIn(f"until {PAST} [expired? confirm", c)
        self.assertNotIn("\r", c)

    # ── bounded, plain text ────────────────────────────────────────────────
    def test_header_block_is_bounded_and_plain(self):
        many = "\n## Holds\n" + "".join(
            f"- HOLD thing {i} \x1b[2J\u202e\u061c\ufeff\u2062 — {'w' * 150} — until decision {i}\n"
            for i in range(20))
        self.write(holds=many)
        c = self.ctx("startup")
        block = c[c.index("Holds this manifest records"):]
        self.assertLessEqual(len(block), rh.HOLDS_BUDGET)
        self.assertNotIn("\x1b", c)
        for ch in ("\u202e", "\u061c", "\ufeff", "\u2062"):
            self.assertNotIn(ch, c)
        self.assertIn("more holds — read the manifest file)", c)
        self.assertLessEqual(block.count("\n- HOLD"), rh.HOLDS_MAX)


if __name__ == "__main__":
    unittest.main()
