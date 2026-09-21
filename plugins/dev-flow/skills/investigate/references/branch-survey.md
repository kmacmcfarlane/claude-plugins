# Branch survey

Loaded from `investigate` Step 3a, for every resolved repo. The rules that decide the base —
the default branch unless proven otherwise, consent for anything else, where the choice is
recorded — stay in Step 3a; this file holds the commands and how to vet a candidate.

## Commands

```bash
git -C <repo> fetch --prune
git -C <repo> remote show origin | grep 'HEAD branch'    # detect the default, don't assume
git -C <repo> branch -a --sort=-committerdate \
  --format='%(refname:short) %(committerdate:relative)' | head -30
```

## Strong candidates

A branch is a **strong candidate** when it touches the same area this work will target
(`git -C <repo> diff --stat origin/<default>...<candidate>`), or is a rebased variant of one
that does.

## Vetting a candidate

Vet each candidate before offering it as a base:

- **Not behind default** — `git -C <repo> log --oneline <candidate>..origin/<default>`. Any
  commits listed mean the candidate is missing default-branch work.
- Prefer the variant that is on current default and is the most complete superset.
