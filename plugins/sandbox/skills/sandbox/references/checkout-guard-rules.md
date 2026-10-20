# Checkout guard path rules

The checkout guard (`hooks/checkout_guard.py`) denies `Edit`/`Write`/`MultiEdit`/`NotebookEdit`
on git-tracked files when the session's cwd is a main checkout. A repo can let some tracked
files be edited in place, while the rest still go through a worktree, by listing path rules in
`.claude/allow-checkout-edits` at the main checkout's root. This file is the format's owner.

## Example

```
# Record files are edited in the main checkout; code goes through a worktree.
allow issues/**
deny issues/templates/**
```

`issues/x.md` is allowed, `issues/templates/t.md` and `bin/tool` are denied. To allow every
tracked file, as the old presence-only marker did, write one line: `allow **`.

## Lines

The file is read from the working tree, tracked or not, as UTF-8. A leading BOM is ignored, and
`\r\n` and `\n` both end lines. Each line is stripped of surrounding whitespace, then:

- an empty line is skipped;
- a line whose first character is `#` is a comment;
- anything else is `allow <glob>` or `deny <glob>`: the keyword in lowercase, then the glob,
  then optionally a trailing comment starting with `#`. Nothing else may follow the glob.

A glob holds no whitespace (`?` matches a space). A glob that starts with `#` reads as a
comment and is an error ("missing glob"); write `\#` to match a path beginning with `#`.

## Which rule decides

An implicit first rule `deny *` comes before the file's rules, and the **last** rule whose glob
matches decides, as in gitignore. So a later narrow `deny` carves out of an earlier broad
`allow`, and a later `allow` re-opens part of a denied directory: unlike gitignore, `deny *`
followed by `allow issues/**` does allow `issues/x.md`.

A denial names the rule that decided it, by line number, or says the default `deny *` applied.

## Globs

Patterns match the file's path as git's index spells it, relative to the repo root, with `/`
separators. Matching is case-sensitive.

- **Anchored.** Every pattern starts at the repo root; one leading `/` is allowed and changes
  nothing. A slash-less pattern does **not** match at any depth: `*.md` is top-level only, and
  `**/*.md` matches at any depth.
- **Within a segment:**
  - `*` matches any run of characters except `/`, a leading `.` included;
  - `?` matches one character except `/`;
  - `[...]` matches one character from the class, never `/`. `[!...]` or `[^...]` negates it;
    a `]` right after the opening (or after the negation mark) is literal; `a-z` is a range,
    and a reversed range is an error. Inside a class `\` is a literal, so `[\]` matches a
    backslash;
  - `\x` matches `x` literally (outside a class);
  - every other character is literal.
- **`**`** must be a whole segment and matches whole segments:
  - `**` alone matches every path;
  - `a/**` matches everything under `a`, but not a file named exactly `a`;
  - `**/x` matches `x` at any depth, the top level included;
  - `a/**/b` matches `a/b` and `a/x/y/b`;
  - consecutive `**` segments act as one (`**/**` is `**`).
- **Directories.** A pattern ending in `/` matches directories only. A pattern without one
  matches a path when it matches the path itself **or any directory above it**, so `allow
  issues`, `allow issues/` and `allow issues/**` all cover `issues/a/b.md`, while `allow
  issues/*.md` covers `issues/x.md` but not `issues/a/b.md`.
- **Errors.** An empty segment (`a//b`), a `.` or `..` segment, a `**` that is not a whole
  segment (`a**b`), an unclosed `[`, a trailing `\`, and a leading `!` (no negation here;
  write `\!` for a literal `!`) are all errors.

## What the rules decide

Only what the guard already judges: tracked files, edited from a main checkout, inside the repo,
outside `.claude/` and `.claude-sandbox/`. A `deny` rule does not reach new, untracked files,
and the rules do nothing in a linked worktree or a non-git cwd.

The path judged is the file the write lands on: symlinks and `..` are resolved first, so a
tracked symlink `issues/link.md -> ../bin/tool`, or a write through a directory symlink, is
judged as `bin/tool`.

## When the file cannot be used

The rules file fails closed. Each of these allows nothing, exactly as if the file had no
`allow` rules, and the denial names the cause:

- the file is empty or holds only comments (the denial says `allow **` allows everything);
- any line fails to parse; no rule from the file applies, and the denial names the first bad
  line;
- the file is not UTF-8, is larger than 64 KiB, is not a regular file, or cannot be read;
- the file, or its `.claude` directory, is a symlink;
- `.claude` is not a directory;
- an internal error while reading or applying the rules.

No file at all gives the guard's plain denial. Errors outside the rules file (git missing or
broken, a payload that does not parse) still fail open, as they always have.

## The file is the operator's

Agents' `Edit`/`Write`/`MultiEdit`/`NotebookEdit` on any `.claude/allow-checkout-edits` are
denied, from any cwd (main checkout, linked worktree or non-git), whether the file exists or
not. The check compares both the path as given and its resolved path, case-folded, so a
symlink alias or a case variant is caught too, and it fails closed. Write the rules by hand, or
in a session started with `SANDBOX_ALLOW_CHECKOUT_EDITS=1`.

`SANDBOX_ALLOW_CHECKOUT_EDITS=1` (or its deprecated alias `CLAUDE_KIT_ALLOW_CHECKOUT_EDITS=1`)
stays the blanket override: it allows everything, above the rules, a broken file and the
file's own protection.

## Limitations

- **Bash writes** (sed, heredocs, redirects) are not guarded, the rules file included. The
  guard enforces a convention against accidental main-checkout edits; it is not a boundary.
- **Submodules:** files inside a submodule, edited from the superproject's checkout, read as
  untracked (the superproject tracks only the gitlink).
- **Case:** on a case-insensitive filesystem, a path spelled in a different case from the
  index reads as untracked, so the guard allows it, rules or no rules.
- **Symlinks:** a repo whose `.claude` directory, or whose rules file, is a symlink cannot use
  path rules; the file is treated as broken.
