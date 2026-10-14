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
  "Use `X-Harbor-Session` on every session endpoint (MTG-001)"), each line traceable to a BR, a calculation
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
