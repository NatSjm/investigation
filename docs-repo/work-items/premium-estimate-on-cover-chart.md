---
request: premium-estimate-on-cover-chart
title: "Premium estimate column on the cover ratio chart of both product overviews"
status: draft
generated: { by: copilot/analyst, at: 2026-10-20T13:10:00Z }
contexts: [cover, product1, product2]
specs: [P1-001, P2-001]
flows: []
pack: .context/cover-ratio-p1-001-p2-001-context-cover.md
---

# Premium estimate column on the cover ratio chart of both product overviews

## Request
> Add a premium estimate column to the cover ratio chart on both product overviews.

## Reading
"Coverage" is the **cover ratio** (glossary): the share of the projected value of a month covered by `cover_policy`
rows, computed by `cover_ratio` and drawn per sub-product as the `CoverRatioChart` on the Product 1 and Product 2
overviews (BR-P1-001-9, BR-P2-001-7). "Premium" is the **premium rate** (glossary): `cover_policy.premium_rate`, the
price of cover as a fraction of covered value, default `cover.default_premium_rate` (0.012). The request wants, next
to each month's cover ratio, an estimate of what cover would cost - a number the **cover** context owns (it owns
`cover_policy`, `cover_quote`, `CoverQuoteService` and the only pricing path, `requestCoverQuote` to cover-provider).
The cover context has code but **no spec yet**.
**I read this as: cover_ratio + P1-001 + P2-001 + context:cover, with a new estimate owned by cover - right?**

## Parts
| # | Part of the request | State | Context | Owner (spec / calculation / flow) | Evidence |
|---|---|---|---|---|---|
| 1 | Cover ratio chart on the Product 1 overview | changed | product1 | P1-001 | BR-P1-001-1 (cover ratio chart series per sub-product), BR-P1-001-9; `component:CoverRatioChart` (`src/pages/shared/components/CoverRatioChart/CoverRatioChart.tsx:18`, shared by both overviews) |
| 2 | Cover ratio chart on the Product 2 overview | changed | product2 | P2-001 | BR-P2-001-7 (as BR-P1-001-9); same component |
| 3 | Premium estimate per month and sub-product | new | cover | no spec (COV-001 to be created); nearest: `cover_ratio` (outputs `coveredValue(m)`), `cover_policy.premium_rate`, `CoverQuoteService` | context overview: tables `cover_policy` (covered share, premium rate, validity), `cover_quote`; endpoint `getCoverSummary` (cover ratio per month per sub-product); `requestCoverQuote` prices the uncovered part at cover-provider |
| 4 | Where the number travels | changed | cover, product1, product2 | `getCoverSummary` or the overview responses | the overview responses carry the cover series (BR-P1-001-1); `getCoverSummary` returns the same per sub-product (`CoverController.kt:23`) |

## Trust
`cover_ratio`: `draft · unverified`, worked examples TODO, two conventions marked "to confirm" (policy without
sub-product, overlapping policies); P1-001, P2-001: `draft · unverified`; cover context: no spec, graph only.
Everything derived here is `needs-spec-review`.

## What is reused, what changes, what is built
- **Reused as is**: `cover_ratio` (its `coveredValue(m)` is the base of the estimate), `cover_policy.premium_rate`,
  `CoverRatioChart`.
- **Changed**: the cover series returned to both overviews (and `getCoverSummary`) gain a `premiumEstimate` per
  month and sub-product; the chart shows it as a column next to the ratio.
- **Built**: the estimate itself - either computed locally (`uncovered value x premium_rate`, or the covered
  value times the rate: which one is the question) or taken from a cover-provider quote (`requestCoverQuote`,
  asynchronous, per session) - a decision for the owner of the cover context before any rule is written.

## Contracts
Changed: `getCoverSummary` response (new field per month and sub-product) and, if the overview keeps carrying the
cover series, `getProduct1Overview` / `getProduct2Overview` responses. No new operation if computed locally; a new
provider call if quoted (cover-provider contract has `POST /quotes` only, per session).

## Data
Read: `cover_policy` (`premium_rate`, `covered_share`, validity), `projection_by_subproduct` (value). No new table
if computed on request, like the ratio.

## Flows
None affected if computed on request; the session-inputs-recalculation flow stays as is (the estimate follows the
projection like the ratio does).

## Calculations
- Used as is: `cover_ratio`.
- New: a premium estimate calculation (name to be given with COV-001) - inputs `value`, `coveredShare`,
  `premiumRate` per policy and month; output `premiumEstimate(m, subProduct)`; formula open (question 1).

## Gaps and questions
1. What is the estimate: the premium for the cover already in place (`coveredValue x premium_rate`), the premium
   it would cost to cover the uncovered part (`uncoveredValue x rate`, the rate from the default parameter when no
   policy exists), or a provider quote? Owner decision; it decides whether the chart column is informative or a sales
   figure.
2. The cover context has no spec: **COV-001 must be created first** (`spec-skeleton-from-graph cover COV-001`), then
   the estimate becomes a proposed rule of COV-001, the chart change proposed rules of P1-001 and P2-001.
3. `cover_ratio` conventions "to confirm" (policy without sub-product, overlapping policies) affect the estimate the
   same way; `calc-auditor` should settle them before the new calculation is drafted.
Forwarded: `spec-writer` - create COV-001 (draft) from the graph neighbourhood of `context:cover` and `CoverManager.kt`;
`calc-auditor` - `cover_ratio` worked examples and the two conventions.

## Proposed rules introduced
None yet - blocked on question 2 (no spec to hold a cover rule). No epic until COV-001 exists.

## Stories outline
Not written: the request has no rule to cite in the context that owns its new part. After COV-001: one epic with
S1 estimate calculation + `getCoverSummary` field (cover), S2 chart column on both overviews (product1, product2,
depends on S1).

## Sources
- pack: `python3 scripts/context-pack.py --task cover_ratio --task P1-001 --task P2-001 --task context:cover --budget 1400` (built 2026-10-20T12:10:23Z)
- catalogue: `generated/catalogue.md` (generated 2026-10-20); glossary: coverage -> Cover ratio, premium -> Premium rate
- no other file opened
