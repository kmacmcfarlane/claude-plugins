#!/usr/bin/env python3
"""Where did the context window go?  Forensics over a Claude Code transcript.

    context_forensics.py [transcript.jsonl]        # default: newest for this cwd

Reads the session's .jsonl and reports, per compaction segment:
  - the token trajectory (from each assistant message's `usage`, i.e. what the
    API actually charged) with compaction boundaries and their preTokens
  - what filled the window: tool results by tool, assistant output, user text,
    and the harness's own attachments (hook output, file-change diffs, skill
    listings) which never appear in the terminal
  - the biggest single injections, so the avoidable ones can be named
  - model switches (each is a full prompt-cache rebuild)
  - whether hidden thinking was persisted (it is not; this proves it per file)

Output is ~60 lines. Read the whole thing before drawing a conclusion: the
point of the tool is that the obvious suspect (tool output) is usually not
the main consumer.
"""
import collections, glob, json, os, sys


def newest_transcript():
    cfg = os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"))
    slug = os.getcwd().replace("/", "-")
    paths = glob.glob(os.path.join(cfg, "projects", slug, "*.jsonl"))
    paths = [p for p in paths if "/subagents/" not in p]
    return max(paths, key=os.path.getmtime) if paths else None


def size_of(content):
    if isinstance(content, str):
        return len(content)
    if isinstance(content, list):
        return sum(len(x.get("text", "")) for x in content if isinstance(x, dict))
    return 0


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else newest_transcript()
    if not path or not os.path.exists(path):
        sys.exit("no transcript found; pass a path")

    seg = 0
    segs = [dict(out=0, msgs=0, prompts=0, tools=collections.Counter(), calls=collections.Counter(),
                 att=collections.Counter(), user_text=0, asst_text=0, peak=0, pre=None)]
    traj, jumps, models, biggest = [], [], [], []
    pending, thinking_n, thinking_chars = {}, 0, 0
    prev_tok, prev_model, n = 0, None, 0

    with open(path, errors="replace") as fh:
        for line in fh:
            n += 1
            try:
                d = json.loads(line)
            except Exception:
                continue
            t = d.get("type")
            s = segs[seg]

            if t == "system" and d.get("subtype") == "compact_boundary":
                meta = d.get("compactMetadata") or {}
                s["pre"] = meta.get("preTokens")
                traj.append((n, "COMPACT", meta.get("preTokens") or prev_tok, meta.get("trigger")))
                seg += 1
                segs.append(dict(out=0, msgs=0, prompts=0, tools=collections.Counter(),
                                 calls=collections.Counter(), att=collections.Counter(),
                                 user_text=0, asst_text=0, peak=0, pre=None))
                prev_tok = 0
                continue

            if t == "attachment":
                a = d.get("attachment") or {}
                k = a.get("type", "?")
                if k == "hook_success":
                    k = f"hook:{a.get('hookName', '?')}"
                sz = len(json.dumps(a))
                # A payload the harness persisted to a file reached the model
                # only as a short stub - count the stub, not the emission.
                # Measured: 13 of 98 SessionStart payloads were stubs; counting
                # emissions overstated hook cost ~15x for that kind.
                if "<persisted-output>" in json.dumps(a):
                    s["att_emitted"] = s.get("att_emitted", 0) + sz
                    sz = 400
                s["att"][k] += sz
                biggest.append((sz, f"attachment {k}", ""))
                continue

            m = d.get("message") or {}
            c = m.get("content")
            if t == "assistant":
                s["msgs"] += 1
                u = m.get("usage") or {}
                s["out"] += u.get("output_tokens") or 0
                tok = sum(u.get(k) or 0 for k in
                          ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
                if tok:
                    traj.append((n, "a", tok, None))
                    s["peak"] = max(s["peak"], tok)
                    if prev_tok and tok - prev_tok > 15000:
                        jumps.append((tok - prev_tok, n, prev_tok, tok))
                    prev_tok = tok
                mdl = m.get("model")
                if mdl and mdl != "<synthetic>" and mdl != prev_model:
                    models.append((n, mdl, tok))
                    prev_model = mdl
                if isinstance(c, list):
                    for b in c:
                        bt = b.get("type")
                        if bt == "thinking":
                            thinking_n += 1
                            thinking_chars += len(b.get("thinking") or "")
                        elif bt == "tool_use":
                            pending[b.get("id")] = (b.get("name"), json.dumps(b.get("input"))[:80])
                            s["calls"][b.get("name")] += 1
                            s["tool_in"] = s.get("tool_in", 0) + len(json.dumps(b.get("input")))
                        elif bt == "text":
                            s["asst_text"] += len(b.get("text", ""))
            elif t == "user":
                if isinstance(c, str):
                    s["prompts"] += 1
                    s["user_text"] += len(c)
                elif isinstance(c, list):
                    for b in c:
                        if b.get("type") == "tool_result":
                            name, inp = pending.get(b.get("tool_use_id"), ("?", ""))
                            sz = size_of(b.get("content"))
                            s["tools"][name] += sz
                            biggest.append((sz, name, inp))
                        elif b.get("type") == "text":
                            s["prompts"] += 1
                            s["user_text"] += len(b.get("text", ""))

    print(f"transcript: {path}\nrecords: {n}   segments: {len(segs)}   "
          f"thinking blocks: {thinking_n} persisted chars: {thinking_chars:,}"
          + ("   <- hidden reasoning is NOT on disk" if thinking_n and not thinking_chars else ""))

    for i, s in enumerate(segs):
        tool_tok = sum(s["tools"].values()) // 4
        att_tok = sum(s["att"].values()) // 4
        print(f"\n== segment {i}: {s['prompts']} user turns, {s['msgs']} assistant msgs, "
              f"peak {s['peak']:,} tok" + (f", compacted at {s['pre']:,}" if s["pre"] else ""))
        print(f"   assistant output (text+thinking) : {s['out']:>9,} tok generated  "
              f"(text alone ~{s['asst_text'] // 4:,})")
        print(f"   tool-call inputs (Write payloads): {s.get('tool_in', 0) // 4:>9,} tok")
        print(f"   tool results                     : {tool_tok:>9,} tok")
        print(f"   user-turn text                   : {s['user_text'] // 4:>9,} tok  "
              f"(incl. pasted output, compaction summaries)")
        emitted = s.get("att_emitted", 0) // 4
        print(f"   harness attachments (accepted)   : {att_tok:>9,} tok  (hooks, diffs, listings"
              + (f"; +{emitted:,} emitted but persisted-to-file, never in context" if emitted else "") + ")")
        visible = (s["asst_text"] + s.get("tool_in", 0) + s["user_text"]) // 4 + tool_tok + att_tok
        if s["peak"]:
            print(f"   visible categories sum to {visible:,} of peak {s['peak']:,}; "
                  f"the remaining ~{100 - 100 * visible // s['peak']}% is retained thinking "
                  f"(+ system prompt and tool definitions)")
        top = s["tools"].most_common(5)
        if top:
            print("   tool results by tool: " + ", ".join(
                f"{k.split('__')[-1]}={v // 4:,}({s['calls'][k]})" for k, v in top))
        topa = s["att"].most_common(4)
        if topa:
            print("   attachments by kind : " + ", ".join(f"{k}={v // 4:,}" for k, v in topa))

    print("\n== biggest single injections (tokens ~ chars/4) ==")
    for sz, name, inp in sorted(biggest, reverse=True)[:10]:
        print(f"   {sz // 4:>8,}  {name.split('__')[-1]:<34} {inp}")

    print("\n== biggest single-step jumps in context ==")
    for dlt, ln, a, b in sorted(jumps, reverse=True)[:6]:
        print(f"   +{dlt:>8,}  line {ln}  {a:,} -> {b:,}")

    if len(models) > 1:
        print("\n== model switches (each rebuilds the prompt cache) ==")
        for ln, mdl, tok in models:
            print(f"   line {ln}: {mdl} at {tok:,} tok")

    print("\n== trajectory (every ~10%) ==")
    last_pct = -10
    for ln, k, tok, trig in traj:
        if k == "COMPACT":
            print(f"   line {ln}: ---- compact ({trig}) at {tok:,} ----")
            last_pct = -10
            continue
        pct = tok // 100_000 * 10
        if pct >= last_pct + 10:
            print(f"   line {ln}: {tok:,}")
            last_pct = pct


main()
