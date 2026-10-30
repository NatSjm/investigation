---
source: Confluence HARBOR/Meeting flow
last_modified: 2025-09-02
author: unknown
confluence_id: 48103610
url: https://confluence.example.com/display/HARBOR/Meeting+flow
---

# Meeting flow

> Imported Confluence page. Quarantined — see `confluence-import/README.md`. Not authoritative.

This page describes how a representative runs a client meeting in Harbor, from finding the client to handing over
the report.

## Before the meeting

1. Open **Clients** and search by name or registry reference (at least two characters).
2. Open the client. The overview shows one card per product group with volume, value, the importer/exporter flag,
   the cover ratio and a small chart of the last twelve months.
3. Press **Prepare** on a card to open a preparation session. A preparation session behaves exactly like a meeting
   but is marked as a dry run and does not change anything about the client afterwards.

## The four steps of a meeting

Press **Start meeting** on a product group card. Harbor creates a session and every screen from now on belongs to
that session (the session id is sent with every request).

| Step | Screen | What happens |
|---|---|---|
| 1 | Product overview | The projection tables for the selected product group and the cover charts. The representative can enter modelled movements per month and run the peer simulation. |
| 2 | Scenarios | Representative and client define price scenarios on top of the market curve. |
| 3 | Stress test | The scenarios are run against the projection; results per city or transport mode. |
| 4 | Summary | Review, optional role override with a reason, **Close meeting**. |

## After closing

- The session appears on the **Meetings** page.
- The report is generated as PDF and can be downloaded from the Meetings page once it is ready.
- Use **Export to spreadsheet** on the Meetings page to download the four tables as an XLS file for the client.
- If the role was overridden during a real meeting, the client's role is updated accordingly.

## Notes

- A meeting that is left open is closed automatically overnight.
- Only one meeting per client and product group can be open at a time.
