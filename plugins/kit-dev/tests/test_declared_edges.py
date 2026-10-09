"""Every cross-plugin reference is declared (README principle 4).

A plugin's files reference another plugin when they name one of its skills, its CLIs or a
data path it owns. Each such reference must be declared in two places: the source plugin's
plugin.json description names the target plugin, and the source's README catalog "Depends
on" cell lists it as a top-level entry (a backticked name outside any parenthesis). A
reference with neither, or with only one, fails here, naming the file and line.

What counts as a reference to plugin Q, from a file of plugin P (P != Q):

- a skill: `Q:<skill>`, a backticked `<skill>` or `/<skill>`, a bare /<skill> command, or
  "<skill> skill", for each skill directory under plugins/Q/skills/ (a name P also uses for
  itself is not counted);
- a CLI: the file name of a script under plugins/Q/skills/*/scripts/, or the CLIS command
  names below (`wi`);
- a data path: plugins/data/Q-..., a path into the repo's plugins/Q/, a config-dir path in
  OWNED_PATHS (written a/b, as joined string parts "a", "b", or as a pathlib / "a" / "b")
  that P does not co-own, or, in a .py file outside tests/, a quoted "Q" or "Q-" (a path
  built in code).

A descriptive mention (an example, a credit, a test fixture standing in for another plugin)
is not a dependency; ALLOWED lists those, each with its reason, keyed by file, target and a
substring of the line, so a new reference elsewhere in the same file still fails. An entry
that no longer matches anything fails too, so the lists only shrink.

Runs only in the source repo (it reads README.md and every plugin); in an isolated copy of
kit-dev it skips. Standard library only. Run from plugins/kit-dev:

    python3 -m unittest discover -s tests -q
"""
import json
import re
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
REPO = KIT.parent.parent
PLUGINS = REPO / "plugins"
README = REPO / "README.md"
IN_REPO = README.is_file() and (REPO / ".claude-plugin" / "marketplace.json").is_file()

# Command names a plugin ships beyond its script file names.
CLIS = {"work-items": ["wi"]}

# Config-dir paths (under ${CLAUDE_CONFIG_DIR:-~/.claude}) each plugin writes and owns. The
# sensor record has two writers, the hub's tee and statusline's own sensor, so either
# declared covers it.
OWNED_PATHS = {
    "statusline-hub": ["statusline-hub/hooks.d", "statusline-hub/segments", "statusline/sensor"],
    "statusline": ["statusline/sensor"],
    "context-guard": ["claude-kit/context-gate", "claude-kit/ledger", "claude-kit/handoff"],
    "dev-flow": ["claude-kit/librarian"],
}

# (source file relative to plugins/, target plugin, a substring of the referencing line)
# -> why it is not a dependency. Descriptive mentions only. The substring pins the entry to
# its line, so a new reference to the same target elsewhere in the file still fails. An
# undeclared real dependency belongs in the plugin's description and catalog cell, not
# here; see UNDECLARED below for the ones still open.
ALLOWED = {
    # context-guard: dev-flow skill names as examples of a resume command a manifest may
    # carry, and as fixtures for that field; context-guard runs the same without dev-flow
    # (spike 72ef CG-8).
    ("context-guard/skills/checkpoint/references/handoff-format.md", "dev-flow",
     "(e.g. `/dev-flow:librarian-mode start`)"): "example resume command",
    ("context-guard/skills/checkpoint/references/handoff-format.md", "dev-flow",
     "(e.g. `/dev-flow:implement 8cc2-turn-gate-port`)"): "example resume command",
    ("context-guard/skills/checkpoint/references/operator-playbook.md", "dev-flow",
     "/dev-flow:librarian-mode start — Read (the Read tool)"): "example resume command",
    ("context-guard/skills/checkpoint/references/design-rationale.md", "dev-flow",
     "investigate skill on every run"): "a past finding about one skill's reads, history",
    ("context-guard/hooks/tests/test_rehydrate.py", "dev-flow",
     'NS = "/dev-flow:implement 8cc2-turn-gate-port"'): "fixture skill name",
    ("context-guard/hooks/tests/test_rehydrate.py", "dev-flow",
     "mode_skill: /dev-flow:librarian-mode start"): "fixture skill name",
    ("context-guard/hooks/tests/test_rehydrate.py", "dev-flow",
     "re-enter it first with `/dev-flow:librarian-mode start`"): "fixture skill name",
    ("context-guard/hooks/tests/test_window_mirror.py", "dev-flow",
     'self.warn("/dev-flow:librarian-mode")'): "fixture skill name",
    # context-guard: the bare-/checkpoint scan's list of files it must see (item aebc).
    ("context-guard/hooks/tests/test_checkpoint_namespaced.py", "dev-flow",
     '"plugins/dev-flow/skills/librarian-mode/SKILL.md",'):
        "a repo scan's list of files it guards, not a use",
    ("context-guard/hooks/tests/test_checkpoint_namespaced.py", "statusline",
     '"plugins/statusline/settings.json",'):
        "a repo scan's list of files it guards, not a use",
    # kit-dev: install advice and a who-calls credit, needed by nothing (72ef KD-4, KD-6).
    ("kit-dev/skills/new-project-from-template/SKILL.md", "work-items",
     "usually means `dev-flow`, `work-items`, `sandbox`"): "install advice",
    ("kit-dev/skills/new-project-from-template/SKILL.md", "sandbox",
     "usually means `dev-flow`, `work-items`, `sandbox`"): "install advice",
    ("kit-dev/skills/update-kit/SKILL.md", "dev-flow",
     "the retrospective step of `investigate` / `implement`"): "names who calls update-kit",
    # kit-dev: update-kit's map of the claude-plugins checkout it syncs (an external repo to
    # kit-dev, declared as such), not a use of the plugins it lists (72ef KD-5).
    ("kit-dev/skills/update-kit/references/repo-map.md", "context-guard",
     "checkpoint/scripts/  (context_forensics.py"): "repo map",
    ("kit-dev/skills/update-kit/references/repo-map.md", "context-guard",
     "usage-report/scripts/ (usage_report.py"): "repo map",
    ("kit-dev/skills/update-kit/references/repo-map.md", "dev-flow",
     "research/scripts/ (tool-preflight.sh"): "repo map",
    ("kit-dev/skills/update-kit/references/repo-map.md", "dev-flow",
     "librarian-mode/scripts/ (quota_budget.py"): "repo map",
    ("kit-dev/skills/update-kit/references/repo-map.md", "statusline-hub",
     "install-statusline-hub/scripts/ (install_hub.py"): "repo map",
    ("kit-dev/skills/update-kit/references/repo-map.md", "work-items",
     "work-items/    (wi CLI incl. `wi estate`"): "repo map",
    ("kit-dev/skills/update-kit/references/repo-map.md", "work-items",
     "work-items/scripts/ (wi.py, the wi CLI)"): "repo map",
    ("kit-dev/skills/update-kit/references/repo-map.md", "work-items",
     "work-review/   (the on-demand cross-repo review, written from `wi estate`)"): "repo map",
    # work-items: a credit to the step that closes items on landing (72ef WI-5); the other
    # provider of the interface and its grooming skill, declared from ralph's side (WI-1);
    # and `implement` as an item stage name, not the skill.
    ("work-items/skills/work-items/SKILL.md", "dev-flow", "`implement` Step 10a"): "credit",
    ("work-items/skills/work-items/references/provider-interface.md", "ralph",
     "(the `backlog-yaml` skill, canonical"): "names the other provider",
    ("work-items/skills/work-items/references/provider-interface.md", "ralph",
     "closure belongs to grooming (`/backlog-grooming`)"): "names the other provider's closer",
    ("work-items/skills/work-items/references/provider-interface.md", "ralph",
     "`/backlog-grooming` closes"): "names the other provider's closer",
    ("work-items/skills/work-items/references/provider-interface.md", "dev-flow",
     "(with optional stage `implement` / `review`"): "a stage name",
}

# (source file relative to plugins/, target plugin, a substring of the referencing line)
# -> the follow-up that declares it. Real dependencies that are not yet declared: each is a
# finding for the declaration sweep (spike 72ef F7) or factor-analysis's declare-and-degrade
# (F3), which remove their entries as they land. Listed so the lint passes meanwhile.
UNDECLARED = {
    # context-guard's moved notice reads statusline's data dir to stay quiet when it is
    # installed (72ef CG-3): named in plugin.json ("installing statusline brings it"), not a
    # catalog entry. The code line that builds the path, and its docstring.
    ("context-guard/hooks/rehydrate.py", "statusline", '_data_dirs(cfg, "statusline-")'):
        "F7 (CG-3)",
    ("context-guard/hooks/rehydrate.py", "statusline", "any plugins/data/statusline-<mkt>"):
        "F7 (CG-3)",
    # The research quota read points at statusline's install-statusline references for the
    # safe_sid rules (72ef DF-7); F7 moves the pointer to the hub's hook-contract.md.
    ("dev-flow/skills/research/references/intensity-and-routing.md", "statusline",
     "`safe_sid` rules are in `statusline`'s `install-statusline` references"): "F7 (DF-7)",
    # factor-analysis's Step 7 files work items and writes an investigate-format series
    # (72ef KD-2, KD-3). F3 declares both and adds the fallbacks.
    ("kit-dev/skills/factor-analysis/SKILL.md", "work-items", "(`work-items` skill)"):
        "F3 (KD-2)",
    ("kit-dev/skills/factor-analysis/SKILL.md", "dev-flow", "migration is planned by `implement`"):
        "F3 (KD-3)",
    ("kit-dev/skills/factor-analysis/SKILL.md", "dev-flow", "(`investigate` format)"):
        "F3 (KD-3)",
    ("kit-dev/skills/factor-analysis/SKILL.md", "dev-flow", "for `implement` to consume"):
        "F3 (KD-3)",
    # The hub treats context-guard's deprecated footer copy as the footer's entry (72ef
    # SH-3): owner.py names that copy's data-dir home, and the tests fingerprint its path.
    # F7 declares it, or it goes with the copy (a95a).
    ("statusline-hub/hooks/owner.py", "context-guard",
     'FOOTER_HOMES = (STATUSLINE, "context-guard"'): "F7 (SH-3)",
    ("statusline-hub/hooks/tests/test_owner.py", "context-guard",
     "/plugins/data/context-guard-"): "F7 (SH-3)",
    # work-items points at the sandbox skill for worktree-mode details (72ef WI-4); F7
    # inlines or declares.
    ("work-items/skills/work-items/SKILL.md", "sandbox", "the sandbox skill's worktree-mode"):
        "F7 (WI-4)",
}

EXCUSES = {**ALLOWED, **UNDECLARED}

TEXT_SUFFIXES = {".md", ".py", ".json", ".sh", ".js", ".html", ".txt", ".yaml", ".yml", ""}


def plugin_names():
    return sorted(p.name for p in PLUGINS.iterdir()
                  if (p / ".claude-plugin" / "plugin.json").is_file())


def description(name):
    data = json.loads((PLUGINS / name / ".claude-plugin" / "plugin.json").read_text("utf-8"))
    return data.get("description", "")


def name_re(name):
    """A plugin or skill name as a whole word: no letter, digit, '_' or '-' either side."""
    return re.compile(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])")


def catalog_cells():
    """Plugin name -> its catalog "Depends on" cell, from README.md § Catalog."""
    cells = {}
    for line in README.read_text("utf-8").splitlines():
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) == 4:
            m = re.fullmatch(r"`([a-z0-9-]+)`", cols[1])
            if m:
                cells[m.group(1)] = cols[3]
    return cells


def top_level_names(cell):
    """Backticked names at parenthesis depth 0 in a catalog cell: its declared entries."""
    names, depth, i = set(), 0, 0
    while i < len(cell):
        ch = cell[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif ch == "`":
            j = cell.find("`", i + 1)
            if j < 0:
                break
            if depth == 0:
                names.add(cell[i + 1:j])
            i = j
        i += 1
    return names


def skills(name):
    d = PLUGINS / name / "skills"
    return sorted(p.name for p in d.iterdir() if p.is_dir()) if d.is_dir() else []


def scripts(name):
    return sorted({p.name for p in (PLUGINS / name / "skills").glob("*/scripts/*")
                   if p.is_file() and p.suffix in (".py", ".sh", ".js")})


def path_re(path):
    """A config-dir path written a/b, as joined parts "a", "b", or as pathlib / "a" / "b"."""
    parts = path.split("/")
    q = r"""["']"""
    slash = r"(?<![\w-])" + "/".join(map(re.escape, parts)) + r"(?![\w-])"
    joined = q + (q + r"\s*,\s*" + q).join(map(re.escape, parts)) + q
    pathlib = r"/\s*" + q + (q + r"\s*/\s*" + q).join(map(re.escape, parts)) + q
    return re.compile(slash + "|" + joined + "|" + pathlib)


def markers(target, source, py=False):
    """(kind, regex) pairs that mark a reference from `source`'s files to `target`; py adds
    the marker only Python source carries (a quoted plugin name that builds a path)."""
    own = {source, *skills(source)}
    out = []
    for s in skills(target):
        out.append(("skill", re.compile(r"(?<![\w-])" + re.escape(target) + ":" + re.escape(s)
                                        + r"(?![\w-])")))
        if s not in own:
            out.append(("skill", re.compile("`/?" + re.escape(s) + "`")))
            out.append(("skill", re.compile(r"(?<![\w:/-])/" + re.escape(s) + r"(?![\w-])")))
            out.append(("skill", re.compile(r"(?<![\w-])" + re.escape(s) + r" skill\b")))
    for f in scripts(target):
        out.append(("cli", name_re(f)))
    for c in CLIS.get(target, []):
        out.append(("cli", re.compile("`" + re.escape(c) + r"[` ]|(?<![\w$./-])" + re.escape(c)
                                      + r" (?=[a-z][a-z-]+\b)")))
    out.append(("data", re.compile(r"plugins/data/" + re.escape(target) + r"-")))
    out.append(("data", re.compile(r"(?<![\w-])plugins/" + re.escape(target) + r"/")))
    for p in OWNED_PATHS.get(target, []):
        if p not in OWNED_PATHS.get(source, []):  # a path the source co-owns is its own
            out.append(("data", path_re(p)))
    if py:
        out.append(("data", re.compile(r"""["']""" + re.escape(target) + r"""-?["']""")))
    return out


def owners():
    """Data paths with more than one owner: a reference is declared if any owner is."""
    by_path = {}
    for name, paths in OWNED_PATHS.items():
        for p in paths:
            by_path.setdefault(p, set()).add(name)
    return by_path


def files(name):
    for p in sorted((PLUGINS / name).rglob("*")):
        # This file names every plugin's paths and commands as its own data; not edges.
        if p.resolve() == Path(__file__).resolve():
            continue
        if p.is_file() and "__pycache__" not in p.parts and p.suffix in TEXT_SUFFIXES:
            yield p


def is_code(rel):
    """The quoted-name marker is for shipped code only: tests use plugin names as fixture
    names (a segment called "sandbox", install-record keys), not as paths."""
    return rel.endswith(".py") and "tests" not in rel.split("/")


def tables(source, names):
    """Per is_code: the (target, kind, regex) markers for every other plugin."""
    return {py: [(t, k, rx) for t in names if t != source for k, rx in markers(t, source, py)]
            for py in (False, True)}


def line_refs(source, rel, n, line, table):
    """One finding per target on the line (the first marker kind that hits), so a line
    naming a target twice, or by two markers, is reported once."""
    out = {}
    for target, kind, rx in table:
        if target not in out and rx.search(line):
            out[target] = (source, target, rel, n, kind, line.strip())
    return list(out.values())


def references():
    """Every (source, target, rel, line_no, kind, line) cross-plugin reference."""
    names = plugin_names()
    found = []
    for source in names:
        by_code = tables(source, names)
        for path in files(source):
            try:
                text = path.read_text("utf-8")
            except UnicodeDecodeError:
                continue
            rel = path.relative_to(PLUGINS).as_posix()
            table = by_code[is_code(rel)]
            for n, line in enumerate(text.splitlines(), 1):
                found.extend(line_refs(source, rel, n, line, table))
    return found


def is_declared(target, desc, cell):
    """(named in the plugin.json description, a top-level entry of the catalog cell)."""
    return bool(name_re(target).search(desc)), target in top_level_names(cell)


def declared(source, target, desc_cache, cells):
    if source not in desc_cache:
        desc_cache[source] = description(source)
    return is_declared(target, desc_cache[source], cells.get(source, ""))


def excused(finding, table):
    """The keys of table, (file, target, line substring), that excuse this finding."""
    _, target, rel, _, _, line, _ = finding
    return [k for k in table if k[0] == rel and k[1] == target and k[2] in line]


def undeclared(refs=None):
    """(source, target, rel, line_no, kind, line, where-missing) for each undeclared ref
    (of refs, or of every reference in the repo)."""
    refs = references() if refs is None else refs
    shared = owners()
    cells, cache, out = catalog_cells(), {}, []
    for source, target, rel, n, kind, line in refs:
        # A shared data path is declared when any of its owners is.
        alts = {target}
        for p, names in shared.items():
            if target in names and path_re(p).search(line):
                alts |= names - {source}
        missing = []
        for t in alts:
            in_desc, in_cell = declared(source, t, cache, cells)
            if in_desc and in_cell:
                missing = []
                break
            missing.append(f"{t}: " + ", ".join(
                w for w, ok in (("plugin.json", in_desc), ("catalog", in_cell)) if not ok))
        if missing:
            out.append((source, target, rel, n, kind, line, "; ".join(missing)))
    return out


@unittest.skipUnless(IN_REPO, "not in the source repo: no README catalog or sibling plugins")
class DeclaredEdges(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.found = undeclared()

    def test_every_plugin_has_a_catalog_cell(self):
        cells = catalog_cells()
        for name in plugin_names():
            self.assertIn(name, cells, f"{name} has no README catalog row")

    def test_every_reference_is_declared(self):
        bad = [f for f in self.found if not excused(f, EXCUSES)]
        self.assertEqual(bad, [], "undeclared cross-plugin references:\n" + "\n".join(
            f"  plugins/{rel}:{n} -> {t} ({kind}; missing in {miss}): {line[:120]}"
            for _, t, rel, n, kind, line, miss in bad))

    def test_every_excuse_still_matches(self):
        live = {k for f in self.found for k in excused(f, EXCUSES)}
        for key in EXCUSES:
            with self.subTest(key=key):
                self.assertIn(key, live, f"{key} matches nothing now; remove its entry")

    # The probes write from sandbox, which declares no plugin edge (only the external
    # claude-sandbox repo), so a later declaration elsewhere cannot make them pass vacuously.
    PROBE = "sandbox/skills/sandbox/SKILL.md"
    PROBE_EXCUSES = {**EXCUSES, (PROBE, "dev-flow", "an excused `/dev-cycle` line"): "probe"}

    def failing(self, rel, line, table=None):
        """The targets a new line in plugins/<rel> would fail the lint for."""
        source = rel.split("/", 1)[0]
        refs = line_refs(source, rel, 0, line, tables(source, plugin_names())[is_code(rel)])
        table = EXCUSES if table is None else table
        return sorted({f[1] for f in undeclared(refs) if not excused(f, table)})

    def test_the_probe_plugin_declares_no_edge(self):
        cells, cache = catalog_cells(), {}
        for target in plugin_names():
            if target != "sandbox":
                self.assertEqual(declared("sandbox", target, cache, cells), (False, False),
                                 f"sandbox now declares {target}; move the probes")

    def test_probe_a_slash_skill_fails(self):
        self.assertEqual(self.failing(self.PROBE, "then run `/dev-cycle` on it"), ["dev-flow"])
        self.assertEqual(self.failing(self.PROBE, "then run /dev-cycle on it"), ["dev-flow"])

    def test_probe_a_new_line_in_an_excused_file_fails(self):
        # The file has an excused dev-flow line; it does not cover a new one.
        self.assertEqual(self.failing(self.PROBE, "then run `/dev-flow:dev-cycle` on it",
                                      self.PROBE_EXCUSES), ["dev-flow"])

    def test_probe_the_excused_line_itself_passes(self):
        self.assertEqual(self.failing(self.PROBE, "see an excused `/dev-cycle` line here",
                                      self.PROBE_EXCUSES), [])

    def test_probe_a_path_built_in_code_fails(self):
        self.assertEqual(self.failing("sandbox/hooks/x.py", 'HOMES = ("work-items-",)'),
                         ["work-items"])
        self.assertEqual(self.failing("sandbox/hooks/tests/test_x.py",
                                      'HOMES = ("work-items-",)'), [])

    def test_findings_are_unique_by_file_line_and_target(self):
        keys = [(f[2], f[3], f[1]) for f in self.found]
        self.assertEqual(len(keys), len(set(keys)))


class Markers(unittest.TestCase):
    """Marker shapes, on synthetic lines; needs only the plugin dirs, no README."""

    def setUp(self):
        if not PLUGINS.is_dir() or not (PLUGINS / "dev-flow" / "skills").is_dir():
            self.skipTest("not in the source repo: no sibling plugins")

    def found(self, target, line, source="kit-dev", py=False):
        return any(rx.search(line) for _, rx in markers(target, source, py))

    def test_skill_cli_and_data_shapes(self):
        self.assertTrue(self.found("work-items", "then run `wi add` for each"))
        self.assertTrue(self.found("dev-flow", "hand it to `/dev-flow:dev-cycle`"))
        self.assertTrue(self.found("dev-flow", "then run `/dev-cycle` on it"))
        self.assertTrue(self.found("dev-flow", "then run /dev-cycle on it"))
        self.assertTrue(self.found("context-guard", "read ~/.claude/claude-kit/context-gate/x"))
        self.assertTrue(self.found("statusline-hub", 'cfg / "statusline" / "sensor" / sid'))
        self.assertTrue(self.found("context-guard", 'HOMES = ("context-guard",)', py=True))
        self.assertFalse(self.found("context-guard", 'HOMES = ("context-guard",)'))
        self.assertFalse(self.found("work-items", "a wide, wild idea"))
        self.assertFalse(self.found("dev-flow", "see docs/dev-cycle and x:/dev-cycle"))

    def test_a_co_owned_path_is_not_a_reference(self):
        # statusline-hub writes statusline/sensor itself; naming it is not using statusline.
        line = 'join(base, "statusline", "sensor")'
        self.assertFalse(self.found("statusline", line, source="statusline-hub"))
        self.assertTrue(self.found("statusline", line, source="dev-flow"))


class Parsing(unittest.TestCase):
    def test_top_level_names_skip_parenthesised_mentions(self):
        cell = ("`a` (soft; installing `b` brings it), `c` (hard; x (`d`) y), "
                "claude-sandbox repo (external)")
        self.assertEqual(top_level_names(cell), {"a", "c"})

    def test_is_declared_needs_both_places(self):
        desc = "Tools (soft dependency: alpha, for x; installing beta brings it)."
        cell = "`alpha` (soft; x; installing `beta` brings it), gamma repo (external)"
        self.assertEqual(is_declared("alpha", desc, cell), (True, True))
        self.assertEqual(is_declared("beta", desc, cell), (True, False))
        self.assertEqual(is_declared("gamma", desc, cell), (False, False))
        self.assertEqual(is_declared("alph", desc, cell), (False, False))

    def test_excused_needs_file_target_and_line(self):
        table = {("a/SKILL.md", "q", "run `x`"): "why"}
        f = lambda rel, t, line: ("a", t, rel, 1, "skill", line, "")
        self.assertTrue(excused(f("a/SKILL.md", "q", "then run `x` now"), table))
        self.assertFalse(excused(f("a/SKILL.md", "q", "then run `y` now"), table))
        self.assertFalse(excused(f("a/SKILL.md", "r", "then run `x` now"), table))
        self.assertFalse(excused(f("a/other.md", "q", "then run `x` now"), table))

    def test_name_re_is_whole_word(self):
        rx = name_re("statusline")
        self.assertTrue(rx.search("needs statusline, too"))
        self.assertFalse(rx.search("needs statusline-hub"))

    def test_path_re_matches_every_spelling(self):
        rx = path_re("statusline/sensor")
        self.assertTrue(rx.search("CFG/statusline/sensor/<sid>.json"))
        self.assertTrue(rx.search('os.path.join(base, "statusline", "sensor")'))
        self.assertTrue(rx.search('cfg / "statusline" / "sensor" / f"{sid}.json"'))
        self.assertFalse(rx.search("CFG/statusline-hub/sensor"))


if __name__ == "__main__":
    unittest.main()
