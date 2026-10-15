---
name: source-priority-from-code
description: Rewrite the code rows of .github/skills/write-feature-spec/references/source-priority.md (backend and frontend sources, cheapest first) from the real layout of the code repositories; the documentation rows stay as they are.
argument-hint: "product name; optional: backend path, frontend path"
agent: architect
---
Product: ${input:product:Harbor}
Backend repository: ${input:backend:../harbor-backend}
Frontend repository: ${input:frontend:../harbor-frontend}

## Role
Maintain one reference file of this repository: `.github/skills/write-feature-spec/references/source-priority.md`.
It tells every writing agent which source to open first and which last when the context pack leaves a question
open. Rows 1 to 7 describe this documentation repository and stay as they are. Rows 8 and below describe the
backend and frontend source code; rewrite only those rows and the rules of thumb, for the real layout of the
product's repositories. Keep the table shape, the column names and the "cheapest first" order.

## Inputs (read-only)
- The current file (read it first).
- `contexts.yml`: bounded contexts, backend class-name prefixes, frontend feature folders.
- Backend repository: Kotlin/Spring, layered packages.
- Frontend repository: React/TypeScript, feature folders.
- `generated/be/codebase-map.md` and `generated/fe/codebase-map.md` if they exist; otherwise the source trees.

## Investigation
1. **Backend.** List the layer packages that actually exist under the main source root (`api`, `manager`,
   `service`, `dao`, `event`, `job`, `utils`, `validator`, `mapper`, `client`, `config`, ...) with their paths and
   what each holds in this code (one phrase each, from the classes in it, not from the folder name). Find where
   the entry point of a context lives (the class a spec's `context:` node names). Find where calculators live and
   where their unit tests live (test source root, package, naming pattern such as `<Class>Test.kt`). Find where
   validation and error mapping live (validators, exception handlers, problem-detail mapping).
2. **Frontend.** For one feature folder, list the sub-folders and what they hold (page components, hooks that
   call the API, types, local components), the routing file, the shared component library, the generated API
   client, client-side validation if any, and the test location and naming pattern.
3. **Cost.** For each candidate source, estimate the reading cost (very low, low, medium, high) by the size of
   the range a writer would open, and name the question it answers that nothing cheaper answers.

## Output
**A. The rewritten file.** Rows 1 to 7 unchanged. From row 8: one row per backend or frontend source kind,
cheapest first, with the real path pattern of the repositories (for example
`core/src/main/kotlin/<pkg>/manager/<Ctx>Manager.kt`, `src/features/<ctx>/api/use*.ts`), a cost, and the
"gives you" phrase naming the facts it is the best source for: rule intent, orchestration, edge cases and worked
examples, validation and error codes, UI flow, client-side validation, cross-window or cross-feature channels.
Tests come before services where the tests carry the examples. Keep the table under 15 rows.
Rules of thumb: keep the four existing ones; add at most three specific to this layout (for example where the
error codes are defined, or that generated API clients are never opened). State the range size a writer should
open, consistent with the task-context skill (40 to 120 lines).

**B. In chat, under 15 lines:** which rows changed, which paths you verified exist (one example file per row),
and anything in the code layout that `contexts.yml` does not describe (a layer holding classes of several
contexts, a feature folder with no entry in `contexts.yml`).

## Rules
- Every path pattern must match at least one real file you saw.
- Do not invent layers or folders to match the example; if the backend has no validator layer, there is no
  validator row.
- Do not edit any other file. Do not run scripts.
- English only; no product names other than this product's; no client data.
