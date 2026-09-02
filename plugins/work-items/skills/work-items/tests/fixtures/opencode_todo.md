# TODO

Work that is ready to pick up. Items promoted from `WATCH.md` land here once
they become actionable; investigated items point at their series under
`.claude-sandbox/investigations/`.

## Open

- [ ] **Make ComfyUI a systemd unit on lucy so GPU consumers can't collide**
      A model loaded while ComfyUI holds VRAM is placed on CPU permanently —
      cost us a session at 2.4 t/s instead of 40 (2026-08-28). ComfyUI is
      currently started ad hoc, so there is nothing for systemd to arbitrate:
      only `llama-router` and `ollama` are units on lucy.
      As a unit it could declare `Conflicts=llama-router.service` (or the
      reverse), making the collision impossible rather than merely detectable.
      Interim mitigations already in place: `scripts/start.sh` prints GPU
      state at launch, `llama-router.sh --check` diagnoses placement, and
      `reload_models.sh` fixes it.
      Consider the same treatment for Forge and text-generation-webui.

- [ ] **Find a small fast model to pair with the daily driver**
      The router supports co-residency via `--models-max N` (currently `1`), so
      a tiny model could stay loaded alongside the main one for sub-agent and
      low-stakes work without evicting it.
      Budget: the daily driver (Qwen 3.8 27B Q6_K_L) uses 63 of 96 GiB at
      4×256K, leaving ~31 GiB — enough for a small model plus its KV cache, or
      more if the main model's context is reduced.
      Wants: strong tool-calling, high tokens/sec, small enough to leave real
      headroom. Benchmark per CLAUDE.md's "Adding a New Model" procedure and
      confirm the pair co-fits before raising `--models-max`.
      Note: with `--models-max 2` the router evicts least-recently-used on
      demand, and `last_used` is bumped only by POST requests — a model kept
      alive by GETs alone can still be evicted.

- [ ] **Warm model switching**
      A switch currently costs a full 30-60 s weight load from ZFS. This build
      has no TTL flag, and `--sleep-idle-seconds` frees VRAM and wakes via a
      full `load_model`, so nothing keeps weights resident across a switch.
      Worth revisiting if upstream adds a warm-standby mode, or if a faster
      storage tier for the hot models is worthwhile.

## Done

- [x] **On-demand model switching** — adopted llama.cpp's native router
      (`--models-preset`) on 2026-08-24, rather than llama-swap as originally
      planned. The OpenCode dropdown now genuinely switches the model on lucy.
      Series: [`.claude-sandbox/investigations/llama-swap-model-switching/`](.claude-sandbox/investigations/llama-swap-model-switching/INDEX.md)
