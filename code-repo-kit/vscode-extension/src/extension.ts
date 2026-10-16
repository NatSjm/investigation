import * as path from 'path';
import * as vscode from 'vscode';
import { clip, loadBundle, mapRows, scoreConcept, section, Concept, Graph, loadGraph, resolveNodes, impact, renderImpact } from './knowledge';

// --- configuration -------------------------------------------------------

function resolveRel(p: string): string {
  if (path.isAbsolute(p)) return p;
  const base = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath ?? process.cwd();
  return path.resolve(base, p);
}
const cfg = () => vscode.workspace.getConfiguration('harborDocs');
const docsRoot = () => resolveRel(cfg().get<string>('docsRepoPath', '../docs-repo'));
const generatedDirs = () => {
  const dirs = new Set<string>();
  for (const g of cfg().get<string[]>('generatedPaths', ['docs/_generated'])) {
    if (path.isAbsolute(g)) dirs.add(g);
    else for (const f of vscode.workspace.workspaceFolders ?? []) dirs.add(path.resolve(f.uri.fsPath, g));
  }
  dirs.add(path.join(docsRoot(), 'generated'));
  return [...dirs];
};
const maxChars = () => cfg().get<number>('maxResultChars', 6000);

// Bundle cache invalidated on any .md change inside the docs repo.
let cache: Concept[] | undefined;
const bundle = () => (cache ??= loadBundle(docsRoot()));
let graphCache: Graph | undefined | null;   // null = looked, not found
const graphFile = () => resolveRel(cfg().get<string>('graphPath', path.join(docsRoot(), 'generated', 'graph', 'graph.json')));
const graph = () => (graphCache === undefined ? (graphCache = loadGraph(graphFile()) ?? null) : graphCache);

// --- tool implementations (shared by LM tools and the chat participant) --

function docsLookup(query: string, heading?: string): string {
  const ranked = bundle().map(c => ({ c, s: scoreConcept(c, query) })).filter(x => x.s > 0).sort((a, b) => b.s - a.s).slice(0, 5);
  if (!ranked.length) return `No concept matches "${query}" in ${docsRoot()}.`;
  const lines = ranked.map(({ c }) => `- ${c.rel} | ${c.type} | ${c.status ?? '-'} | ${c.trust}${c.id ? ` | id=${c.id}` : ''}${c.description ? ` - ${c.description}` : ''}`);
  const best = ranked[0].c;
  const warn = best.trust === 'unverified' || best.trust === 'STALE' ? `\n> trust: ${best.trust} - treat as hypothesis, add @needs-review downstream.\n` : '';
  return clip(`Matches:\n${lines.join('\n')}\n\n### ${best.rel}${warn}\n${section(best.body, heading)}`, maxChars());
}

function codeMap(map: string, query: string): string {
  const names = map === 'any' || !map ? ['api-index', 'events', 'db-schema', 'jobs', 'codebase-map', 'components', 'routes', 'types-index', 'docs-tags'] : [map];
  const out: string[] = [];
  for (const dir of generatedDirs()) for (const n of names) {
    const rows = mapRows(path.join(dir, `${n}.md`), query);
    if (rows.length) out.push(`#### ${n} (${path.relative(resolveRel('.'), dir).replace(/\\/g, '/')})\n${rows.join('\n')}`);
  }
  return out.length ? clip(out.join('\n\n'), maxChars()) : `No rows match "${query}" in ${names.join(', ')} under ${generatedDirs().join('; ')}.`;
}

function specToCode(id: string): string {
  const rows = generatedDirs().flatMap(d => mapRows(path.join(d, 'docs-tags.md'), id).slice(2));
  if (!rows.length) return `No @docs ${id} tags found. Check docs-tags.md freshness (scripts/docs/gen-all.py) or tag the code.`;
  return clip(['| Spec ID | Declaration | Summary | Location |', '|---|---|---|---|', ...rows].join('\n'), maxChars());
}

/** Blast radius from the architectural graph; `target` may be a node id, substring or a changed file path. */
function graphImpact(target: string, depth = 2): string {
  const g = graph();
  if (!g) return `No graph at ${graphFile()} - run docs repo scripts/gen-graph.py (falls back to flat maps).\n\n` + codeMap('any', target);
  const start = resolveNodes(g, target);
  if (!start.length) return `No graph node matches "${target}". Try #codeMap or a shorter substring.`;
  if (start.length > 8) return `"${target}" is ambiguous (${start.length} nodes): ${start.slice(0, 8).map(n => n.id).join(', ')} ... - be more specific.`;
  const res = impact(g, start, Math.min(Math.max(depth, 1), 4));
  return clip(`Start: ${start.map(n => `\`${n.id}\``).join(', ')} (depth ${depth}, ${res.levels.flat().length} nodes)\n${renderImpact(res)}`, maxChars());
}

// --- activation ----------------------------------------------------------

export function activate(ctx: vscode.ExtensionContext) {
  const watcher = vscode.workspace.createFileSystemWatcher(new vscode.RelativePattern(vscode.Uri.file(docsRoot()), '**/*.md'));
  watcher.onDidChange(() => (cache = undefined)); watcher.onDidCreate(() => (cache = undefined)); watcher.onDidDelete(() => (cache = undefined));
  const gw = vscode.workspace.createFileSystemWatcher(new vscode.RelativePattern(vscode.Uri.file(path.dirname(graphFile())), 'graph.json'));
  gw.onDidChange(() => (graphCache = undefined)); gw.onDidCreate(() => (graphCache = undefined)); gw.onDidDelete(() => (graphCache = undefined));
  ctx.subscriptions.push(watcher, gw, vscode.workspace.onDidChangeConfiguration(() => { cache = undefined; graphCache = undefined; }));

  const text = (s: string) => new vscode.LanguageModelToolResult([new vscode.LanguageModelTextPart(s)]);

  ctx.subscriptions.push(
    vscode.lm.registerTool<{ query: string; section?: string }>('harbor-docs_docsLookup', {
      invoke: async ({ input }) => text(docsLookup(input.query, input.section)),
      prepareInvocation: async ({ input }) => ({ invocationMessage: `Looking up "${input.query}" in docs bundle` }),
    }),
    vscode.lm.registerTool<{ map?: string; query: string }>('harbor-docs_codeMap', {
      invoke: async ({ input }) => text(codeMap(input.map ?? 'any', input.query)),
      prepareInvocation: async ({ input }) => ({ invocationMessage: `Querying ${input.map ?? 'all'} map for "${input.query}"` }),
    }),
    vscode.lm.registerTool<{ id: string }>('harbor-docs_specToCode', {
      invoke: async ({ input }) => text(specToCode(input.id)),
      prepareInvocation: async ({ input }) => ({ invocationMessage: `Resolving @docs ${input.id}` }),
    }),
    vscode.lm.registerTool<{ target: string; depth?: number }>('harbor-docs_impact', {
      invoke: async ({ input }) => text(graphImpact(input.target, input.depth ?? 2)),
      prepareInvocation: async ({ input }) => ({ invocationMessage: `Computing blast radius of ${input.target}` }),
    }),
  );

  // @docs participant: retrieval first, then one bounded model call with only the retrieved context.
  const participant = vscode.chat.createChatParticipant('com.acme.harbor.docs', async (request, _chatCtx, stream, token) => {
    const q = request.prompt.trim();
    let context = '';
    switch (request.command) {
      case 'where': context = specToCode(q) + '\n\n' + codeMap('any', q); break;
      case 'impact': context = [graphImpact(q), docsLookup(q)].join('\n\n'); break;
      case 'spec': default: context = docsLookup(q); break;
    }
    stream.markdown(`_Retrieved ${context.length} chars of context (no source files opened)._\n\n`);
    const system = [
      'You answer from the provided docs/maps only. Cite spec IDs and file:line from the context.',
      'If the context is insufficient, say which file:line range should be opened next - do not guess.',
      'Flag unverified/STALE concepts. Keep answers under 20 lines.',
    ].join(' ');
    const messages = [vscode.LanguageModelChatMessage.User(`${system}\n\n<context>\n${context}\n</context>\n\nQuestion: ${q}`)];
    const model = request.model ?? (await vscode.lm.selectChatModels({ vendor: 'copilot' }))[0];
    if (!model) { stream.markdown(context); return; }
    const res = await model.sendRequest(messages, {}, token);
    for await (const chunk of res.text) stream.markdown(chunk);
    stream.markdown('\n\n---\n<details><summary>Retrieved context</summary>\n\n' + context + '\n\n</details>');
  });
  participant.iconPath = new vscode.ThemeIcon('book');
  ctx.subscriptions.push(participant);
}

export function deactivate() { /* nothing to dispose beyond subscriptions */ }
