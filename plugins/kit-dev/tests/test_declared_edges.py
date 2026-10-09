"""Every cross-plugin reference is declared (README principle 4).

A plugin's files reference another plugin when they name one of its skills, its CLIs or a
data path it owns. Each such reference must be declared in two places: the source plugin's
plugin.json description names the target plugin, and the source's README catalog "Depends
on" cell lists it as a top-level entry (a backticked name outside any parenthesis). A
reference with neither, or with only one, fails here, naming the file and line.

What counts as a reference to plugin Q, from a file of plugin P (P != Q):

- a skill: `Q:<skill>`, a backticked `<skill>`, or "<skill> skill", for each skill
  directory under plugins/Q/skills/ (a name P also uses for itself is not counted);
- a CLI: the file name of a script under plugins/Q/skills/*/scripts/, or the CLIS command
  names below (`wi`);
- a data path: plugins/data/Q-..., a path into the repo's plugins/Q/, or a config-dir path in
  OWNED_PATHS (written a/b or as joined string parts "a", "b").

A descriptive mention (an example, a credit, a test fixture standing in for another plugin)
is not a dependency; ALLOWED lists those, each with its reason, keyed by file and target.
An ALLOWED entry that no longer matches anything fails too, so the list only shrinks.

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

# (source file relative to plugins/, target plugin) -> why it is not a dependency.
# Descriptive mentions only. An undeclared real dependency belongs in the plugin's
# description and catalog cell, not here; see UNDECLARED below for the ones still open.
ALLOWED = {
    # context-guard: dev-flow skill names as examples of a resume command a manifest may
    # carry, and as fixtures for that field; context-guard runs the same without dev-flow
    # (spike 72ef CG-8).
    ("context-guard/skills/checkpoint/references/handoff-format.md", "dev-flow"):
        "example resume commands",
    ("context-guard/skills/checkpoint/references/operator-playbook.md", "dev-flow"):
        "example resume command",
    ("context-guard/skills/checkpoint/references/design-rationale.md", "dev-flow"):
        "a past finding about one skill's reads, history",
    ("context-guard/hooks/tests/test_rehydrate.py", "dev-flow"): "fixture skill names",
    ("context-guard/hooks/tests/test_window_mirror.py", "dev-flow"): "fixture skill names",
    # kit-dev: install advice and who-calls credits, needed by nothing (72ef KD-4, KD-6).
    ("kit-dev/skills/new-project-from-template/SKILL.md", "work-items"): "install advice",
    ("kit-dev/skills/new-project-from-template/SKILL.md", "sandbox"): "install advice",
    ("kit-dev/skills/update-kit/SKILL.md", "dev-flow"): "names who calls update-kit",
    # kit-dev: update-kit's map of the claude-plugins checkout it syncs (an external repo to
    # kit-dev, declared as such), not a use of the plugins it lists (72ef KD-5).
    ("kit-dev/skills/update-kit/references/repo-map.md", "context-guard"): "repo map",
    ("kit-dev/skills/update-kit/references/repo-map.md", "dev-flow"): "repo map",
    ("kit-dev/skills/update-kit/references/repo-map.md", "statusline-hub"): "repo map",
    ("kit-dev/skills/update-kit/references/repo-map.md", "work-items"): "repo map",
    # work-items: a credit to the step that closes items on landing (72ef WI-5); the other
    # provider of the interface, declared from ralph's side (WI-1); and `implement` as an
    # item stage name, not the skill.
    ("work-items/skills/work-items/SKILL.md", "dev-flow"): "credit",
    ("work-items/skills/work-items/references/provider-interface.md", "ralph"):
        "names the other provider",
    ("work-items/skills/work-items/references/provider-interface.md", "dev-flow"):
        "a stage name",
}

# (source file relative to plugins/, target plugin) -> the follow-up that declares it.
# Real dependencies that are not yet declared: each is a finding for the declaration sweep
# (work item declaration-sweep, spike 72ef F7) or factor-analysis's declare-and-degrade
# (F3), which remove their entries as they land. Listed so the lint passes meanwhile.
UNDECLARED = {
    # context-guard's moved notice reads statusline's data dir to stay quiet when it is
    # installed (72ef CG-3): named in plugin.json ("installing statusline brings it"), not a
    # catalog entry. F7.
    ("context-guard/hooks/rehydrate.py", "statusline"): "F7 (CG-3)",
    # The research quota read points at statusline's install-statusline references for the
    # safe_sid rules (72ef DF-7); F7 moves the pointer to the hub's hook-contract.md.
    ("dev-flow/skills/research/references/intensity-and-routing.md", "statusline"):
        "F7 (DF-7)",
    # factor-analysis's Step 7 files work items and writes an investigate-format series
    # (72ef KD-2, KD-3). F3 declares both and adds the fallbacks.
    ("kit-dev/skills/factor-analysis/SKILL.md", "work-items"): "F3 (KD-2)",
    ("kit-dev/skills/factor-analysis/SKILL.md", "dev-flow"): "F3 (KD-3)",
    # The hub treats context-guard's deprecated footer copy as the footer's entry (72ef
    # SH-3); its tests fingerprint that copy's data path. F7 declares it, or it goes with
    # the copy (a95a).
    ("statusline-hub/hooks/tests/test_owner.py", "context-guard"): "F7 (SH-3)",
    # work-items points at the sandbox skill for worktree-mode details (72ef WI-4); F7
    # inlines or declares.
    ("work-items/skills/work-items/SKILL.md", "sandbox"): "F7 (WI-4)",
}

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
    """A config-dir path written a/b or as joined parts "a", "b"."""
    parts = path.split("/")
    slash = r"(?<![\w-])" + "/".join(map(re.escape, parts)) + r"(?![\w-])"
    joined = r"""["']""" + r"""["']\s*,\s*["']""".join(map(re.escape, parts)) + r"""["']"""
    return re.compile(slash + "|" + joined)


def markers(target, source):
    """(kind, regex) pairs that mark a reference from `source`'s files to `target`."""
    own = {source, *skills(source)}
    out = []
    for s in skills(target):
        out.append(("skill", re.compile(r"(?<![\w-])" + re.escape(target) + ":" + re.escape(s)
                                        + r"(?![\w-])")))
        if s not in own:
            out.append(("skill", re.compile("`" + re.escape(s) + "`")))
            out.append(("skill", re.compile(r"(?<![\w-])" + re.escape(s) + r" skill\b")))
    for f in scripts(target):
        out.append(("cli", name_re(f)))
    for c in CLIS.get(target, []):
        out.append(("cli", re.compile("`" + re.escape(c) + r"[` ]|(?<![\w$./-])" + re.escape(c)
                                      + r" (?=[a-z][a-z-]+\b)")))
    out.append(("data", re.compile(r"plugins/data/" + re.escape(target) + r"-")))
    out.append(("data", re.compile(r"(?<![\w-])plugins/" + re.escape(target) + r"/")))
    for p in OWNED_PATHS.get(target, []):
        out.append(("data", path_re(p)))
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


def references():
    """Every (source, target, rel, line_no, kind, line) cross-plugin reference."""
    names = plugin_names()
    shared = owners()
    found = []
    for source in names:
        table = [(t, k, rx) for t in names if t != source for k, rx in markers(t, source)]
        for path in files(source):
            try:
                text = path.read_text("utf-8")
            except UnicodeDecodeError:
                continue
            rel = path.relative_to(PLUGINS).as_posix()
            for n, line in enumerate(text.splitlines(), 1):
                for target, kind, rx in table:
                    if rx.search(line):
                        found.append((source, target, rel, n, kind, line.strip()))
    return found, shared


def declared(source, target, desc_cache, cells):
    if source not in desc_cache:
        desc_cache[source] = description(source)
    in_desc = bool(name_re(target).search(desc_cache[source]))
    in_cell = target in top_level_names(cells.get(source, ""))
    return in_desc, in_cell


def undeclared():
    """(source, target, rel, line_no, kind, line, where-missing) for each undeclared ref."""
    refs, shared = references()
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
        excused = set(ALLOWED) | set(UNDECLARED)
        bad = [f for f in self.found if (f[2], f[1]) not in excused]
        self.assertEqual(bad, [], "undeclared cross-plugin references:\n" + "\n".join(
            f"  plugins/{rel}:{n} -> {t} ({kind}; missing in {miss}): {line[:120]}"
            for _, t, rel, n, kind, line, miss in bad))

    def test_a_new_undeclared_reference_would_fail(self):
        # kit-dev declares neither work-items nor dev-flow today; a fresh line naming their
        # CLI, a skill or a data path is marked, and is not declared.
        found = lambda target, line: any(rx.search(line) for _, rx in markers(target, "kit-dev"))
        self.assertTrue(found("work-items", "then run `wi add` for each"))
        self.assertTrue(found("dev-flow", "hand it to `/dev-flow:dev-cycle`"))
        self.assertTrue(found("context-guard", "read ~/.claude/claude-kit/context-gate/x"))
        self.assertFalse(found("work-items", "a wide, wild idea"))
        self.assertEqual(declared("kit-dev", "work-items", {}, catalog_cells()), (False, False))
        self.assertEqual(declared("kit-dev", "create-repo", {}, catalog_cells()), (True, True))

    def test_every_excuse_still_matches(self):
        live = {(f[2], f[1]) for f in self.found}
        for key in list(ALLOWED) + list(UNDECLARED):
            with self.subTest(key=key):
                self.assertIn(key, live, f"{key} matches nothing now; remove its entry")


class Parsing(unittest.TestCase):
    def test_top_level_names_skip_parenthesised_mentions(self):
        cell = ("`a` (soft; installing `b` brings it), `c` (hard; x (`d`) y), "
                "claude-sandbox repo (external)")
        self.assertEqual(top_level_names(cell), {"a", "c"})

    def test_name_re_is_whole_word(self):
        rx = name_re("statusline")
        self.assertTrue(rx.search("needs statusline, too"))
        self.assertFalse(rx.search("needs statusline-hub"))

    def test_path_re_matches_both_spellings(self):
        rx = path_re("statusline/sensor")
        self.assertTrue(rx.search("CFG/statusline/sensor/<sid>.json"))
        self.assertTrue(rx.search('os.path.join(base, "statusline", "sensor")'))
        self.assertFalse(rx.search("CFG/statusline-hub/sensor"))


if __name__ == "__main__":
    unittest.main()
