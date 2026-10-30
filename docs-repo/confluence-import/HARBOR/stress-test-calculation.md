---
source: Confluence HARBOR/Stress test calculation
last_modified: 2025-06-14
author: unknown
confluence_id: 48103522
url: https://confluence.example.com/display/HARBOR/Stress+test+calculation
---

# Stress test calculation

> Imported Confluence page. Quarantined — see `confluence-import/README.md`. Not authoritative.

## What the stress test shows

For each scenario defined on the Scenarios page the Stress test page shows a table with one row per month of the
planning horizon. The columns are the dimension values (cities for Product 1, transport modes for Product 2) and
the last column is the cumulative figure.

## Who is an importer

The client is treated as an **importer** when more than half of the goods moved in the last year came in, otherwise
as an **exporter**:

```
share = inbound / (inbound + outbound)
share > 0.5  -> importer
share <= 0.5 -> exporter
```

If the client moved less than 100 units in the year the stress test is not shown at all.

## Formula

For every month `m`, scenario `s` and dimension value `d`:

```
exposure(m, d) = uncoveredQty(m, d) * (scenarioPrice(m) - baselinePrice(m))      for an importer
exposure(m, d) = -uncoveredQty(m, d) * (scenarioPrice(m) - baselinePrice(m))     for an exporter
cumulative(m, d) = cumulative(m - 1, d) + exposure(m, d)
```

`uncoveredQty` is the projected quantity of the month minus the quantity covered by valid policies.
Transport prices are shown in the chart below the table for information only; they do not enter the table.

## Example

Importer, 100 uncovered units, baseline price 10.00, scenario price 11.00:

| Month | Exposure | Cumulative |
|---|---|---|
| 1 | 100.00 | 100.00 |
| 2 (scenario price 12.00) | 200.00 | 300.00 |

## Rounding

Two decimal places, commercial rounding.

## Open points (as of June 2025)

- The product owner asked whether the transport price change should be added to the table. Decision pending.
- Mixed clients (roughly equal in and out) are currently shown as exporters; a third category may be introduced.
