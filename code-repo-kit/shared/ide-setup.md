# IDE setup for token-efficient Copilot sessions

## IntelliJ IDEA (backend developers)

| Setting | Why |
|---|---|
| **File > Project Structure > Modules > Unload Modules** - keep `core` (+ `kafka-client` only for topic/payload changes) | Copilot's workspace context, symbol search and `@project` only see loaded modules |
| **Settings > Appearance & Behavior > Scopes** - create `product1-src` = `file:harbor-core/src/main/kotlin/com/acme/harbor//Product1*.kt||file:harbor-core/src/main/kotlin/com/acme/harbor//Projection*.kt` (one scope per context, prefixes from the docs repo `contexts.yml`; layers are folders, contexts are name prefixes) | use the scope in *Find in Files* and when attaching context to chat |
| **Settings > Editor > File Types > Ignored Files and Folders** add `target;build;*.iml` | removes noise from indexing and Copilot file pickers |
| **Copilot plugin** - `AGENTS.md` (since 2026-03), `.github/copilot-instructions.md`, `*.instructions.md`, `.prompt.md` and `.agent.md` are picked up automatically; `.github/hooks/*.json` and skills are preview in JetBrains | same rules in both IDEs |
| Chat: attach `docs/_generated/<map>.md` + the context manager (`manager/<Ctx>Manager.kt`) and its `components.md` rows; avoid "whole project" context | the maps are ~300 tokens each |
| Graph questions: `python3 ../harbor-docs/scripts/graph-query.py --node spec:P1-001 --depth 2` and paste the result | same data as the VS Code `#impact` tool |

No custom IntelliJ plugin is required; Copilot tools/participants are not exposed to third-party JetBrains plugins,
so the retrieval helpers live in VS Code only (`vscode-extension/`).

## VS Code (frontend developers, analysts, QA)

- Open `shared/workspaces/<context>.code-workspace` (e.g. `product1.code-workspace`), never the repo root. Each workspace
  adds the backend `core` sources (`harbor/` layers) and resources, the frontend feature, both `_generated` folders and the docs repo;
  narrow searches with the context prefixes (`**/Product1*.kt`, `**/Projection*.kt`).
- Enable **remote workspace index** (`github.copilot.chat.codesearch.enabled`, repo indexed on GitHub) so `#codebase` returns snippets instead of whole files.
- Install the in-house **Harbor Docs for Copilot** extension (`vscode-extension/`) to get `#docsLookup`, `#codeMap`, `#specToCode`,
  `#impact` tools and the `@docs` participant.
- Prefer `#file`, `#sym`, `#selection`, `#docsLookup:P1-001`, `#specToCode:monthly_projection` over `@workspace`.
- `.github/hooks/docs-maps.json` runs `gen-all.py --check` when an agent session stops; leave it enabled.

## Both

- Content exclusion is configured on GitHub (repo settings) - see `copilot-content-exclusion.yml`; it applies to every Copilot surface.
- Run `scripts/docs/gen-all.py` before asking architecture questions if `docs/_generated/*` is older than your branch.
- Contract changes start in `harbor-backend/harbor-core/src/main/resources/openapi/openapi_harbor.yaml`; the generated `*Api` interfaces and the FE client are never edited.
