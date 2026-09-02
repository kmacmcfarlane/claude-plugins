---
id: work-plugin-36f5
title: "Extract work plugin: wi CLI + work-source provider interface + backlog provider"
type: feature
status: done
priority: 1
deps:
  - doctrine-9411
parent: plugin-factoring-924b
created: 2026-09-02
updated: 2026-09-02
closed: 2026-09-02
---

The support plugin. Move work-items (wi CLI + store) in, then take the first step toward pluggable ticket management: write the provider interface contract (verbs: next, claim, show, status, create, handoff/comment, query) as a reference doc; declare wi store and backlog.yaml as the two named local file providers (backlog keeps flock/claim semantics for unattended safety). Design for later remote providers (Linear/GitLab via MCP) as provider swaps, not replumbing. Do NOT unify the two file formats or build remote providers now - the contract is the deliverable; start file-based, upgrade later if necessary (operator decision 2026-09-02).

## Handoff
- doing: implemented, pending review
- next: fable review, then wi done
- blocked: —
- learned: —

## Notes
- 2026-09-02 claimed by unknown@e7c6135255e0
- 2026-09-02 done: c7fbbee + contract fixes 3a8a4d7; fable review APPROVED, doc certified as Phase 5 contract
