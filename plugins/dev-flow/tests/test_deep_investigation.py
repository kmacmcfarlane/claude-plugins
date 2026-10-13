"""deep-investigation's security parity with the research family (caef F2, item 1ffd).

The skill is prose, so most rules are held by what its files say:

- lanes launch on the `research-lane` agent type, routed by the research skill's
  § Profiles, never `general-purpose`, and the interim routing row is gone;
- lanes write to the run's staging area, never into the series;
- the scan floor, the verifier and the toolkit gate stand between staging and the series;
- the strategy doc's ledger carries no lane wording;
- a lane's staged file is scanned before a later lane reads it, and only scanned files with
  no HOLD at the landing rescan are copied into the series (review r1, findings 1 and 2);
- a held lane goes to `H/.claude-sandbox/research/_held/<run>/`, where `H` is the parent of
  the git common dir of the session's primary working directory (05 A2.1, the A3.9 anchor).
  The gate's procedure and the anchor live in `references/security-gate.md`.

The anchor is also run: the skill's own snippet, executed against a worktree fixture whose
Bash cwd is a nested sidecar repo, must give the main checkout.

Standard library only. Run from plugins/dev-flow:

    python3 -m unittest discover -s tests -q
"""
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
SKILL_DIR = PLUGIN / "skills" / "deep-investigation"
SKILL = SKILL_DIR / "SKILL.md"
LANE_CONTRACT = SKILL_DIR / "references" / "lane-contract.md"
STRATEGY = SKILL_DIR / "references" / "research-strategy-format.md"
GATE = SKILL_DIR / "references" / "security-gate.md"
ROUTING = PLUGIN / "skills" / "research" / "references" / "intensity-and-routing.md"

PLACEHOLDER = "<project dir>"
HELD = "$H/.claude-sandbox/research/_held/"


def text(path):
    return path.read_text(encoding="utf-8")


def section(body, heading):
    """The body of the `## <heading>` section, up to the next `## ` heading."""
    m = re.search(r"^## " + re.escape(heading) + r"\n(.*?)(?=^## |\Z)", body, re.S | re.M)
    return m.group(1) if m else None


def flat(s):
    """Whitespace runs folded to one space, so a rule wrapped across lines still matches."""
    return re.sub(r"\s+", " ", s)


def anchor_block():
    """The one fenced bash block in the skill (SKILL.md or its gate reference) computing H."""
    blocks = re.findall(r"^```bash\n(.*?)^```", text(SKILL) + text(GATE), re.S | re.M)
    hits = [b for b in blocks if "--git-common-dir" in b]
    return hits[0] if len(hits) == 1 else None


class TestLaneAgentType(unittest.TestCase):
    def test_skill_launches_research_lane(self):
        body = text(SKILL)
        self.assertIn('subagent_type: "dev-flow:research-lane"', body)
        self.assertNotIn("general-purpose", body)

    def test_lane_contract_launches_research_lane(self):
        self.assertIn("research-lane", section(text(LANE_CONTRACT), "Lane prompt skeleton"))

    def test_interim_routing_row_is_gone(self):
        body = text(ROUTING)
        self.assertNotIn("1ffd", body)
        outside = section(body, "Dispatches outside the profiles")
        self.assertIsNotNone(outside)
        self.assertNotRegex(outside, r"(?m)^\| `deep-investigation` lanes")

    def test_profiles_row_names_deep_investigation(self):
        profiles = section(text(ROUTING), "Profiles")
        row = next(l for l in profiles.splitlines() if l.startswith("| `research-lane` |"))
        self.assertIn("`deep-investigation`", row)
        self.assertNotIn("until", row)
        verifier = next(l for l in profiles.splitlines() if l.startswith("| `research-verifier` |"))
        self.assertIn("`deep-investigation`", verifier)


class TestStaging(unittest.TestCase):
    def test_output_contract_writes_to_staging(self):
        body = section(text(LANE_CONTRACT), "The output contract (verbatim, every lane)")
        self.assertIsNotNone(body)
        contract = "\n".join(l for l in body.splitlines() if l.startswith(">"))
        self.assertIn("`<staging>/findings/<lane-id>.md`", contract)
        self.assertNotIn("<series>/findings/", contract)

    def test_skill_names_the_staging_area(self):
        self.assertIn("<scratchpad>/research/<series-slug>/", text(SKILL))

    def test_cross_lane_citation_reads_staging(self):
        cite = section(text(LANE_CONTRACT), "Cross-lane citation (where it applies)")
        self.assertIn("<staging>/findings/", cite)
        self.assertNotIn("<series>/", cite)


class TestGate(unittest.TestCase):
    def test_scan_verify_and_toolkit_gate_named(self):
        body = flat(text(SKILL) + text(GATE))
        for needle in ("§ The scan floor", "§ The toolkit gate", "§ The verifier prompt",
                       "dev-flow:research-verifier", "--strip", "references/security-gate.md"):
            self.assertIn(needle, body, needle)

    def test_landing_copies_only_scanned_files_without_a_hold(self):
        """Review r1 finding 1: the copy is conditional on step 1's scan and the rescan."""
        land = flat(section(text(GATE), "Step 6.5 — scan, verify, hold, land") or "")
        self.assertIn("rescan what will land", land)
        self.assertIn("Copy only findings that step 1 scanned, and only files in which this "
                      "rescan finds no HOLD; anything else stays in staging, and a failed "
                      "rescan holds every file it covered.", land)
        self.assertIn("`late, not landed`", land)
        self.assertIn("`late, not landed`", text(STRATEGY))
        self.assertIn("Only files the scan saw and the rescan finds no HOLD in are copied",
                      flat(text(SKILL)))

    def test_verifier_routes_on_its_own_row(self):
        """Review r1 finding 8: not the lane model from Step 1."""
        verify = flat(section(text(GATE), "Step 6.5 — scan, verify, hold, land") or "")
        self.assertIn("from its own row in the `research` skill's "
                      "`references/intensity-and-routing.md` § Profiles (not the lane model",
                      verify)

    def test_a_lane_reads_another_lanes_file_only_after_a_scan(self):
        """Review r1 finding 2: read-first files and the mining plan are scanned before the
        reading lane is dispatched; a HOLD keeps the file out of its prompt."""
        pre = flat(section(text(GATE), "Before a lane reads another lane's file") or "")
        self.assertIn("Before you dispatch any lane whose prompt names a staged file to read "
                      "first", pre)
        self.assertIn("mining plan", pre)
        self.assertIn("with `--scripts`", pre)
        self.assertIn("keeps the file out of every reading lane's prompt", pre)
        self.assertIn("A held mining plan is never cleaned", pre)
        self.assertIn("the mining plan also with `--scripts` and into the toolkit gate's "
                      "script review", flat(text(SKILL)))
        self.assertIn("§ Before a lane reads another lane's file", flat(text(SKILL)))


class TestEdgeCases(unittest.TestCase):
    def test_sensitive_data_is_removed_from_the_series(self):
        """Review r1 finding 3: the orchestrator first reads findings after landing."""
        body = flat(text(SKILL))
        self.assertIn("Remove it from `<series>/findings/` before anything is committed", body)
        self.assertNotIn("before Step 6.5 lands it", body)


class TestLedger(unittest.TestCase):
    def test_done_lines_carry_no_lane_wording(self):
        body = text(STRATEGY)
        self.assertNotIn("Notable:", body)
        self.assertNotIn("results a reader would want", body)
        self.assertNotIn("notable results", text(SKILL))

    def test_entry_kinds(self):
        kinds = re.search(r"^Entry kinds: (.*?)\.\n", text(STRATEGY), re.S | re.M)
        self.assertIsNotNone(kinds)
        for kind in ("SCANNED", "TOOLS REVIEWED", "STRIPPED", "VERIFIED", "HELD", "LANDED"):
            self.assertIn(f"`{kind}`", kinds.group(1), kind)


class TestHeldAnchorText(unittest.TestCase):
    """05 A2.1: the held path uses the A3.9 anchor."""

    def test_one_anchor_block(self):
        self.assertIsNotNone(anchor_block(), "exactly one bash block computing H")

    def test_block_runs_against_the_project_dir_only(self):
        block = anchor_block()
        self.assertIsNotNone(block)
        self.assertIn(f"'{PLACEHOLDER}'", block)
        self.assertIn("--path-format=absolute", block)
        self.assertNotIn("CLAUDE_PROJECT_DIR", block)
        for line in block.splitlines():
            if "rev-parse" in line:
                self.assertIn("git -C ", line)

    def test_held_path_is_at_h(self):
        gate = text(GATE)
        self.assertIn(HELD, gate)
        self.assertIn("primary working directory", flat(gate))
        for body in (text(SKILL), gate):
            self.assertNotRegex(body, r"(?<![$/H])\.claude-sandbox/research/_held/")


@unittest.skipUnless(shutil.which("git") and shutil.which("bash"), "git and bash needed")
class TestHeldAnchorRuns(unittest.TestCase):
    """Run the skill's own snippet: a worktree session whose Bash cwd sits in a nested
    sidecar repo still anchors at the main checkout."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(self.tmp),
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid",
            "LC_ALL": "C",
        }
        self.main = self.tmp / "main"
        self.main.mkdir()
        self.git(self.main, "init", "-q")
        (self.main / "f").write_text("x\n")
        self.git(self.main, "add", "f")
        self.git(self.main, "commit", "-q", "-m", "init")
        self.wt = self.tmp / "wt"
        self.git(self.main, "worktree", "add", "-q", str(self.wt))
        self.sidecar = self.main / ".claude-sandbox"
        self.sidecar.mkdir()
        self.git(self.sidecar, "init", "-q")
        self.plain = self.tmp / "plain"
        self.plain.mkdir()

    def git(self, cwd, *args):
        subprocess.run(["git", "-C", str(cwd), *args], env=self.env, check=True,
                       capture_output=True)

    def anchor(self, project_dir, cwd, extra_env=None):
        block = anchor_block()
        self.assertIsNotNone(block)
        script = block.replace(PLACEHOLDER, str(project_dir)) + '\nprintf "%s\\n" "$H"\n'
        env = dict(self.env, **(extra_env or {}))
        out = subprocess.run(["bash", "-c", script], cwd=str(cwd), env=env,
                             capture_output=True, text=True, timeout=30)
        self.assertEqual(out.returncode, 0, "the anchor snippet failed")
        return os.path.realpath(out.stdout.strip())

    def test_worktree_with_sidecar_cwd_anchors_at_main(self):
        h = self.anchor(self.wt, self.sidecar, {"CLAUDE_PROJECT_DIR": str(self.sidecar)})
        self.assertEqual(h, os.path.realpath(self.main))

    def test_main_checkout_anchors_at_itself(self):
        self.assertEqual(self.anchor(self.main, self.sidecar), os.path.realpath(self.main))

    def test_no_git_anchors_at_the_project_dir(self):
        self.assertEqual(self.anchor(self.plain, self.plain), os.path.realpath(self.plain))


if __name__ == "__main__":
    unittest.main()
