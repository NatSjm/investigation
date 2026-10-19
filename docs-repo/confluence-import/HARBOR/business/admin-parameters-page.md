---
source: Confluence HARBOR/Admin parameters page
title: Admin parameters page
section: business
confluence_id: 48103700
url: https://confluence.example.com/pages/viewpage.action?pageId=48103700
author: John Roe
last_modified: 2025-10-03
path: HARBOR > Business > Cover quote rules > Admin parameters page
parent: cover-quote-rules.md
source_lang: cs
status: imported
attachments:
  - _attachments/admin-parameters-page/parameters-screen.png
attachments_not_imported: [manual.pdf]
imported_from: confluence-import/raw-html/business/Admin-parameters-page_48103700/48103700.html
---

# Admin parameters page

> Exported legacy page. Quarantined — see `confluence-import/README.md`. Not authoritative.

The **Parameters** page lets an administrator change the *cover factor* and the `stress.threshold` value without a deployment. Values are read by the calculations at the start of every session \<session id>.

## Screen

![Parameters screen](../_attachments/admin-parameters-page/parameters-screen.png)

Status of the screen: **LIVE** (tick)

## Rules

- Only users with the **ADMIN** role see the menu entry.
- A change takes effect for new sessions only:
  - open sessions keep the values they started with;
  - closed sessions are never recalculated.
- Every change is logged with user and time.  
  The log is kept for 12 months.

> **Info**
>
> The thresholds themselves are documented on the [Cover quote rules](cover-quote-rules.md) page; the topics on [Kafka topics](../technical/kafka-topics.md#Kafkatopics-Parameters).

## Parameters

| Key | Scope | Default \| unit | Notes |
|---|---|---|---|
| `cover.factor` | global | 1.15 \| ratio | - applies to Product 1<br>- applies to Product 2 |
| `stress.threshold` | per product | 0.80 \| ratio | See the admin manual (attachment not imported: manual.pdf) and [the external wiki](https://example.com/wiki). |

Related: [cover rules by id](cover-quote-rules.md), section index.
