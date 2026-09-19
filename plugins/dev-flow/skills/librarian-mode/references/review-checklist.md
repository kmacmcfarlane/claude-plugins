# Review checklist

Two readers run this list: the **review sub-agent** briefed from `review-brief.md`
(sections 1–5, as the check commands pasted into its brief), and the **librarian itself**
at Land (all sections, inside the worktree before the merge and again on `main` after it).
Both run the same commands so a verdict and a landing rest on the same evidence; a verdict
never substitutes for the librarian's own run. Every item is pass or fail; a fail stops the
landing. `W` is the worktree path.

```bash
W=<absolute worktree path>
```

## 1. Scope

- [ ] `git -C $W diff --stat main...HEAD` lists only the files the item names (plus the
      catalog and layout edits when the marketplace's shape changed).
- [ ] Nothing under `.claude-sandbox/` or `.claude/`, nothing outside the `## Librarian`
      Scope in CLAUDE.md, nothing inside its Exclude.
- [ ] One commit on the branch, message `<verb>: <aspect> - <description>` — plus, per
      review fix round, one or more new commits on top of it. No amend, rebase or squash
      of a reviewed commit — except the secret rebuild in `references/fix-loop.md`;
      nothing outside the item's files in any of them.

```bash
git -C $W log --oneline main..HEAD
git -C $W diff --stat main...HEAD
```

## 2. Skill hygiene (every skill directory touched)

- [ ] Folder name equals the frontmatter `name`; the file is exactly `SKILL.md`.
- [ ] Frontmatter keys follow the house rule (create-skill's frontmatter reference states
      the same): every skill declares `name, description, disable-model-invocation,
      allowed-tools, argument-hint`, none missing; the other documented fields `model,
      context, license, compatibility, metadata` are allowed; no other key.
- [ ] No angle brackets in `name` or `description` (they are allowed in `argument-hint`,
      where about half the skills here use them); description under 1024 characters and states
      what + when + trigger phrases.
- [ ] Reference paths are bare relative paths: no dot-slash prefix, no skill-dir
      variable (the two tokens the lint below greps for).
- [ ] No `README.md` inside the skill folder.
- [ ] SKILL.md under ~5000 tokens; detail lives in `references/`.
- [ ] Every `references/*.md` the SKILL.md names exists: in the skill itself, or, for a
      sibling pointer written `` `name` skill's `references/…` `` (CLAUDE.md's Cross-skill
      references convention), in that named sibling. `references/x.md` is the reserved
      placeholder for examples and is skipped.

```bash
for s in $(git -C $W diff --name-only main...HEAD | grep -o 'plugins/[^/]*/skills/[^/]*' | sort -u); do
  d=$W/$s
  echo "== $s"
  test -f $d/SKILL.md || echo "FAIL: no SKILL.md"
  test -f $d/README.md && echo "FAIL: README.md inside skill"
  name=$(sed -n 's/^name: *//p' $d/SKILL.md | head -1)
  test "$name" = "$(basename $s)" || echo "FAIL: name '$name' != folder"
  keys=$(awk 'NR>1 && /^---$/ {exit} NR>1 && /^[a-z-]+:/ {sub(":.*",""); print}' $d/SKILL.md | sort | tr '\n' ' ')
  for k in name description disable-model-invocation allowed-tools argument-hint; do
    case " $keys" in *" $k "*) ;; *) echo "FAIL: missing key $k (keys: $keys)";; esac
  done
  for k in $keys; do
    case " name description disable-model-invocation allowed-tools argument-hint model context license compatibility metadata " in
      *" $k "*) ;; *) echo "FAIL: key $k not allowed (keys: $keys)";; esac
  done
  grep -n '^\(name\|description\):.*[<>]' $d/SKILL.md && echo "FAIL: angle brackets in name/description"
  desc=$(sed -n 's/^description: *//p' $d/SKILL.md | head -1); test ${#desc} -le 1024 || echo "FAIL: description ${#desc} chars"
  grep -rn '[.]/\|CLAUDE_SKILL_DI[R]' $d && echo "FAIL: non-bare reference path"
  wc -w $d/SKILL.md
  python3 - $d <<'PY'
import os, re, sys
d = sys.argv[1]; p = os.path.dirname(d); fence = False
lines = open(d + '/SKILL.md').read().split('\n')
for n, line in enumerate(lines, 1):
    if line.lstrip().startswith('```'): fence = not fence
    prev = lines[n - 2] if n > 1 else ''
    for m in re.finditer(r'([^\s`(\'"]*/)?(references/[\w.-]+?\.md)\b', line):
        pre, r = m.group(1), m.group(2)
        if pre:  # a path into some skill by directory; fenced example output is exempt
            if not fence: print(f'FAIL: path by directory, use the sibling form: {pre}{r} (line {n})')
            continue
        if r == 'references/x.md' or os.path.isfile(f'{d}/{r}'): continue
        named = re.search(r"`([\w-]+)`(?: skill)?'s\s+`?$", prev + ' ' + line[:m.start()])
        if not named: print(f'FAIL: missing {r} (line {n})'); continue
        sib = named.group(1)
        if sib == os.path.basename(d) or not os.path.isdir(f'{p}/{sib}'):
            print(f'FAIL: `{sib}` is not a sibling in this plugin: {r} (line {n})')
        elif os.path.isfile(f'{p}/{sib}/{r}'): print(f'ok (sibling {sib}): {r}')
        else: print(f'FAIL: missing {r} in sibling {sib} (line {n})')
PY
done
```

The dot-slash grep also catches the prefix in prose or shell, including in a checklist
that quotes it — which is why the pattern above is written with a bracket class, so the
lint file passes its own lint. A hit in a code block that genuinely needs the prefix (rare)
is reviewed by eye, not waved through.

The reference check tries the skill's own file first. Failing that, the path must be a
sibling pointer: the backticked name immediately before it (`` `name` skill's `` or
`` `name`'s ``, on the same line or wrapped from the one before) must be another skill of
this plugin that has the file. Any other named skill, including one in another plugin, fails;
so does a bare mention without backticks. A path that reaches a skill's `references/` by
directory (`beta/references/…`, `plugins/…/references/…`) fails outside a fenced block — use
the sibling form; inside a fence it is taken for example output and skipped. `.mdx` and
other longer extensions are not read as `.md`.

## 3. Doctrine

Read the full diff — `git -C $W diff main...HEAD` — against the repo's doctrine, one
principle at a time, plus the repo's own workflow. In this marketplace that is README.md
§ The doctrine, the canonical statement of the seven principles; the checks below apply
them, and a finding cites a principle by its number there. A repo with no such
section is measured by the checks below alone, each where its subject exists — on a repo
with no plugins/ tree most are vacuous:

- [ ] **One plugin, one aim.** No plugin description gained an "and".
- [ ] **Standalone test.** Nothing new requires another plugin from this marketplace to be
      useful, unless declared as a soft dependency in the catalog.
- [ ] **Harness-behavior quarantine.** No hook, status line, or `settings.json` write
      outside the plugin whose stated aim is that behavior.
      `grep -rln 'hooks\|settings.json' $W/plugins --include=*.json` shows nothing new
      outside it.
- [ ] **Dependencies soft, declared, directional.** Any new cross-plugin reference is named
      in the plugin description and the catalog row.
- [ ] **Names are API.** No plugin renamed; the marketplace `name` untouched; no `claude-`
      prefix on a new plugin.
- [ ] **New aim → new plugin.** A new capability did not stretch an existing description.
- [ ] **Repo workflow.** The change follows the `Workflow:` notes in `## Librarian`, when
      present.
- [ ] **Catalog is the front door.** If the shape changed — plugin added/moved/retired, a
      skill added to or removed from a plugin — README.md's catalog row and per-plugin skill
      table, and CLAUDE.md's layout block where it enumerates skills, changed in this same
      commit.

```bash
git -C $W diff --name-only main...HEAD | grep -q '^plugins/.*/skills/[^/]*/SKILL.md$' && \
  { git -C $W diff --name-only main...HEAD | grep -q '^README.md$' || echo "CHECK: skill added/changed — is a catalog edit needed?"; }
git -C $W diff --name-only main...HEAD | grep -q '\.claude-plugin/' && \
  { git -C $W diff --name-only main...HEAD | grep -q '^README.md$' || echo "FAIL: plugin shape changed without README"; }
```

## 4. Tests where they exist

Run the suite for every tree the diff touches; run both when in doubt — they are seconds.
Then the repo's own gates: every command under `Checks:` in CLAUDE.md's `## Librarian`
section, run from `$W`, on every item — they come on top of the generic ones, never
instead of them.

- [ ] Each repo `Checks:` command exits 0.
- [ ] The `work-items` skill touched → wi tests green.
- [ ] A plugin's `hooks/` touched → that plugin's hook tests green.
- [ ] Any `scripts/*.py` touched → at least `python3 -m py_compile` on it.

```bash
git -C $W diff --name-only main...HEAD | grep -q '/skills/work-items/' && \
  (cd $W/plugins/*/skills/work-items && python3 -m unittest discover -s tests -q)
for h in $(git -C $W diff --name-only main...HEAD | grep -o '^plugins/[^/]*/hooks' | sort -u); do
  (cd $W/$h && python3 -m unittest discover -s tests -q); done
for p in $(git -C $W diff --name-only main...HEAD | grep '\.py$'); do python3 -m py_compile $W/$p && echo "ok $p"; done
# then, from $W, each command listed under Checks: in ## Librarian, one per line
```

## 5. Config validity

- [ ] Every `.json` in the diff parses.
- [ ] `.claude-plugin/marketplace.json`, when present, still lists exactly the plugins
      on disk.

```bash
for j in $(git -C $W diff --name-only main...HEAD | grep '\.json$'); do python3 -m json.tool $W/$j >/dev/null && echo "ok $j" || echo "FAIL $j"; done
test -f $W/.claude-plugin/marketplace.json && python3 -c "import json,os,sys; m=json.load(open('$W/.claude-plugin/marketplace.json')); names={p['name'] for p in m['plugins']}; disk=set(os.listdir('$W/plugins')); print('marketplace==disk' if names==disk else 'FAIL: '+str(names^disk))"
```

## 6. After the merge, on `main`

- [ ] Sections 4 and 5 re-run in the main checkout on `main`.
- [ ] `git -C "$MAIN" status --short` is empty, or shows only first-start dirt (the
      store and any `.gitignore` line `wi init` wrote) — expected: commit it with the
      first landed item or leave it for the operator; it never blocks a merge.
- [ ] The worktree was removed and the branch deleted only after both of the above.

A result that passes every box lands. A fail found by the reviewer is a finding at medium
or above in its report; a fail found by the librarian at Land goes back into the Review fix
loop with the failing line quoted, to the implementer as a new commit — see `agent-brief.md`
§ Sharpening a brief for re-dispatch when the implementer must be re-dispatched.
