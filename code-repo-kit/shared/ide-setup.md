# IDE setup for token-efficient Copilot sessions

## IntelliJ IDEA (BE developers)

| Setting | Why |
|---|---|
| **File > Project Structure > Modules > Unload Modules** - keep only the Maven modules you touch (+ `shared-kernel`) | Copilot's workspace context, symbol search and `@project` only see loaded modules |
| **Settings > Appearance & Behavior > Scopes** - create `hedges-src` = `hedges/src/main//*` | use the scope in *Find in Files* and when attaching context to chat |
| **Settings > Editor > File Types > Ignored Files and Folders** add `target;build;*.iml` | removes noise from indexing and Copilot file pickers |
| **Copilot plugin > Custom instructions** - repo `.github/copilot-instructions.md` is picked up automatically; verify the plugin version supports `*.instructions.md` and `.prompt.md` (2025.x+) | same rules in both IDEs |
| Chat: attach `docs/_generated/<map>.md` + the facade; avoid "whole project" context | the maps are ~300 tokens each |

No custom IntelliJ plugin is required for the first phase; Copilot tools/participants are not exposed to third-party JetBrains plugins yet, so the retrieval helpers live in VS Code only (`vscode-extension/`).

## VS Code (FE developers, analysts, QA)

- Open `shared/workspaces/<context>.code-workspace`, never the repo root. Each workspace adds only the BE module, the FE feature, both `_generated` folders and the docs for one bounded context.
- Enable **remote workspace index** (`github.copilot.chat.codesearch.enabled`, repo indexed on GitHub) so `#codebase` returns snippets instead of whole files.
- Install the in-house **Bank Docs** extension (`vscode-extension/`) to get `#docsLookup`, `#codeMap`, `#specToCode` tools and the `@docs` participant.
- Prefer `#file`, `#sym`, `#selection`, `#docsLookup:HEDGE-001` over `@workspace`.

## Both

- Content exclusion is configured on GitHub (repo settings) - see `copilot-content-exclusion.yml`; it applies to both IDEs.
- Run `scripts/docs/gen-all.ps1` before asking architecture questions if `docs/_generated/*` is older than your branch.
