# TODO

- **Require the `pre-commit` check on `main` via branch protection / ruleset.**
  A GitHub repo setting, not a file, so it cannot be done from here. Renovate
  PRs auto-merge into `main` and Flux deploys `main` to the cluster, so the merge
  gate is effectively a deploy gate.
  `.github/workflows/automerge.yaml` now refuses to merge unless the `Lint`
  workflow concluded `success`, which closes the immediate hole, but that gate
  lives inside the one workflow it names. Branch protection is the layer that
  covers *every* merge path — including merging by hand in the UI — and lets new
  checks be required without editing YAML. `pascalgn/automerge-action` already
  handles it: a required check that has not passed leaves the PR
  `mergeable_state: blocked`, and the configured `UPDATE_RETRIES: 24` /
  `UPDATE_RETRY_SLEEP: 60000` gives it ~24 minutes to go green.
  Watch for: a required check that never reports (e.g. the workflow gets
  renamed) blocks every PR until someone notices.

- **Check back on Prometheus TSDB compaction.** `PrometheusTSDBCompactionsFailing`
  fired 2026-08-13 on `corruption in segment /prometheus/wal/00000066 ...
  unexpected full record` — every 2h head compaction failing, so the WAL never
  truncated and grew to 604MB. Fixed by removing `/prometheus/wal` and
  `/prometheus/chunks_head` and restarting; blocks were untouched and no
  historical data was lost. **Verify a compaction has since succeeded** —
  `increase(prometheus_tsdb_compactions_failed_total[3h])` should stay 0 and the
  WAL should be truncating rather than only growing.
  Two things make this worth revisiting rather than closing: the corruption
  appeared *during normal operation* (Prometheus started clean at 20:26 and
  logged every block healthy), and ZFS reports no errors on `tank/vm`, so the
  cause is unexplained. If it recurs, suspect the disk before Prometheus.
  Note a restart alone is **not** sufficient — the first attempt looked fine but
  restored from a chunk snapshot and never touched the corrupt segment; the tell
  was `checkpoint.00000064` still sitting at its pre-failure timestamp.

- **Revisit `disableCompaction: true` (after the WAL work above).** Set in the
  kube-prometheus-stack HelmRelease, inherited from the original clustertool
  install rather than chosen, and there is no Thanos here to justify it. It keeps
  every 2h block forever, which steadily grows file count and I/O against the
  disk that is this cluster's binding constraint. Sequence matters: confirm
  compaction is healthy first, because turning this on will start real block
  compaction and that is I/O the pool currently cannot spare — do it after the
  brainboy storage fixes, not before.

