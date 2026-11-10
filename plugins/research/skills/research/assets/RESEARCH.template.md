---
kind: research-corpus
updated: <ISO date>
kb: <the default knowledge base's path from the repo root; the line left out when there is none>
runs: <the runs directory's path from the repo root; the line left out when there is none>
---
# Research — <repo name>

> <the summary: the listed knowledge bases' purpose sentences, or, with no knowledge base, "Research for <repo name>: where it lands and how it is laid out.">

## Where research lands

- [<kb path>/](<kb path>/KB.md): knowledge base — <its KB.md purpose sentence>; charter in KB.md
- [<runs path>/](<runs path>/): run records, one directory per run (<YYYY-MM-DD>-<slug>/)
- [docs/research/](docs/research/): promoted runs

## Shape

- `<kb path>/`: the `<scheme>` scheme (KB.md); read `INDEX.md` first, then `notes/`; its runs
  are under `runs/<YYYY-MM-DD>-<slug>/`.
- `<runs path>/`: one directory per run, holding `00-brief.md`, `findings/`,
  `01-synthesis.md`, `verification.md` and `sources.md`; read `01-synthesis.md` first.
- `docs/research/`: promoted runs, in the run layout, each with `promoted_from:`.

Every landed file carries the research frontmatter: `question`, `run`, `date`, `retrieved`,
`intensity`, `shape`, `confidence`, `supersedes`, `volatile`, `audience`.

## Before you research

Read each INDEX.md above, then grep notes/ and runs/ for the question's nouns. A hit is
extended with the research-refine skill, not re-run. Cite a note or a run by its path.

## Optional

- [<path>](<path>): superseded runs, archives, older locations
