---
description: Produce a high-level design document for a feature or epic.
agent: architect
---

Feature/Epic ID: ${input:id}
Scope: ${input:scope:new feature|change to existing|integration}

Create `architecture/hld/${input:id}.md`: context, C4 container + component Mermaid, main sequence diagram,
data model delta, integration/Kafka impact, NFRs, risks, open decisions (link/create ADRs).
