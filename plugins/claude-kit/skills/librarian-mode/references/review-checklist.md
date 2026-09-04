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
- [ ] Nothing under `.claude-sandbox/`, `.claude/`, or a product repo.
- [ ] One commit on the branch, message `<verb>: <aspect> - <description>` — plus one
      further commit per review fix round, never an amend. Any other extra commit is a fail.

```bash
git -C $W log --oneline main..HEAD
git -C $W diff --stat main...HEAD
```

## 2. Skill hygiene (every skill directory touched)

- [ ] Folder name equals the frontmatter `name`; the file is exactly `SKILL.md`.
- [ ] Frontmatter keys are exactly `name, description, disable-model-invocation,
      allowed-tools, argument-hint` — no others, none missing.
- [ ] No angle brackets in `name` or `description` (they are allowed in `argument-hint`,
      where about half the skills here use them); description under 1024 characters and states
      what + when + trigger phrases.
- [ ] Reference paths are bare relative paths: no dot-slash prefix, no skill-dir
      variable (the two tokens the lint below greps for).
- [ ] No `README.md` inside the skill folder.
- [ ] SKILL.md under ~5000 tokens; detail lives in `references/`.
- [ ] Every `references/*.md` the SKILL.md names exists.

```bash
for s in $(git -C $W diff --name-only main...HEAD | grep -o 'plugins/[^/]*/skills/[^/]*' | sort -u); do
  d=$W/$s
  echo "== $s"
  test -f $d/SKILL.md || echo "FAIL: no SKILL.md"
  test -f $d/README.md && echo "FAIL: README.md inside skill"
  name=$(sed -n 's/^name: *//p' $d/SKILL.md | head -1)
  test "$name" = "$(basename $s)" || echo "FAIL: name '$name' != folder"
  keys=$(awk 'NR>1 && /^---$/ {exit} NR>1 && /^[a-z-]+:/ {sub(":.*",""); print}' $d/SKILL.md | sort | tr '\n' ' ')
  test "$keys" = "allowed-tools argument-hint description disable-model-invocation name " || echo "FAIL: keys: $keys"
  grep -n '^\(name\|description\):.*[<>]' $d/SKILL.md && echo "FAIL: angle brackets in name/description"
  desc=$(sed -n 's/^description: *//p' $d/SKILL.md | head -1); test ${#desc} -le 1024 || echo "FAIL: description ${#desc} chars"
  grep -rn '[.]/\|CLAUDE_SKILL_DI[R]' $d && echo "FAIL: non-bare reference path"
  wc -w $d/SKILL.md
  for r in $(grep -o 'references/[A-Za-z0-9_.-]*\.md' $d/SKILL.md | sort -u); do test -f $d/$r || echo "FAIL: missing $r"; done
done
```

The dot-slash grep also catches the prefix in prose or shell, including in a checklist
that quotes it — which is why the pattern above is written with a bracket class, so the
lint file passes its own lint. A hit in a code block that genuinely needs the prefix (rare)
is reviewed by eye, not waved through.

## 3. Doctrine

Read the full diff — `git -C $W diff main...HEAD` — against the README's doctrine section
when present (the seven principles below are its content; apply them regardless), one
principle at a time:

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

- [ ] The `work-items` skill touched → wi tests green.
- [ ] A plugin's `hooks/` touched → that plugin's hook tests green.
- [ ] Any `scripts/*.py` touched → at least `python3 -m py_compile` on it.

```bash
git -C $W diff --name-only main...HEAD | grep -q '/skills/work-items/' && \
  (cd $W/plugins/*/skills/work-items && python3 -m unittest discover -s tests -q)
for h in $(git -C $W diff --name-only main...HEAD | grep -o '^plugins/[^/]*/hooks' | sort -u); do
  (cd $W/$h && python3 -m unittest discover -s tests -q); done
for p in $(git -C $W diff --name-only main...HEAD | grep '\.py$'); do python3 -m py_compile $W/$p && echo "ok $p"; done
```

## 5. Config validity

- [ ] Every `.json` in the diff parses.
- [ ] `.claude-plugin/marketplace.json` still lists exactly the plugins on disk.

```bash
for j in $(git -C $W diff --name-only main...HEAD | grep '\.json$'); do python3 -m json.tool $W/$j >/dev/null && echo "ok $j" || echo "FAIL $j"; done
python3 -c "import json,os,sys; m=json.load(open('$W/.claude-plugin/marketplace.json')); names={p['name'] for p in m['plugins']}; disk=set(os.listdir('$W/plugins')); print('marketplace==disk' if names==disk else 'FAIL: '+str(names^disk))"
```

## 6. After the merge, on `main`

- [ ] Sections 4 and 5 re-run in the main checkout on `main`.
- [ ] `git -C "$MAIN" status --short` is empty.
- [ ] The worktree was removed and the branch deleted only after both of the above.

A result that passes every box lands. A fail found by the reviewer is a finding at medium
or above in its report; a fail found by the librarian at Land goes back into the Review fix
loop with the failing line quoted, to the implementer as a new commit — see `agent-brief.md`
§ Sharpening a brief for re-dispatch when the implementer must be re-dispatched.
