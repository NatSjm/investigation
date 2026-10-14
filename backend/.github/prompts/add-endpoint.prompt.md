---
agent: agent
description: Contract-first checklist for adding or changing a REST operation (harbor-api.yaml -> regenerate -> override fun -> maps).
argument-hint: "operationId and purpose, e.g. getProduct1Projection - four projection tables for the session"
---
Add or change the operation `${input:operationId:getProduct1Projection}` following the contract-first rules in `AGENTS.md`
and `.github/instructions/api.instructions.md`.

Work through this checklist and report each step:

1. **Contract** - edit `core/src/main/resources/openapi/harbor-api.yaml`: path item under the context tag, unique `operationId`, request/response schemas in
   `components/schemas`; `/session/**` paths reference `components/parameters/SessionHeader` (`X-Harbor-Session`).
   Reuse existing schemas before adding new ones.
2. **Regenerate** - `mvn -q -pl core -am -DskipTests generate-sources`; confirm the new method appears on the `*Api` interface
   (do not open or edit `target/`).
3. **Implement** - `override fun ${input:operationId:getProduct1Projection}(...)` in the context controller (`harbor/api/<Ctx>Controller.kt`)
   (no mapping annotations), delegating to the context manager (`harbor/manager/<Ctx>Manager.kt`); add the manager method with KDoc.
4. **Tests** - controller contract test through the generated interface (with the session header where required) and
   a manager unit test with synthetic data (mock the dependencies listed in `components.md`).
5. **Maps** - run `python3 scripts/docs/gen-all.py`; check `docs/_generated/api-index.md` shows the operation with its handler
   (not `_not implemented_`) and include the regenerated maps in the change.
6. **Spec** - state the spec ID the operation implements (e.g. `P1-001`); if no spec exists, say so and propose the ID
   (`<CONTEXT>-<nnn>`) so the docs repo can add it.

Return the diff only, then the checklist with one line per step.
