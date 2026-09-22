# Resolving the issue

Loaded from `investigate` Step 1, to resolve the argument. Step 1 names each case's rule; this
file holds them in full.

The argument is a problem description, a pointer to one, or absent.

**A work-item reference** (an id like `etcd-alerting-3f9a`, or a title fragment, in a repo
with a `.work/` or `.claude-sandbox/work/` store): resolve it with the `work-items` skill's
CLI — `wi show <id>` for an id, `wi ls --plain` to match a fragment — and use the item's
description and `## Handoff` block as the starting description. `wi claim` it once the
investigation begins. With **no argument** in such a repo, offer `wi next --plain` (the
ready-ranked queue) before falling back to the conversation.

**A TODO.md reference** (`TODO.md item 3`, `the second TODO`, or just a phrase matching one) —
the fallback when no work-item store exists: read `TODO.md` from the repo root, find the
matching `- [ ]` item, and use its text as the starting description. A `TODO.md` that carries
the work-items deprecation notice means the store has moved — use `wi`, do not resurrect the
file. If `TODO.md` does not exist, say so and treat the argument as ad hoc text. Do not create
`TODO.md`.

**An existing slug** (matches a directory under `.claude-sandbox/investigations/`): this is a
re-investigation. Go to Step 1a.

**Ad hoc text**: use it as the starting description.

**No argument**: take the problem from the conversation so far — the error, the failure, the
finding that prompted this. If the conversation gives you nothing to anchor on, ask.

**The description you start with is expected to be thin.** Filling it in is the job, not a
precondition — Step 2 exists for exactly that. What you cannot proceed without is *something
to anchor on*: an observable symptom, a named component, a file, or a stated goal. If you have
none of those, ask for one before continuing.
