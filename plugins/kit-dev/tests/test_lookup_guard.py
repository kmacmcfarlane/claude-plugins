"""The guard against new checkout-first lookups and relative script runs (item 185f, F4).

A lookup that finds another plugin's script, or the kit's instructions, must never take a
file from the working checkout, and a script run must name an absolute, guarded base. The
earlier features fixed every known site and run each one; this suite keeps new ones out of
all skill text (every `.md` under plugins/, tests excluded), in three parts.

1. **One template.** Every lookup copy, from its `P=` line through the line that binds its
   result (`if test -f "$VAR"; then …`), matches TEMPLATE byte for byte. Only the named
   holes vary, each to its own shape: the record key, the ranking argument (`$MAIN` or
   `$WORKTREE`), the bound variable, the plugin (equal to the key's), the file under the
   install, and the bind line's tail. Everything else is literal: the absolute-`P` guard,
   the `python3 -I` read, the heredoc, the `rc=$?` capture, the `case $IP in /*)` line and
   the cache condition. A copy is any fenced block that reads `installed_plugins.json`, or
   any other shipped file outside tests that does. One variant of the template is named:
   a `REL=` line between `P=` and `IP=`, the file then written `$REL` (the research
   plugin's quota-sense lookup); only the copies in REL_LINE_COPIES may use it. A block
   that does not match is one of the frozen VARIANTS, each held to its own literal lines.

2. **No checkout path, no relative run.** Every command (a fenced line, or an inline code
   span that begins with a command word) is checked against RULES:
   - `checkout-var`: `$MAIN`, `"${MAIN}"`, `$WORKTREE`, `$PWD` or `$(git rev-parse …)`
     followed by `/plugins`;
   - `plugins-path`: a path `plugins/*` or `plugins/<x>/{skills,hooks,agents}/`, unless it
     sits under `"$P"/cache/kmacmcfarlane/` or `$IP/` (relative, it resolves against the
     checkout);
   - `cd-ls`: `cd … && ls`, a listing of the checkout;
   - `find-name`: `find` with a `-name` of a script (`.py`, `.js`, `.sh`), `SKILL.md` or
     `wi`;
   - `ls-script`: `ls` of a script or `SKILL.md` not under `"$P"/cache/kmacmcfarlane/` or
     `$IP/`;
   - `rel-run`: an interpreter run of `scripts/…` or `hooks/…`, which resolves against the
     working directory;
   - `placeholder-run`: an interpreter run of `<placeholder>/…` without the guard: unfilled
     or filled with a relative path, it runs a checkout file;
   - `unguarded-var`: a variable bound to a `<placeholder>` and run without the
     `case $V in /*)` guard directly before the run;
   - `var-in-ref`: `${CLAUDE_PLUGIN_ROOT}` in a command inside a `references/` file, which
     is read with a tool, so nothing fills the variable in and Bash runs `/hooks/…`
     (https://code.claude.com/docs/en/plugins-reference § Environment variables).

3. **Frozen lists.** ALLOWED excuses the known safe hits, each keyed by (rule, file, a
   substring of the line, how many lines it covers) with its reason; VARIANTS and
   REL_LINE_COPIES are the template's exceptions. Each list must be a subset of its
   FROZEN_* literal, fixed at landing, so a list can only shrink: a new entry fails, and
   an entry that no longer matches fails as stale. Adding one needs an operator ruling
   (CLAUDE.md § Conventions).

Every check is proved by a mutant: one changed byte in each literal line of each copy, each
hole set to a wrong literal, the REL line in a copy not listed, a variant's held line
changed, each bypass spelling of each rule, a duplicated allowed line, and a new entry in
each list.

Runs only in the source repo (it reads every plugin); in an isolated copy of kit-dev it
skips. Standard library only. Run from plugins/kit-dev:

    python3 -m unittest discover -s tests -q
"""
import re
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
REPO = KIT.parent.parent
PLUGINS = REPO / "plugins"
IN_REPO = ((REPO / "README.md").is_file()
           and (REPO / ".claude-plugin" / "marketplace.json").is_file())

# -- 1. the template --------------------------------------------------------------------
P_LINE = ('P="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugins"; '
          'case $P in /*) ;; *) P=/dev/null/plugins;; esac')
HEREDOC = '''import json, os, sys
try:  # any failure here means the record cannot answer: exit 1, and the cache is asked
    es = json.load(open(sys.argv[1]))["plugins"][sys.argv[2]]
    here = os.path.realpath(sys.argv[3])
    def rank(e):  # the install that applies here: deepest local/project path, then user
        pp = e.get("projectPath")
        if e.get("scope") in ("local", "project") and pp:
            pp = os.path.realpath(pp)
            if here == pp or here.startswith(pp.rstrip("/") + "/"):
                return (2, len(pp), e["scope"] == "local")
        return (1, 0, False) if e.get("scope") == "user" else (0, 0, False)
    best = max(es, key=rank)
    ip = best["installPath"] if rank(best)[0] else ""
    print(ip if os.path.isabs(ip) else "")
except Exception:
    sys.exit(1)
PY
)"; rc=$?'''
TEMPLATE = (P_LINE + "\n"
            "{RELLINE}"
            'IP="$(python3 -I - "$P/installed_plugins.json" {KEY} "{RANK}" 2>/dev/null <<\'PY\'\n'
            + HEREDOC + "\n"
            '{VAR}=; case $IP in /*) test -f "$IP/{REL}" && {VAR}=$IP/{REL};; esac\n'
            'test -n "${VAR}" || { test "$rc" -ne 0 && {VAR}=$(ls -t '
            '"$P"/cache/kmacmcfarlane/{PLUGIN}/*/{REL} 2>/dev/null | head -1); }\n'
            'if test -f "${VAR}"; then {BIND}')
HOLES = {
    "RELLINE": r"(?:REL=(?:skills|hooks|agents)/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*\n)?",
    "KEY": r"[a-z][a-z0-9-]*@kmacmcfarlane",
    "RANK": r"\$MAIN|\$WORKTREE",
    "VAR": r"[A-Z][A-Z0-9_]*",
    "PLUGIN": r"[a-z][a-z0-9-]*",
    "REL": r"\$REL|(?:skills|hooks|agents)/[A-Za-z0-9_-][A-Za-z0-9_.-]*(?:/[A-Za-z0-9_-][A-Za-z0-9_.-]*)*",
    "BIND": r"[^\n]+",
}


def template_re():
    out, pos, seen = "", 0, set()
    for m in re.finditer(r"\{([A-Z]+)\}", TEMPLATE):
        out += re.escape(TEMPLATE[pos:m.start()])
        name = m.group(1)
        if name in seen:
            out += f"(?P={name})"
        else:
            out += f"(?P<{name}>{HOLES[name]})"
            seen.add(name)
        pos = m.end()
    return re.compile(out + re.escape(TEMPLATE[pos:]))


TEMPLATE_RE = template_re()

# Copies allowed the REL= line, keyed by (file relative to plugins/, record key).
REL_LINE_COPIES = {
    ("research/skills/research/references/intensity-and-routing.md", "dev-flow@kmacmcfarlane"):
        "the quota-sense lookup names its file once in REL=, used by the case, cache and run",
}
FROZEN_REL_LINE_COPIES = frozenset({
    ("research/skills/research/references/intensity-and-routing.md", "dev-flow@kmacmcfarlane"),
})

# Lookups that are not the template, keyed by (file relative to plugins/, a substring of
# the block): (reason, the literal lines the block must still hold).
VARIANTS = {
    ("dev-flow/skills/deep-investigation/references/research-peer.md", "complete() {"): (
        "the research peer checks a multi-file install (two scripts, two agent bodies) and "
        "walks the cache for a complete copy; its P line, read, rc capture, absolute check "
        "and cache condition are the template's",
        (P_LINE, 'IP="$(python3 -I - "$P/installed_plugins.json" research@kmacmcfarlane '
         '"$MAIN" 2>/dev/null <<\'PY\'', HEREDOC,
         'case $IP in /*) complete "$IP" && RESEARCH_ROOT=$IP FROM=installed;; esac',
         'if test -z "$RESEARCH_ROOT" && test "$rc" -ne 0; then',
         '< <(ls -td "$P"/cache/kmacmcfarlane/research/*/ 2>/dev/null)')),
    ("context-guard/skills/checkpoint/references/operator-playbook.md", 'MC="$(python3 -I'): (
        "the operator-run checkpoint mark ranks by the working directory and falls back to "
        "the data dir's current-hooks link; P only when absolute, an absolute installPath "
        "only, and a guarded run (kit-dev's test_checkout_lookups.py runs it)",
        (P_LINE, 'print(ip if os.path.isabs(ip) else "")',
         'case $MC in /*) python3 "$MC" <session_id>;; *) echo "no mark_checkpoint.py found";; esac')),
    ("work-items/skills/work-items/scripts/wi", "exec python3"): (
        "the work-items launcher, a shell script: its P line honours one more variable "
        "than the skill copies, and work-items reviews it; it runs only an absolute "
        "installPath and never the cache",
        ("python3 -I - \"$P/installed_plugins.json\" work-items@kmacmcfarlane \"$MAIN\"",
         'if os.path.isabs(ip) else "")',
         '[ -n "$py" ] && [ -f "$py" ] ||')),
}
FROZEN_VARIANTS = frozenset({
    ("dev-flow/skills/deep-investigation/references/research-peer.md", "complete() {"),
    ("context-guard/skills/checkpoint/references/operator-playbook.md", 'MC="$(python3 -I'),
    ("work-items/skills/work-items/scripts/wi", "exec python3"),
})

FENCE = re.compile(r"^([ \t]*)(```+|~~~+)[^\n]*\n(.*?)^\1\2[ \t]*$", re.S | re.M)
RECORD = "installed_plugins.json"


def skill_text_files():
    """Every .md under plugins/, tests excluded, relative to plugins/."""
    return sorted(str(p.relative_to(PLUGINS)) for p in PLUGINS.rglob("*.md")
                  if "tests" not in p.relative_to(PLUGINS).parts)


def other_files():
    """Shipped non-markdown, non-Python files outside tests that read the record."""
    out = []
    for p in sorted(PLUGINS.rglob("*")):
        rel = p.relative_to(PLUGINS)
        if (p.is_file() and "tests" not in rel.parts and p.suffix not in (".md", ".py", ".pyc")
                and "__pycache__" not in rel.parts):
            try:
                if RECORD in p.read_text(encoding="utf-8"):
                    out.append(str(rel))
            except (UnicodeDecodeError, OSError):
                pass
    return out


def read(rel):
    return (PLUGINS / rel).read_text(encoding="utf-8")


def fenced(text):
    """(first line number, body) for each fenced block."""
    return [(text[:m.start(3)].count("\n") + 1, m.group(3)) for m in FENCE.finditer(text)]


def lookup_blocks(texts):
    """(file, block) for every fenced block, or other file, that reads the record."""
    out = []
    for rel, text in texts.items():
        if rel.endswith(".md"):
            out += [(rel, b) for _, b in fenced(text) if RECORD in b]
        elif RECORD in text:
            out.append((rel, text))
    return out


def template_problems(texts, variants=None, rel_line=None):
    """(copies found, problems) for the template check over {file: text}."""
    variants = VARIANTS if variants is None else variants
    rel_line = REL_LINE_COPIES if rel_line is None else rel_line
    copies, problems, used = [], [], set()
    for rel, b in lookup_blocks(texts):
        m = TEMPLATE_RE.search(b)
        if m:
            g = m.groupdict()
            copies.append((rel, g["KEY"]))
            if g["KEY"] != g["PLUGIN"] + "@kmacmcfarlane":
                problems.append(f"{rel}: key {g['KEY']} is not the plugin {g['PLUGIN']}'s")
            if g["RELLINE"] and (rel, g["KEY"]) not in rel_line:
                problems.append(f"{rel}: a REL= line in a copy not in REL_LINE_COPIES")
            if g["REL"] == "$REL" and not g["RELLINE"]:
                problems.append(f"{rel}: $REL with no REL= line")
            if g["RELLINE"]:
                used.add(("rel", rel, g["KEY"]))
            continue
        keys = [k for k in variants if k[0] == rel and k[1] in b]
        if not keys:
            problems.append(f"{rel}: a lookup block that is not the template nor a variant: "
                            f"{b.strip().splitlines()[0][:80]!r}")
            continue
        for k in keys:
            used.add(("variant",) + k)
            for held in variants[k][1]:
                if held not in b:
                    problems.append(f"{rel}: variant lost its held line {held[:60]!r}")
    for k in variants:
        if ("variant",) + k not in used:
            problems.append(f"stale variant: {k}")
    for k in rel_line:
        if ("rel",) + k not in used:
            problems.append(f"stale REL-line copy: {k}")
    return copies, problems


def all_texts():
    return {rel: read(rel) for rel in skill_text_files() + other_files()}


# -- 2. the token rules -------------------------------------------------------------------
INTERP = r"(?:python3?|node|bash|sh)(?: -I)?"
SAFE_ROOTS = ('"$P"/cache/kmacmcfarlane/', "$IP/", '"$IP"/')
SCRIPTISH = re.compile(r"(?:\.py|\.js|\.sh|SKILL\.md)(?![A-Za-z0-9_])")
RULES = {
    "checkout-var": re.compile(
        r'(?:\$\{?(?:MAIN|PWD|WORKTREE)\}?|\$\(git rev-parse[^)]*\))"?/plugins(?![\w-])'),
    "plugins-path": re.compile(
        r'(?<![A-Za-z0-9_.-])plugins/(?:\*|[^/\s"\'`]+/(?:skills|hooks|agents)/)'),
    "cd-ls": re.compile(r"\bcd\b[^;&|\n]*&&\s*ls\b"),
    "find-name": re.compile(
        r"\bfind\b[^|;&\n]*\s-i?name\s+['\"]?[^\s'\"]*(?:\.py|\.js|\.sh|SKILL\.md|\bwi)['\"]?(?=[\s)|;&]|$)"),
    "ls-script": None,  # ls_script() below
    "rel-run": re.compile(r"\b" + INTERP + r" +['\"]?(?:\./)?(?:scripts|hooks)/"),
    "placeholder-run": re.compile(r"\b" + INTERP + r" +['\"]?<[^>]+>/"),
    "unguarded-var": None,  # unguarded_var() below
    "var-in-ref": re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}"),
}
COMMAND_SPAN = re.compile(
    r"^\(?\s*(?:env(?:\s+-u\s+\S+|\s+[A-Z_]+=\S*)*\s+)?(?:timeout\s+\S+\s+)?"
    r"(?:python3?|node|bash|sh|ls|find|cd|cat|source)\b")
SPAN = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")


def ls_script(line):
    """An `ls` whose argument names a script or SKILL.md not under the cache or $IP."""
    for m in re.finditer(r"\bls\b([^|;&)\n]*)", line):
        for tok in m.group(1).split():
            if SCRIPTISH.search(tok) and not re.match(
                    r'"\$P"/cache/kmacmcfarlane/|"?\$\{?IP\}?"?/', tok):
                return True
    return False


def unguarded_var(lines):
    """Line indexes that run `$V/…` for a V bound to a <placeholder> with no guard before."""
    bound, out = set(), []
    for i, line in enumerate(lines):
        bound |= set(re.findall(r"\b([A-Za-z_]\w*)=['\"]?<[^>]+>['\"]?", line))
        for m in re.finditer(r"\b" + INTERP + r" +['\"]?\$\{?([A-Za-z_]\w*)\}?/", line):
            v = m.group(1)
            if v in bound and not line[:m.start()].endswith(f"case ${v} in /*) "):
                out.append(i)
    return out


def command_lines(rel, text):
    """(line number, command text, is fenced) for each command in a file."""
    out = []
    for start, body in fenced(text):
        lines = body.splitlines()
        out.append((start, lines, True))
    blank = FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    for n, line in enumerate(blank.splitlines(), 1):
        spans = [m.group(1) for m in SPAN.finditer(line) if COMMAND_SPAN.match(m.group(1))]
        for s in spans:
            out.append((n, [s], False))
    return out


def hits_in(rel, text):
    """(rule, file, line number, line) for every rule hit in a file."""
    out = []
    in_ref = "/references/" in "/" + rel
    for start, lines, _ in command_lines(rel, text):
        unguarded = set(unguarded_var(lines))
        for i, line in enumerate(lines):
            for rule, rx in RULES.items():
                if rule == "var-in-ref" and not in_ref:
                    continue
                if rule == "ls-script":
                    hit = ls_script(line)
                elif rule == "unguarded-var":
                    hit = i in unguarded
                elif rule == "plugins-path":
                    hit = any(not line[:m.start()].endswith(SAFE_ROOTS)
                              for m in rx.finditer(line))
                else:
                    hit = bool(rx.search(line))
                if hit:
                    out.append((rule, rel, start + i, line.strip()))
    return out


# (rule, file relative to plugins/, a substring of the line, the number of lines it covers)
# -> why the line is safe. The count pins the entry: a second such line in the file fails.
ALLOWED = {
    ("placeholder-run", "context-guard/skills/checkpoint/references/operator-playbook.md",
     'Bash(python3 "<root>/hooks/', 3):
        "permission-rule patterns the operator pastes into settings, not commands run",
    ("placeholder-run", "context-guard/skills/checkpoint/references/operator-playbook.md",
     'python3 "<root>/hooks/handoff_path.py" --path', 1):
        "an operator-run command in the operator's own shell, <root> the install they name",
    ("placeholder-run", "research/skills/research/references/run-record.md",
     "skill dir>/scripts/", 4):
        "the placeholder is the absolute skill dir of the resolved research install "
        "(research-peer.md § Where each read goes, or the loaded SKILL.md), never a checkout path",
    ("plugins-path", "dev-flow/skills/dev-cycle/references/review-checklist.md",
     "grep -q '^plugins/.*/skills/", 1):
        "a pattern matched against changed file names; no file is resolved, read or run",
    ("plugins-path", "dev-flow/skills/dev-cycle/references/review-checklist.md",
     "(cd $W/plugins/*/skills/work-items && python3 -m unittest", 1):
        "runs the change's own tests in its worktree by design, as every Checks command does",
    ("plugins-path", "kit-dev/skills/update-kit/SKILL.md", "## claude-plugins (plugins/", 1):
        "a heading in a fenced sample report, not a command",
    ("plugins-path", "kit-dev/skills/update-kit/SKILL.md", "## claude-expertise (plugins/", 1):
        "a heading in a fenced sample report, not a command",
    ("plugins-path", "kit-dev/skills/update-kit/references/repo-map.md",
     "ls ../claude-plugins/plugins/*/skills", 1):
        "update-kit, invoked only by the user, lists the sibling kit repo it syncs",
    ("plugins-path", "work-items/skills/work-items/SKILL.md", "install-launcher", 1):
        "a developer-only command in this kit's own checkout, run by its path as an explicit act",
    ("rel-run", "kit-dev/skills/create-skill/references/best-practices.md",
     "python scripts/validate.py --input", 1):
        "sample skill text quoted as an example of good wording, not a command",
    ("ls-script", "statusline-hub/skills/statusline-hub/SKILL.md",
     't=$(ls -td "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/kmacmcfarlane/', 1):
        "the tee launcher globs the install cache under the config dir, never the checkout "
        "(a relative config dir or HOME is the poisoned-root residual, out of scope)",
}
FROZEN_ALLOWED = frozenset({
    ("placeholder-run", "context-guard/skills/checkpoint/references/operator-playbook.md",
     'Bash(python3 "<root>/hooks/', 3),
    ("placeholder-run", "context-guard/skills/checkpoint/references/operator-playbook.md",
     'python3 "<root>/hooks/handoff_path.py" --path', 1),
    ("placeholder-run", "research/skills/research/references/run-record.md",
     "skill dir>/scripts/", 4),
    ("plugins-path", "dev-flow/skills/dev-cycle/references/review-checklist.md",
     "grep -q '^plugins/.*/skills/", 1),
    ("plugins-path", "dev-flow/skills/dev-cycle/references/review-checklist.md",
     "(cd $W/plugins/*/skills/work-items && python3 -m unittest", 1),
    ("plugins-path", "kit-dev/skills/update-kit/SKILL.md", "## claude-plugins (plugins/", 1),
    ("plugins-path", "kit-dev/skills/update-kit/SKILL.md", "## claude-expertise (plugins/", 1),
    ("plugins-path", "kit-dev/skills/update-kit/references/repo-map.md",
     "ls ../claude-plugins/plugins/*/skills", 1),
    ("plugins-path", "work-items/skills/work-items/SKILL.md", "install-launcher", 1),
    ("rel-run", "kit-dev/skills/create-skill/references/best-practices.md",
     "python scripts/validate.py --input", 1),
    ("ls-script", "statusline-hub/skills/statusline-hub/SKILL.md",
     't=$(ls -td "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/kmacmcfarlane/', 1),
})


def rule_problems(texts, allowed=None):
    """Every hit no entry covers, every entry covering more or fewer hits than it says."""
    allowed = ALLOWED if allowed is None else allowed
    problems, counts = [], {k: 0 for k in allowed}
    for rel, text in texts.items():
        if not rel.endswith(".md"):
            continue
        for rule, f, n, line in hits_in(rel, text):
            keys = [k for k in allowed if k[0] == rule and k[1] == f and k[2] in line]
            if keys:
                counts[keys[0]] += 1
            else:
                problems.append(f"{rule}: {f}:{n}: {line[:100]}")
    for k, c in counts.items():
        if c != k[3]:
            problems.append(f"allowed entry covers {c} lines, not {k[3]}: {k[:3]}")
    return problems


def frozen_problems(lists=None):
    lists = lists or {"ALLOWED": (ALLOWED, FROZEN_ALLOWED),
                      "VARIANTS": (VARIANTS, FROZEN_VARIANTS),
                      "REL_LINE_COPIES": (REL_LINE_COPIES, FROZEN_REL_LINE_COPIES)}
    return [f"{name}: a new entry {k}" for name, (got, frozen) in lists.items()
            for k in got if k not in frozen]


# -- tests --------------------------------------------------------------------------------
KNOWN_COPIES = {
    ("dev-flow/skills/dev-cycle/references/bindings.md", "kit-dev@kmacmcfarlane"),
    ("dev-flow/skills/dev-cycle/references/bindings.md", "context-guard@kmacmcfarlane"),
    ("dev-flow/skills/dev-cycle/references/bindings.md", "work-items@kmacmcfarlane"),
    ("research/skills/research/references/intensity-and-routing.md", "work-items@kmacmcfarlane"),
    ("research/skills/research/references/intensity-and-routing.md", "dev-flow@kmacmcfarlane"),
    ("context-guard/skills/checkpoint/SKILL.md", "work-items@kmacmcfarlane"),
    ("ralph/skills/backlog-yaml/SKILL.md", "work-items@kmacmcfarlane"),
}


def _once(text, old, new):
    if old not in text:
        raise AssertionError(f"mutant target not found: {old[:60]!r}")
    return text.replace(old, new, 1)


@unittest.skipUnless(IN_REPO, "not in the source repo: the other plugins are not here")
class TestTemplate(unittest.TestCase):
    def setUp(self):
        self.texts = all_texts()

    def test_every_copy_is_the_template(self):
        copies, problems = template_problems(self.texts)
        self.assertEqual(problems, [])
        self.assertTrue(KNOWN_COPIES <= set(copies), KNOWN_COPIES - set(copies))

    def copy_blocks(self):
        out = []
        for rel, b in lookup_blocks(self.texts):
            m = TEMPLATE_RE.search(b)
            if m:
                out.append((rel, b, m))
        self.assertGreaterEqual(len(out), len(KNOWN_COPIES))
        return out

    def problems_with(self, rel, old_block, new_block):
        texts = dict(self.texts)
        texts[rel] = _once(texts[rel], old_block, new_block)
        return template_problems(texts)[1]

    def test_mutant_one_changed_byte_in_each_literal_line(self):
        for rel, b, m in self.copy_blocks():
            region = m.group(0)
            for line in region.splitlines():
                # a literal line: no hole value in it, or the template line it came from
                literal = [t for t in TEMPLATE.splitlines() if "{" not in t]
                if line not in literal:
                    continue
                i = next(k for k, ch in enumerate(line) if not ch.isspace())
                bad = line[:i] + ("X" if line[i] != "X" else "Y") + line[i + 1:]
                with self.subTest(file=rel, line=line[:50]):
                    mutant = _once(b, line, bad)
                    self.assertNotEqual(self.problems_with(rel, b, mutant), [])

    def test_mutant_each_held_line_of_the_template(self):
        # the lines that carry holes: one byte changed in their literal part
        held = ['"; rc=$?', "case $IP in /*) test -f", 'test "$rc" -ne 0 && ',
                "2>/dev/null | head -1); }", "python3 -I - ", 'if test -f "$']
        for rel, b, m in self.copy_blocks():
            for h in held:
                with self.subTest(file=rel, held=h):
                    mutant = _once(b, h, h.replace(" ", "  ", 1) if " " in h else h + "x")
                    self.assertNotEqual(self.problems_with(rel, b, mutant), [])

    def test_mutant_each_hole_set_to_a_wrong_literal(self):
        for rel, b, m in self.copy_blocks():
            g = m.groupdict()
            wrong = {
                "KEY": (f'{g["KEY"]} "{g["RANK"]}"', f'other@kmacmcfarlane "{g["RANK"]}"'),
                "RANK": (f'{g["KEY"]} "{g["RANK"]}"', f'{g["KEY"]} "$PWD"'),
                "PLUGIN": (f"kmacmcfarlane/{g['PLUGIN']}/*/", "kmacmcfarlane/*/*/"),
                "REL": (f'test -f "$IP/{g["REL"]}"', 'test -f "$IP/../x.py"'),
                "VAR": (f'{g["VAR"]}=; case', "x=; case"),
            }
            for hole, (old, new) in wrong.items():
                with self.subTest(file=rel, key=g["KEY"], hole=hole):
                    self.assertNotEqual(self.problems_with(rel, b, _once(b, old, new)), [])

    def test_mutant_rel_line_in_a_copy_not_listed(self):
        rel = "dev-flow/skills/dev-cycle/references/bindings.md"
        b = next(b for r, b, m in self.copy_blocks()
                 if r == rel and m.group("KEY") == "work-items@kmacmcfarlane")
        mutant = _once(b, P_LINE + "\n", P_LINE + "\nREL=skills/work-items/scripts/wi.py\n")
        problems = self.problems_with(rel, b, mutant)
        self.assertTrue(any("REL= line" in p for p in problems), problems)

    def test_mutant_variant_loses_a_held_line(self):
        for (rel, sub), (_, held) in VARIANTS.items():
            b = next(b for r, b in lookup_blocks(self.texts) if r == rel and sub in b)
            for h in held:
                with self.subTest(file=rel, held=h[:40]):
                    first = h.splitlines()[0]
                    mutant = _once(b, first, first.replace(" ", "  ", 1))
                    self.assertNotEqual(self.problems_with(rel, b, mutant), [])

    def test_mutant_a_new_lookup_block(self):
        texts = dict(self.texts)
        rel = "kit-dev/skills/create-skill/SKILL.md"
        texts[rel] += ('\n```bash\nIP="$(python3 - "$P/installed_plugins.json" k <<\'PY\'\n'
                       'PY\n)"\n```\n')
        self.assertTrue(any("not the template" in p for p in template_problems(texts)[1]))

    def test_mutant_stale_entries(self):
        v = dict(VARIANTS)
        v[("kit-dev/skills/create-skill/SKILL.md", "nothing")] = ("x", ())
        r = dict(REL_LINE_COPIES)
        r[("kit-dev/skills/create-skill/SKILL.md", "kit-dev@kmacmcfarlane")] = "x"
        problems = template_problems(self.texts, v, r)[1]
        self.assertTrue(any(p.startswith("stale variant") for p in problems), problems)
        self.assertTrue(any(p.startswith("stale REL-line") for p in problems), problems)


# One spelling of each bypass, as a fenced line in a reference file: (rule, line).
BYPASSES = [
    ("checkout-var", 'WI_PY=$(ls "$MAIN"/plugins/*/skills/work-items/scripts/wi.py 2>/dev/null | head -1)'),
    ("checkout-var", 'cat "${MAIN}"/plugins/x/README.md'),
    ("checkout-var", "python3 $PWD/plugins/x/run.py"),
    ("checkout-var", 'python3 "$(git rev-parse --show-toplevel)/plugins/x/run.py"'),
    ("checkout-var", 'cat "$WORKTREE"/plugins/x/README.md'),
    ("plugins-path", "python3 plugins/x/skills/y/scripts/z.py"),
    ("plugins-path", "cat plugins/*"),
    ("cd-ls", 'cd "$MAIN" && ls'),
    ("find-name", 'find "$MAIN" -name wi.py'),
    ("find-name", "find . -iname 'SKILL.md'"),
    ("ls-script", 'CS=$(ls -t "$WORKTREE"/*/skills/create-skill/SKILL.md | head -1)'),
    ("ls-script", "ls -t ./x/*/scripts/z.py"),
    ("rel-run", "python3 scripts/z.py"),
    ("rel-run", "python3 -I ./hooks/z.py"),
    ("rel-run", "node scripts/z.js"),
    ("placeholder-run", 'python3 "<plugin root>/hooks/z.py"'),
    ("placeholder-run", "node '<skill dir>/scripts/z.js'"),
    ("unguarded-var", 'R="<plugin root>"; python3 "$R/hooks/z.py"'),
    ("unguarded-var", 'R="<plugin root>"; case $R in /*) :;; esac; node "$R/scripts/z.js"'),
    ("var-in-ref", 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/z.py"'),
]
# Lines each rule must leave alone.
CLEAN = [
    'WI_PY=$(ls -t "$P"/cache/kmacmcfarlane/work-items/*/skills/work-items/scripts/wi.py 2>/dev/null | head -1)',
    'R="<plugin root>"; case $R in /*) python3 "$R/hooks/z.py";; *) echo "plugin root not absolute: $R" >&2; false;; esac',
    'for d in "$MAIN/.work-items" "$MAIN/.work"; do test -d "$d/items"; done',
    "find <corpus> -name '*.jsonl' | wc -l",
    'test -f "$IP/skills/x/SKILL.md"',
]
REF = "kit-dev/skills/create-skill/references/z.md"


def fence(*lines):
    return "```bash\n" + "\n".join(lines) + "\n```\n"


@unittest.skipUnless(IN_REPO, "not in the source repo: the other plugins are not here")
class TestRules(unittest.TestCase):
    def test_tree_is_clean_but_for_the_frozen_list(self):
        self.assertEqual(rule_problems(all_texts()), [])

    def test_each_bypass_is_caught(self):
        for rule, line in BYPASSES:
            with self.subTest(rule=rule, line=line):
                hits = {h[0] for h in hits_in(REF, fence(line))}
                self.assertIn(rule, hits)
                self.assertNotEqual(rule_problems({REF: fence(line)}, {}), [])

    def test_each_bypass_is_caught_in_an_inline_span(self):
        for rule, line in BYPASSES:
            if not COMMAND_SPAN.match(line):
                continue
            with self.subTest(rule=rule, line=line):
                self.assertIn(rule, {h[0] for h in hits_in(REF, f"Run `{line}` now.\n")})

    def test_clean_lines_pass(self):
        for line in CLEAN:
            with self.subTest(line=line):
                self.assertEqual(hits_in(REF, fence(line)), [])

    def test_var_in_a_skill_md_command_passes(self):
        line = 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/z.py"'
        self.assertEqual(hits_in("kit-dev/skills/create-skill/SKILL.md", fence(line)), [])

    def test_prose_naming_a_path_passes(self):
        self.assertEqual(hits_in(REF, "The tests live in `plugins/*/hooks/tests/`.\n"), [])

    def test_mutant_today_fixed_spin_off_line_is_flagged(self):
        # handoff-format.md:65 before F6
        line = 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/spin_off.py" --help'
        self.assertIn("var-in-ref", {h[0] for h in hits_in(
            "context-guard/skills/checkpoint/references/handoff-format.md", fence(line))})

    def test_mutant_a_bypass_in_a_real_file(self):
        texts = all_texts()
        rel = "dev-flow/skills/dev-cycle/references/bindings.md"
        for rule, line in BYPASSES:
            with self.subTest(rule=rule):
                t = dict(texts)
                t[rel] = t[rel] + "\n" + fence(line)
                self.assertNotEqual(rule_problems(t), [])

    def test_mutant_duplicated_allowed_line(self):
        texts = all_texts()
        for (rule, rel, sub, _) in ALLOWED:
            line = next(h[3] for h in hits_in(rel, texts[rel]) if h[0] == rule and sub in h[3])
            with self.subTest(file=rel, sub=sub):
                t = dict(texts)
                t[rel] = t[rel] + "\n" + fence(line)
                problems = rule_problems(t)
                self.assertTrue(any("covers" in p for p in problems), problems)

    def test_mutant_stale_allowed_entry(self):
        a = dict(ALLOWED)
        a[("rel-run", "kit-dev/skills/create-skill/SKILL.md", "nothing here", 1)] = "x"
        self.assertTrue(any("covers 0 lines" in p for p in rule_problems(all_texts(), a)))


class TestFrozenLists(unittest.TestCase):
    def test_lists_only_shrink(self):
        self.assertEqual(frozen_problems(), [])

    def test_mutant_new_entry_in_each_list(self):
        new = {
            "ALLOWED": ({**ALLOWED, ("rel-run", "a.md", "x", 1): "x"}, FROZEN_ALLOWED),
            "VARIANTS": ({**VARIANTS, ("a.md", "x"): ("x", ())}, FROZEN_VARIANTS),
            "REL_LINE_COPIES": ({**REL_LINE_COPIES, ("a.md", "k"): "x"},
                                FROZEN_REL_LINE_COPIES),
        }
        for name, pair in new.items():
            with self.subTest(list=name):
                self.assertEqual(len(frozen_problems({name: pair})), 1)


if __name__ == "__main__":
    unittest.main()
