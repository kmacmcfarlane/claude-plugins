# Review checklist

Two readers run this list: the **review sub-agent** briefed from `review-brief.md`
(sections 1–5, as the check commands pasted into its brief), and the **orchestrator
itself** at Land (all sections, inside the worktree before the merge and again on the base
after it). Both run the same commands so a verdict and a landing rest on the same evidence;
a verdict never substitutes for the orchestrator's own run. Every item is pass or fail; a
fail stops the landing. `W` is the worktree path, `BASE` the Base binding
(`bindings.md`).

```bash
W=<absolute worktree path>
BASE=<the Base binding>
```

Sections 2, 3 and 5 are written for this marketplace's conventions (skills, plugins, a
README catalog). On another repo each item applies where its subject exists, and most of
them are vacuous on a repo with no `plugins/` tree; the Checks binding (section 4) is
where such a repo's own gates come in.

## 1. Scope

- [ ] `git -C $W diff --stat $BASE...HEAD` lists only the files in scope (plus the
      catalog and layout edits when the marketplace's shape changed). With Files in
      scope `undeclared` (`bindings.md` § Undeclared files), compare the stat against the
      record sink's cumulative `changed:` block instead (the union of every round's
      CHANGED): every file in one is in the other, each with its one-line reason.
- [ ] Nothing under `.claude-sandbox/` or `.claude/`, nothing outside the Ground binding.
- [ ] One commit on the branch, message `<verb>: <aspect> - <description>` — plus, per
      review fix round, one or more new commits on top of it. No amend, rebase or squash
      of a reviewed commit — except the secret rebuild in `fix-loop.md`; a merge of the
      base only in a merge-conflict round (`fix-loop.md` § A merge conflict); nothing
      outside the files in scope in any of them.

```bash
git -C $W log --oneline $BASE..HEAD
git -C $W diff --stat $BASE...HEAD
```

## 2. Skill hygiene (every skill directory touched)

- [ ] Folder name equals the frontmatter `name`; the file is exactly `SKILL.md`.
- [ ] Frontmatter keys follow the house rule, whose allowed list lives in the create-skill
      skill's frontmatter reference, in the kit-dev plugin. The code below copies that
      list — 20 keys, the 5 required plus the 15 other documented fields — and must be
      kept in step with it: count both when either changes. The five required keys
      `name, description, disable-model-invocation, allowed-tools, argument-hint` are all
      present; every other key is a field the Claude Code skills docs define; no key
      appears twice; keys match exactly (`Model` fails). The set is closed because
      undocumented keys are usually typos, and claude.ai / Skills API uploads hard-fail
      on unknown keys. (`allowed-tools` pre-approves the listed tools; it never restricts
      the others.)
- [ ] No angle brackets in `name` or `description` (they are allowed in `argument-hint`,
      where about half the skills here use them); description under 1024 characters and
      states what + when + trigger phrases.
- [ ] The frontmatter parses under a strict YAML parser, and `name`, `description` and
      `argument-hint` each load as a string. An unquoted value that starts with `[` is a
      flow sequence: one bracket group loads as a list, and a second group after it
      (`[a] [b]`) makes the whole frontmatter fail to parse, so a stricter loader drops
      the skill without a word. Quote `argument-hint` always. The strict-YAML block at the
      end of this section checks it; a `SKIP` there is a gap to report, not a pass.
- [ ] Reference paths are bare relative paths: no dot-slash prefix, no skill-dir
      variable (the two tokens the lint below greps for).
- [ ] No `README.md` inside the skill folder.
- [ ] SKILL.md under ~5000 tokens; detail lives in `references/`.
- [ ] Every `references/*.md` the SKILL.md names exists: for a sibling pointer written
      `` `name` skill's `references/…` `` (CLAUDE.md's Cross-skill references convention),
      in that named sibling; otherwise in the skill itself. `references/x.md` is the
      reserved placeholder for examples and is skipped.

```bash
for s in $(git -C $W diff --name-only $BASE...HEAD | grep -o 'plugins/[^/]*/skills/[^/]*' | sort -u); do
  d=$W/$s
  echo "== $s"
  test -f $d/SKILL.md || echo "FAIL: no SKILL.md"
  test -f $d/README.md && echo "FAIL: README.md inside skill"
  name=$(sed -n 's/^name: *//p' $d/SKILL.md | head -1)
  test "$name" = "$(basename $s)" || echo "FAIL: name '$name' != folder"
  # every top-level key (indented lines, such as those under metadata:, do not count),
  # with surrounding quotes and whitespace trimmed
  keys=$(awk 'NR>1 && /^---$/ {exit} NR>1 && /^[^ \t#-][^:]*:/ {sub(/:.*/, ""); gsub(/^[ \t"\047]+|[ \t"\047]+$/, ""); print}' $d/SKILL.md)
  dups=$(printf '%s\n' "$keys" | sort | uniq -d | tr '\n' ' ')
  test -z "$dups" || echo "FAIL: duplicate keys: $dups"
  for k in name description disable-model-invocation allowed-tools argument-hint; do
    printf '%s\n' "$keys" | grep -qxF -e "$k" || echo "FAIL: missing key $k"
  done
  # the 20 allowed keys: 5 required + 15 documented (create-skill frontmatter reference)
  printf '%s\n' "$keys" | grep -v '^$' | grep -vxF -e name -e description \
    -e disable-model-invocation -e allowed-tools -e argument-hint -e when_to_use \
    -e arguments -e user-invocable -e disallowed-tools -e model -e effort -e context \
    -e agent -e background -e hooks -e paths -e shell -e metadata -e license \
    -e compatibility | sed 's/^/FAIL: key not allowed: /'
  grep -n '^\(name\|description\):.*[<>]' $d/SKILL.md && echo "FAIL: angle brackets in name/description"
  desc=$(sed -n 's/^description: *//p' $d/SKILL.md | head -1); test ${#desc} -le 1024 || echo "FAIL: description ${#desc} chars"
  grep -rn '[.]/\|CLAUDE_SKILL_DI[R]' $d && echo "FAIL: non-bare reference path"
  wc -w $d/SKILL.md
  python3 - $d <<'PY'
import os, re, sys
d = sys.argv[1]; p = os.path.dirname(d); me = os.path.basename(d)
lines = open(d + '/SKILL.md').read().split('\n')
fence = None  # (char, length) of the open fence; backtick or tilde, any length >= 3
ref = re.compile(r'([^\s`(\'"]*/)?(references/[\w.-]+?\.md)(?![\w-]|\.\w)')
for n, line in enumerate(lines, 1):
    f = re.match(r'\s*(`{3,}|~{3,})(.*)', line)
    if f:
        run, rest = f.groups()
        if fence is None: fence = (run[0], len(run))
        elif run[0] == fence[0] and len(run) >= fence[1] and not rest.strip(): fence = None
        continue
    prev = lines[n - 2] if n > 1 else ''
    nxt = lines[n] if n < len(lines) else ''
    text = line.rstrip()
    # a path wrapped across lines: this line ends inside it, the next finishes it
    if re.search(r'references/[\w.-]*$', text) and not text.endswith('.md'):
        head = re.match(r'\s*([\w.-]*\.md)', nxt)
        if head: text += head.group(1)
    for m in ref.finditer(text):
        pre, r = m.group(1), m.group(2)
        if pre:
            if '://' in pre: continue  # a URL, not a path into a skill
            # a path into some skill by directory; fenced example output is exempt
            if not fence: print(f'FAIL: path by directory, use the sibling form: {pre}{r} (line {n})')
            continue
        if r == 'references/x.md': continue
        named = re.search(r"`([\w-]+)`(?: skill)?'s\s+`?$", prev + ' ' + text[:m.start()])
        if named:  # a named sibling is checked even when this skill has a file of that name
            sib = named.group(1)
            if sib == me or not os.path.isdir(f'{p}/{sib}'):
                print(f'FAIL: `{sib}` is not a sibling in this plugin: {r} (line {n})')
            elif os.path.isfile(f'{p}/{sib}/{r}'): print(f'ok (sibling {sib}): {r}')
            else: print(f'FAIL: missing {r} in sibling {sib} (line {n})')
        elif not os.path.isfile(f'{d}/{r}'): print(f'FAIL: missing {r} (line {n})')
PY
done
```

The dot-slash grep also catches the prefix in prose or shell, including in a checklist
that quotes it — which is why the pattern above is written with a bracket class, so the
lint file passes its own lint. A hit in a code block that genuinely needs the prefix (rare)
is reviewed by eye, not waved through.

What the reference check reads, so a reviewer can tell a real miss from a lint gap:

- **Named sibling first.** When the backticked name immediately precedes the path
  (`` `name` skill's `` or `` `name`'s ``, on the same line or wrapped from the one
  before), the file must exist in that sibling — even when this skill has a file of the
  same name, which would otherwise shadow a missing one. A named skill that is this skill
  itself, or is not a folder beside it in the same plugin (another plugin included),
  fails. With no name before it, the path must exist in this skill; a bare mention of a
  sibling without backticks fails.
- **Wrapped paths.** A path split at a line break inside the path (`references/` at the
  end of one line, `x.md` at the start of the next) is joined and checked. A break
  anywhere else — inside the sibling's name, say — is not; write the pointer so the name
  and the start of the path share a line or the name ends the line before.
- **By directory.** A path that reaches a skill's `references/` by directory
  (`beta/references/…`, `plugins/…/references/…`) fails outside a fenced block — use the
  sibling form; inside a fence it is taken for example output and skipped. A URL
  (anything with `://` before the path) is not a path into a skill and is skipped.
- **Fences.** Backtick and tilde fences of three or more characters both count; a fence
  closes only on the same character, at least as long as its opener, with nothing after
  it, so a shorter fence or the other character nests inside. The fence lines themselves
  are not read.
- **Extensions.** Only a path ending in `.md` counts: `.mdx`, `.md.bak` and other
  longer names are not read as `.md`. A sentence-ending full stop after `.md` is fine.

The strict-YAML check (ruamel.yaml's safe loader, else PyYAML's; `SKIP` when neither
imports, never a silent pass):

```bash
for s in $(git -C $W diff --name-only $BASE...HEAD | grep -o 'plugins/[^/]*/skills/[^/]*' | sort -u); do
  echo "== $s (strict YAML)"
  python3 - $W/$s/SKILL.md <<'PY'
import sys
try:
    from ruamel.yaml import YAML; load = YAML(typ='safe').load
except ImportError:
    try: import yaml; load = yaml.safe_load
    except ImportError: print('SKIP: no strict YAML parser'); sys.exit()
text = open(sys.argv[1]).read()
if not text.startswith('---\n'): print('FAIL: no frontmatter'); sys.exit()
if '\n---' not in text[4:]: print('FAIL: frontmatter not closed'); sys.exit()
try: fm = load(text[4:].split('\n---', 1)[0])
except Exception as e:
    m = getattr(e, 'problem_mark', None); at = f' at frontmatter line {m.line + 1}' if m else ''
    print(f"FAIL: frontmatter does not parse{at}: {getattr(e, 'problem', None) or type(e).__name__}"); sys.exit()
if not isinstance(fm, dict): print('FAIL: frontmatter is not a mapping'); sys.exit()
for k in ('name', 'description', 'argument-hint'):
    if k in fm and not isinstance(fm[k], str): print(f'FAIL: {k} loads as {type(fm[k]).__name__}, not a string')
PY
done
```

## 3. Doctrine

Read the full diff — `git -C $W diff $BASE...HEAD` — against the repo's doctrine, one
principle at a time, plus the Workflow binding. In this marketplace that is README.md
§ The doctrine, the canonical statement of the seven principles; the checks below apply
them, and a finding cites a principle by its number there. A repo with no such
section is measured by the checks below alone, each where its subject exists — on a repo
with no plugins/ tree most are vacuous:

- [ ] **One plugin, one aim.** No plugin description gained an "and".
- [ ] **Standalone test.** Nothing new requires another plugin from this marketplace to be
      useful, unless declared as a soft dependency in the catalog, or as a hard one in the
      dependent's `plugin.json` `dependencies` — the test then covers the plugin plus its
      declared hard dependencies.
- [ ] **Harness-behavior quarantine.** No hook, status line, or `settings.json` write
      outside the plugin whose stated aim is that behavior.
      `grep -rln 'hooks\|settings.json' $W/plugins --include=*.json` shows nothing new
      outside it.
- [ ] **Dependencies soft by default, declared, directional.** Any new cross-plugin reference is named
      in the plugin description and the catalog row.
- [ ] **Hard dependencies only where they must be.** Every `plugin.json` `dependencies`
      entry is same-marketplace (no `marketplace` key naming another), the dependent has no
      function at all without it, and it is not a data read that could fall back; the
      catalog marks it (hard), and every catalog (hard) is declared. §5's hard-dependency
      script checks the mechanical half.
- [ ] **Names are API.** No plugin renamed; the marketplace `name` untouched; no `claude-`
      prefix on a new plugin.
- [ ] **New aim → new plugin.** A new capability did not stretch an existing description.
- [ ] **Repo workflow.** The change follows the Workflow binding, when set.
- [ ] **Catalog is the front door.** If the shape changed — plugin added/moved/retired, a
      skill added to or removed from a plugin — README.md's catalog row and per-plugin skill
      table, and CLAUDE.md's layout block where it enumerates skills, changed in this same
      commit.

```bash
git -C $W diff --name-only $BASE...HEAD | grep -q '^plugins/.*/skills/[^/]*/SKILL.md$' && \
  { git -C $W diff --name-only $BASE...HEAD | grep -q '^README.md$' || echo "CHECK: skill added/changed — is a catalog edit needed?"; }
git -C $W diff --name-only $BASE...HEAD | grep -q '\.claude-plugin/' && \
  { git -C $W diff --name-only $BASE...HEAD | grep -q '^README.md$' || echo "FAIL: plugin shape changed without README"; }
```

## 4. Tests where they exist

Run the suite for every tree the diff touches; run both when in doubt — they are seconds.
Then the repo's own gates: every command in the Checks binding, run from `$W`, on every
change — they come on top of the generic ones, never instead of them.

- [ ] Each Checks-binding command exits 0.
- [ ] The `work-items` skill touched → wi tests green.
- [ ] A plugin's `hooks/` touched → that plugin's hook tests green.
- [ ] Any `scripts/*.py` touched → at least `python3 -m py_compile` on it.

```bash
git -C $W diff --name-only $BASE...HEAD | grep -q '/skills/work-items/' && \
  (cd $W/plugins/*/skills/work-items && python3 -m unittest discover -s tests -q)
for h in $(git -C $W diff --name-only $BASE...HEAD | grep -o '^plugins/[^/]*/hooks' | sort -u); do
  (cd $W/$h && python3 -m unittest discover -s tests -q); done
for p in $(git -C $W diff --name-only $BASE...HEAD | grep '\.py$'); do python3 -m py_compile $W/$p && echo "ok $p"; done
# then, from $W, each command in the Checks binding, one per line
```

## 5. Config validity

- [ ] Every `.json` in the diff parses.
- [ ] `.claude-plugin/marketplace.json`, when present, still lists exactly the plugins
      on disk.
- [ ] Hard dependencies match the catalog: every `dependencies` entry in a `plugin.json`
      is a name or an object with a `name`, same-marketplace, and marked (hard) in
      README.md's catalog row for its plugin; every (hard) there is declared; no
      `marketplace.json` entry declares `dependencies` (plugin.json is the one place); no
      `allowCrossMarketplaceDependenciesOn` is set.

```bash
for j in $(git -C $W diff --name-only $BASE...HEAD | grep '\.json$'); do python3 -m json.tool $W/$j >/dev/null && echo "ok $j" || echo "FAIL $j"; done
test -f $W/.claude-plugin/marketplace.json && python3 -c "import json,os,sys; m=json.load(open('$W/.claude-plugin/marketplace.json')); names={p['name'] for p in m['plugins']}; disk=set(os.listdir('$W/plugins')); print('marketplace==disk' if names==disk else 'FAIL: '+str(names^disk))"
test -f $W/.claude-plugin/marketplace.json && python3 - "$W" <<'EOF'
import json, os, re, sys
w = sys.argv[1]; bad = []; declared = set()
def load(f):
    try: d = json.load(open(f))
    except (OSError, ValueError) as e: bad.append(f'{f} unreadable ({e.__class__.__name__})'); return None
    if not isinstance(d, dict): bad.append(f'{f} is not a JSON object'); return None
    return d
m = load(f'{w}/.claude-plugin/marketplace.json') or {}
if 'allowCrossMarketplaceDependenciesOn' in m: bad.append('allowCrossMarketplaceDependenciesOn is set')
for e in m.get('plugins', []) if isinstance(m.get('plugins'), list) else []:
    if isinstance(e, dict) and 'dependencies' in e:
        bad.append(f"marketplace entry {e.get('name')} declares dependencies; declare them in its plugin.json")
for p in sorted(os.listdir(f'{w}/plugins')):
    f = f'{w}/plugins/{p}/.claude-plugin/plugin.json'
    if not os.path.exists(f): continue
    deps = (load(f) or {}).get('dependencies', [])
    if not isinstance(deps, list): bad.append(f'{p}: dependencies is not a list'); continue
    for d in deps:
        if isinstance(d, str) and d: n, mk = d, None
        elif isinstance(d, dict) and isinstance(d.get('name'), str) and d['name']: n, mk = d['name'], d.get('marketplace')
        else: bad.append(f'{p} has a malformed dependency entry: {d!r}'); continue
        if mk not in (None, m.get('name')): bad.append(f'{p} -> {n}@{mk} crosses marketplaces')
        declared.add((p, n))
marked = set()
for line in open(f'{w}/README.md') if os.path.exists(f'{w}/README.md') else []:
    c = [x.strip() for x in line.split('|')]
    if len(c) >= 6 and (r := re.fullmatch(r'`([^`]+)`', c[2])):
        marked |= {(r.group(1), n) for n in re.findall(r'`([^`]+)` \(hard', c[4])}
bad += [f'{p} declares {n}; catalog does not mark it (hard)' for p, n in sorted(declared - marked)]
bad += [f'catalog marks {p} -> {n} (hard); not declared' for p, n in sorted(marked - declared)]
print('\n'.join('FAIL: ' + b for b in bad) or f'hard deps: catalog==declared ({len(declared)})')
EOF
```

## 6. After the merge, on the base

- [ ] Sections 4 and 5 re-run in the main checkout on the base.
- [ ] `git -C "$MAIN" status --short` shows nothing the merge introduced. Dirt the
      cycle wrote itself — the record sink or store, the Series home, `.claude/worktrees/`
      — is expected and never blocks a merge; any other dirt stopped the merge before it
      ran (`troubleshooting.md` § Landing).
- [ ] The worktree was removed and the branch deleted only after both of the above.

A result that passes every box lands. A fail found by the reviewer is a finding at medium
or above in its report; a fail found by the orchestrator at Land goes back into the fix
loop with the failing line quoted, to the implementer as a new commit — see
`agent-brief.md` § Sharpening a brief for re-dispatch when the implementer must be
re-dispatched.
