---
name: code-comments
description: Rules for writing and reviewing code comments in any language - Go, Terraform, YAML, SQL, shell, and prose docs like README.md or CLAUDE.md. Use when writing a comment, reviewing a diff that adds comments, being asked to document or explain code, or when a comment feels like it needs to be a paragraph. Covers why-not-what, changelog tells, one canonical home per fact, and treating long comments as a design signal.
disable-model-invocation: false
allowed-tools: Read, Edit, Grep, Glob
---

# Code comments

Comments are for what the code cannot say. Default to none and earn each one.

## Rules

- **Say why, never what.** A comment that restates the line below it is noise. Rename the
  variable or extract the function instead — that fix cannot go stale.
- **Write for the next reader, not for this session.** Never narrate the debugging you just did
  ("previously this returned nil", "I moved this up because the test failed"). Git blame and the
  ticket hold that. Keep it only if a future edit would otherwise reintroduce the bug — and then
  state the *constraint*, not the story.
- **One canonical home per fact.** Document a rule where the rule lives (the shared helper, the CI
  anchor, the type) and leave call sites bare. A rule repeated at each call site is a set of copies
  that will drift.
- **Keep the comment shorter than the code it explains.** One or two lines is normal. Anything
  longer needs a reason from the next rule; otherwise cut it.
- **A long comment is usually a design signal.** If you feel the need to write a paragraph, question
  the solution first: the name may be wrong, the function may do two things, or a constraint may be
  implicit that could be enforced in code — a guard, a type, a test. Enforcing a constraint beats
  describing it. If the story genuinely matters after that, link the ticket rather than retelling it.
- **Don't state what the code's presence already proves.** `apk add aws-cli` proves aws-cli was
  missing; a guard proves its condition is reachable; a retry proves the call is flaky. If deleting
  the line would delete the fact, the comment carries nothing.
- **Do comment code that is genuinely hard to read** — convoluted for performance, an awkward API, a
  protocol constraint. But needing to is a smell: try making it clearer first. A comment is the last
  resort when the code cannot be simplified, not a substitute for simplifying it.
- **"now", "no longer", "previously", "currently" are changelog tells.** A comment that only parses
  for someone who saw the previous version is a commit message in the wrong file.
- **A wrong comment is worse than no comment.** When you change code, re-read the comments around it
  and delete any that no longer hold.
- **No counts or inventories in prose.** "the four anchors that…", "~8 domains", "all three callers"
  — these are wrong the moment someone adds a fifth, and nothing fails when they drift. Name the
  thing or point at the source of truth. Applies equally to `README.md`, `CLAUDE.md` and skill docs.

## Worth the words

An invariant a future edit would silently break; a non-obvious ordering or dependency constraint; a
security or compliance rationale; a workaround for an external defect; godoc on exported
identifiers. Link a ticket only when the why is genuinely unrecoverable from the code — not as a
changelog.

## Applying to a diff

Read every comment the diff adds or touches, and for each one ask in order:

1. Does it restate the code? → delete it, or rename the thing it was explaining.
2. Does it only parse for someone who saw the previous version? → delete it.
3. Does this fact already live somewhere better? → leave a pointer, or nothing.
4. Is it longer than the code? → the design is the problem; fix that first.
5. Did the change make a nearby comment wrong? → that is a defect in the diff, fix it now.

Where a rationale is genuinely worth keeping but too long to sit inline, put it in the doc that owns
the subject and leave one line pointing there.
