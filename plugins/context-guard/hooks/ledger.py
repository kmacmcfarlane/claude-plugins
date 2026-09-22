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


def _lock(fh):
    """An exclusive advisory lock on the open ledger, released when it is
    closed. SessionStart(clear) runs postcompact_epoch.py (the epoch header)
    and rehydrate.py (successor_title) side by side on the same new ledger;
    the lock keeps the title's rewrite from losing the header. Best effort."""
    try:
        import fcntl
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
    except Exception:
        pass


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
            _lock(fh)
            if new:
                fh.write(f"# ledger {session_id}\n")
            fh.write(line + "\n")
        return True
    except Exception:
        return False


def epoch_header(session_id, epoch_n, tokens):
    try:
        with open(L.ledger_path(session_id), "a") as fh:
            _lock(fh)
            fh.write(f"\n## epoch {epoch_n} — {time.strftime('%F %T')} — {tokens:,} tok\n")
    except Exception:
        pass


def successor_title(session_id, predecessor):
    """A linked /clear successor's ledger starts `# ledger <sid> (successor
    of <predecessor>)`, so the lineage is in the file, not only in state. It
    is put first whether or not the epoch header got there before it; a
    ledger that already starts with a `# ledger` title is left alone. digest()
    keeps this line (it is not the plain title), so it survives the
    successor's own compactions. True when it wrote. Never raises."""
    try:
        with open(L.ledger_path(session_id), "a+", errors="replace") as fh:
            _lock(fh)
            fh.seek(0)
            body = fh.read()
            if body.startswith("# ledger "):
                return False
            fh.seek(0)
            fh.truncate()
            fh.write(f"# ledger {session_id} (successor of {predecessor})\n"
                     + body)
        return True
    except Exception:
        return False


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
    when anything is left out or cut a closing line counts it and names the
    ledger file. The whole result never exceeds `budget` chars; a budget too
    small for even the short closing line gives "". `# ` lines other than
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
    ncut = sum(1 for i in kept if disp[i] != lines[i])
    body = "\n".join(render(kept))
    if not left and not ncut:
        return body
    np = sum(1 for i in left if _tier(lines[i]) == 2)
    nr = len(left) - np
    said = []
    if left:
        bits = [f"{n} {w}" for n, w in ((nr, "reasoning"), (np, "pointer")) if n]
        said.append(f"{' and '.join(bits)} line(s) left out, pointers first, "
                    f"then older reasoning by kind")
    if ncut:
        said.append(f"{ncut} line(s) cut")
    short = ", ".join(x for x in (f"{len(left)} left out" if left else "",
                                  f"{ncut} cut" if ncut else "") if x)
    for note in (f"[ledger digest: {'; '.join(said)}; the full ledger is {path}]",
                 f"[ledger digest: {short}; {path}]"):
        out = (body + "\n" + note) if body else note
        if len(out) <= budget:
            return out
    return ""   # not even the short note fits: say nothing rather than a stub
