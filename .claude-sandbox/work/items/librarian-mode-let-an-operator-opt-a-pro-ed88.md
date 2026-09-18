---
id: librarian-mode-let-an-operator-opt-a-pro-ed88
title: "librarian-mode: let an operator opt a product repo in as custody"
type: feature
status: doing
priority: 1
owner: unknown@e3a28d2cc009
claimed: 2026-09-18T18:44Z
created: 2026-09-18
updated: 2026-09-18
refs:
  - peer claude-sandbox librarian; claude-sandbox 9468
---

Peer 'claude-sandbox librarian' (its item 9468), 2026-09-18, relaying the claude-sandbox operator: /kit-dev:librarian-mode start declined in claude-sandbox (a Go CLI, no plugins/, no ## Librarian) because of the product-code clip, which applies even to an explicit declaration. Ask: remove or relax the clip so an operator can opt a product repo in; the peer runs there now on an operator override. Its 7 open questions become decisions 19-25 (opt-in mechanism, custody extent, repo-own checks, routing, push policy, dev-flow dispatch, red flag scope). Acceptance: the declared repo gets a custody layer; undeclared code repos still decline; checklist, brief, route and push follow the decisions. Doctrine change: fable for the implementer is not required, but opus is (rule 2: doctrine). Waits on the operator's answers to 19-25.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —

decision 19: opt-in mechanism (declaration alone vs marker vs start flag)
decision 20: custody extent for a declared product repo (listed paths vs whole repo)
decision 21: repo-own gates via a Checks: list under ## Librarian
decision 22: routing for product repos (keep table vs own table)
decision 23: push policy for product repos
decision 24: dispatch dev-flow investigate/implement vs stay independent
decision 25: product-code red flag scope

## Operator answers (2026-09-18)
- 19: opt a repo in through a process, not a hard refusal. Librarian to propose the process for review first; no implementation until it is approved.
- 20: at start, ask the operator for the scope, with "whole repo" preselected so Enter accepts it. An existing ## Librarian section names the scope and the question is skipped. The answer creates or updates ## Librarian in CLAUDE.md.
- 21: repo-specific checks go in ## Librarian.
- 22: a (keep the routing table), but update the routing guidance for the skill's new scope.
- 23: a (fast-forward main after a Report; `Push: none` opt-out).
- 24: use dev-flow investigate/implement when they are installed; otherwise mention at work-item start that they can be used, and continue without them.
- 25: a (red flag kept outside the declared scope).

## Approved design (operator approved 2026-09-18, "approved, go ahead with ed88")
1. start with no `## Librarian` section: no decline. One AskUserQuestion dialog, three questions, first option in each preselected so Enter x3 accepts the defaults:
   - Scope: Whole repo (first) / Plugin layer (only when plugins/ exists: skills, hooks, README catalog, CLAUDE.md, i.e. today's default) / Listed paths (globs via Other) / Not now (creates nothing, stops; the only remaining decline).
   - Checks every change must pass: multiSelect, prefilled with commands detected in the repo (go test ./..., make test, npm test, scripts/check-*.sh), more via Other.
   - Push: main (fast-forward after each Report, first) / none (land to local main only).
2. The answer writes `## Librarian` into CLAUDE.md, committed as `librarian: opt in (<scope>)`. A named exception to "you do not edit custody files" (transcribing the operator's answer, not a behaviour change). Later edits to the section are ordinary work items. Format:
   ## Librarian
   Scope: whole repo            (or a list of paths/globs)
   Exclude: vendor/             (optional)
   Checks:
   - go test ./...
   Push: main                   (main | none)
   Workflow: <optional repo workflow notes, e.g. spec-first order>
3. Section present: skip the dialog, use Scope as written. `status` stays read-only; in an undeclared repo it prints "not opted in; `start` offers opt-in".
4. Checks and Workflow feed the implementer brief, the reviewer checklist and the Land checks, on top of the generic checklist.
5. Routing: code inside Scope = executable logic → opus; security surfaces (mounts, permissions, host access, sockets, credentials) → fable; docs-only changes inside Scope stay sonnet. model-routing.md gains a product-repo case and worked example.
6. Push follows `Push:`; `none` means land to local main and skip the push step.
7. dev-flow: when installed, spikes go through /investigate and features through /implement inside the implementer's worktree (the brief says so); when not, intake notes they can be used and work continues without them.
8. Red flag "touching product code" applies outside Scope, including Exclude:.
9. Unchanged: one librarian per repo, work items first, the review gate.

## Notes
- 2026-09-18 claimed by unknown@e3a28d2cc009

dispatch: implementer opus — doctrine change (custody resolution, routing guidance), >3 files

impl round 0: DONE_WITH_CONCERNS 35c04df (concerns: README/plugin.json narrower than skill; this repo has no ## Librarian so next start defaults Whole repo; dev-flow vs one-commit rules untested)
dispatch: reviewer opus — rule 4 (implementer opus)

review round 1 (opus): NEEDS_CHANGES. high 1 (dev-flow /implement branches main checkout, asks questions, dirty investigations); medium 2 (status stops at no-store before not-opted-in msg), 3 (Checks question may have <2 options; empty submit undefined), 4 (section without Scope: line undefined), 5 (README 72/171-179 + plugin.json:3 narrower than skill), 6 (kit-dev->dev-flow soft dep undeclared in catalog); low 7-9, nit 10-11.
dispatch: implementer opus fix round 1 — resume, tier unchanged

fix round 1: DONE f0bb818 (all 11 fixed; README soft-dep count corrected three->four)
dispatch: reviewer opus review round 2 — resume, tier unchanged

review round 2 (opus): SHOW_STOPPER. Prior 1-11 all FIXED. New: 12 [medium] principle 6: kit-dev description stretched to "any repo its operator opts in" (reverting reopens finding 5); 13 [low] /implement Step 1 looks only in .claude-sandbox/investigations; 14 [low] whole-repo carve-out not in the written section; 15 [nit] model-routing wrap. Reviewer: work-items soft dep in plugin.json is correct (principle 4).
decision 26: product-repo custody home: (a) land in kit-dev now + follow-up to split librarian-mode into its own plugin [reviewer rec]; (b) split now, widening ed88 scope.
