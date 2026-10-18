---
agent: agent
description: Review the scripts/docs generators for safety and adapt them to this backend repository WITHOUT running anything - security review table, proposed docs-gen.json with evidence paths, minimal regex diffs; a human reviews and runs.
argument-hint: "optional: what to focus on, e.g. kafka, api, migrations (default all)"
---
Focus: ${input:focus:all}
Known facts (optional, from the person: the call flow, where calculations and tests live, what the backend has no
document for): ${input:facts:none}

## Role
You are adapting the documentation generators of `scripts/docs/` (standard-library Python, regex scanners, no build)
to this repository. The scripts came from a reference kit written for another layout; `scripts/docs/README.md` lists
every layout key of `scripts/docs/docs-gen.json`. You read the scripts and this repository; **you never execute
anything** (no `gen-all.py`, no `python`, no `mvn`, no shell). A person reviews your output for safety first and then
runs the generators.

## Inputs (read-only)
- `scripts/docs/*.py`, `scripts/docs/docs-gen.json`, `scripts/docs/README.md` (the key table and the assumptions
  the generators keep beyond the config).
- This repository: the root build file and its modules, the application class (its package is the base package),
  one class per sub-package of `dao`, `api` and `client`, the OpenAPI file and one controller, one Kafka listener
  and one publisher, the application properties file, one migration, the scheduled jobs, the test resources.

## Procedure
1. **Security review, one row per script.** Columns: script | files it reads | files it writes | processes it starts |
   network | imports outside the Python standard library | verdict. `gen-all.py` is the only script expected to start
   processes (the sibling generators with `sys.executable`); every other row must say "none" for processes and
   network, "none" for non-standard imports, and "under `--out` only" for writes (`tag-candidates.py` writes only with
   `--out`). Quote the line for anything else and stop there: a script that downloads, uploads, deletes outside
   `docs/_generated`, edits source files or evaluates code (`exec`, `eval`, `pickle`, `subprocess` with a shell) is
   reported, never adapted.
2. **Layout evidence.** For every key in the README table write the value for this repository and one path that
   proves it (the module folder, the package line of the application class, a file in the sub-package, the contract
   file, the annotation in a listener, the migrations folder, the enum, the fixture folder). Unknown or absent
   things get the default and the reason (for example `parameters.enum_name` empty and `skip_generators` listing
   `gen-parameters.py` when the repository has no parameter-key enum; `datasets` skipped when there are no SQL
   datasets with the header convention). Four keys are decisions, not folder facts, and get a sentence each:
   `entry_layer` is the layer of the class the controllers inject (open one controller: `service` when it injects
   a service that delegates to managers, `manager` when it injects a manager); `calculation_layer` is the layer of
   the pure calculators that have unit tests; `graph_layers` / `graph_exclude_layers` are every key of `layers`
   split into behaviour (controllers, services, managers, repositories, listeners, jobs, clients, calculators,
   validators) and data (entities, API models, enums); `db_docs.generate` is `false` when a database tool already
   writes the `docs/db` folder and `asyncapi` is `""` when the backend keeps Avro / JSON schemas but no AsyncAPI
   document (then `kafka.schema_dirs` lists the schema folders). Use the known facts above when given; otherwise
   decide from the files and say which file decided it.
3. **Proposed `docs-gen.json`**, complete, as a code block, with a `_comment` naming the repository and the date.
4. **Gaps the config cannot express.** When a convention of this repository is outside the config (a Liquibase
   changelog, a Quartz job class, a topic name built by an expression, a controller that is neither a generated
   interface nor an annotated route, JSON contracts in a folder the collector does not scan), propose the smallest
   change to the one generator concerned as a unified diff with the regex before and after and one example line of
   this repository that must match. Never widen a pattern to match everything; never add a dependency.
5. **Expected outcome.** For each table of `docs/_generated/` say in one line what a correct run must show for this
   repository (number of modules, the layers listed with a role, no `_not implemented_` row for an operation that
   exists, every topic resolved, no `<expr>` topic, the jobs with their lock names, the parameter keys or "skipped").
6. **Commands the person will run**, in order, after the review: `python3 scripts/docs/gen-all.py --root .`, then
   `python3 scripts/docs/gen-all.py --root . --check`, then `python3 scripts/docs/tag-candidates.py --root . --contexts
   <docs repo>/contexts.yml`, and what to compare with step 5.

## Output
A. the security table (step 1); B. the evidence table (step 2); C. the `docs-gen.json` (step 3); D. the diffs (step 4)
or "none"; E. the expected outcome (step 5); F. the commands (step 6). Under 120 lines in total; no file is written by you.

## Rules
- Never run a script, a build or a shell command; never edit `scripts/docs/*`. Diffs are proposals in the answer.
- Evidence only: every value and every regex change points at a real path or line of this repository.
- No product, client or environment names that are not in this repository; no secrets, no property values that look
  like credentials or hosts (write `<redacted>`).
