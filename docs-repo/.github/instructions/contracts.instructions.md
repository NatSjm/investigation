---
applyTo: "contracts/**"
description: Proposed API / topic contracts designed in the docs repo before code exists - proposals, not evidence.
---

# Proposed contracts

Files under `contracts/proposed/` describe what is **being designed**. What the code **implements** is under
`generated/openapi/` and `generated/asyncapi/` and arrives there only through a code repository and the collector.
Rules and lifecycle: `contracts/conventions.md`.

- One file per spec and kind: `<SPEC-ID>.openapi.yaml` / `<SPEC-ID>.asyncapi.yaml`, from `_template.openapi.yaml`.
- `info` carries `x-spec`, `x-status: proposed`, `x-generated-by`, `x-generated-at`.
- Every operation has an `operationId`; cite operations by it in specs, stories and scenarios.
- In the spec's API / Events table the contract column points at `contracts/proposed/<file>#/paths/...` and the
  Purpose column says **proposed**.
- Never copy a proposal into `generated/**`; never cite a proposal as current behaviour; stories built on one carry
  the label `needs-contract`.
- When the collector brings the implemented contract, switch the spec's links to `generated/`, add a change-log row,
  and delete the proposal or set `x-status: implemented` with `x-implemented-in`.
