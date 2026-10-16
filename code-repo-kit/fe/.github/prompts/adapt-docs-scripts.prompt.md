---
agent: agent
description: Review the scripts/docs generators for safety and adapt them to this frontend repository WITHOUT running anything - security review table, proposed docs-gen.json with evidence paths, minimal regex diffs; a human reviews and runs.
argument-hint: "optional: what to focus on, e.g. routes, hooks, types (default all)"
---
Focus: ${input:focus:all}

## Role
You are adapting the documentation generators of `scripts/docs/` (standard-library Python regex scanners plus the
optional TypeScript exporter `gen-graph-fe.ts`) to this repository. The scripts came from a reference kit written
for another layout; `scripts/docs/README.md` lists every layout key of `scripts/docs/docs-gen.json`. You read the
scripts and this repository; **you never execute anything** (no `gen-all.py`, no `python`, no `npx`, no shell). A
person reviews your output for safety first and then runs the generators.

## Inputs (read-only)
- `scripts/docs/*.py`, `scripts/docs/gen-graph-fe.ts`, `scripts/docs/tsconfig.gen.json`, `scripts/docs/docs-gen.json`,
  `scripts/docs/README.md` (the key table and the assumptions the generators keep beyond the config).
- This repository: `package.json` (scripts, router and query libraries, generated client tooling), the pages folder
  and one page folder with its hook and component folders, the routing files, the route-constants file, the shared
  component library, the types folder, the generated client folder, one test file.

## Procedure
1. **Security review, one row per script.** Columns: script | files it reads | files it writes | processes it starts |
   network | imports outside the Python standard library (or outside `typescript` and `@types/node` for the
   exporter) | verdict. `gen-all.py` is the only script expected to start processes (the sibling generators with
   `sys.executable`); every other row must say "none" for processes and network, "none" for non-standard imports,
   and "under `--out` only" for writes (`tag-candidates.py` writes only with `--out`; the exporter writes only its
   output JSON). Quote the line for anything else and stop there: a script that downloads, uploads, deletes outside
   `docs/_generated`, edits source files or evaluates code (`exec`, `eval`, `pickle`, `subprocess` with a shell,
   `child_process`) is reported, never adapted.
2. **Layout evidence.** For every key in the README table write the value for this repository and one path that
   proves it (the pages folder, a hook folder, a component folder with its `index.ts`, the routing file and the
   route object or `<Route>` it contains, the route-constants export, a types file, the generated client folder, a
   test file name). Unknown or absent things get the default and the reason.
3. **Proposed `docs-gen.json`**, complete, as a code block, with a `_comment` naming the repository and the date.
4. **Gaps the config cannot express.** When a convention of this repository is outside the config (a router that
   is neither route objects nor `<Route>`, hooks that call a generated client instead of literal paths, pages whose
   purpose is not a JSDoc above `export function <Page>`, a BroadcastChannel opened in more than one module),
   propose the smallest change to the one generator concerned as a unified diff with the regex before and after and
   one example line of this repository that must match. Never widen a pattern to match everything; never add a
   dependency.
5. **Expected outcome.** For each table of `docs/_generated/` say in one line what a correct run must show for this
   repository (one row per page with a purpose and a non-empty hooks column, every route absolute with its page
   component and layout, the shared components with their users, the types per file, the `@docs` tags).
6. **Commands the person will run**, in order, after the review: `python3 scripts/docs/gen-all.py --root .`, then
   `python3 scripts/docs/gen-all.py --root . --check`, then `python3 scripts/docs/tag-candidates.py --root . --contexts
   <docs repo>/contexts.yml`, optionally `npx tsc -p scripts/docs/tsconfig.gen.json && node scripts/docs/out/gen-graph-fe.js src docs/_generated/graph-export-fe.json`,
   and what to compare with step 5.

## Output
A. the security table (step 1); B. the evidence table (step 2); C. the `docs-gen.json` (step 3); D. the diffs (step 4)
or "none"; E. the expected outcome (step 5); F. the commands (step 6). Under 120 lines in total; no file is written by you.

## Rules
- Never run a script, a build or a shell command; never edit `scripts/docs/*`. Diffs are proposals in the answer.
- Evidence only: every value and every regex change points at a real path or line of this repository.
- No product, client or environment names that are not in this repository; no secrets, no API hosts (write `<redacted>`).
