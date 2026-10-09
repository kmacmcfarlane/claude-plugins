"""No skill, agent or hook text tells the agent or the operator to type a bare
`/checkpoint` (item aebc, operator 2026-10-09): the bare name can resolve to a
built-in command of the same name, so a pasted or typed line would not run the
checkpoint skill. Every such instruction says `/context-guard:checkpoint`.

The one exception is text that describes what the HARD prompt gate lets
through: the gate passes the bare form as well as the plugin-prefixed one,
since the operator may type either, and saying so is not telling anyone to
type it. Those lines are listed in ALLOWED by file and an exact fragment of
the line, so a new bare mention fails until it is namespaced or listed. Every
bare match on an allowed line must fall inside its fragment, so an instruction
appended to a whitelist line still fails; and every fragment names `/compact`
and `/clear` too, so the allowlist holds whitelist text and nothing else.
"""
import glob, os, re, unittest

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HOOKS)))
# A bare /checkpoint: not plugin-prefixed (`x:`), not a path segment
# (`skills/checkpoint/`), not a longer name (`/checkpointing`, `/checkpoint-x`).
BARE = re.compile(r"(?<![\w:/-])/checkpoint(?![\w/-])")

# (path relative to the repo, fragment of the line) - gate-whitelist text only.
ALLOWED = {
    ("plugins/context-guard/hooks/context_warn.py",
     "/checkpoint, /compact or /clear, in the bare or the plugin-prefixed form"),
    ("plugins/context-guard/hooks/context_warn.py",
     "# /checkpoint, /compact, /clear - bare or plugin-qualified"),
    ("plugins/context-guard/hooks/read_list.py",
     "/checkpoint, /compact or /clear and is not hard-stopped"),
    ("plugins/context-guard/skills/checkpoint/SKILL.md",
     "the prompt gate erases every prompt except `/checkpoint`, `/compact` and `/clear`"),
    ("plugins/context-guard/skills/checkpoint/references/operator-playbook.md",
     "`/checkpoint`, `/compact` and `/clear`, bare or plugin-prefixed"),
}


def bare_outside(rel, line):
    """The bare matches on `line` not covered by an ALLOWED fragment of `rel`,
    and the ALLOWED entries that covered one."""
    spans, used = [], set()
    for a in ALLOWED:
        if a[0] == rel:
            i = line.find(a[1])
            while i >= 0:
                spans.append((i, i + len(a[1]), a))
                i = line.find(a[1], i + 1)
    out = []
    for m in BARE.finditer(line):
        cover = next((sp for sp in spans if sp[0] <= m.start() and m.end() <= sp[1]), None)
        if cover:
            used.add(cover[2])
        else:
            out.append(m.group())
    return out, used


def scanned():
    """Every skill, agent and hook text in the marketplace, plus the root docs.
    Tests are left out: they feed the gate the bare form on purpose."""
    pats = ("plugins/*/skills/**/*", "plugins/*/agents/**/*", "plugins/*/hooks/*.py",
            "plugins/*/hooks/*.json", "plugins/*/.claude-plugin/plugin.json",
            "plugins/*/settings.json", ".claude-plugin/marketplace.json")
    out = {os.path.join(REPO, "README.md"), os.path.join(REPO, "CLAUDE.md")}
    for pat in pats:
        for p in glob.glob(os.path.join(REPO, pat), recursive=True):
            rel = os.path.relpath(p, REPO)
            if (os.path.isfile(p) and "/tests/" not in "/" + rel
                    and "__pycache__" not in rel):
                out.add(p)
    return sorted(out)


# The scan reads the repo's README, CLAUDE.md, marketplace.json and sibling plugins, which
# sit around this plugin only in the source repo; a copy of this plugin alone has none
# (kit-dev's standalone check runs it that way).
IN_REPO = all(os.path.isfile(os.path.join(REPO, f))
              for f in (".claude-plugin/marketplace.json", "CLAUDE.md", "README.md"))


@unittest.skipUnless(IN_REPO, "not in the source repo: no marketplace.json, CLAUDE.md or README.md")
class CheckpointNamespacedTest(unittest.TestCase):
    def test_no_bare_checkpoint_outside_the_gate_whitelist_text(self):
        bad, used = [], set()
        for p in scanned():
            rel = os.path.relpath(p, REPO)
            try:
                with open(p, encoding="utf-8") as f:
                    lines = f.read().splitlines()
            except UnicodeDecodeError:
                continue
            for n, line in enumerate(lines, 1):
                out, hits = bare_outside(rel, line)
                used |= hits
                if out:
                    bad.append(f"{rel}:{n}: {line.strip()}")
        self.assertEqual(bad, [], "bare /checkpoint - namespace it as "
                         "/context-guard:checkpoint, or list gate-whitelist text in ALLOWED")
        self.assertEqual(sorted(ALLOWED - used), [], "stale ALLOWED entries")

    def test_an_instruction_appended_to_an_allowed_line_still_fails(self):
        for rel, frag in sorted(ALLOWED):
            with self.subTest(rel=rel):
                self.assertEqual(bare_outside(rel, frag)[0], [])
                self.assertEqual(bare_outside(rel, frag + " Type `/checkpoint` now.")[0],
                                 ["/checkpoint"])
                self.assertEqual(bare_outside("README.md", frag)[0], ["/checkpoint"])

    def test_every_allowed_fragment_is_whitelist_text(self):
        for rel, frag in sorted(ALLOWED):
            with self.subTest(rel=rel, frag=frag):
                self.assertTrue(BARE.search(frag))
                self.assertIn("/compact", frag)
                self.assertIn("/clear", frag)

    def test_the_scan_sees_the_files_it_guards(self):
        rels = {os.path.relpath(p, REPO) for p in scanned()}
        for rel in ("README.md", "CLAUDE.md",
                    "plugins/context-guard/skills/checkpoint/SKILL.md",
                    "plugins/context-guard/skills/checkpoint/references/operator-playbook.md",
                    "plugins/context-guard/hooks/context_warn.py",
                    "plugins/context-guard/hooks/turn_gate.py",
                    "plugins/context-guard/hooks/stop_relay.py",
                    "plugins/context-guard/hooks/rehydrate.py",
                    "plugins/dev-flow/skills/librarian-mode/SKILL.md",
                    "plugins/context-guard/.claude-plugin/plugin.json",
                    "plugins/statusline/settings.json",
                    ".claude-plugin/marketplace.json"):
            self.assertIn(rel, rels)

    def test_the_pattern(self):
        for s in ("run `/checkpoint`", "/checkpoint handoff", "Run /checkpoint first"):
            self.assertTrue(BARE.search(s), s)
        for s in ("/context-guard:checkpoint", "skills/checkpoint/SKILL.md",
                  "--checkpointing", "/checkpointx", "/checkpoint-x", "the checkpoint"):
            self.assertFalse(BARE.search(s), s)


if __name__ == "__main__":
    unittest.main()
