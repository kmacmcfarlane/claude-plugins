# Retrospective

Loaded from `investigate` Step 16, which is optional and user-gated.

Offer a lightweight retrospective so the skills improve from real use:

```text
Run a quick retrospective on this investigate run and update the skill docs?
* Yes — capture stumbles, gotchas, and undocumented steps, then update the skills
* No — skip
```

If **Yes**: note where the run hit friction — a missed search idiom, an undocumented step, a
wrong assumption — then **read and follow `update-kit`'s SKILL.md**. It owns the mechanics:
locating the real checkout rather than the plugin cache, settling the branch, the staleness
check, and the context-cost bar for what earns a place in a skill. Do not re-derive any of
that here.

`update-kit` is `disable-model-invocation: true`, so it is **user-invoked only and cannot be
called through the Skill tool** — open its `SKILL.md` from the `claude-plugins` checkout and
follow it directly.

The likely targets are the `investigate` skill, `investigation-format.md`, and any project
skill whose gap cost you time during the run.
