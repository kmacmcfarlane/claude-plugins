"""The research verifier's procedure rules (item 2e75), held by what its files say.

- the score sheet's claims table carries the Opened column and the columns the sheet
  check reads, so the verifier's template and `check-sheet.py` stay in step;
- the body says a source it did not open gets no verdict on its content, a run file is
  never a source, fetch prompts are neutral, and the header is counted from the table;
- the verifier prompt names the run files, and the research skill and deep-investigation
  run the sheet check and record its TALLY.

Standard library only. Run from plugins/dev-flow:

    python3 -m unittest discover -s tests -q
"""
import importlib.util
import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
AGENT = PLUGIN / "agents" / "research-verifier.md"
RESEARCH = PLUGIN / "skills" / "research"
RUN_RECORD = RESEARCH / "references" / "run-record.md"
SKILL = RESEARCH / "SKILL.md"
GATE = PLUGIN / "skills" / "deep-investigation" / "references" / "security-gate.md"
CHECK = RESEARCH / "scripts" / "check-sheet.py"


def text(path):
    return path.read_text(encoding="utf-8")


def flat(s):
    return re.sub(r"\s+", " ", s)


def load_check():
    spec = importlib.util.spec_from_file_location("check_sheet", CHECK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class VerifierRules(unittest.TestCase):
    def test_sheet_template_matches_the_check(self):
        body = text(AGENT)
        row = next(l for l in body.splitlines() if l.startswith("| # | File |"))
        cols = [c.strip().lower() for c in row.strip("|").split("|")]
        for name in ("source", "opened", "verdict"):
            self.assertIn(name, cols)
        check = load_check()
        for s in check.SECTIONS:
            self.assertIn("## " + s, body)
        for f in check.FIELDS:
            self.assertRegex(body, r"(?m)^" + f + r": <n>$")
        for v in check.VERDICTS:
            self.assertIn("`" + v + "`", body)

    def test_procedure_rules(self):
        body = flat(text(AGENT))
        for needle in ("**Never a run file.**", "**Open it yourself, this run.**",
                       "**Ask neutrally.**", "never ask a yes/no confirmation",
                       "noted `own-run source`",
                       "then the header counts by counting that table's rows",
                       "No verdict on a source you did not open in this run"):
            self.assertIn(needle, body)

    def test_callers_run_the_check(self):
        rr = flat(text(RUN_RECORD))
        self.assertIn("Run files (never a source): <staging>[, <series dir>]", rr)
        self.assertIn("## The sheet check", text(RUN_RECORD))
        self.assertIn("**The counts you record are the TALLY's**", rr)
        self.assertIn("scripts/check-sheet.py", rr)
        skill = flat(text(SKILL))
        self.assertIn("§ The sheet check", skill)
        self.assertIn("Ledger `VERIFIED` with the TALLY's counts", skill)
        gate = flat(text(GATE))
        self.assertIn("§ The sheet check", gate)
        self.assertIn("`TALLY` counts", gate)


if __name__ == "__main__":
    unittest.main()
