---
type: Document
title: Proposed contracts - conventions
description: Where an API or topic contract lives while it is being designed in the docs repo (before any code), how it is marked, who reviews it, and how it moves into a code repository and comes back as evidence under generated/.
tags: [conventions, contracts, proposals]
status: stable
generated: { by: human:platform-team, at: 2026-10-13T09:00:00Z }
verified: { by: human:platform-team, at: 2026-10-13T09:00:00Z }
stale_after: 2027-04-13T00:00:00Z
---

# Proposed contracts - conventions

Analysis often designs an API before any code exists. Such a contract is a **proposal**, like a story or a test
design, and it must never be mistaken for evidence of what the application does. The repository keeps the two apart
by folder:

| Folder | Meaning | Owner |
|---|---|---|
| `generated/openapi/`, `generated/asyncapi/` | what the code implements; copied from the code repositories by the collector, never edited by hand | `scripts/collect-evidence.py` |
| `contracts/proposed/` | what is being designed; written in a PR, reviewed, then handed to a code repository | analyst, architect, tech lead |

## Writing a proposal

- One file per spec and kind: `contracts/proposed/<SPEC-ID>.openapi.yaml` or `<SPEC-ID>.asyncapi.yaml`; several specs
  may share one file only when they share one service boundary (name it after the service, list the specs in `x-specs`).
- Start from `contracts/proposed/_template.openapi.yaml`. The `info` block carries the provenance the OKF frontmatter
  carries elsewhere: `x-spec` (or `x-specs`), `x-status: proposed`, `x-generated-by: copilot/<agent> | human:<id>`,
  `x-generated-at`.
- Every operation has an `operationId`; stories and acceptance criteria cite operations by that id, never by path alone.
- Schemas use the glossary terms; synthetic examples only.
- The spec's **API / Events** table lists the operations with the contract column `contracts/proposed/<file>#/paths/...`
  and the word **proposed** in the Purpose column, so a reader and the context pack see the state at a glance.
- CI lints `contracts/proposed/*.yaml` with the same OpenAPI / AsyncAPI linters as the published contracts.

## Lifecycle

1. **Draft** - the analyst (or architect) writes the proposal in the same PR as the spec or story. Status in the
   file: `proposed`.
2. **Review** - the architect or tech lead reviews it with the spec. Conflicts with an existing operation in
   `generated/openapi/backend.yaml` are recorded as open questions in the spec.
3. **Handover** - the backend (or the owning service) team copies the file into its repository as the contract it
   generates code from. From that moment the code repository owns it; the proposal is not edited any more.
4. **Evidence** - the collector copies the implemented contract back into `generated/`. Operations present in the
   contract but without a handler show as `_not implemented_` in `generated/be/api-index.md`, so partially built
   APIs stay visible.
5. **Close** - `doc-sync` switches the spec's API table from the proposal link to the `generated/` anchor, adds a
   change-log row, and either deletes the proposal or sets `x-status: implemented` with `x-implemented-in: generated/openapi/backend.yaml`.
   Keep it only while someone still needs the design history; the spec's change log is the record.

## Rules

- A proposed contract is never cited as current behaviour; the analyst labels stories built on it `needs-contract`.
- Agents read `generated/` for what exists and `contracts/proposed/` for what is being designed; never the generated
  clients or DTO classes.
- Nothing under `contracts/proposed/` is copied into `generated/` by hand; the only way in is through a code repository.
