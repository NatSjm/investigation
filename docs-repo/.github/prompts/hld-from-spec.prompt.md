---
name: hld-from-spec
description: Produce a high-level design document for a feature or epic.
argument-hint: "featureId [scope]"
agent: architect
---
Feature/Epic ID: ${input:id:MKT-001}
Scope: ${input:scope:new feature|change to existing|integration}

Create `architecture/hld/${input:id}.md` (`type: HLD`): context, C4 container + component Mermaid, main sequence
diagram (session header, Kafka hops, external contracts), data model delta, integration impact, NFRs, risks, open
decisions (link or create ADRs). Validate and rebuild indexes.
