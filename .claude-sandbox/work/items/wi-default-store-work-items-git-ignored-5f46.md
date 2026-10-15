---
id: wi-default-store-work-items-git-ignored-5f46
title: "wi: default store .work-items/, git-ignored on init; env vars renamed to WORK_ITEMS_"
short_display_name: wi store .work-items, WORK_ITEMS_ env
type: feature
status: todo
priority: 1
created: 2026-10-15
updated: 2026-10-15
refs:
  - answer 227, operator 2026-10-15
---

Answer 227 b (operator 2026-10-15): the default work-item store is .work-items/ at the repo root, git-ignored when established, because it matches the plugin's name and works without claude-sandbox. Also rename wi's env vars to the WORK_ITEMS_ prefix (WI_ROOT -> WORK_ITEMS_ROOT, WI_OWNER -> WORK_ITEMS_OWNER, ...). Decided alone: the old WI_* names and the .work/ and .claude-sandbox/work/ stores keep working as deprecated fallbacks with a one-line warning, so no repo breaks mid-migration. Acceptance: wi finds .work-items/ first; the estate sweep includes it; every skill and reference naming WI_ROOT or the old store paths is updated; tests; README/CLAUDE.md layout. Coordinate with claude-sandbox decision 115.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
target: series .claude-sandbox/investigations/wi-default-store-work-items-git-ignored-5f46/
budget: waived (operator 2026-10-08); spend measured
dispatch: planner opus high — plan the store default and env-var rename (answer 227 b)
agent: planner ac82427bf27ca5eb5 round 1
return: planner DONE .claude-sandbox/investigations/wi-default-store-work-items-git-ignored-5f46 (00_initial.md; F1 env rename, F2 .work-items default and lookup order, F3 dev-flow, F4 context-guard, F5 ralph and ownership; 3c06 lands first as built; OQ1 this repo's store, OQ2 nested .git store)
baseline: 66828c2369cb833c7af58dcba081aea7c108e92be6a81ff72a80796921933e6e  00_initial.md 476e811190bfe5bd27743d53602dfd56b507ed898043c06bfb8475446754e878  INDEX.md 
dispatch: reviewer opus high — plan review round 1 (fresh)
agent: reviewer ada90b0ef30b65b3c plan round 1
verdict: NEEDS_CHANGES plan round 1 (8 medium: two-store check never runs with an exported root; a worktree init creates a stray store; test harness leaks old names; first-start sets only the new name; librarian's store-and-git premise is a doctrine question (new OQ3); OQ1 misses a private versioned option and the decision-numbering reset; 3c06 must be a hard prerequisite; the move recipe empties other clones' stores; 6 low; 1 nit)
dispatch: planner opus high — resume, plan fix round 1
agent: planner ac82427bf27ca5eb5 round 2
