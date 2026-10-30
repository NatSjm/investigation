---
source: Confluence HARBOR/Kafka topics
title: Kafka topics
section: technical
confluence_id: 48103800
url: https://confluence.example.com/pages/viewpage.action?pageId=48103800
author: Tom Brown
last_modified: 2025-09-02
path: HARBOR > Technical > Kafka topics
parent: Technical
source_lang: cs
status: imported
imported_from: confluence-import/raw-html/technical/Kafka-topics_48103800/48103800.html
---

# Kafka topics

> Imported Confluence page. Quarantined — see `confluence-import/README.md`. Not authoritative.

Topics the backend produces. Consumers are listed in [Deployment notes](deployment-notes.md); the parameter topic feeds the [admin parameters page](../business/admin-parameters-page.md).

## Parameters

| Topic | Key | Payload |
|---|---|---|
| `harbor.parameters.changed` | parameter key | ParameterChanged |
| `harbor.session.closed` | session id | SessionClosed |

## Payload

```js
{ "key": "cover.factor", "value": "1.15", "changedBy": "admin" }
```

- **Retention**: 7 days
- **Partitions**: 3
