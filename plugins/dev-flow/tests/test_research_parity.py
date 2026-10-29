"""dev-flow's homes and pointers held to the research family, wherever the family sits.

dev-flow names the research family's files in its own: deep-investigation runs the research
skill's scan floor, sheet check and profiles and asks through its ask section; dev-cycle and
foundation point at its routing and record lines; dev-cycle's agent brief is the home of a
rule the family's agents copy; and the family's chain-of-verification dispatches dev-flow's
`scout`. This test stays in dev-flow and holds those links across the seam:

- **stop rule:** the family's home bullet (`research-lane.md`) equals dev-cycle's
  `agent-brief.md` bullet, and the home paragraph names the family's three copies;
- **store lookup:** research's § Resolving the store passes test_store_lookup.py's copy
  checks, its item rule keeps the "wi commits an own store" sentence, and every family file
  that assigns the store variables assigns both, with no hand commit of the store;
- **scout:** the `scout` row's pin in research's § Profiles equals dev-flow's
  `agents/scout.md`, and scout keeps the tools chain-of-verification's checks use;
- **anchors:** every "the `research` skill's `references/<file>` § <heading>" named in a
  dev-flow file outside the family resolves to an existing file and heading;
- **deep-investigation:** its SKILL.md points at § Putting an ask to the operator, its gate
  names § The sheet check and the TALLY counts, and research's § Profiles rows name it with
  no interim routing row left.

The family is found by research_home(): this plugin's own skills/ when research/ is in it,
else a sibling plugin named research. A copy of dev-flow alone has neither, and every check
here skips with that reason (kit-dev's standalone check runs it that way).

Standard library only. Run from plugins/dev-flow:

    python3 -m unittest discover -s tests -q
"""
import re
import shutil
import tempfile
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
SKILLS = PLUGIN / "skills"
FAMILY_SKILLS = ("research", "research-deep", "research-refine", "research-prune",
                 "chain-of-verification")
FAMILY_AGENTS = ("research-lane", "research-lane-deep", "research-verifier")
NO_HOME = ("the research family is in neither this plugin's skills/ nor a sibling "
           "research plugin (a standalone copy of dev-flow)")


def research_home(plugin):
    """(the skills dir holding research/, None) or (None, the skip reason)."""
    for skills in (plugin / "skills", plugin.parent / "research" / "skills"):
        if (skills / "research" / "SKILL.md").is_file():
            return skills, None
    return None, NO_HOME


RESEARCH_SKILLS, SKIP = research_home(PLUGIN)
if RESEARCH_SKILLS is not None:
    RESEARCH = RESEARCH_SKILLS / "research"
    REFS = RESEARCH / "references"
    ROUTING = REFS / "intensity-and-routing.md"
    RESEARCH_AGENTS = RESEARCH_SKILLS.parent / "agents"
    COVE = RESEARCH_SKILLS / "chain-of-verification" / "SKILL.md"

BRIEF = SKILLS / "dev-cycle" / "references" / "agent-brief.md"
SCOUT = PLUGIN / "agents" / "scout.md"
DEEP = SKILLS / "deep-investigation"
GATE = DEEP / "references" / "security-gate.md"
START = "Never send a signal"


def text(path):
    return path.read_text(encoding="utf-8")


def flat(s):
    """Whitespace runs folded to one space, so a rule wrapped across lines still matches."""
    return re.sub(r"\s+", " ", s)


def h2(body, heading):
    """The body of the `## <heading>` section, up to the next `## ` heading."""
    m = re.search(r"^## " + re.escape(heading) + r"\n(.*?)(?=^## |\Z)", body, re.S | re.M)
    return m.group(1) if m else None


def stop_rule(path):
    """The one list item that starts with START, continuation lines joined, whitespace
    collapsed (test_stop_rule.py's reader)."""
    lines = text(path).splitlines()
    found = []
    for i, line in enumerate(lines):
        m = re.match(r"^(\s*)(- |\d+\. )" + re.escape(START), line)
        if not m:
            continue
        indent = len(m.group(1)) + len(m.group(2))
        item = [line[indent:]]
        for nxt in lines[i + 1:]:
            if not nxt.strip() or not nxt.startswith(" " * indent):
                break
            item.append(nxt.strip())
        found.append(" ".join(" ".join(item).split()))
    if len(found) != 1:
        raise AssertionError(f"{path.name}: {len(found)} stop-rule bullets, want 1")
    return found[0]


def pin(path):
    """(model, effort) from an agent file's frontmatter."""
    head = text(path).split("\n---\n", 1)[0]
    get = lambda k: (re.search(r"(?m)^%s: (\S+)$" % k, head) or [None, None])[1]
    return get("model"), get("effort")


def headings(path):
    """Every anchor a '§' can name in a file, fenced blocks left out: a markdown heading's
    text, or a paragraph's bold lead (`**Creating staging.** When you ...`)."""
    out, fenced = [], False
    for line in text(path).splitlines():
        if line.startswith("```"):
            fenced = not fenced
        elif not fenced:
            m = re.match(r"#{1,6} (.+?)\s*$", line) or re.match(r"\*\*([^*]+?)\.?\*\*", line)
            if m:
                out.append(m.group(1))
    return out


def resolves(heading_text, files):
    """True when the text after a '§ ' starts with a heading of one of files, ending at a
    word boundary (so '§ Profiles routes these lanes' resolves to '## Profiles')."""
    for f in files:
        for h in headings(f):
            if heading_text.startswith(h) and not re.match(r"\w", heading_text[len(h):]):
                return True
    return False


ANCHOR = re.compile(r"the `research` skill's(?: `(references/[\w.-]+)`)?")
LIST = re.compile(r"^ sections named here \(((?:§ [^,)]+(?:, )?)+)\)")


def anchors(body):
    """(file or None, [heading texts]) for each reference into the research skill in flat
    text: a file, then ' § <heading>' or ' sections named here (§ A, § B)'."""
    out = []
    for m in ANCHOR.finditer(body):
        rest = body[m.end():]
        if rest.startswith(" § "):
            heads = [rest[3:3 + 80]]
        else:
            lm = LIST.match(rest)
            heads = [h.strip()[2:] for h in lm.group(1).split(", ")] if lm else []
        out.append((m.group(1), heads))
    return out


def dev_flow_files():
    """dev-flow's *.md outside the research family."""
    for p in sorted(PLUGIN.rglob("*.md")):
        rel = p.relative_to(PLUGIN).parts
        if rel[0] == "skills" and rel[1] in FAMILY_SKILLS:
            continue
        if rel[0] == "agents" and p.stem in FAMILY_AGENTS:
            continue
        yield p


class TestResolver(unittest.TestCase):
    """research_home finds the family in this plugin or a sibling, else says why it skips."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.plugin = self.tmp / "plugins" / "dev-flow"
        (self.plugin / "skills").mkdir(parents=True)

    def plant(self, skills):
        (skills / "research").mkdir(parents=True)
        (skills / "research" / "SKILL.md").write_text("x\n")

    def test_own_skills_first(self):
        self.plant(self.plugin / "skills")
        self.plant(self.tmp / "plugins" / "research" / "skills")
        self.assertEqual(research_home(self.plugin), (self.plugin / "skills", None))

    def test_sibling_plugin(self):
        self.plant(self.tmp / "plugins" / "research" / "skills")
        self.assertEqual(research_home(self.plugin),
                         (self.tmp / "plugins" / "research" / "skills", None))

    def test_standalone_copy_skips_with_the_reason(self):
        (self.plugin / "skills" / "research").mkdir()  # a dir with no SKILL.md is not it
        home, reason = research_home(self.plugin)
        self.assertIsNone(home)
        self.assertEqual(reason, NO_HOME)
        self.assertIn("standalone copy of dev-flow", reason)

    def test_anchor_reader(self):
        body = flat("the `research` skill's `references/run-record.md` sections named here "
                    "(§ The scan floor, § The sheet check); and the `research` skill's "
                    "`references/a.md` § Profiles routes; the `research` skill's § Recording")
        got = anchors(body)
        self.assertEqual(got[0], ("references/run-record.md",
                                  ["The scan floor", "The sheet check"]))
        self.assertEqual(got[1][0], "references/a.md")
        self.assertTrue(got[1][1][0].startswith("Profiles routes;"))
        self.assertEqual(got[2], (None, ["Recording"]))
        self.assertEqual(len(got), 3)

    def test_heading_resolution(self):
        f = self.tmp / "r.md"
        f.write_text("# Top\n\n## Profiles\n\n**Creating staging.** When ...\n\n"
                     "```\n## Fenced\n```\n")
        self.assertTrue(resolves("Profiles routes these lanes", [f]))
        self.assertTrue(resolves("Creating staging. Then launch", [f]))
        self.assertFalse(resolves("Profilesx", [f]))
        self.assertFalse(resolves("Fenced", [f]))
        self.assertFalse(resolves("The sheet check", [f]))


@unittest.skipIf(RESEARCH_SKILLS is None, SKIP)
class TestStopRule(unittest.TestCase):
    def test_family_home_equals_the_brief(self):
        self.assertEqual(stop_rule(RESEARCH_AGENTS / "research-lane.md"), stop_rule(BRIEF))

    def test_home_paragraph_names_the_family_copies(self):
        body = text(BRIEF)
        self.assertIn("**The stop rule's home.**", body)
        for name in ("`research-lane`", "`research-lane-deep`", "`research-verifier`"):
            self.assertIn(name, body)


# test_store_lookup.py's copy checks, run on the research family's copy.
LOOP_LOCATIONS = ['"$MAIN/.work-items"', '"$MAIN/.claude-sandbox/work"', '"$MAIN/.work"']
PROSE_LOCATIONS = ["`.work-items/`", "`.claude-sandbox/work/`", "`.work/`"]
NEW, OLD = "WORK_ITEMS_ROOT", "WI_ROOT"
ASSIGN = re.compile(r"(?<![A-Za-z0-9_])(WORK_ITEMS_ROOT|WI_ROOT)=")
IGNORE_TEST = 'check-ignore -q "$WORK_ITEMS_ROOT"'
HAND_COMMIT = 'git -C "$WORK_ITEMS_ROOT" commit'


def subsection(path, heading):
    """The text from `heading` to the next heading of the same or a higher level."""
    lines = text(path).split("\n")
    level = len(heading) - len(heading.lstrip("#"))
    start = lines.index(heading)
    out, fenced = [], False
    for line in lines[start + 1:]:
        if line.startswith("```"):
            fenced = not fenced
        if not fenced and re.match(r"#{1,%d} " % level, line):
            break
        out.append(line)
    return "\n".join(out)


def family_md():
    out = sorted(RESEARCH_AGENTS.glob("research-*.md"))
    for name in FAMILY_SKILLS:
        out += sorted((RESEARCH_SKILLS / name).rglob("*.md"))
    return out


@unittest.skipIf(RESEARCH_SKILLS is None, SKIP)
class TestStoreLookup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sec = subsection(ROUTING, "### Resolving the store")
        cls.loops = [l for l in cls.sec.split("\n") if l.startswith("for d in ")]

    def test_one_loop(self):
        self.assertEqual(len(self.loops), 1)

    def test_loop_names_the_three_locations_in_order(self):
        found = re.findall(r'"\$MAIN/[^"]*"', self.loops[0].split(";")[0])
        self.assertEqual(found, LOOP_LOCATIONS)

    def test_prose_names_the_three_locations_in_order(self):
        prose = self.sec.split("```")[0]
        at = [prose.find(n) for n in PROSE_LOCATIONS]
        self.assertTrue(all(i >= 0 for i in at) and at == sorted(at), at)

    def test_loop_exports_both_names(self):
        self.assertIn(f'export {NEW}="$d" {OLD}="$d"', self.loops[0])

    def test_research_item_says_wi_commits_an_own_store(self):
        """d1e9 F5: the research run never commits its item, and says that in
        a store that is its own repo `wi` commits each write itself."""
        self.assertIn("The run never commits it; in a store that is its own "
                      "repo, `wi` commits each write itself.", flat(text(ROUTING)))

    def test_every_family_assignment_sets_both_names(self):
        bad, seen = [], 0
        for path in family_md():
            for n, line in enumerate(text(path).split("\n"), 1):
                found = set(ASSIGN.findall(line))
                seen += bool(found)
                if found and found != {NEW, OLD}:
                    bad.append(f"{path.name}:{n}: {line.strip()}")
        self.assertEqual(bad, [])
        self.assertGreaterEqual(seen, 1)  # the loop at least: guards the scan

    def test_no_hand_commit_of_the_store_in_the_family(self):
        for path in family_md():
            body = flat(text(path))
            with self.subTest(path=path.name):
                self.assertNotIn(IGNORE_TEST, body)
                self.assertNotIn(HAND_COMMIT, body)


@unittest.skipIf(RESEARCH_SKILLS is None, SKIP)
class TestScout(unittest.TestCase):
    NEEDED = {"WebSearch", "WebFetch", "Read", "Glob", "Grep"}

    def test_profiles_scout_row_is_scouts_pin(self):
        rows = h2(text(ROUTING), "Profiles")
        self.assertIsNotNone(rows)
        row = next((l for l in rows.splitlines() if l.startswith("| `scout` |")), None)
        self.assertIsNotNone(row, "research § Profiles has no scout row")
        model, effort = pin(SCOUT)
        self.assertRegex(row.split("|")[2].strip(), r"^%s / %s\b" % (model, effort))

    def test_scout_keeps_coves_tools(self):
        """While chain-of-verification dispatches scout, scout keeps the tools its codebase
        and web checks use: no tools key (every tool), or one that includes them all."""
        if "dev-flow:scout" not in text(COVE):
            self.skipTest("chain-of-verification does not dispatch scout")
        head = text(SCOUT).split("\n---\n", 1)[0]
        m = re.search(r"(?m)^tools: (.*)$", head)
        if not m:
            return
        self.assertLessEqual(self.NEEDED, {t.strip() for t in m.group(1).split(",")})


@unittest.skipIf(RESEARCH_SKILLS is None, SKIP)
class TestAnchors(unittest.TestCase):
    """Every reference into the research skill from a dev-flow file names a file and a
    heading that exist."""

    # The sections dev-flow's files are known to name; each must be seen and resolve, which
    # also guards the reader against matching nothing.
    KNOWN = {"Profiles", "The scan floor", "The sheet check", "Creating staging",
             "The work item", "Closing", "Recording", "Resolving the store",
             "Ledger entries", "The ignore check", "Putting an ask to the operator",
             "The toolkit gate", "The verifier prompt", "Stored names"}

    def test_every_anchor_resolves(self):
        all_refs = [RESEARCH / "SKILL.md", *sorted(REFS.glob("*.md"))]
        bad, seen = [], set()
        for path in dev_flow_files():
            for ref, heads in anchors(flat(text(path))):
                target = RESEARCH / ref if ref else None
                where = f"{path.relative_to(PLUGIN)}: {ref or '(skill)'}"
                if target is not None and not target.is_file():
                    bad.append(f"{where}: no such file")
                    continue
                for h in heads:
                    if resolves(h, [target] if target else all_refs):
                        seen |= {k for k in self.KNOWN
                                 if h.startswith(k) and not re.match(r"\w", h[len(k):])}
                    else:
                        bad.append(f"{where} § {h[:40]}: no such heading")
        self.assertEqual(bad, [], "\n" + "\n".join(bad))
        self.assertEqual(self.KNOWN - seen, set(), "named sections not seen")


@unittest.skipIf(RESEARCH_SKILLS is None, SKIP)
class TestDeepInvestigation(unittest.TestCase):
    def test_skill_points_to_the_ask_section(self):
        self.assertIn("§ Putting an ask to the operator", flat(text(DEEP / "SKILL.md")))

    def test_gate_runs_the_sheet_check(self):
        gate = flat(text(GATE))
        self.assertIn("§ The sheet check", gate)
        self.assertIn("`TALLY` counts", gate)

    def test_interim_routing_row_is_gone(self):
        body = text(ROUTING)
        self.assertNotIn("1ffd", body)
        outside = h2(body, "Dispatches outside the profiles")
        self.assertIsNotNone(outside)
        self.assertNotRegex(outside, r"(?m)^\| `deep-investigation` lanes")

    def test_profiles_row_names_deep_investigation(self):
        profiles = h2(text(ROUTING), "Profiles")
        row = next(l for l in profiles.splitlines() if l.startswith("| `research-lane` |"))
        self.assertIn("`deep-investigation`", row)
        self.assertNotIn("until", row)
        verifier = next(l for l in profiles.splitlines() if l.startswith("| `research-verifier` |"))
        self.assertIn("`deep-investigation`", verifier)


if __name__ == "__main__":
    unittest.main()
