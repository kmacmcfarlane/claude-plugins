"""No skill, agent or hook text tells the agent or the operator to type a bare
`/checkpoint` (item aebc, operator 2026-10-09): the bare name can resolve to a
built-in command of the same name, so a pasted or typed line would not run the
checkpoint skill. Every such instruction says `/context-guard:checkpoint`.

The one exception is text that describes what the HARD prompt gate lets
through: the gate passes the bare form as well as the plugin-prefixed one,
since the operator may type either, and saying so is not telling anyone to
type it. Those lines are listed in ALLOWED by file and an exact fragment of
the line, so a new bare mention fails until it is namespaced or listed.
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
     "unless the prompt is /checkpoint, /compact or"),
    ("plugins/context-guard/hooks/context_warn.py",
     "# /checkpoint, /compact, /clear - bare or plugin-qualified"),
    ("plugins/context-guard/hooks/read_list.py",
     "the next UserPromptSubmit that is not /checkpoint, /compact or"),
    ("plugins/context-guard/skills/checkpoint/SKILL.md",
     "the prompt gate erases every prompt except `/checkpoint`, `/compact` and `/clear`"),
    ("plugins/context-guard/skills/checkpoint/references/operator-playbook.md",
     "`/checkpoint`, `/compact` and `/clear`, bare or plugin-prefixed"),
}


def scanned():
    """Every skill, agent and hook text in the marketplace, plus the root docs.
    Tests are left out: they feed the gate the bare form on purpose."""
    pats = ("plugins/*/skills/**/*", "plugins/*/agents/**/*", "plugins/*/hooks/*.py",
            "plugins/*/hooks/*.json")
    out = {os.path.join(REPO, "README.md"), os.path.join(REPO, "CLAUDE.md")}
    for pat in pats:
        for p in glob.glob(os.path.join(REPO, pat), recursive=True):
            rel = os.path.relpath(p, REPO)
            if (os.path.isfile(p) and "/tests/" not in "/" + rel
                    and "__pycache__" not in rel):
                out.add(p)
    return sorted(out)


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
                if not BARE.search(line):
                    continue
                hit = next((a for a in ALLOWED if a[0] == rel and a[1] in line), None)
                if hit:
                    used.add(hit)
                else:
                    bad.append(f"{rel}:{n}: {line.strip()}")
        self.assertEqual(bad, [], "bare /checkpoint - namespace it as "
                         "/context-guard:checkpoint, or list gate-whitelist text in ALLOWED")
        self.assertEqual(sorted(ALLOWED - used), [], "stale ALLOWED entries")

    def test_the_scan_sees_the_files_it_guards(self):
        rels = {os.path.relpath(p, REPO) for p in scanned()}
        for rel in ("README.md", "CLAUDE.md",
                    "plugins/context-guard/skills/checkpoint/SKILL.md",
                    "plugins/context-guard/skills/checkpoint/references/operator-playbook.md",
                    "plugins/context-guard/hooks/context_warn.py",
                    "plugins/context-guard/hooks/turn_gate.py",
                    "plugins/context-guard/hooks/stop_relay.py",
                    "plugins/context-guard/hooks/rehydrate.py",
                    "plugins/dev-flow/skills/librarian-mode/SKILL.md"):
            self.assertIn(rel, rels)

    def test_the_pattern(self):
        for s in ("run `/checkpoint`", "/checkpoint handoff", "Run /checkpoint first"):
            self.assertTrue(BARE.search(s), s)
        for s in ("/context-guard:checkpoint", "skills/checkpoint/SKILL.md",
                  "--checkpointing", "/checkpointx", "/checkpoint-x", "the checkpoint"):
            self.assertFalse(BARE.search(s), s)


if __name__ == "__main__":
    unittest.main()
