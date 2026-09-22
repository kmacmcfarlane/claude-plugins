"""Reasoning-ledger helpers. The ledger is session-addressed (never in a repo):
an append-only markdown file of one-line entries the live session writes as it
works, so an end-of-window checkpoint is a delta rather than a reconstruction.

Line grammar:  - <D|X|C|U|R|Q|P> <text> [-> path]
  D decided  X rejected  C corrected  U unverified  R refused  Q open question
  P pointer (machine-written: commits, investigation writes)
"""
import os, time
import lib_context as L

KINDS = "DXCURQP"


def append(session_id, kind, text, ref=None):
    if kind not in KINDS or not text:
        return False
    line = f"- {kind} {text.strip()}"
    if ref:
        line += f" -> {ref}"
    try:
        p = L.ledger_path(session_id)
        new = not os.path.exists(p) or os.path.getsize(p) == 0
        with open(p, "a") as fh:
            if new:
                fh.write(f"# ledger {session_id}\n")
            fh.write(line + "\n")
        return True
    except Exception:
        return False


def epoch_header(session_id, epoch_n, tokens):
    try:
        with open(L.ledger_path(session_id), "a") as fh:
            fh.write(f"\n## epoch {epoch_n} — {time.strftime('%F %T')} — {tokens:,} tok\n")
    except Exception:
        pass


def tail(session_id, max_chars=4000):
    """Newest-first bounded read (raw, every kind alike). Re-injection after
    compaction uses digest(), which keeps reasoning ahead of pointers."""
    try:
        with open(L.ledger_path(session_id), errors="replace") as fh:
            lines = fh.read().splitlines()
    except Exception:
        return ""
    out, size = [], 0
    for ln in reversed(lines):
        if size + len(ln) > max_chars:
            break
        out.append(ln)
        size += len(ln) + 1
    return "\n".join(reversed(out))


# Digest tiers: R/C first (a refusal or correction outranks everything), then
# the rest of the reasoning (D/X/U/Q, and any hand-written line outside the
# grammar), then the machine-written P pointers, which are already durable in
# git or the repo and so are the first to go.
_TIER = {"R": 0, "C": 0, "D": 1, "X": 1, "U": 1, "Q": 1, "P": 2}


def _tier(line):
    if len(line) > 3 and line.startswith("- ") and line[3:4] in (" ", ""):
        return _TIER.get(line[2], 1)
    return 1


def digest(session_id, budget=2500):
    """Bounded read for re-injection after compaction, by kind rather than by
    recency: R and C lines from every epoch first (newest first, up to half
    the room), then D/X/U/Q ranked together newest first, then the remaining
    R/C, then P pointers newest first. A line too long for half the room is
    cut with a marker rather than dropped. The kept lines print in file order
    under their epoch headers (a header only when a kept line follows it), and
    when anything is left out a closing line counts it and names the ledger
    file. The whole result never exceeds `budget` chars. `# ` lines other than
    the plain `# ledger <sid>` title count as reasoning. The ledger itself is
    only read. Returns "" for a missing or empty ledger.
    """
    try:
        path = L.ledger_path(session_id)
        with open(path, errors="replace") as fh:
            lines = fh.read().splitlines()
    except Exception:
        return ""
    title = f"# ledger {session_id}"
    head_of, entries, cur = {}, [], None
    for i, ln in enumerate(lines):
        if ln.startswith("## "):
            cur = i
        elif ln.strip() and ln.strip() != title:
            head_of[i] = cur
            entries.append(i)
    if not entries:
        return ""
    disp = {i: lines[i] for i in entries}

    def render(keep):
        out, shown = [], set()
        for i in sorted(keep):
            h = head_of[i]
            if h is not None and h not in shown:
                shown.add(h)
                out += ([""] if out else []) + [lines[h]]
            out.append(disp[i])
        return out

    whole = "\n".join(render(entries))
    if len(whole) <= budget:
        return whole

    room = max(0, budget - 200 - len(path))   # the closing line's share
    cut = max(40, room // 2 - 80)             # fits the R/C pass with a header
    for i in entries:
        if len(disp[i]) > cut:
            disp[i] = disp[i][:cut - 6] + " [cut]"
    kept, heads, size = set(), set(), 0

    def take(idxs, limit):
        nonlocal size
        for i in idxs:
            if i in kept:
                continue
            h = head_of[i]
            cost = len(disp[i]) + 1
            if h is not None and h not in heads:
                cost += len(lines[h]) + 2          # header plus its blank line
            if size + cost > limit:
                continue
            kept.add(i)
            if h is not None:
                heads.add(h)
            size += cost

    newest = list(reversed(entries))
    by = {t: [i for i in newest if _tier(lines[i]) == t] for t in (0, 1, 2)}
    take(by[0], room // 2)
    take(by[1], room)
    take(by[0], room)
    take(by[2], room)
    left = [i for i in entries if i not in kept]
    np = sum(1 for i in left if _tier(lines[i]) == 2)
    nr = len(left) - np
    bits = [f"{n} {w}" for n, w in ((nr, "reasoning"), (np, "pointer")) if n]
    body = "\n".join(render(kept))
    for note in (f"[ledger digest: {' and '.join(bits)} line(s) left out, pointers "
                 f"first, then older reasoning by kind; the full ledger is {path}]",
                 f"[ledger digest: {len(left)} line(s) left out; {path}]"):
        out = (body + "\n" + note) if body else note
        if len(out) <= budget:
            return out
    return out[:budget]
