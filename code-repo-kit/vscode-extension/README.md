# Bank Docs for Copilot (VS Code extension)

MCP is not permitted in our environment, so this in-house extension gives Copilot agent mode the same
benefit - retrieval instead of file dumps - through the public VS Code API (`vscode.lm.registerTool`,
`vscode.chat.createChatParticipant`). No runtime dependencies; `@types/vscode` and `typescript` are dev-only.

## What it adds

| Reference in chat | Tool | Returns (capped by `bankDocs.maxResultChars`, default 6k chars) |
|---|---|---|
| `#docsLookup` | `bank-docs_docsLookup` | top-5 concepts from the OKF bundle (path, type, status, trust) + one section of the best match |
| `#codeMap` | `bank-docs_codeMap` | matching rows from `docs/_generated/{api-index,events,db-schema,codebase-map,routes,types-index,docs-tags}.md` |
| `#specToCode` | `bank-docs_specToCode` | `@docs <ID>` locations across BE/FE (`file:line`) |
| `#impact` | `bank-docs_impact` | BFS over `generated/graph/graph.json` (from docs repo `scripts/gen-graph.ps1`): neighbours by depth, edges, spec IDs in the blast radius. Input = node id, substring or changed file path |
| `@docs /spec`, `/where`, `/impact` | chat participant | retrieval -> one bounded model call -> answer with citations; `/impact` = graph BFS + docs lookup |

Agent mode picks the tools automatically from `modelDescription`; users can also pin them with `#docsLookup:HEDGE-001`.

## Why this saves tokens
- A lookup costs ~200-800 tokens (index lines + one section) instead of a 2-5k-token spec file or 15k+ tokens of source.
- Map rows carry `file:line`, so the follow-up read is a range, not a file.
- Trust badges (`human-reviewed / machine-confirmed / unverified / STALE`) come back with every hit, so downstream agents can mark `@needs-review` without a second read.

## Settings
`bankDocs.docsRepoPath`, `bankDocs.generatedPaths`, `bankDocs.maxResultChars`, `bankDocs.graphPath` - see `package.json`; the sample
`shared/workspaces/hedges.code-workspace` sets them per workspace. Without a `graph.json` the `#impact` tool degrades to the flat maps.

## Build
```
npm install
npm run compile      # -> out/
npm run package      # -> .vsix for internal distribution (needs @vscode/vsce)
```
Install via *Extensions: Install from VSIX* or push to an internal extension gallery.

## Security review notes
- Reads only `.md` files under configured paths; never writes; no network.
- `knowledge.ts` is pure Node `fs`/string handling (~220 lines incl. graph BFS) - reviewable in one sitting.
- If dev dependencies are also disallowed, vendor `vscode.d.ts` from the VS Code repo (MIT) instead of `@types/vscode`.

## Not covered
JetBrains: Copilot's JetBrains plugin does not expose tool/participant APIs to third-party plugins.
BE developers on IntelliJ rely on the same maps via `copilot-instructions.md` and prompt files (see `shared/ide-setup.md`).
