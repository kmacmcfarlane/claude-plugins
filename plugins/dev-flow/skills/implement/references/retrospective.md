# Retrospective

Loaded from `implement` Step 12, which is optional and user-gated. Offer it with:

```text
Run a quick retrospective on this implement run and update the skill docs?
* Yes — capture stumbles, gotchas, and undocumented steps, then update the skills
* No — skip
```

If **Yes**: note where the run deviated from the steps or hit friction — an undocumented
workflow, a wrong assumption, a gotcha that cost time. Derive those findings from the skill
files in the **checkout**, not the copy you are running from: the plugin cache lags the repo,
and a finding diffed against it may already be fixed upstream. Then present them and **ask
the user to run `/kit-dev:update-kit`**. That skill is `disable-model-invocation: true`, so
it is user-invoked only and cannot be launched from here; do not replicate its workflow by
other means. It owns locating the real checkout rather than the plugin cache, settling the
branch, the staleness check, and the bar for what earns a place in a skill. Do not re-derive
any of that here.

Likely targets: the `implement` skill, `worktree-orchestration.md`, `investigation-format.md`,
and any project skill whose gap cost you time.
