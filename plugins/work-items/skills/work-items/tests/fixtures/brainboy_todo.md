# TODO — brainboy & the wider mcfacehead backup estate

Open items that are agreed but not yet done. Cross-repo entries live here because
brainboy is where the backup estate is coordinated from; each entry names the repo
it actually lands in.

---
## TrueNAS SCALE upgrade — research the path before touching anything

**Current:** TrueNAS SCALE **24.04.1.1 "Dragonfish"** (`/etc/version`).
**Want:** latest stable.

iXsystems changes direction between releases often enough that the upgrade path
matters more than the destination. Research before scheduling:

- **Map the release train from 24.04.** Dragonfish (24.04) → ElectricEel (24.10) →
  Fangtooth (25.04) → whatever is current. Confirm which hops are supported
  directly and which require an intermediate stop; TrueNAS does not always allow
  skipping a train.
- **The k3s/ix-applications removal.** The apps platform was replaced with Docker
  Compose in 24.10/25.04. `tank/ix-applications` (25.7G) and `tank/openebs*` are
  already vestigial here — real workloads moved to the Talos VM — so confirm the
  upgrade will not try to migrate or trip over them. Consider destroying them
  first (see below), which also removes their monitor exclusions.
- **API/middleware changes.** `midclt` call signatures move between versions.
  Known already: `cloudcredential.query` does not exist on 24.04 (it is
  `cloudsync.credentials.query`). The backup monitor calls `cloudsync.query`,
  `replication.query`, `pool.snapshottask.query` and reads `job.state` /
  `time_finished` / `{"$date": ms}` wrappers — re-run `--dry-run` immediately after
  any upgrade and expect at least one of these to have shifted.
- **VM subsystem — the highest-risk part, and the least understood.** 25.04
  replaced libvirt/QEMU VM management with **Incus 6.0.3**, then **25.04.2
  brought classic libvirt VMs back**, so both stacks ship in the Fangtooth
  train. **What actually happens to the two existing VM definitions across that
  path is UNVERIFIED and must be answered before scheduling the upgrade:**
    - Are existing libvirt-defined VMs migrated to Incus automatically, left on
      the libvirt stack, or do they need manual recreation?
    - If recreated, what carries over — the zvol disk devices, the PCI
      passthrough (GPU), the USB passthrough (HA's two radios, currently keyed
      by port path `usb_5_1`/`usb_5_2`), the MAC addresses, the SPICE config?
    - Does the 25.04.2 libvirt restoration mean an upgrade can *stay* on
      libvirt, avoiding the migration entirely?
    - `talos` is the k8s control plane and its disk is now a zvol on `vm-pool`;
      `home_assistant` runs the house. Neither tolerates a "recreate it and
      hope" migration.
  Note the VM disks are no longer on `tank` — that moved to `vm-pool`
  2026-08-28. Also note **Incus does not configure a QEMU iothread either**
  (verified in Incus 6.0.3/6.10.0/main source), so the upgrade buys the kernel
  fix, not the etcd latency fix.
- **Cron jobs.** Confirm `cronjob.query`/`cronjob.create`-managed jobs survive the
  upgrade (jobs 2/3/4 = producers, plus the monitor job).
- **Snapshot before upgrading**, and read the release notes' "known issues" for
  every hop, not just the last one.

## ~~Discord webhook key rename~~ — DONE 2026-08-06 (clustertool repo)

Alertmanager's keys now name their channels: `DISCORD_WEBHOOK_MCFACEHEAD_KUBE_APPS`
(general) and `DISCORD_WEBHOOK_MCFACEHEAD_BACKUPS`, alongside the existing
`..._MEDIA` in `clusterenv.yaml`. `alertmanagerconfig.yaml` updated to match.
brainboy's `secrets.env` keeps `DISCORD_WEBHOOK_URL` — that is the monitor's own
config key, not the cluster secret, so there is no longer a collision.

**Near-miss worth remembering:** the old key was initially *replaced* rather than
added alongside, leaving the secret with three keys while the manifest still
referenced four. Alertmanager rejects its **entire** config on a missing key — so
email, #backups and the Watchdog heartbeat would all have stopped together, with
the healthchecks dead-man's switch firing only afterwards because Watchdog went
quiet. Caught before pushing by cross-checking every `key:` in the manifest against
the keys present in the secret; that check is now written into clustertool
`docs/monitoring.md` and should be run whenever either file changes.

Still outstanding in that file: the **header comment** says
`forgetool decrypt -> edit -> forgetool encrypt`. Fix to `clustertool` during the
next decrypt/encrypt cycle — it is the last stale `forgetool` reference anywhere,
left alone because hand-editing an encrypted file risks its MAC.

## ~~HIGH — lucy offsite incrementals contain no data~~ — FIXED 2026-08-06

→ **`plans/2026-08-05-lucy-archiver-incremental-bug.md`** (implementation log at the end)

The monthly base is now anchored by a ZFS **bookmark** (`#archbase-<month>`)
instead of a snapshot. Bookmarks are not snapshots, so the hourly forced receive
leaves them alone — confirmed live: a bookmark survived a replication cycle that
destroyed three snapshots on the same dataset. The archiver also fails loudly
(non-zero exit) rather than manufacturing a base, and treats a full with no
matching bookmark as orphaned, rewriting it and purging that month's
incrementals, which is what makes the fix self-healing across the cutover.

Remaining, spun out of that work:

- ~~**`repos` (338G) has no offsite backup at all.**~~ **DONE 2026-08-15** —
  added to the archiver `allowlist`. It was never covered, despite the plan's
  original symptom table listing it as "not sampled", which read as though it
  were. Most of it is third-party checkouts recoverable from their origins, but
  it carries the local modifications that are not: start scripts and config
  tweaks as uncommitted changes inside a dozen upstream clones, with no remote of
  ours to push to. Deferred until after the snapshot retention reduction, which
  brought it from 338G to ~290G before its first full was written.
- **`-R` fulls carry the entire snapshot history.** ~~Every ai-main dataset holds
  ~4,690 snapshots~~ — as of the 2026-08-14 cleanup, ~89. `zfs send -R` embeds
  all of them, so restore time scales with snapshot count rather than data size:
  ~15.6 hours of pure metadata replay for a full seven-dataset restore, now
  **~17 minutes**. **Settled: keep `-R`** — the retention reduction removed the
  cost that made `-p` tempting, and `-R` preserves offsite point-in-time
  recovery. Do not switch to `-p`
  purely for storage — the measured saving is ~38G of a ~1.4T monthly upload,
  because `models-custom` dominates the upload but carries almost no history.
- **Size-anomaly check for the backup monitor.** Freshness checking cannot tell
  useful output from worthless output; this bug shipped daily, on time, correctly
  named, for a month. A flat threshold will not work — `guides` legitimately
  produces 624 bytes while `models-custom` produces terabytes. The tell was that
  *every incremental was identical across datasets of wildly different sizes*.

## STILL OPEN — replication task 3's destination retention is a no-op

The orphans above will come back at **~192/day** until this is fixed.

Task 3 selects snapshots with `name_regex`, and zettarepl's target-side
retention is driven *only* by naming schemas:

```python
# zettarepl/replication/task/naming_schema.py
def replication_task_naming_schemas(replication_task):
    return (set(pst.naming_schema for pst in replication_task.periodic_snapshot_tasks)
            | set(replication_task.also_include_naming_schema))
```

Both inputs are empty for this task, so it parses zero destination snapshots and
deletes none. `retention_policy: SOURCE` under `name_regex` is silently
guaranteed to prune nothing — and `task.py` explicitly permits the combination.

The fixing `midclt call replication.update 3 …` is written out in
`plans/2026-08-05-snapshot-retention-reduction.md`. **It was deliberately not
applied**, for two reasons:

1. Ordering. Applying it while a large orphan set exists makes the next `:15`
   run delete them all in one unthrottled burst. That is now moot — the orphans
   are gone — so this is safe to apply whenever.
2. It rewrites the same task record the lucy archiver work touches, and
   `replication.update` is last-writer-wins. Coordinate before applying.

It has never been executed, so TrueNAS has never validated it. Verify
afterwards that `zfs list -t snapshot -r tank/lucy | wc -l` stays flat over a
few days rather than climbing.

## LOW — Move the boot device off the 2011 OCZ Vertex3

Raised 2026-08-28 after the ROMED8-2T swap, on a hunch that the boot drive was
behind sluggish TrueNAS UI response. **The measurements do not support that
diagnosis, but they do support replacing the drive for a different reason.**

**Why it is probably not the UI slowness.** Measured on the Vertex3:

| | |
|---|---|
| `boot-pool` fsync p50 / p99 | 0.403 ms / 0.444 ms |
| `/data` (middleware sqlite) | `freenas-v1.db` is 864 KB, dataset 1% used |
| `boot-pool` | 56% capacity, 53% fragmentation, scrub clean |

A 0.444 ms p99 is not what a laggy web UI looks like. The sluggishness was
observed while load average was **60+ with 29% iowait**, during the Talos VM's
post-reboot etcd recovery against `tank`. Once that settled the same host sat at
**load 4.07, 87% idle**. The UI was starved by `tank` contention and CPU, not by
the boot device. Re-measure UI responsiveness after the `vm-pool` migration
before spending money on this — the migration removes the actual cause.

**Why replace it anyway — reliability, not speed.** The Vertex3 is a 2011
consumer SSD with:

- **33,441 power-on hours** (~3.8 years continuous)
- **SSD_Life_Left 88%**, 84 TB lifetime writes
- **No power-loss protection**
- **Single device — `boot-pool` is not mirrored.** Its death is a config-restore
  event, not a resilver.

The config is backed up daily to `offsite-backup-staging/truenas/` with 365-day
retention, so this is a recoverable failure, not a catastrophic one. That is what
makes it low priority rather than urgent.

**If done, do it properly:** the ROMED8-2T has **two M.2 slots, and both are live
under the jumper position already set** (position B — see
`.claude-sandbox/investigations/motherboard-replacement/09_romed8-2t-config.md`
and `10_swap-outcome.md`):

| Slot | Gated? | Length | Interface |
|---|---|---|---|
| `M2_1` | Yes, by the PCIE2 jumpers — **enabled under B** | 2280 | SATA3 / PCIe |
| `M2_2` | No, always live | **22110** | SATA3 or PCIe 4.0 x4 |

So a **mirrored NVMe `boot-pool`** is available for the first time on this
machine, with no jumper change and no card. Boot-pool mirroring is the actual win
here; raw speed is not. Note the length difference — `M2_1` takes 2280 only, so
buy two 2280 drives rather than one of each.

## Extend the SOPS pre-commit hook with entropy/pattern detection (clustertool repo)

`scripts/check-sops-encryption.sh` currently catches two shapes: files matching a
`.sops.yaml` `path_regex`, and any `kind: Secret` whose `data`/`stringData` is not
`ENC[...]`. That covers **one** of the two plaintext leaks this repo has actually
had:

- 2025-08-20 Cloudflare token in `cloudflare-api-token-secret.yaml` — a
  `kind: Secret`. **Caught** (verified by replaying the real blob).
- 2025-12-28 gluetun API key + qBittorrent `admin`/`adminadmin` in
  `apps/qbittorrent/app/helm-release.yaml` — plain Helm *values*, not a Secret
  object. **Still slips through today.**

So the gate has a known hole in exactly the shape that is easiest to create
accidentally: a credential pasted into ordinary app values.

Add a third pass over all tracked YAML, independent of filename and kind:

- literal patterns: `discord.com/api/webhooks/\d+/`, `hc-ping.com/<uuid>`,
  `AKIA[0-9A-Z]{16}`, `BEGIN [A-Z ]*PRIVATE KEY`, `AGE-SECRET-KEY-`, `xox[bp]-`,
  `gh[pousr]_`
- high-entropy values (≥20 chars, mixed case+digits, Shannon entropy over a
  threshold) under keys matching `pass|password|token|apikey|api_key|secret|key`

Must **not** fire on:
- `${VAR}` Flux substitution placeholders (values are injected at apply time)
- `credentials: backup_s3` and similar — a credential *name*, not a value
- `ENC[AES256_GCM,...]` ciphertext, and base64 blobs inside a `sops:` block
- `iv:`/`mac:` fields, which are base64 and will trip naive entropy checks

Budget a false-positive tuning pass against the whole existing tree before wiring
it in: a gate that cries wolf gets bypassed with `--no-verify`, which is strictly
worse than not having it. Test it by replaying the 2025-12-28 blob
(`git show 65fc8859:clusters/main/kubernetes/apps/qbittorrent/app/helm-release.yaml`)
and confirming it fails the commit.

