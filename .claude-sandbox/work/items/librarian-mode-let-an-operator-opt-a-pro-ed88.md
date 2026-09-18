---
id: librarian-mode-let-an-operator-opt-a-pro-ed88
title: "librarian-mode: let an operator opt a product repo in as custody"
type: feature
status: todo
priority: 1
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
