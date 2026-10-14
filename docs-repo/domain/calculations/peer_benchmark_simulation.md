---
type: Attested Computation
title: Peer benchmark simulation (segment median × scaling factor)
description: "Models the monthly movements of similar products at peer firms: the median monthly quantity of the clients of the chosen peer segment, multiplied by a scaling factor, as a separate chart series of the product page."
tags: [calculation, product1, product2, peer]
status: draft
runtime: kotlin
parameters:
  - { name: segmentQuantities, type: Decimal, required: true }
  - { name: scalingFactor, type: Decimal, required: true }
executor:
  resource: backend/core/src/test/kotlin/harbor/utils/PeerBenchmarkTest.kt
  receipt: [test_class, inputs, expected, actual]
attester:
  resource: /scripts/attest-calculation.py
generated: { by: copilot/calc-auditor, at: 2026-10-12T12:00:00Z }
stale_after: 2027-01-10T00:00:00Z
sources:
  - id: impl
    resource: https://git.example.com/harbor/harbor-backend/blob/main/core/src/main/kotlin/harbor/utils/PeerBenchmark.kt
    title: PeerBenchmark.kt
  - id: tests
    resource: https://git.example.com/harbor/harbor-backend/blob/main/core/src/test/kotlin/harbor/utils/PeerBenchmarkTest.kt
    title: PeerBenchmarkTest.kt
  - id: rounding
    resource: https://git.example.com/harbor/harbor-backend/blob/main/core/src/main/kotlin/harbor/utils/Rounding.kt
    title: Rounding.kt
# --- repo extensions ---
name: peer_benchmark_simulation
used_by: [P1-001]
code_refs:
  - backend/core/src/main/kotlin/harbor/utils/PeerBenchmark.kt
  - backend/core/src/main/kotlin/harbor/utils/Rounding.kt
  - backend/core/src/test/kotlin/harbor/utils/PeerBenchmarkTest.kt
last_verified: null
---

# Peer benchmark simulation (segment median × scaling factor)

## Purpose
Modal 2 of the product pages ("Peer simulation", P1-001 BR-P1-001-7) answers "what do similar firms move?". For
every month the calculation takes the **median** monthly quantity of all clients of the chosen peer segment and
multiplies it by a **scaling factor**. The result is a separate chart series; it is never merged into the projection
tables.[^impl]

The implementation KDoc states that no specification existed before this concept and that the behaviour is "the
minimum the UI needs and expected to change". Everything below is therefore the current code, recorded for the
owner's decision (see Open questions), not an approved business rule.[^impl]

## Inputs
| Name | Type | Unit | Source | Constraints |
|---|---|---|---|---|
| segmentQuantities(m) | list of Decimal | units | monthly quantities of every client of the peer segment, per month `m` (assembled by `PeerSimulationService` from `movement_monthly`, last 12 full months) | may be empty for a month |
| scalingFactor | Decimal | ratio | request `scalingFactor`, default parameter `peer.scaling_default` | 0.1-5.0 (BR-P1-001-7) |

## Parameters
| Key (`parameter_set.key`) | Default | Scope |
|---|---|---|
| `peer.scaling_default` | 1.0 | global (`V9__parameters.sql`) |

## Outputs
| Name | Type | Unit | Precision / rounding |
|---|---|---|---|
| peerQty(m) | Decimal | units | `median(m) × scalingFactor`, scale 2, HALF_EVEN |
| median(m) | Decimal | units | middle value for an odd count; mean of the two middle values at scale 4 for an even count; 0 for no values |

The series is ordered by month ascending. Only quantities are simulated; no value, landed cost or price index is
applied.

## Formula
$$ median(m) = \begin{cases} q_{(n+1)/2} & n \text{ odd} \\ \frac{q_{n/2} + q_{n/2+1}}{2} & n \text{ even} \\ 0 & n = 0 \end{cases} $$
$$ peerQty(m) = median(m) \cdot scalingFactor $$

Step list:
1. Sort the quantities of month `m`; take the median as defined above (even count: scale 4, HALF_EVEN).[^impl][^rounding]
2. Multiply by `scalingFactor`; round to scale 2 HALF_EVEN.[^impl][^rounding]
3. Emit one point per month, months sorted ascending.[^impl]

# Computation
```kotlin
// mirrors PeerBenchmark.kt — pure Kotlin, no Spring
fun median(values: List<BigDecimal>): BigDecimal {
    if (values.isEmpty()) return BigDecimal.ZERO
    val sorted = values.sorted(); val mid = sorted.size / 2
    return if (sorted.size % 2 == 1) sorted[mid]
    else (sorted[mid - 1] + sorted[mid]).divide(bd(2), Rounding.RATIO_SCALE, Rounding.MODE)
}

fun simulate(segmentQuantities: Map<YearMonth, List<BigDecimal>>, scalingFactor: BigDecimal): List<PeerPoint> =
    segmentQuantities.entries.sortedBy { it.key }
        .map { (period, quantities) -> PeerPoint(period, (median(quantities) * scalingFactor).money()) }
```

## Conventions
Rounding: median scale 4 (even count), result scale 2, HALF_EVEN · Missing data: a month without peer quantities
yields `0.00`; the month still appears when it is present in the input map · Segment: the peer segment is a label of
the client profile; which clients belong to it is decided upstream, not here · Time zone: UTC.

## Worked examples
Copied from the executor test.[^tests]

| # | Case | Inputs | Expected output | Test method |
|---|---|---|---|---|
| 1 | odd count | quantities 30, 10, 20 | median **20** | `median of an odd count is the middle value` |
| 2 | even count | quantities 10, 40, 20, 30 | median **25.0000** | `median of an even count is the mean of the two middle values at scale 4` |
| 3 | no values | — | median **0** | `median of no values is zero` |
| 4 | two months, factor 1.5 | Jan: 30, 10, 20 · Feb: 10, 40, 20, 30 | Jan **30.00**, Feb **37.50**, months ascending | `peer quantity is the segment median times the scaling factor at scale 2 with months sorted` |
| 5 | month without peers | Jan: none, factor 2 | **0.00** | `a month without peer data yields zero` |

## Audit 2026-10-12
Auditor: copilot/calc-auditor (Run 3, first concept). Files opened: `core/src/main/kotlin/harbor/utils/PeerBenchmark.kt`
(L1-L45) and `core/src/test/kotlin/harbor/utils/PeerBenchmarkTest.kt` (L1-L55; the test did not exist and was added
in the same run so that the concept has an executor).

| # | Item | Documentation says | Code/test says | Severity | Action |
|---|---|---|---|---|---|
| 1 | median, odd / even / empty | as in Formula | `median`: identical; tests 1-3 | MATCH | — |
| 2 | peer quantity | `median × scalingFactor`, scale 2 | `simulate`: `(median(q) * scalingFactor).money()`; test 4 | MATCH | — |
| 3 | month order | ascending | `sortedBy { it.key }`; test 4 | MATCH | — |
| 4 | default scaling factor | `peer.scaling_default` = 1.0 | `V9__parameters.sql` L35: 1.0 | MATCH | — |
| 5 | segment and look-back (12 full months, which clients) | stated in the KDoc only | assembled outside the calculator (`PeerSimulationService`); no test | UNDOCUMENTED | open question Q1 |
| 6 | business definition | — | KDoc: "no specification exists yet ... expected to change" | UNDOCUMENTED | open question Q2 |

## Open questions
- [ ] Q1 (owner: harbor-platform-team) — Define the peer segment population and the look-back window (currently all
  clients with the same segment label, last 12 full months, per `PeerSimulationService`); add a service-level test.
- [ ] Q2 (owner: harbor-platform-team) — Confirm median (not mean) and quantity-only output as the intended business
  rule, or specify the target definition; until then the series stays a draft and reports must not cite it (RPT-001).

## Performance notes
At most 12 months × clients of the segment; computed in memory on `postProduct1PeerSimulation` and stored as
`session_peer_simulation` (BR-P1-001-7).

## Change log
| Date | Change | Ref |
|---|---|---|
| 2026-10-12 | Created from the calculator and a new executor test (was "code only" in REPO_MAP); 2 open questions for the owner | — |

[^impl]: PeerBenchmark.kt (harbor-backend, `core`, layer `utils`)
[^rounding]: Rounding.kt (harbor-backend, `core`, layer `utils`)
[^tests]: PeerBenchmarkTest.kt (harbor-backend, `core` tests, `utils`)
