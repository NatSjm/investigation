---
source: Confluence HARBOR/Cover quote rules
title: Cover quote rules
section: business
confluence_id: 48103701
url: https://confluence.example.com/pages/viewpage.action?pageId=48103701
author: Jane Doe
last_modified: 2025-09-02
path: HARBOR > Business > Cover quote rules
parent: Business
source_lang: cs
status: imported
imported_from: confluence-import/raw-html/business/Cover-quote-rules_48103701/48103701.html
---

# Cover quote rules

> Imported Confluence page. Quarantined — see `confluence-import/README.md`. Not authoritative.

## Purpose

A cover quote is offered when the projected cover ratio of a product group falls under the threshold. This page keeps the rules the representatives agreed on in 2024; the [admin parameters](admin-parameters-page.md) page lists the values.

---

## Rules

1. The quote covers the next 6 months.
2. The premium is `exposure * cover.factor`, rounded to whole units.

   Rounding is half up.
3. No quote when the client is an exporter only.

- [x] Confirm the rounding with finance
- [ ] Agree the exporter rule with the product owner

> **Warning: Out of date?**
>
> The 6-month horizon was questioned in SES-001 meetings; check the code before quoting it.

**Premium query**

```sql
select client_id, exposure * 1.15 as premium
  from cover_exposure
 where cover_ratio < 0.80;
```

**Expand: Worked example**

Exposure 1 250, factor 1.15: premium 1 437.5, rounded to 1 438.

> Quote from the 2024 workshop: "the factor is a business decision, not a formula".

### Matrix

<!-- merged cells flattened by confluence-import.py -->
| Role | Product |  |
|---|---|---|
|  | Product 1 | Product 2 |
| importer | quote | quote |
| exporter | no quote |  |

|  |  |
|---|---|
| **Owner** | product owner, cover |
| **Reviewed** | 2025-01 |

**Decision**

Kept as is until the product owner decides.
