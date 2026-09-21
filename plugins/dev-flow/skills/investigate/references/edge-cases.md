# Edge cases

Loaded from `investigate` when a run goes off the main path. Most of these restate a step's
rule at the point you are likely to need it; a few live only here (a named path missing in a
container, every question deferred, a sweep with no candidates, a problem that is several).

- **No argument and nothing in the conversation to anchor on** — ask for an observable symptom,
  a component, or a goal. Do not guess a problem.
- **Description is thin** — expected. Step 2 fills it in. Only stop when there is nothing to
  anchor on at all.
- **`TODO.md` does not exist** — say so, treat the argument as ad hoc text, do not create it.
- **Slug already exists** — re-investigation. Read the whole series first, confirm intent, then
  write the *next* serial. Never edit an existing file.
- **`.claude-sandbox/` not scaffolded** — warn once, continue, recommend `claude-sandbox init`.
  Never create `.claude-sandbox/CLAUDE.md`.
- **Repo has no local checkout** — ask: path, clone, or exclude. Never clone silently.
- **Branch survey finds nothing** — one line saying every repo bases off its default. No empty
  table.
- **A non-default base looks right** — explicit `AskUserQuestion` consent, never silent.
- **Requirements gate unresolved** — do not build the plan. Loop until the user confirms.
- **An answer at the gate opens a question the code can settle** — go back to Steps 4–8 and
  settle it, then resume the gate. Interleaving is expected.
- **A path the user names does not exist** — inside a claude-sandbox container only the project
  and configured mounts are visible, and a symlinked host path appears elsewhere. Check the
  `mounts:` cascade before reporting it unreachable; the `sandbox` skill has the procedure.
- **Tempted to write an Open Question** — triage it first
  (`references/investigation-format.md`). Verifiable → verify it. Requirement → ask at Step 9.
- **Background agent returns "could not determine"** — that becomes an Open Question, or a user
  question if a decision would settle it. Never promote a guess to a finding.
- **User defers every question** — legitimate. Record each with owner and blocks-or-not, and
  do not re-ask on the next loop iteration.
- **Sweep finds no candidates** — say so in one line at the gate and move on.
- **No relevant code found anywhere** — still write the plan; say so in Existing Architecture
  and suggest where else to look.
- **User rejects at the gate** — nothing written. Confirm that to the user.
- **Problem turns out to be several problems** — say so, and propose one series each rather
  than one plan covering all of them. Cross-reference the sibling slugs in each Out of Scope.
