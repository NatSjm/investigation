# Update Log

## 2026-10-20
* **Catalogue for free-text requests.** `scripts/gen-catalogue.py` writes [generated/catalogue.md](/generated/catalogue.md):
  one line per context (also code-only ones), flow, spec with aliases, calculation with parameters, API endpoint
  (also code-only ones), Kafka topic, table with owner, external service and glossary alias. An agent given a request
  that names no ID reads it first, picks the subjects itself and builds one pack per subject (analyst agent step 1,
  skill `task-context`); `collect-evidence.py --graph` rebuilds it, CI checks it with `--check`.
* **One context pack for several subjects; flows and contexts as subjects.** `scripts/context-pack.py --task` may
  be repeated (one pack, shared sections merged and deduplicated, budget +300 per extra subject); a flow
  (`flows/<name>.md`: body, the rules it cites per spec, graph impact of its code_refs) and a context
  (`context:<name>`: specs, endpoints, tables, calculations, topics, classes by layer, pages, integrations, proposed
  contracts - the overview for placing new work) are subjects; the free-text fallback applies glossary aliases and
  scores flows. Section markers: `.github/skills/task-context/references/pack-anatomy.md`.
* **Request epics.** A request spanning several specs gets `work-items/<slug>.yml` (`request:`, `specs: [...]`, a
  story may cite rules of several specs) and the analysis document `work-items/<slug>.md` written first from
  `work-items/_analysis-template.md`; `validate-work-items.py` checks both shapes, `coverage-matrix.py` counts the
  stories for every spec they cite. Rule kept: nothing new without a (draft) rule.

## 2026-10-19
* **Confluence HTML export importer; four legacy pages imported.** `scripts/confluence-import.py` (standard library)
  turns a Confluence HTML space export kept under `confluence-import/raw-html/<section>/` into
  `confluence-import/<SPACE>/<section>/<slug>.md` pages with the quarantine header block, copies the images a page
  shows to `<SPACE>/_attachments/<slug>/`, rewrites the links between pages and regenerates the inventory of
  `confluence-import/README.md`; pages already under `_done/` are skipped, `--check` for CI. Imported (synthetic
  fixture, two page trees): `HARBOR/business/admin-parameters-page.md`, `HARBOR/business/cover-quote-rules.md`,
  `HARBOR/technical/kafka-topics.md`, `HARBOR/technical/deployment-notes.md` (`status: imported`, Run 2 due; listed
  in `migration/all.md`).

## 2026-10-15
* **Meetings prefix renamed `MTG` → `SES`.** [SES-001](/features/meetings/SES-001.md) (was `MTG-001`), rule IDs `BR-SES-001-n`, dataset `ses-session-snapshot`, `contexts.yml`, `docs-map.yml`, every citation in specs, flows, work items and the `@docs` tags of the meetings classes and hooks; generated maps, graph and boards regenerated.
* **Specs cut by screen and modal; product mirrors; two flows.** `features/conventions.md` gains the section
  "Shaping specs" (contexts follow the code, first spec = screen, modals with own rules = own spec, ownership by
  rule, product types as a dimension or a mirrored context, flows for cross-context behaviour, formulas as
  calculations, optional screenshots). [P1-001](/features/product1/P1-001.md) is now the screen only; its modal
  rules moved to [P1-002](/features/product1/P1-002.md) (modelled movements, former BR-5/6 withdrawn with pointers)
  and [P1-003](/features/product1/P1-003.md) (peer simulation, former BR-7; the 0.1-5.0 factor range became an
  open question because neither the contract nor the code enforces it). Product 2 documented as mirrors
  [P2-001](/features/product2/P2-001.md), [P2-002](/features/product2/P2-002.md), [P2-003](/features/product2/P2-003.md).
  New flows [meeting-journey](/flows/meeting-journey.md) and
  [session-inputs-recalculation](/flows/session-inputs-recalculation.md) (the stress test is not rerun
  automatically). Work items split accordingly (`P1-002.yml`, `P1-003.yml`); `docs-map.yml`, the context map,
  the glossary references, the calculations' `used_by` and the `@docs` tags of the validator, the peer service and
  the four modal hooks updated; generated maps, graph, indexes, coverage matrix and migration boards regenerated.

## 2026-10-14
* **Scripts ported from PowerShell to Python (standard library, 3.11+).** Every `scripts/*.py`, `scripts/hooks/guard-generated.py`
  and the code-repo generators (`scripts/docs/*.py`, `check-file-size.py`, `seed-local.py`, `apply-kit.py`) replace the former
  `.ps1` files one to one; flags are long options (`--check`, `--strict`, `--task`). Hooks, CI workflows and all documentation
  updated; `python3` in CI and on macOS, `python` on Windows. Generated maps, graph, indexes and analytics regenerated with the
  new scripts (same content; tables now sort case-insensitively by a rule inside the scripts, no locale involved).

## 2026-10-12
* **audited horizon_totals: 13 findings.** Re-audit of [horizon_totals](/domain/calculations/horizon_totals.md) against `ProjectionAggregator` and `ProjectionAggregatorTest`: 7 MATCH, 4 DOC-STALE, 2 UNDOCUMENTED, 0 CODE-SUSPECT. Corrects the Run 3 audit, which reported 6 MATCH: worked example 2 had a hand-computed share (0.3354) that the test does not assert, and the rows lacked test method names. Both are fixed by keeping only values the test asserts. Still open: share rounding (per key, no remainder correction), the `UNKNOWN` key, and the city-filter wording (Q1-Q3). Status stays draft. Inherited by [P1-001](/features/product1/P1-001.md) (BR-P1-001-11).
* **product1: Run 2 and Run 3 done, Run 4 due.** Legacy page "Product 1 overview tables" merged into [P1-001](/features/product1/P1-001.md) (4 confirmations, 2 conflicts → open questions; page moved to `_done/`). Audits: [monthly_projection](/domain/calculations/monthly_projection.md) 11 items (6 MATCH, 3 DOC-STALE corrected, 1 UNDOCUMENTED, 1 CODE-SUSPECT → status draft, Q1-Q2), [horizon_totals](/domain/calculations/horizon_totals.md) 6 MATCH. New concept [peer_benchmark_simulation](/domain/calculations/peer_benchmark_simulation.md) (draft) with executor `PeerBenchmarkTest` added to the backend (was code only). P1-001 and `monthly_projection` are drafts until the owner answers the open questions and re-verifies.
* **Horizon totals added.** New calculation [horizon_totals](/domain/calculations/horizon_totals.md) (draft, Run 1 from the aggregator and its test): each projection table summed over the horizon per key with share of value, returned as `tables.totals` and shown as three separate tables under the monthly ones ([P1-001](/features/product1/P1-001.md) BR-P1-001-11, mirrored by [PRS-001](/features/presentation/PRS-001.md)); glossary entry *Projection* extended.
* **Presentation context added (FE-only).** [PRS-001](/features/presentation/PRS-001.md) (draft, Run 1 from `feature:presentation` and the channel module) and the first flow document [client-presentation](/flows/client-presentation.md) (`type: Flow`, new folder `flows/`); `contexts.yml` gained `presentation`, the FE maps a `components.md` (shared component library) and a Channels column (BroadcastChannel), the graph `channel:` and `shared-ui` `component:` nodes. [SES-001](/features/meetings/SES-001.md): meetings list split into client / preparation pages (change log).

## 2026-10-09
* **Spec lifecycle and migration planning added.** Skill `spec-lifecycle` (run-by-run lifecycle + review checklist),
  agent `migration-lead` with prompt `migration-plan`, script `scripts/migration-status.py`; first plan
  [migration/all.md](/migration/all.md): 16 runs due, 1 of 10 contexts ready for the analyst.
* **Bundle rebuilt for the Harbor simulated domain.** Concepts: [CLI-001](/features/clients/CLI-001.md),
  [SES-001](/features/meetings/SES-001.md), [P1-001](/features/product1/P1-001.md),
  [STR-001](/features/stress/STR-001.md), [MKT-001](/features/market/MKT-001.md), [RPT-001](/features/reports/RPT-001.md);
  calculations [client_role_classification](/domain/calculations/client_role_classification.md),
  [monthly_projection](/domain/calculations/monthly_projection.md),
  [stress_test_monthly](/domain/calculations/stress_test_monthly.md),
  [cover_ratio](/domain/calculations/cover_ratio.md) (draft), [scenario_price_path](/domain/calculations/scenario_price_path.md) (draft);
  [Glossary](/domain/glossary.md), [Context map](/domain/context-map.md), [Architecture overview](/architecture/overview.md),
  [Integrations map](/architecture/integrations.md), ADR-0001..0003. Legacy pages quarantined under
  `confluence-import/HARBOR/`; work items `P1-001.yml`; test design `STR-001.feature` + fixture.
* **Backend restructured to layered layout; docs paths and graph contexts updated.** `harbor-backend` is now
  `core` (package-by-layer) + `kafka-client` + `init_docker_compose`; specs, calculations, `docs-map.yml`, agents and
  skills point at `harbor-core/src/main/kotlin/com/acme/harbor/<layer>/` paths, contexts come from `contexts.yml`
  ([ADR-0004](/architecture/adr/0004-layered-backend-and-context-prefixes.md)), the BE map `components.md` was added
  and the per-module graph nodes became `context:<x>` nodes.
