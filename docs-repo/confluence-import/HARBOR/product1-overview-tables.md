---
source: Confluence HARBOR/Product 1 overview tables
last_modified: 2025-07-21
author: legacy
confluence_id: 48103588
url: https://confluence.example.com/display/HARBOR/Product+1+overview+tables
---

# Product 1 overview tables

> Exported legacy page. Quarantined — see `confluence-import/README.md`. Not authoritative.

The Product 1 page of a session shows the monthly projection for the corridor Veldora - Norland as three tables.
All tables cover the planning horizon of the session (default 24 months) and every column is cumulative, i.e. the
value of month 6 already contains months 1 to 5.

## Table 1 - by grade

One column per grade: `P1-STD`, `P1-PRM`, `P1-ECO`. Rows are months. Cells show quantity and value.

## Table 2 - by city

One column per city hub: Aldmoor, Brightwater, Carrow, Dunmere. The city selector above the tables restricts this
table to one city; the other tables are not affected.

## Table 3 - by direction

Two columns: inbound and outbound. This is the table used to explain to the client whether they are more of an
importer or an exporter in the period.

## Values

- Value = quantity × unit price × the price index of the month (from the market curve).
- Landed cost = value plus tariff plus handling cost per city plus transport cost.
- Figures are in the price basis selected for the session (Veldora or Norland).

## Modals

- **Model movements**: enter quantity and unit price per month, grade, city and direction. Saving replaces all
  previously modelled movements of the session and the tables refresh.
- **Peer simulation**: pick a peer segment and a scaling factor; the peer series is drawn in the chart.

## Cover charts

Below the tables one chart per grade shows the cover ratio per month.
