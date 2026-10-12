# Update Log

## 2026-10-12
* **product1: Run 2 and Run 3 done, Run 4 due.** Legacy page "Product 1 overview tables" merged into [P1-001](/features/product1/P1-001.md) (4 confirmations, 2 conflicts → open questions; page moved to `_done/`). Audits: [monthly_projection](/domain/calculations/monthly_projection.md) 11 items (6 MATCH, 3 DOC-STALE corrected, 1 UNDOCUMENTED, 1 CODE-SUSPECT → status draft, Q1-Q2), [horizon_totals](/domain/calculations/horizon_totals.md) 6 MATCH. New concept [peer_benchmark_simulation](/domain/calculations/peer_benchmark_simulation.md) (draft) with executor `PeerBenchmarkTest` added to the backend (was code only). P1-001 and `monthly_projection` are drafts until the owner answers the open questions and re-verifies.
* **Horizon totals added.** New calculation [horizon_totals](/domain/calculations/horizon_totals.md) (draft, Run 1 from the aggregator and its test): each projection table summed over the horizon per key with share of value, returned as `tables.totals` and shown as three separate tables under the monthly ones ([P1-001](/features/product1/P1-001.md) BR-P1-001-11, mirrored by [PRS-001](/features/presentation/PRS-001.md)); glossary entry *Projection* extended.
* **Presentation context added (FE-only).** [PRS-001](/features/presentation/PRS-001.md) (draft, Run 1 from `feature:presentation` and the channel module) and the first flow document [client-presentation](/flows/client-presentation.md) (`type: Flow`, new folder `flows/`); `contexts.yml` gained `presentation`, the FE maps a `components.md` (shared component library) and a Channels column (BroadcastChannel), the graph `channel:` and `shared-ui` `component:` nodes. [MTG-001](/features/meetings/MTG-001.md): meetings list split into client / preparation pages (change log).

## 2026-10-09
* **Spec lifecycle and migration planning added.** Skill `spec-lifecycle` (run-by-run lifecycle + review checklist),
  agent `migration-lead` with prompt `migration-plan`, script `scripts/migration-status.ps1`; first plan
  [migration/all.md](/migration/all.md): 16 runs due, 1 of 10 contexts ready for the analyst.
* **Bundle rebuilt for the Harbor simulated domain.** Concepts: [CLI-001](/features/clients/CLI-001.md),
  [MTG-001](/features/meetings/MTG-001.md), [P1-001](/features/product1/P1-001.md),
  [STR-001](/features/stress/STR-001.md), [MKT-001](/features/market/MKT-001.md), [RPT-001](/features/reports/RPT-001.md);
  calculations [client_role_classification](/domain/calculations/client_role_classification.md),
  [monthly_projection](/domain/calculations/monthly_projection.md),
  [stress_test_monthly](/domain/calculations/stress_test_monthly.md),
  [cover_ratio](/domain/calculations/cover_ratio.md) (draft), [scenario_price_path](/domain/calculations/scenario_price_path.md) (draft);
  [Glossary](/domain/glossary.md), [Context map](/domain/context-map.md), [Architecture overview](/architecture/overview.md),
  [Integrations map](/architecture/integrations.md), ADR-0001..0003. Legacy pages quarantined under
  `confluence-import/HARBOR/`; work items `P1-001.yml`; test design `STR-001.feature` + fixture.
* **Backend restructured to layered layout; docs paths and graph contexts updated.** `harbor-backend` is now
  `core` (package-by-layer) + `kafka_client` + `init_docker_compose`; specs, calculations, `docs-map.yml`, agents and
  skills point at `core/src/main/kotlin/harbor/<layer>/` paths, contexts come from `contexts.yml`
  ([ADR-0004](/architecture/adr/0004-layered-backend-and-context-prefixes.md)), the BE map `components.md` was added
  and the per-module graph nodes became `context:<x>` nodes.
