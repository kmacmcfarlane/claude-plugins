---
id: context-guard-the-manifest-read-path-tak-0836
title: "context-guard: the manifest READ path takes the store file on existence alone, with no identity test"
type: bug
status: todo
priority: 1
created: 2026-09-22
updated: 2026-09-22
refs:
  - F3b-2 implementer, after the F3b-1 merge
---

Found by F3b-2's implementer after merging F3b-1 (landed 92c9738), 2026-09-22. rehydrate's read_store_manifest/own_manifest accept <store>/<sid>/HANDOFF.md on os.path.exists alone, with no L.manifest_sid check. On the WRITE path this was F3b-2's r1 medium and is now guarded by own_store_manifest; on the READ path a symlink planted at that path would be INJECTED as that session's own memory in full. The store directory is shared by every session in a container. Acceptance: the read path applies the same containment/identity test as the write path (L.manifest_sid(p) == L.safe_sid(sid)), anything failing falls through to the legacy arm, plus a test for a symlinked file and a symlinked <sid>/ directory. Route: fable signal (it gates what memory a session is given); fable unavailable in that session → opus, recorded.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
