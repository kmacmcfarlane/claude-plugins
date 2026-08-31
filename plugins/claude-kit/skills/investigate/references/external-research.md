# External research

Loaded from `investigate` Step 6d, when the plan will rest on a fact the codebase cannot
answer. How to *record* an external claim is owned by `investigation-format.md` — this file
covers only how to go and get one.

## Source hierarchy

Prefer, in order:

1. **The manufacturer's or standards body's own document** — user manual, datasheet, product
   brief, spec PDF. This is what a purchase or a migration should rest on.
2. **The project's own documentation** for a third-party tool, at the version in use.
3. **A first-party page recovered from an archive** when the live one is unreachable.
4. **A reseller or distributor reprint** of vendor text — usable, but say so.
5. **A forum post from someone with the hardware in hand** — genuinely valuable for facts no
   vendor documents, and frequently the only source. Mark it as such and prefer posts that
   report a measurement or a part number over ones that reason.
6. **A search-result summary.** Weakest. Use to find sources, not as one.

A claim that survives only at level 5 or 6 is not wrong, but the plan should not depend on it
without saying so — and a physical check before spending money is cheap by comparison.

## Documents beat product pages

Marketing pages summarise and round off; the manual states the constraint. Block diagrams,
population tables and BIOS menu listings routinely contain the answer that no product page
mentions — and the answer that decides the work.

**Where a manual only shows a drawing, the drawing is often to scale.** Extracting geometry
from the PDF, then validating the scale against a known dimension elsewhere in the same
document, turns a picture into a measurement. This is worth doing when the alternative is
guessing about physical fit.

## Fetch-blocking is the normal case

Expect many vendor and retail hosts to refuse automated clients — 403 or 503, often on the
HTML pages while other paths on the same host serve fine. Budget for it rather than treating
each block as a surprise.

Routes that have actually worked when the obvious one was blocked:

- **A different path on the same host.** Document and asset directories are frequently open
  when the product pages are not. Try the manual or datasheet URL directly.
- **The Internet Archive**, especially for retired or superseded first-party pages.
- **A distributor or reseller reprinting the vendor's own text** verbatim — check it reads as
  vendor copy, not as the reseller's paraphrase.
- **A mirror or aggregator** for a marketplace that blocks you directly.
- **The project's source repository** when its documentation site is unreachable.

State in the investigation which route produced each claim. "Vendor-official" and "a reseller
reprinting the vendor" are different confidence levels and a reader cannot tell them apart
otherwise.

## Prices and availability

- **An asking price is not a clearing price.** Marketplace listings carry a long unsold tail;
  where completed-sale data is unavailable, say so and treat the low end of the band as the
  realistic figure.
- **A page with no cart is not a transactable price.** Quote-request and lead-capture pages
  publish numbers that no longer match anything buyable. When a "price guide" sits well below
  every live listing, it is stale or bait — worth one enquiry, never worth planning around.
- **Check stock, not just price.** In a constrained market, availability binds before cost,
  and a recommendation nobody can fill is not a recommendation.
- **Prices rot fastest of anything you will cite.** Date every one, and prefer stating the
  market condition — direction, and whether it is expected to persist — over a bare number.

## Reconcile against the live system

Where an external fact and the machine disagree, **the machine wins and the disagreement is a
finding.** Firmware-reported inventories in particular are worth distrusting: they are
routinely wrong about what is populated, and a physical inspection settles it. Record which
source lost, so nobody re-derives the wrong answer later.
