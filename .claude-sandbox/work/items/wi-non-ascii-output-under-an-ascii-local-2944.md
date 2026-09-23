---
id: wi-non-ascii-output-under-an-ascii-local-2944
title: "wi: non-ASCII output under an ascii locale without UTF-8 mode is a UnicodeEncodeError traceback"
type: bug
status: todo
priority: 4
created: 2026-09-23
updated: 2026-09-23
refs:
  - c68b review r2
---

c68b review r2 low, 2026-09-22 (pre-existing on main): wi show on a non-ASCII item under LC_ALL=C PYTHONUTF8=0 with no PYTHONIOENCODING exits 1 with a traceback on stdout. Pass: sys.stdout.reconfigure(errors='backslashreplace') (or utf-8) in main(); test.

## Handoff
- doing: —
- next: —
- blocked: —
- learned: —
