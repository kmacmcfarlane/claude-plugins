---
id: research-tooling-the-tools-research-agen-04f7
title: "research tooling: the tools research agents always need, and how each environment gets them"
type: spike
status: todo
priority: 2
created: 2026-09-24
updated: 2026-09-24
refs:
  - operator 2026-09-24 (R10, poppler-utils)
---

Operator 2026-09-24, instead of adding poppler-utils alone (R10): ask agent-research - librarian to list the tools the research skills should always have (pdftotext/poppler-utils was the first gap: lanes could not read PDF primaries) and the proper steps to get them in each scenario (sandbox child Dockerfile, the upstream claude-sandbox base image, a host session, pip-only fallbacks) before a run needs them; get claude-sandbox - librarian's input, since adding them to the upstream parent Dockerfile may be the most ergonomic. Acceptance: a list with per-scenario steps and a recommendation on where each tool lives, back to the operator; then a research-skill note (preflight/fallback) filed here if needed.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
- 2026-09-24 agent-research - librarian filed research-tooling-the-tools-research-agen-39ae (spike); list comes back after its review
- 2026-09-24 claude-sandbox librarian (item a864): small stable Debian tools such as poppler-utils go in the base image (batch them, since each change rebuilds every child); heavy or niche tools (pandoc, tesseract, Chromium, LaTeX) go in a documented opt-in child-Dockerfile snippet; pip only as a degraded path; skills must detect and name a missing tool; it measures sizes once the list arrives and puts the cut to the operator
- 2026-09-24 agent-research - librarian result (its 39ae; series /home/rt/work/src/github.com/kmacmcfarlane/agent-research/.claude-sandbox/investigations/research-tooling/ 00-02, read applying Supersedes): only poppler-utils has observed failures (Read with pages calls pdftoppm; the w2 lane lost five PDF sources); base: poppler-utils (24.6 MiB); opt-in: OCR (tesseract/ocrmypdf/qpdf), pandoc; fallback: whole-PDF Read up to ~5 MB, WebFetch-saved PDF, pip --target into the scratchpad; the pip "refusal" was a root-owned venv, and container-context.md:12's "pip install works" is wrong at runtime. Proposes a POSIX preflight at research Step 5.1 and a lane PDF rule (branch a: Read; branch b: pdftotext, needs research-lane rule 8 amended). Open questions: OQ1-3 base vs child, inclusion bar, size budget (operator via claude-sandbox a864); OQ4 OCR snippet; OQ5 missing tool unattended: continue degraded or stop; OQ6 rule 8; OQ7 unattended pip --target; OQ8-9 claude-sandbox.
decision 85: when a research tool is missing in an unattended run — (a) stop and ask, naming the tool and the one-line fix (claude-sandbox's view; no unattended pip) [recommended]; (b) continue degraded (whole-PDF Read, WebFetch-saved file), mark the sources could-not-verify, no pip; (c) continue degraded and allow pip --target into the scratchpad; (z) decide later
  raised: 2026-09-24
  what: what an unattended research run does when a tool it needs (today: the PDF reader) is missing (OQ5 with OQ7)
  why now: blocks the unattended branch of the research preflight; the interactive branch is ungated
  (a): the run stops at recon and asks; nothing silently degraded; the run waits for you
  (b): the run finishes with weaker evidence, flagged per source; no install at runtime
  (c): as (b), but it may install pypdf-style packages into its scratchpad; more sources verified, and runtime code you did not vet
  rec: (a) · basis: partial — claude-sandbox and container-context.md:23 already say stop; no unattended research runs today (the hold)
  unknown: how often unattended research will run once the scheduler lands
decision 86: may web research lanes run pdftotext on PDFs they fetched (research-lane rule 8 forbids a web lane a shell) — (a) yes, a narrow exception: pdftotext and pdfinfo on a file the lane itself saved [recommended]; (b) no, lanes use Read only (whole PDF up to ~5 MB, else could-not-verify); (z) decide later
  raised: 2026-09-24
  what: whether to amend rule 8 so web lanes can extract PDF text with a shell command (OQ6)
  why now: blocks branch (b) of the lane PDF rule; branch (a) ships without it
  (a): long PDFs become readable once poppler is installed; a web lane gains a narrow shell use, which a lane already took anyway (w2)
  (b): no shell for web lanes; PDFs over ~5 MB stay unverifiable
  rec: (a) · basis: partial — one observed failure (w2, five sources lost) and two earlier ones
  unknown: whether other file types will want the same exception
