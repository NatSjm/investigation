# External patterns reviewed (2026-10-11) and what to take from them

Sources: Erik Lieben, "Agentic dev workflow: documentation" (blog + repo `eriklieben/agentic-dev-workflow`, skills
`doc-init`, `doc-adr`, `doc-design`, `doc-rfc`, `doc-prd`, `doc-runbook`, `doc-postmortem`, `doc-spike`, `meta-wrap-up`);
GitLab `.ai/principles/` (distillation prompt, manifest, baselines, distilled checklists); Luke Wilson's gist
"Repo-local documentation system for humans & agents". All three are Claude Code / GitLab Duo oriented; the skill
format (`SKILL.md`, agentskills.io) is the same one Copilot reads, so procedures port one to one.

## 1. What each one is

| Source | Core idea | Where it is strong | Where it does not fit us |
|---|---|---|---|
| Lieben | One shared docs repo for several code repos; each code repo has a `workflow.json` pointing at it; typed documents (ADR, RFC, PRD, design, runbook, post-mortem, spike) generated *during* the session; `doc-init` bootstraps docs for an existing codebase in phases with an approval gate; `meta-wrap-up` checks for documentation gaps at session end | typed templates with hard quality rules (ADR needs 2 real options, a "because", one negative consequence; inferred ADRs marked "Inferred, needs review"); phased bootstrap; gap detection as a habit | no code-derived maps or graph, no traceability IDs, no freshness gate; docs are prose for humans first; VitePress publishing we do not need |
| GitLab | *Distillation*: long SSOT docs are compressed by a scheduled agent into short, imperative, traceable checklists per domain (`distilled/<domain>.md`) that coding agents load automatically; `manifest.yml` maps domain -> source paths, file filters, owner team, baseline; `baselines/` are human-curated rules that pass through verbatim; weekly re-distillation diffs sources since the last run; MRs open as drafts, routed to owner teams, never auto-merged; prompt size budget | the only one with a real **two-layer** model (SSOT for people, distilled layer for agents) and a maintenance loop with ownership and budgets | their SSOT is developer guidelines, not functional specs; the consumer is a coding/review agent, not an analyst; needs Duo Workflow infrastructure (we would use Copilot coding agent + a scheduled workflow) |
| Wilson gist | `AGENTS.md` is only an index; `docs/systems/`, `docs/flows/`, `docs/architecture/`, ADRs, glossary; templates with "Questions this doc answers", "Invariants and assumptions", "Downstream effects", "Common pitfalls", "Source map"; a PR that changes behaviour updates docs in the same change | the **Flow** document type for behaviour that crosses systems; the retrieval-oriented "questions this doc answers"; the source map per doc | single repo, no generation, no agents or scripts, no trust/freshness metadata |

## 2. What we already have (no action)

- Shared docs repo fed by several code repos: yes (`docs-repo/` + the single collector `collect-evidence.py` / `collect-evidence.yml`), with
  code maps and a graph the others do not have.
- Typed documents with frontmatter and quality rules: yes (OKF concepts: Feature Spec, Attested Computation,
  Decision, HLD, Glossary; ADR template with alternatives).
- `AGENTS.md` as index + read order; glossary; traceability IDs; freshness gate; task-scoped context packs.
- Session-end gap check: partly (agentStop hook validates the bundle; `check-freshness.py` in code repos).

## 3. Adopt

### A. A distilled layer for coding agents (from GitLab) - highest value
Our specs are the SSOT for people and for the analyst. Developers' Copilot in `backend/` and `frontend/` does not
read them (too long, wrong repo). Distil each context into one short checklist that the code repos load
automatically:

- `docs-repo/distilled/<context>.md`: 30-80 imperative lines ("DO NOT round before summing (BR-P1-001-4)",
  "Use `X-Harbor-Session` on every session endpoint (SES-001)"), each line traceable to a BR, a calculation
  concept or an ADR; nothing that is not checkable in code; US/UK spelling fixed; size budget enforced.
- Published into the code repos as `.github/instructions/<context>.instructions.md` with
  `applyTo: "**/harbor/**/{Product1,Projection,Peer}*.kt"` (BE, prefixes from `contexts.yml`) and
  `applyTo: "src/features/product1/**"` (FE). Copilot then applies the rules whenever a developer edits that context.
- `manifest` = our `contexts.yml` + `docs-map.yml` extended with `owners:` per context; `baselines/<context>.md` =
  hand-written rules that survive regeneration verbatim (e.g. conventions from `features/conventions.md`).
- Agent `distiller` (new) + script `distill-check.py`: frontmatter `distilled_at` + `sources_sha`; re-run when a
  spec, calculation or ADR of the context changed since `sources_sha`; weekly scheduled workflow opens a draft PR
  per owner team, never auto-merged. Rules copied from GitLab: traceability, selectivity, imperative mood, merge
  duplicates, keep rule + exception in one bullet, drop an item only when confirmed absent from the full source
  (not merely missing from the diff), leave accurate items untouched.

### B. Flow documents (from the gist)
Cross-context behaviour has no home today (meeting flow: client search -> product selection -> product page ->
report; import pipeline: XLS -> tables -> Kafka -> projection refresh; session lifecycle incl. header). Add
`docs-repo/flows/<slug>.md` (`type: Flow`) with Trigger, Participants (contexts), Steps with `file:line` from the
graph, Data changes, Failure behaviour, Invariants, Source map. `gen-graph.py` can seed the step list from
`depends-on` edges across communities. The analyst packs include the flows that mention the spec.

### C. "Questions this doc answers" (from the gist)
Add `questions: [...]` to spec and calculation frontmatter (3-6 questions a person would type). `context-pack.py`
free-text matching uses `description` + `aliases` today; adding `questions` improves hits for analysts' phrasing.
Cheap, no new tooling.

### D. Phased bootstrap with an approval gate (from Lieben `doc-init`)
Our `migration-status.py` already produces the plan; add the gate: `migration-lead` must present the plan and
wait for approval before any Run 1 is started in batch; Run 1 batch = one Copilot coding agent issue per context.
Also take the **git-history phase**: an `architect` task that infers ADRs from history ("Inferred, needs review",
"Rationale unknown, confirm with the team"), for decisions nobody wrote down. Our ADR template already requires
alternatives; add the "at least one negative consequence" rule.

### E. Wrap-up gap check in the code repos (from Lieben `meta-wrap-up`)
A prompt `/wrap-up` in `code-repo-kit/{be,fe}`: `git diff --name-only` -> `map-paths.py` -> list specs to touch,
calculations changed (-> calc-auditor), new endpoint/topic/table without spec section, decision without ADR.
Output is a checklist the developer acts on; the freshness CI gate remains the hard stop.

## 4. Consider later
- Lieben's extra types (runbook, post-mortem, spike): not needed for the analyst; a `spike` type could hold the
  investigations the analyst agent performs ("what is covered by tests?") instead of chat output.
- GitLab's owner-team fan-out into CODEOWNERS: useful once more than one team owns contexts; `owners:` in
  `contexts.yml` prepares it.
- Wilson's "promote a system doc to a flow when it becomes cross-system": a rule for `doc-sync`.

## 5. Skip
- VitePress / GitHub Pages site: Confluence publish covers reading; agents read Markdown.
- `workflow.json` pointer per code repo: our kit already fixes the paths in `AGENTS.md`/scripts; a pointer file
  only helps when the docs repo location varies per developer. Could be added as `docs-repo.json` later.
- Daily memory files per session: Copilot has no equivalent; `log.md` + context packs cover it.

# Second review (2026-10-22): does anything like the whole project exist?

Question asked: does anywhere exist something like our documentation project? Answer: no. Every slice of it has a
neighbour, nobody has put the slices together for the analyst, and nobody works under our constraints (Copilot
only, no MCP, Python standard library, nothing an agent writes trusted until a person verified it).

Sources: Reversa (arXiv 2605.18684, "reverse documentation engineering" of legacy software into operational
specifications for AI agents); CoreStory (corestory.ai, commercial "Code Intelligence Model"); business-rule
recovery research - Kalohia, ACL 2026 industry track (COBOL / PL/I requirements extraction), AgentModernize
(arXiv 2605.17535, Behavioral Specification Graphs), COBRAIN (ACM 2025, LLM vs rule-based extraction); generated
repository wikis - Google Code Wiki (developers.googleblog.com, public preview Nov 2025), GitNexus
(github.com/abhigyanpatwari/GitNexus, PolyForm Noncommercial); spec-driven development tools - OpenSpec, GitHub
Spec Kit, Kiro, Tessl (comparisons at getnima.io, entalpa.com/en/vs, cameronsjo/spec-compare); doc-to-code sync -
Swimm, CODENS (arXiv 2607.18356, DocEng 2026); Google Cloud Open Knowledge Format (June 2026) and the Karpathy
"LLM wiki" pattern it formalises; GitHub Copilot for Jira (generally available 2026-06-25); the living-architecture
overview at ceaksan.com; OpenAI "Harness engineering" (AGENTS.md as a map, docs/ as the system of record).

## 1. What each one is

| Source | Core idea | Where it is strong | Where it does not fit us |
|---|---|---|---|
| Reversa | multi-agent pipeline: map the project, analyse modules, extract implicit business rules, synthesise architecture, write unit-level specs, review the claims; every claim traceable to code and marked with a confidence index; gaps registered for human validation; Gherkin "parity scenarios"; a Node CLI installs the skills into several agent engines | the nearest in spirit: code -> traceable specs -> Gherkin, with confidence and open gaps as first-class output; proposes an evaluation protocol (coverage, traceability, confidence, utility, cost) | reader is a coding agent doing a migration, not an analyst; one exploratory COBOL-to-Go case study (517 claims, 10 gaps, 53 scenarios, parity never validated); Node, several engines, no freshness after the first run |
| CoreStory | commercial platform: ingests a codebase, builds a model of architecture, workflows and business rules, generates executive overviews, personas, user stories, data models, API specs and integration points; each business spec records rule, implementation location, data dependencies and a confidence score; served to agents over MCP and API | the nearest product: names PMs and BAs as readers next to engineers and agents; rule-level provenance and confidence; vendor reports 1,984 specs with an 85.5% SME approval rate | hosted service over MCP (our constraints exclude both); no Jira, Confluence, freshness or verification story on the site; licence and deployment not stated |
| Business-rule recovery research | Kalohia: deterministic parsing plus control- and data-flow analysis feed an enriched intermediate representation, an LLM writes rule catalogues, data lineage, CRUD matrices and field-level mappings, each linked to code (93% agreement with expert rules on one financial corpus, ~70% less documentation effort, self-reported); AgentModernize: a reviewable Behavioral Specification Graph, each rule with source location, inputs, outputs and a high / medium / low confidence; COBRAIN: open-source one-shot extraction, benchmarked against a rule-based tool | the hybrid "deterministic facts first, LLM prose second" is exactly our gen-* scripts plus agents; the reviewable intermediate artifact before anything is generated is our graph plus context pack | COBOL, PL/I and JCL only; purpose-built tools still miss about a quarter of the rules and add false positives; nothing about keeping the output alive |
| Google Code Wiki, GitNexus | Code Wiki: a Gemini-generated wiki per public repository, architecture, class and sequence diagrams regenerated after every commit, sections link to code, a chat agent answers from the wiki; a local Gemini CLI extension announced. GitNexus: tree-sitter knowledge graph (files, symbols, calls, inheritance, clusters, execution flows, optional data dependence), CLI with `impact`, `trace`, `detect-changes`, an MCP server with ~19 tools, writes AGENTS.md and one skill file per functional area, can emit a wiki | our `generated/` + graph layer done by others, with execution flows traced from entry points and a per-area skill file we do not generate | everything is "what the code says", no verified business meaning, no analyst; Code Wiki is Gemini and public repositories only; GitNexus is an MCP server under a non-commercial licence |
| Spec-driven development tools | spec before code for an agent: Spec Kit (specify, plan, tasks, implement; 30+ agents incl. Copilot; a branch per spec), Kiro (AWS IDE, review-gated), Tessl (spec regenerates code, beta, JS only), OpenSpec (repo-resident living specs, change deltas ADDED / MODIFIED / REMOVED, recommended for brownfield) | OpenSpec's delta format for a change against an existing spec; the idea that the spec, not the ticket, is what the agent reads | forward direction and developer workflow; comparisons agree the spec goes stale after the first merge in Spec Kit and Kiro; no rule IDs, freshness, verification or analyst reader anywhere |
| Swimm, CODENS | Swimm: a doc references code tokens, a change to them flags or auto-patches the doc; CODENS: Neo4j graph from code changes and pull requests, graph RAG for queryable design knowledge | the freshness gate as a product; mining pull requests and reviews for the "why" | token-level sync is for developer docs; paid; CODENS is a paper with a database server |
| OKF and the LLM wiki | OKF v0.1 (Google Cloud, June 2026): concept files with YAML frontmatter, `index.md` per folder, `log.md`, only `type` mandatory, extra keys preserved; framed as a formalisation of Karpathy's raw/ -> wiki/ -> schema pattern with ingest / query / lint operations; community skills (Astro-Han, Ar9av with delta-tracking manifests, lewislulu) | we are already on it; the delta-tracking manifest (re-ingest only changed sources) is the pattern behind our `generated/` collection and the planned distiller | the implementations are personal knowledge bases, not software specs; no traceability, no verification by a person |
| Copilot for Jira | assign a Jira issue to the Copilot coding agent, it reads description and comments, asks in Jira, opens a draft pull request; custom agents, custom fields, Confluence context through MCP | the downstream consumer of our `work-items/`: a story with Gherkin acceptance criteria and BR citations is what it needs | Confluence through MCP is not ours to use; the Confluence mirror of the specs serves the same purpose read-only |

## 2. What we already have (no action)

- Code -> traceable specs -> Gherkin -> Jira: yes, with stable IDs (`P1-002`, `BR-P1-002-3`) that Reversa and
  CoreStory do not have; `generated/` maps, contracts and the graph are the deterministic layer the ACL paper puts
  before the LLM.
- Reviewable intermediate artifact before anything is written: the graph plus the task-scoped context pack
  (AgentModernize's Behavioral Specification Graph, GitNexus' clusters and execution flows).
- Freshness and verification per concept: `stale_after`, `generated`, `verified`, `status: draft` until a person
  verifies, the freshness gate in code-repo CI (Swimm's sync, Code Wiki's regenerate-on-commit, done by hashes and
  dates instead of a product).
- OKF bundle with indexes and `log.md`; flow documents (`flows/`, adopted from the first review).
- Human readers first: the analyst; the specs are the system of record and `AGENTS.md` is the map (the OpenAI
  harness layout).
- Not yet done from the first review: distilled layer (A), `questions:` (C), phased bootstrap gate (D), `/wrap-up`
  prompt (E). Nothing in this review changes their order.

## 3. Adopt

### F. Provenance per business rule (from Reversa, AgentModernize, CoreStory)
Today the whole concept carries `status` and `verified`; a single rule does not say where it came from. Every rule
that `spec-writer`, `doc-sync` or `confluence-migrator` writes from evidence gets a source marker at the end of the
line until a person verifies the spec: `(source: code <file:line>)` from the graph, `(source: legacy <page path>)`
from quarantine, `(source: contract <operationId>)`, `(source: person <id>)`. A rule without a marker in a draft
spec is an `okf-validate --strict` warning. Verification removes nothing: the marker is what the verifier checks.
Cheap: a convention in `write-feature-spec` and `legacy-page-audit`, one check in the validator.

### G. Gaps register (from Reversa)
Open questions stay in the spec's `## Open questions`; `coverage-report` (docs-analytics) lists them bundle-wide
with spec, age and whom the question is addressed to, oldest first, next to stale and unverified specs. A question
older than the spec's `stale_after` horizon is a finding. No new file: the register is a report over what the specs
already hold.

### H. Delta vocabulary for change requests (from OpenSpec)
`analyse-request` and `jira-from-spec` describe a change to an existing spec as ADDED / MODIFIED / REMOVED against
rule IDs ("MODIFIED BR-P1-002-3: ...", "ADDED BR-P1-002-7"), in the request epic, in each story and in the spec's
`## Change log`. Reviewers and Copilot for Jira then see exactly which rules a story touches; `coverage-report`
can count rules changed without a story.

## 4. Consider later
- Reversa's evaluation protocol (coverage, traceability, confidence, utility, cost) as the metric set of
  `docs-analytics` once the first analytics tasks have run; coverage and traceability exist, utility and cost do not.
- Data lineage and CRUD matrix per context (from the ACL paper): `generated/be/db` plus the graph already relate
  entities to endpoints and jobs; a generated table per context in the codebase map would answer "which screens
  write this table" without a spec.
- Per-area skill files generated from the graph (GitNexus `analyze --skills`): one short file per bounded context
  with entry points, key files and flows for the code-repo Copilot - the same place the distilled layer (A) lands,
  decide together with A.
- CoreStory's executive overview and personas per context: for product owners, not the analyst; wait for a reader.
- Google Code Wiki's local extension, when it ships, only as a benchmark of our generated maps on the same
  repository, never as a dependency (Gemini).

## 5. Skip
- CoreStory, GitNexus, Hjarni and every MCP-served or hosted code model: excluded by the no-MCP, no-server
  constraint; GitNexus' licence is non-commercial besides.
- Spec Kit, Kiro, Tessl: developer-side, spec-before-code workflows; Tessl is a JS-only beta.
- Swimm: paid token-level sync for developer docs; the freshness gate covers the need.
- Google Code Wiki as a product: Gemini, public repositories.
- The LLM-wiki skills: personal knowledge bases; OKF is what we keep from that lineage.
