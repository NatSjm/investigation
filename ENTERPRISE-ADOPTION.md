# Enterprise implementation and adoption guide

## Outcome and scope

Build a separate documentation repository that GitHub Copilot can use for business and system analysis without routinely reading application source code.

This guide assumes four real repositories: frontend, backend, automated tests, and a new documentation repository. It does not require MCP, a custom IDE extension, a vector database, or a knowledge graph. Git, an approved CI platform, Copilot, and approved local scripts are sufficient.

This is an implementation guide, not a deployed solution. Repository names, paths, script names, metadata, and workflow names below are proposed enterprise conventions. The new scripts and workflows must be implemented and validated before use.

Use the investigation repository as a source of selected examples, not as a production-ready kit. Do not run `apply-kit.py` against enterprise repositories as the first step.

**First milestone:** one reviewed business feature that an analyst can explain correctly from the docs repo, followed by one source change that correctly triggers a documentation review.

## Ownership

| Role | Responsibility |
|---|---|
| Technical lead | Source locations, contracts, observed behavior, extraction accuracy |
| Business/domain owner | Intended behavior, terminology, conflicting requirements |
| Documentation maintainer | Imports, draft specifications, evidence requests, maintenance queue |
| QA owner | Test-design review, mapping to implemented tests, execution evidence |
| Platform engineer | Repository permissions, CI, publication, validation |
| Analyst | Uses reviewed knowledge, cites evidence, reports gaps |

One person can cover several roles during the pilot. A named human remains accountable for approval; an agent cannot approve its own generated documentation.

## Delivery stages

| Stage | Work | Exit condition |
|---|---|---|
| A. Manual pilot | Steps 1-6 | Reviewed feature and usable docs-first analyst |
| B. Reliable maintenance | Steps 7-10 | Versioned publication, drift detection, test evidence |
| C. Team adoption | Steps 11-12 | Repeatable team workflow and demonstrated answer quality |

Do not automate publication before confirming that the content helps analysts. Do not expand across the application before demonstrating change detection.

## Step 1. Agree the pilot and baseline

**Owner:** technical lead and business owner. **Repositories:** all four.

1. Select one feature covering a UI flow, backend processing, an external integration, and a calculation or nontrivial business rule.
2. List the analyst questions it must answer: behavior, validation, permissions, failure cases, calculations, integration effects, and test coverage.
3. Identify the FE, BE, and test revisions to inspect. Prefer a known compatible deployed release when available. Otherwise label the baseline a development snapshot, not production.
4. Record the environment, release/build identifiers, applicable configuration profile, and relevant feature flags without copying secrets or customer data.
5. Assign the reviewers and decide who resolves conflicts between implemented behavior and approved requirements.
6. Agree which Copilot client and mode the pilot will use. Verify customization support and enterprise permissions on that actual client; do not assume the prototype's cross-IDE support table is current.

**Deliverable:** `decisions/documentation-baseline.md`, a pilot feature ID such as `FTR-001`, and a short question list.

**Acceptance:** reviewers can identify exactly which application state the pilot documents. Independently selected latest FE and BE commits must not be described as a tested release.

## Step 2. Create and protect the docs repository

**Owner:** platform engineer and documentation maintainer. **Repository:** docs.

Create the repository through the approved enterprise process with this starting layout:

```text
product-docs/
  README.md
  glossary.md
  .github\
    CODEOWNERS
    copilot-instructions.md
    agents/
      analyst.agent.md
      docs-maintainer.agent.md
    workflows/
      docs-check.yml
  features/
  calculations/
  flows/
  decisions/
  templates/
    feature.md
    calculation.md
  sources/
    manifest.yml
    contracts/
    confluence/
    code-index/
    test-results/
  mappings/
    features.yml
  reviews/
  proposals/
    work-items/
    test-design/
  scripts/
```

Keep `README.md` as a short entry point linking to the baseline, glossary, pilot feature, and contribution instructions. Do not start by generating an index in every folder.

Configure branch protection or rulesets to require PRs, validation, and appropriate code-owner approval. Require approval of the latest reviewed content according to enterprise policy; do not rely on an old approval after material changes.

Assign business/technical owners to feature and calculation documentation, and platform ownership to scripts and workflows. Give analysts only the access needed for their workflow.

**Acceptance:** direct changes cannot bypass the agreed review process, and a documentation PR reaches the correct reviewers.

## Step 3. Establish the content and trust rules

**Owner:** documentation maintainer and reviewers. **Repository:** docs.

Use three distinct categories:

| Category | Examples | Meaning |
|---|---|---|
| Source evidence | Contracts, imported pages, source indexes, test receipts | What a particular version of a source says |
| Reviewed knowledge | Features, calculations, flows, decisions | A reviewed interpretation of that evidence |
| Proposals | Stories, acceptance criteria, proposed test cases | Suggested future work, not current application behavior |

Keep existing feature IDs if the enterprise already has them. Otherwise assign stable IDs and business-rule IDs, for example `FTR-001` and `BR-FTR-001-01`. Do not rename application classes or reorganize repositories to suit documentation extractors.

Start feature metadata with:

```yaml
id: FTR-001
title: Example feature
status: draft
owners: [product-team]
baseline: pilot-001
evidence:
  - kind: code
    repo: backend
    revision: REPLACE_WITH_FULL_COMMIT_SHA
    path: REPLACE_WITH_REPOSITORY_RELATIVE_PATH
    symbol: REPLACE_WITH_SYMBOL
  - kind: confluence
    page_id: REPLACE_WITH_PAGE_ID
    version: 1
review:
  decision: pending
  pull_request: null
```

The placeholders are not valid production evidence. Approval comes from the actual PR review record; an agent-written reviewer name is not proof of review. Calculate whether approval remains current from the approved content and relevant evidence, not a manually refreshed date.

Use `draft`, `reviewed`, `needs-review`, and `retired` as the initial lifecycle. Age can trigger a reminder, but a recent review date cannot override a relevant source change.

**Acceptance:** readers can distinguish current observed behavior, intended future behavior, unresolved conflicts, and proposals.

## Step 4. Import the pilot evidence manually

**Owner:** documentation maintainer, with technical and QA help. **Repositories:** all four.

### Contracts

Copy the pilot's FE-to-BE and BE-to-external-service contracts into `sources/contracts`. Reuse your already uploaded Swagger files after identifying their versions.

Record whether each contract is implemented by your application, consumed from a provider, or supplied as a reference. A provider specification does not prove which operations the application actually calls.

Keep the complete contract and its referenced files. If external references cannot be resolved, report the missing dependency rather than producing a successful-looking partial bundle. Record provider version and retrieval time when no source commit is available.

### Confluence

Export the relevant pages into `sources/confluence`. Keep page ID, URL, page version, title, and export time. Preserve relevant tables, diagrams, and attachment references after checking access and sensitive content.

Markdown is convenient, but an approved HTML export is acceptable. If conversion loses a table or macro, record that limitation and retain an accessible source reference.

Keep imported pages unchanged as evidence. Put normalized interpretations in feature documents. Do not make Confluence a read-only mirror until its owners agree that Git is the authoring system for the migrated material.

### Source locations and tests

Create a small source index linking the feature to FE routes/hooks, BE entry points/services/calculators, integration adapters, configuration definitions, and relevant tests. Use commit-pinned URLs and symbol names; line numbers are only valid for that revision.

Copy only approved evidence summaries into the docs repo, not application source trees or raw customer-bearing logs.

**Acceptance:** every imported item has provenance, important content survives conversion, and unknown versions are explicitly marked.

## Step 5. Write and review the first feature

**Owner:** documentation maintainer; technical and business owners approve. **Repository:** docs, with source access during preparation.

Create `features/FTR-001.md` containing:

| Section | Required content |
|---|---|
| Purpose and scope | Users, business outcome, supported baseline, exclusions |
| Behavior | Numbered business rules, preconditions, defaults |
| User flow | Relevant screens, actions, observable outcomes |
| Interfaces | Operations, consumed external APIs, important request/response fields |
| State and failures | State changes, authorization, validation, errors, retries, partial failures |
| Data and configuration | Relevant entities, feature flags, parameters, effective-date behavior |
| Calculations | Links to formulas, units, rounding, boundary examples |
| Tests | Proposed and implemented coverage, clearly distinguished |
| Evidence and gaps | Claim citations, conflicts, unanswered questions and their owners |

Write a separate `flows/FTR-001.md` only if the cross-service sequence is too large for the feature. Include asynchronous behavior, ordering, idempotency, and transaction boundaries only where supported by evidence.

For calculations, document inputs, units, defaults, formula, rounding stage, outputs, and worked examples. Cite specific tests and source revisions. Distinguish expected examples from values actually demonstrated by a test run.

Use Copilot to draft the documents from targeted evidence. Let it inspect enough source to resolve the question; do not impose an arbitrary two-file limit.

Classify contradictions as: matches implementation, differs from implementation, potentially defective implementation, or insufficient evidence. The business owner decides intended behavior; the technical owner confirms observed behavior. Create a defect or change proposal rather than silently rewriting one side to match the other.

**Acceptance:** the reviewed feature answers the pilot questions, or explicitly identifies the missing evidence and decision owner.

## Step 6. Configure the two Copilot workflows

**Owner:** documentation maintainer. **Repositories:** docs; source repos accessible only to the maintenance workflow when needed.

Start with `.github/copilot-instructions.md` and two custom agents if supported by the chosen client. Otherwise use the same procedures as ordinary saved prompts. Copy ideas from the prototype agents, not their graph-dependent procedures or fixed source-file limits.

### Analyst workflow

Open the docs repo alone for normal analysis. Ask the analyst to:

1. Identify the requested feature, baseline, and question.
2. Read the feature and check review state and evidence currency.
3. Follow links to calculations, flows, and contracts as needed.
4. Answer with rule IDs and evidence citations.
5. Separate facts, proposals, and unresolved assumptions.
6. Write proposed work items/test designs under `proposals`, never as established behavior.
7. Raise a specific evidence request when a gap blocks the answer.

An evidence request contains the question, documents checked, missing fact, likely source location if known, and reason the answer matters. Unknown source locations are allowed; incomplete indexes must not prevent escalation.

### Documentation-maintainer workflow

Use a separate workspace containing the docs repo and authorized source checkouts. Check out or inspect the revisions named by the baseline.

The maintainer resolves evidence requests, checks implementation/tests/configuration, and opens a documentation PR. It does not manufacture human verification or change application behavior to make a document true.

If the same analyst is permitted to inspect source, require an explicit escalation and capture the durable result in a documentation PR before reusing it as trusted knowledge.

**Acceptance:** a normal question is answered from docs; a deliberately undocumented question produces a bounded evidence request rather than a guess. A docs-only workspace reduces accidental navigation but is not a security boundary; enforce real restrictions with repository permissions and environment controls.

## Step 7. Implement the minimum documentation checks

**Owner:** platform engineer. **Repository:** docs.

Implement the proposed `scripts/check-docs.py` and `docs-check.yml` using approved tooling. Prefer a real YAML/OpenAPI parser to increasingly complex regular expressions. Dependencies can live in the docs pipeline without adding runtime dependencies to FE or BE.

Check:

| Check | Failure behavior |
|---|---|
| Required metadata, valid lifecycle and unique IDs | Reject malformed documents |
| Internal links and exact business-rule references | Reject broken or unknown references |
| Source revision and imported-page provenance | Reject incomplete provenance in reviewed material |
| OpenAPI syntax and reference resolution | Report unresolved references and fail the contract check |
| Generated artifact hashes/ownership | Reject unexplained hand edits to machine-owned evidence |
| Proposed output references | Reject stories/tests citing nonexistent rules |
| Review and evidence state | Prevent affected documents from appearing currently reviewed without a review decision |

Do not block every PR because unrelated pilot documents remain drafts. Scope approval requirements to the documents and claims affected by the PR.

Use the enterprise's actual runner OS. Validate path handling, case sensitivity, exit codes, and missing inputs on that OS. Hooks can improve local feedback but must not replace CI.

**Acceptance:** controlled changes with an invalid rule ID, broken contract reference, or missing source revision fail for a clear reason.

## Step 8. Automate evidence collection with one publisher

**Owner:** platform engineer and technical lead. **Repositories:** docs first; minimal optional changes in FE/BE.

For the initial enterprise rollout, prefer one collector workflow in the docs repo over separate cross-repository publishers in every application repo. This reduces credentials, duplicated scripts, and concurrent writers.

Implement `scripts/collect-evidence.py` and `collect-evidence.yml` with manual and scheduled execution:

1. Resolve configured source refs to immutable FE/BE/test SHAs and record the baseline type.
2. Check out authorized inputs into separate temporary directories, not inside the destination documentation tree.
3. Copy approved contracts and generate the selected small indexes.
4. Read test evidence when available; explicitly mark missing results.
5. Write a manifest with repository identifiers, source SHAs, extractor version, collection time, and file hashes.
6. Validate the complete candidate snapshot before publication.
7. Replace each collector-owned artifact set, including deleted files; never delete handwritten features or manually owned Confluence imports.
8. Open one docs PR containing the evidence diff and affected-feature report.
9. Publish only a coherent collection result. On partial collection failure, retain the prior snapshot and report the failed collection; do not advance the baseline.

Use an approved GitHub App or enterprise bot with read access to required source repos and only the necessary write/PR permissions in docs. Store credentials in the approved CI secret mechanism.

Verify that bot-created PRs actually trigger required checks on your platform. Serialize updates to a publication branch and avoid one source update overwriting another.

Start scheduled/manual. Add FE/BE release or merge notifications to the collector only when lower latency is needed. If enterprise permissions require producer-owned artifacts instead, have FE/BE CI produce the same manifest format and let the single docs collector consume them.

**Acceptance:** an added, modified, and deleted contract is reflected correctly; a failed collection publishes nothing; a second run against unchanged inputs creates no redundant PR. Compare content excluding volatile timestamps when deciding whether to publish.

## Step 9. Implement change-driven review

**Owner:** technical lead and documentation maintainer. **Repositories:** docs, then FE/BE PR templates.

Maintain `mappings/features.yml` with explicit source ownership. Start with a few manual mappings:

```yaml
features:
  FTR-001:
    backend_paths:
      - "REPLACE_WITH_BACKEND_FEATURE_PATH"
      - "REPLACE_WITH_SHARED_CALCULATOR_PATH"
    frontend_paths:
      - "REPLACE_WITH_FRONTEND_FEATURE_PATH"
    contract_operations:
      - "REPLACE_WITH_OPERATION_ID"
    confluence_pages:
      - "REPLACE_WITH_PAGE_ID"
```

Use the actual repository paths and the selected tool's documented glob syntax. Include shared calculators, configuration and integration adapters, not just controllers/screens. An edited contract can be conservatively mapped to all consumers until operation-level diffing is dependable.

Implement `scripts/find-affected-features.py` to compare the prior baseline with the candidate baseline. Fetch enough Git history, or compare trees; do not assume `HEAD~1` covers all changes. Include additions, modifications, renames and deletions.

Record unmapped relevant changes in a visible triage queue. They are unknown impact, not proof of no impact.

For each affected feature, either update/review its behavior or record a human-approved "no behavioral documentation change" decision tied to the source change and docs PR. Preserve historical approval, but invalidate its current applicability to changed evidence.

Unrelated source commits should not require rereview of the whole knowledge base. Use mapped dependencies and evidence fingerprints; changing a global manifest timestamp is not semantic drift.

Add a short section to FE/BE PR templates: affected feature IDs, expected behavior change, and documentation impact. Begin advisory.

Avoid a circular gate: an application PR cannot require a docs snapshot that can only be generated after that application PR merges. Before merge, require the impact declaration and, for important behavior changes, an agreed documentation proposal. After merge, collect exact evidence and complete review. Enforce release readiness against the final approved release baseline.

**Acceptance:** changing a shared calculation invalidates all mapped consumers; an unrelated file does not; an unmapped change remains visible; collecting evidence alone does not clear review requirements.

## Step 10. Connect the automated tests repository

**Owner:** QA owner and platform engineer. **Repositories:** tests and docs.

Keep executable tests and their framework in the existing tests repo. Do not impose Gherkin if it is not already useful to the team.

Map test identifiers to feature/rule IDs using existing tags, annotations, or a small sidecar mapping. Have test CI publish an approved, sanitized receipt containing test revision, tested FE/BE builds or SHAs, environment, configuration profile, run time, individual result, and report link.

Where tests run against a deployed environment, capture its build identity at run time. If the application version is unknown, mark the result as unbound evidence rather than attributing it to the current docs baseline.

The docs collector imports a summary. Keep these states separate:

| State | Evidence required |
|---|---|
| Designed | Reviewed proposed scenario |
| Implemented | Test identifier exists at the recorded test revision |
| Executed | A matching execution receipt exists |
| Passed/failed/skipped | Actual result from that execution |
| Applicable to this baseline | Tested application identity matches the documented scope |

Transfer approved test proposals through a reviewed tests-repo PR. Do not let both repositories independently own editable executable copies of the same test.

**Acceptance:** the analyst can explain both coverage and its limits. An old passing run or a new Gherkin file cannot appear as a current passing test.

## Step 11. Rehearse the everyday team workflows

**Owner:** documentation maintainer and team leads. **Repositories:** all four.

### An analyst receives a new request

1. Select the feature and baseline in the docs repo.
2. Ask Copilot for analysis with citations and explicit gaps.
3. Review the answer before using it for estimation or requirements.
4. Resolve missing evidence through the maintainer.
5. Store approved proposals separately from descriptions of current behavior.

### A developer changes behavior

1. Add affected feature IDs and documentation impact to the application PR.
2. Link or draft the expected specification/test-design changes.
3. Merge code through normal engineering controls.
4. Collect the new source snapshot and inspect the affected-feature report.
5. Review the documentation diff and obtain the required human decisions.
6. Confirm matching test evidence before making release-readiness claims.

### A Confluence page changes

1. Import the new page version without overwriting its provenance.
2. Identify linked features and highlight changed or conflicting claims.
3. Obtain a domain decision; do not automatically override the implementation description.
4. Record the resolution and update the reviewed knowledge.

### Documentation is discovered to be wrong

1. Mark the affected material `needs-review` and identify which outputs may rely on it.
2. Notify the owner and correct the evidence/specification through a PR.
3. Revisit dependent stories and test proposals where the incorrect claim matters.
4. Retain the correction history; do not erase the previous decision.

Run a weekly review queue covering stale/unreviewed evidence, unresolved conflicts, unmapped changes and outstanding analyst evidence requests. Review the process with the team after the pilot rather than relying on agents to enforce adoption.

**Acceptance:** an analyst, developer and reviewer can each complete their workflow without the person who built the PoC guiding every step.

## Step 12. Prove readiness and expand

**Owner:** technical lead, domain owner and QA owner.

Prepare 15-20 representative questions with owner-reviewed expected answers and required citations. Include normal behavior, errors, a calculation boundary, an external-service failure, a source/version conflict, and a question intentionally not answerable from the docs.

Compare docs-first analysis with the team's existing method using equivalent baselines and supported Copilot clients. Record correctness, unsupported claims, appropriate abstention, evidence gaps, time, and source escalation. Use observed tool activity where available rather than relying only on the agent's self-report.

Before expanding, require:

| Acceptance check | Required outcome |
|---|---|
| Critical business/calculation questions | No unresolved materially incorrect or unsupported answer |
| Deliberately missing evidence | Explicit gap or escalation, not an invented answer |
| Changed source/contract | Affected documentation marked for review |
| Deleted source artifact | Removed from current evidence, history retained in Git |
| Failed collector | Prior snapshot retained and collection failure visible |
| Test coverage question | Design, implementation and execution distinguished |
| Baseline question | Exact documented application state identified |
| Team rehearsal | Analyst, developer and reviewer workflows completed |

If the analyst repeatedly needs source for the same question, improve the relevant specification or evidence index first. Do not begin by adding a graph.

Expand one feature or business context at a time. Move advisory gates to blocking only for adopted areas with working mappings and responsible owners. Keep production baselines explicit; development documentation must not silently replace released-behavior documentation.

## What to reuse from this investigation repository

| Existing asset | Enterprise adoption |
|---|---|
| `docs-repo/features/_template.md` | Reuse section ideas and rule IDs; simplify metadata |
| `docs-repo/domain/calculations/_template.md` | Reuse units/formulas/examples; remove unsupported attestation claims |
| `docs-repo/.github/agents/analyst.agent.md` | Rewrite for docs-first retrieval, explicit trust and escalation; remove graph dependence |
| `docs-repo/.github/agents/doc-sync.agent.md` | Adapt into docs maintainer; do not automatically renew verification dates |
| `docs-repo/.github/skills/imported-page-audit/SKILL.md` | Reuse conflict classification; remove arbitrary source-file limits |
| `docs-repo/docs-map.yml` | Reuse explicit mapping idea; add shared dependencies and unmapped-change handling |
| Code-map generators | Adopt selectively after representative enterprise-source checks |
| `context-pack.py` | Optional later; fix contract selection, reference completeness and total budget first |
| Publisher/validation workflows | Reference only; correct checkout collision, platform handling and freshness semantics |
| Graph, extension, broad kit installer | Defer until a measured problem justifies them |

## Suggested implementation PR order

| Order | Repository | PR scope |
|---|---|---|
| 1 | Docs | Structure, owners, baseline decision, templates and short Copilot instructions |
| 2 | Docs | Pilot evidence, glossary and draft feature/calculation documentation |
| 3 | Docs | Reviewed pilot content and two agent procedures |
| 4 | Docs | Metadata/link/contract validation and controlled failure fixtures |
| 5 | Docs | Single evidence collector, manifest, idempotent publication |
| 6 | Docs | Feature mappings, drift detection and review queue |
| 7 | FE and BE | PR-template impact declaration; optional tags or producer artifacts |
| 8 | Tests | Rule mappings and version-bound execution receipts |
| 9 | Docs | Test-summary import, analyst evaluation results and adoption instructions |

Do not combine all nine into one rollout. Review each change independently and preserve existing application workflows.

## Deferred capabilities and when to add them

| Capability | Add only when |
|---|---|
| Automated Confluence export | Manual import is a recurring bottleneck and API/access policy is settled |
| Confluence publication | Page ownership and one-way authoring policy are agreed |
| Context packs | Relevant-doc discovery is measured as a problem |
| Knowledge graph | Cross-feature impact cannot be served by accurate explicit mappings/indexes |
| Jira synchronization | Story format and ownership are stable and manual transfer is costly |
| Documentation site | Readers need browsing beyond the repository |
| VS Code extension or search service | Built-in file retrieval is demonstrably insufficient |

The success criterion is dependable analyst knowledge and a maintained review process. The number of generated files, agents, or integrations is not a measure of readiness.
