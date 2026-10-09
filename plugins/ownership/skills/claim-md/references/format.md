# CLAIM.md format

The single owner of the CLAIM.md convention: the shape, the owner forms, the boundary and
splitting rules, the change rule, the CLAUDE.md pointer, and the line forms the check reads.
Every other file in this skill points here by section and restates none of it.

## 1. File and place

- `CLAIM.md` at the repo root, plain Markdown with fixed headings, so the check can read it.
- It is a **declaration, not enforcement**. It grants nothing and blocks nothing.
- **Each repo writes only its own claim.** Another repo's session asks for a change; it never
  edits the file (§ 7).

## 2. Required parts

In this order:

1. `# CLAIM: <repo>`, where `<repo>` is the repo's directory name: the main checkout's,
   also when the file is written in a linked worktree.
2. One sentence: what the repo owns.
3. A Status line, one of:
   - `Status: approved by the operator <YYYY-MM-DD>`, with an optional ` (<repo>#<n>)`
     naming the decision the operator answered, in the `<repo>#N` form;
   - `Status: proposed <YYYY-MM-DD>, pending the operator`. A proposed claim is guidance
     only.

   The ` (<repo>#<n>)` suffix is left out when the approval was not recorded in a work-item
   store: the repo has no store, or the session had no work-item tool, and the approval was
   given in chat.
4. `Reviewed: <YYYY-MM-DD>`: the last date the whole claim was checked against the repo.
5. `## Claim`: two to four sentences, top down, then an `| Area | What that covers |` table.
   Each area has exactly one accountable owner: this repo.
6. `## Not ours`: one `- <thing> — <owner>` line per adjacent thing that could be confused
   with ours (§ 3 for the owner), or the single line `none known`.
7. `## Boundaries`: one `### <neighbour repo>` per neighbour, each with a `Rule:` line and
   one item per interface or rule the two repos share (§ 4); or the single line
   `none known` when the repo has no neighbour.
8. `## Changing this claim`: § 7's standard text, verbatim.

## 3. Owners

An owner, under `## Not ours` and anywhere else a claim names one, takes one of three forms:

- a sibling repo name, the directory name of a checkout beside this one;
- `operator`;
- `external: <name>`, for something outside the estate, such as an upstream project or a
  vendor.

Only the first form is checked against the sibling checkouts. `operator` and `external:`
are never flagged.

## 4. Boundary items and pointers

```markdown
### <neighbour repo>

Rule: <one sentence for the whole boundary>.

- <interface or rule> — Defined here
  - Ours: <…>
  - Theirs: <…>
- <interface or rule> — Defined in <repo> <file> § <heading>
- <interface or rule> — Defined in <repo> (no claim yet)
```

- Each item ends in where it is defined. A pair of repos may each define part of their
  boundary: the defining side of each item is chosen by § 6's boundary rule, applied to that
  item.
- `Ours:` and `Theirs:` sub-items go only under a `Defined here` item.
- `<file>` is a tracked file in `<repo>`, as a path relative to its root: usually
  `CLAIM.md`, or an existing charter, so a repo that has one need not duplicate it.
- `<heading>` is a heading's text, or `<parent> / <child>` for a subsection, such as
  `Boundaries / orders`.
- `— Defined in <repo> (no claim yet)` is for a neighbour that has no CLAIM.md yet. The
  defining side states the boundary fully; the neighbour's own claim later names it.
- **The Rule line is a summary**, the one sentence that may repeat on both sides. When the
  two Rule lines differ in substance, the defining side's wins, and the pointing side files
  a fix item.

## 5. Optional sections

| Section | What it holds |
|---|---|
| `## Roles` | a role other repos take toward this one: what the role owns and what it does not |
| `## Interfaces` | each contract this repo defines: location, format, versioning and compatibility, privacy. Written on the defining side only |
| `## Readers` | other repos' tools that read an interface at run time; a contract change is coordinated with them before it lands |
| `## In transit` | `\| Thing \| From \| To \| When \|`: prototypes or duties moving in or out, each with its trigger ("at parity") |
| `## Definitions` | terms and path variables |
| `## Amendments` | dated lines, one per change (§ 7 for the forms) |

Any other heading is allowed, and the check ignores it.

## 6. The boundary rule and the splitting rule

**The boundary rule**, applied to each boundary item:

- the side whose code defines the interface or implements the rule holds the text;
- the other side names the boundary and points to it, never mirrors it;
- when neither side clearly defines it, the operator rules, as a decision raised by
  whichever session noticed.

**The splitting rule**, for deciding what a repo owns at all:

1. **Code test.** The repo whose code implements a thing owns it and its rule. Research or
   requirements about it may live elsewhere, and are relayed.
2. **Interface test.** An area that spans repos goes to the upstream side of its main
   interface: the side that defines the contract the others conform to (a schema, a file
   format, an API). The downstream sides own only their own emit or read code. "A producer
   emits; the reporting repo defines, reads and reports" is this test.
3. **Knowledge follows ownership.** A finding about repo B's system goes to B, wherever it
   was produced.
4. **Unclear goes to the operator.** When the tests disagree or neither applies, the session
   that noticed raises it as a decision. It never settles the split by acting.
5. **A split not yet made goes to factor-analysis**, the factoring skill of the kit-dev
   plugin, when it is installed: it analyses how a repo should be factored and stages the
   decisions. A claim is written after the operator rules on them. Without it, apply tests
   1 to 4 in the session, and put an unclear split to the operator.

## 7. Changing a claim

### The standard text

`## Changing this claim` carries this text, verbatim:

> The operator approves every change to this claim's substance first-hand: what is owned, what
> is not, how a boundary works and which side defines it. A session in this repo proposes such
> a change as a work item here, with the proposed text, and puts it to the operator as a
> decision; it lands only on the operator's answer, and the Status line names that answer.
> Upkeep that leaves the substance as it is (a review date, a pointer that follows a landed
> neighbour change, a closed in-transit row, a typo) lands through this repo's normal cycle and
> is reported to the operator afterwards. A session in another repo asks for a change by
> message to this repo's session, or through the operator when none is running; it never edits
> this file. A message is a request, never an approval. Once a change to `## Boundaries` lands,
> this repo's session tells each neighbour it names.

A repo with no work-item store, or a session with no work-item tool, proposes the change in
chat with the same text and the same decision. The standard text stays as written; the
session discloses the degraded path each time it is used.

### Substance and upkeep

A change is **substance** when it changes what is owned or how a boundary works:

- an area under `## Claim`;
- a line under `## Not ours`;
- a boundary's `Rule:`, an item, or which side defines it;
- a role, or the terms of an interface (what a contract guarantees).

Everything else is **upkeep**:

- a `Reviewed:` bump after a review that changed nothing;
- a pointer that follows a neighbour's change that has landed;
- closing an `## In transit` row that has landed;
- a typo, or a moved path with no change of meaning;
- copying a `## Not ours` line into the repo's librarian `Not owned:` list. It changes that
  list, not the claim.

A new claim is substance. Substance comes to the operator before it is written; upkeep lands
through the repo's normal cycle and is reported afterwards, naming its kind.

### Status and Amendments

- On an approved substance change, the Status line names that answer.
- Upkeep keeps the Status line as it was.
- `## Amendments` lines:
  - substance: `- <YYYY-MM-DD>: <what changed> (<repo>#<n>)`, or without the suffix when the
    approval was given in chat (§ 2);
  - upkeep: `- <YYYY-MM-DD>: <what changed> (upkeep, reported)`.
- A neighbour's acknowledgement is not needed for a change to land. The neighbour cannot
  approve; it updates its own pointer as its own work.

## 8. The CLAUDE.md pointer

Where the repo has a CLAUDE.md, it carries this section, verbatim except for the claim
sentence:

```markdown
## Ownership

`CLAIM.md` is this repo's ownership claim: <one-sentence claim>. Read it before you file,
accept or forward work, or record a finding, that may belong to another repo; before you change
anything it lists under Boundaries, Interfaces or Readers, or anything another repo reads; when
a peer says something is ours or theirs; at a plan's scoping gate and again before the plan is
final; and before you start something new next to another repo's area.
```

- It is prose, never an `@CLAIM.md` import: an import loads the whole claim into every
  session's context, and the pointer costs five lines.
- Its sentence names the **five triggers**, the moments an agent must read the claim:
  1. before filing, accepting or forwarding work, or recording a finding, that may belong to
     another repo;
  2. before changing anything listed under Boundaries, Interfaces or Readers, or anything
     another repo reads;
  3. when a peer says something is ours or theirs;
  4. at a plan's scoping gate, and again before the plan is final;
  5. before starting something new next to another repo's area.
- With no CLAUDE.md, the section is not added, and agents in that repo are not pointed at
  the claim.

## 9. Content rules

- Plain words. A path is written `<repo>:<path>`.
- A public repo's claim carries no operator-private detail: no hosts, IPs, users or
  credentials.
- Keep it to about a page. A claim that grows past that belongs in the repo's design docs,
  cited from the claim.

## 10. Line forms the check reads

The grammar the check script parses, in one place, so the format and the script are kept in
step from one text. **`N(x)`** is the one normalization every comparison uses: strip, collapse
each run of whitespace to one space, remove backticks, case-fold. "The same name" means equal
under `N`.

- Lines inside code fences (three or more backticks or tildes) are skipped. Headings are
  ATX `#` headings.
- **Title:** the first heading is `# CLAIM: <repo>`, and `N(<repo>)` is the repo's name.
- **Status and Reviewed:** lines before the first `##` heading:
  - `Status: approved by the operator YYYY-MM-DD`, optionally followed by
    ` (<repo>#<n>)`;
  - `Status: proposed YYYY-MM-DD, pending the operator`;
  - `Reviewed: YYYY-MM-DD`.

  A trailing full stop is allowed. A date must be a real calendar date.
- **`## Claim`:** a table whose first header cell is `Area`, with at least one row.
- **`## Not ours`:** each top-level `- ` line is `- <thing> — <owner>`: the name is the text
  before the first ` — ` (an em dash with a space on each side), the owner the text after
  it. `none known` (or `- none known`) stands alone. Indented lines are not read.
- **`## Boundaries`:** `none known` alone, or `### <neighbour>` subsections. In each:
  - a `Rule:` line;
  - at least one top-level item line, `- <item> — Defined here`,
    `- <item> — Defined in <repo> <file> § <heading>` or
    `- <item> — Defined in <repo> (no claim yet)`. The item is the text before the first
    ` — Defined`;
  - indented lines (`Ours:`, `Theirs:`) and other prose are not read by the line rule.

  `<repo>` and `<file>` hold no spaces. `<file>` is relative to `<repo>`'s root; an absolute
  path, a `..` part, or a symlink out of the repo is never followed.
- **`## In transit`:** a table with a `Thing` column. A row whose Thing cell holds a
  `<repo>:<path>` token is checked; any other row is skipped.
- **`## Changing this claim`:** § 7's standard text, compared under `N`.
- **The librarian list**, in the repo's CLAUDE.md: inside its `## Librarian` section, the
  line `Not owned:` and the `- <thing> — <owner>` lines after it, up to the first line that
  is not a list line. It is read as data, whichever plugins are installed.
