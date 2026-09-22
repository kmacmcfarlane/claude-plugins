# Probe discipline

Loaded from `investigate` Step 6c, when a probe reproduces a symptom or the plan turns on a
low-level nuance of a tool's behaviour. Step 6c names both rules; this file holds them in full.

## A reproducing probe's own parameters are suspects

A cause that *explains* the symptom is not the same as one you have *isolated*. Before
recording a root cause, vary the harness: anything present in every run — a flag you added to force
re-execution, a fixture, an env var — is an uncontrolled variable, not a constant. Re-run
without it. This is the failure mode that survives longest, because the wrong explanation
fits the evidence and looks confirmed by it; a plausible story plus real corroborating
numbers is exactly what an unisolated cause looks like from the inside.

## Read the tool's source for a low-level nuance

Not for ordinary usage — docs and `--help` are correct and cheaper for that. This is for the
narrow case where the answer turns on precisely *how* something behaves: whether a file is
overwritten or seeded once, whether a step runs on every invocation or only one subcommand,
what exactly gets written where, what happens when it runs twice. Documentation states intent
and rounds off edges; the plan may be resting on an edge.

Applies when the tool's source is reachable — a sibling repo, a vendored dependency, an
installed package. When it is not, say the claim is from documentation and mark it for
`implement` to re-verify. A verified nuance carries `file:line` like any other finding, and
frequently deletes a hazard outright rather than mitigating it.
