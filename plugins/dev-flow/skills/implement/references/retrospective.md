# Retrospective

Loaded from `implement` Step 12, which is optional and user-gated. Offer it with:

```text
Run a quick retrospective on this implement run and update the skill docs?
* Yes — capture stumbles, gotchas, and undocumented steps, then update the skills
* No — skip
```

If **Yes**: note where the run deviated from the steps or hit friction — an undocumented
workflow, a wrong assumption, a gotcha that cost time. Derive each finding from the skill
files in the **checkout**, not the copy you are running from: the plugin cache lags the repo,
and a finding diffed against it may already be fixed upstream. Present the findings, then hand them off by
one rule: **ask the user to run `/kit-dev:update-kit`** — never launch it through the Skill
tool, never read its SKILL.md and replicate it. It is `disable-model-invocation: true`, so it
is user-invoked only, and it owns locating the real checkout rather than the plugin cache,
settling the branch, the staleness check, and the bar for what earns a place in a skill.

`kit-dev` is a soft dependency. A user-invoked-only skill never shows in your
available-skills list, so you cannot tell from here whether it is installed; say that without
`kit-dev` the presented findings are the record, and edit a skill file only if the user asks.

Likely targets: the `implement` skill, `worktree-orchestration.md`, `investigation-format.md`,
and any project skill whose gap cost you time.
