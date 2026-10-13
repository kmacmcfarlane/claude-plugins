# A worked example: a fictional estate

**Fictional.** The repos `orders`, `metrics` and `deploy` are invented for this example. No
real repo's ownership is stated here. The shape is `format.md`'s; this file only shows it
filled.

The estate:

- `orders` takes and stores orders, and emits an event for each one;
- `metrics` defines the order event schema, reads the events, and owns every report and
  dashboard built on them;
- `deploy` runs the release pipeline. It has no claim yet.

What the pair shows:

| Shape point (format.md) | Where |
|---|---|
| a role-based boundary (§ 6, the interface test) | both `Rule:` lines: "a producer emits; metrics defines, reads and reports" |
| a two-way boundary (§ 4) | the event schema is `Defined here` in `metrics`; the event outbox is `Defined here` in `orders` |
| a pointer in the `CLAIM.md § Boundaries / <repo>` form (§ 4) | each side's pointer to the other's item |
| a `(no claim yet)` pointer (§ 4) | `orders` § Boundaries / deploy |
| all three owner forms (§ 3) | `orders` § Not ours |
| an In transit row (§ 5) | `orders` § In transit |
| the Status line with and without its decision suffix (§ 2) | `orders` names `orders#12`; `metrics` was approved in chat |

## `orders/CLAIM.md`

```markdown
# CLAIM: orders

orders owns taking, storing and changing customer orders, and emitting an event for each.

Status: approved by the operator 2026-10-01 (orders#12)
Reviewed: 2026-10-01

## Claim

orders owns the order lifecycle from checkout to fulfilment: the order records, the code
that takes and changes them, and the outbox it emits order events through. It produces
events; it does not define their schema or report on them.

| Area | What that covers |
|---|---|
| Order records | the orders tables and their migrations |
| Order taking | checkout, order changes and cancellation |
| The event outbox | where and when order events are published |

## Not ours

- order-volume and revenue reports — metrics
- dashboards built on order events — metrics
- the order event schema — metrics
- pricing policy and discount rules — operator
- card payment processing — external: the payment provider

## Boundaries

### metrics

Rule: a producer emits; metrics defines, reads and reports.

- the order event schema (field names, types, versions) — Defined in metrics CLAIM.md § Boundaries / orders
- the event outbox (where and when orders publishes events) — Defined here
  - Ours: the outbox table, its retention, and the emit code
  - Theirs: reading the outbox, and anything built from what is read

### deploy

Rule: deploy runs the release pipeline; orders ships through it.

- the release steps and their order — Defined in deploy (no claim yet)

## In transit

| Thing | From | To | When |
|---|---|---|---|
| `orders:scripts/weekly_report.py` | orders | metrics | when metrics' weekly report matches its totals |

## Changing this claim

<the standard text, format.md § 7, verbatim>
```

## `metrics/CLAIM.md`

```markdown
# CLAIM: metrics

metrics owns the order event schema and every report and dashboard built on order events.

Status: approved by the operator 2026-10-01
Reviewed: 2026-10-01

## Claim

metrics defines the schema producers emit, reads the events, and owns the reports and
dashboards built from them. A producer owns only its own emit code.

| Area | What that covers |
|---|---|
| The order event schema | field names, types, versions and compatibility |
| Reports | order-volume and revenue reports |
| Dashboards | every dashboard built on order events |

## Not ours

- order records and the code that takes orders — orders
- the release pipeline — deploy

## Boundaries

### orders

Rule: a producer emits; metrics defines, reads and reports.

- the order event schema (field names, types, versions) — Defined here
  - Ours: the schema, its versions, and the compatibility rule
  - Theirs: emitting events that conform to it
- the event outbox (where and when orders publishes events) — Defined in orders CLAIM.md § Boundaries / metrics

## Changing this claim

<the standard text, format.md § 7, verbatim>
```

