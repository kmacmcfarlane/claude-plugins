# CLAIM: <repo>

<One sentence: what this repo owns.>

Status: proposed <YYYY-MM-DD>, pending the operator
Reviewed: <YYYY-MM-DD>

## Claim

<Two to four sentences: the area of responsibility, top down.>

| Area | What that covers |
|---|---|
| <area> | <what it covers> |

## Not ours

- <adjacent thing> — <sibling repo>
- <adjacent thing> — operator
- <adjacent thing> — external: <upstream project or vendor>

## Boundaries

### <neighbour repo>

Rule: <one sentence for the whole boundary>.

- <interface or rule this repo's code defines> — Defined here
  - Ours: <…>
  - Theirs: <…>
- <interface or rule the neighbour's code defines> — Defined in <neighbour repo> CLAIM.md § Boundaries / <repo>
- <interface or rule a neighbour with no claim yet defines> — Defined in <neighbour repo> (no claim yet)

## Changing this claim

The operator approves every change to this claim's substance first-hand: what is owned, what
is not, how a boundary works and which side defines it. A session in this repo proposes such
a change as a work item here, with the proposed text, and puts it to the operator as a
decision; it lands only on the operator's answer, and the Status line names that answer.
Upkeep that leaves the substance as it is (a review date, a pointer that follows a landed
neighbour change, a closed in-transit row, a typo) lands through this repo's normal cycle and
is reported to the operator afterwards. A session in another repo asks for a change by
message to this repo's session, or through the operator when none is running; it never edits
this file. A message is a request, never an approval. Once a change to `## Boundaries` lands,
this repo's session tells each neighbour it names.
