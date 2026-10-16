# Harbor Docs for Copilot (VS Code extension)

MCP is not permitted in our environment, so this in-house extension gives Copilot agent mode the same
benefit - retrieval instead of file dumps - through the public VS Code API (`vscode.lm.registerTool`,
`vscode.chat.createChatParticipant`). No runtime dependencies; `@types/vscode` and `typescript` are dev-only.

## What it adds

| Reference in chat | Tool | Returns (capped by `harborDocs.maxResultChars`, default 6k chars) |
|---|---|---|
| `#docsLookup` | `harbor-docs_docsLookup` | top-5 concepts from the OKF bundle (path, type, status, trust) + one section of the best match |
| `#codeMap` | `harbor-docs_codeMap` | matching rows from `docs/_generated/{api-index,events,db-schema,jobs,codebase-map,routes,types-index,docs-tags}.md` |
| `#specToCode` | `harbor-docs_specToCode` | `@docs <ID>` locations across backend/frontend (`file:line`) |
| `#impact` | `harbor-docs_impact` | BFS over `generated/graph/graph.json` (from docs repo `scripts/gen-graph.py`): neighbours by depth, edges, spec IDs in the blast radius. Input = node id, substring or changed file path |
| `@docs /spec`, `/where`, `/impact` | chat participant `com.acme.harbor.docs` | retrieval -> one bounded model call -> answer with citations; `/impact` = graph BFS + docs lookup |

Agent mode picks the tools automatically from `modelDescription`; users can also pin them, e.g.
`#docsLookup:P1-001`, `#specToCode:monthly_projection`, `#codeMap:getProduct1Overview`, `#impact:topic:harbor.market.prices-updated`.

## Why this saves tokens
- A lookup costs ~200-800 tokens (index lines + one section) instead of a 2-5k-token spec file or 15k+ tokens of source.
- Map rows carry `file:line`, so the follow-up read is a range, not a file.
- Trust badges (`human-reviewed / machine-confirmed / unverified / STALE`) come back with every hit, so downstream agents can mark `@needs-review` without a second read.

## Settings
`harborDocs.docsRepoPath` (default `../docs-repo`), `harborDocs.generatedPaths`, `harborDocs.maxResultChars`, `harborDocs.graphPath` -
see `package.json`; the sample `shared/workspaces/product1.code-workspace` sets them per workspace.
Without a `graph.json` the `#impact` tool degrades to the flat maps.

## Build
```
npm install
npm run compile      # -> out/
npm run package      # -> .vsix for internal distribution (needs @vscode/vsce)
```
Install via *Extensions: Install from VSIX* or push to an internal extension gallery.

## Security review notes
- Reads only `.md` and `graph.json` files under configured paths; never writes; no network.
- `knowledge.ts` is pure Node `fs`/string handling (~220 lines incl. graph BFS) - reviewable in one sitting.
- If dev dependencies are also disallowed, vendor `vscode.d.ts` from the VS Code repo (MIT) instead of `@types/vscode`.

## Not covered
JetBrains: Copilot's JetBrains plugin does not expose tool/participant APIs to third-party plugins.
Backend developers on IntelliJ rely on the same maps via `AGENTS.md`, prompt files and `harbor-docs/scripts/graph-query.py`
(see `shared/ide-setup.md`).
