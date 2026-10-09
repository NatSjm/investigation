// Zero-dependency retrieval over the OKF docs bundle and generated code maps.
// Everything here is plain fs + string ops so it can pass an internal security review quickly.
import * as fs from 'fs';
import * as path from 'path';

export interface Concept {
  file: string;          // absolute path
  rel: string;           // path relative to bundle root
  type: string;
  id?: string;
  title: string;
  status?: string;
  trust: 'human-reviewed' | 'machine-confirmed' | 'unverified' | 'STALE';
  description?: string;  // from the folder index.md line, if present
  aliases: string[];     // frontmatter aliases (e.g. source-language terms) so non-English queries still match
  body: string;          // full markdown without frontmatter
}

const SKIP_DIRS = new Set(['.git', '.github', 'node_modules', 'scripts', 'ci-examples', 'third-party', 'confluence-import']);

export function listMarkdown(root: string): string[] {
  const out: string[] = [];
  const walk = (dir: string) => {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      if (e.isDirectory()) { if (!SKIP_DIRS.has(e.name)) walk(path.join(dir, e.name)); }
      else if (e.name.endsWith('.md')) out.push(path.join(dir, e.name));
    }
  };
  if (fs.existsSync(root)) walk(root);
  return out;
}

/** Minimal YAML frontmatter reader: top-level scalars + nested `verified[].by` / `generated.by` / `stale_after`. */
export function parseFrontmatter(text: string): { fm: Record<string, string>; body: string; verifiedBy: string[] } {
  const m = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/.exec(text);
  if (!m) return { fm: {}, body: text, verifiedBy: [] };
  const fm: Record<string, string> = {};
  const verifiedBy: string[] = [];
  let section = '';
  for (const raw of m[1].split(/\r?\n/)) {
    const line = raw.replace(/\s+#.*$/, '');
    const top = /^(\w[\w-]*):\s*(.*)$/.exec(line);
    if (top) {
      section = top[1];
      const flow = /^\{(.*)\}$/.exec(top[2].trim());
      if (flow) {
        // inline mapping: `verified: { by: human:x, at: ... }`
        const by = /(?:^|,)\s*by:\s*([^,}]+)/.exec(flow[1])?.[1]?.trim().replace(/^["']|["']$/g, '');
        if (by && section === 'verified') verifiedBy.push(by);
        if (by && section === 'generated') fm['generated.by'] = by;
        continue;
      }
      if (top[2]) fm[top[1]] = top[2].replace(/^["']|["']$/g, '');
      continue;
    }
    const nested = /^\s+(?:-\s+)?(\w+):\s*(.+)$/.exec(line);
    if (nested) {
      const v = nested[2].replace(/^["']|["']$/g, '');
      if (section === 'verified' && nested[1] === 'by') verifiedBy.push(v);
      if (section === 'generated' && nested[1] === 'by') fm['generated.by'] = v;
    }
  }
  return { fm, body: text.slice(m[0].length), verifiedBy };
}

export function trustOf(fm: Record<string, string>, verifiedBy: string[]): Concept['trust'] {
  if (fm['stale_after'] && new Date(fm['stale_after']) < new Date()) return 'STALE';
  if (verifiedBy.some(v => v.startsWith('human:'))) return 'human-reviewed';
  if (verifiedBy.length) return 'machine-confirmed';
  return 'unverified';
}

export function loadBundle(root: string): Concept[] {
  const descriptions = new Map<string, string>();
  const concepts: Concept[] = [];
  const files = listMarkdown(root);
  // Pass 1: index.md descriptions (they may sort after the concepts they describe).
  for (const file of files) {
    if (path.basename(file).toLowerCase() !== 'index.md') continue;
    const text = fs.readFileSync(file, 'utf8');
    // "- [Title](rel.md): description" or "* [Title](rel.md) - description · badge" (build-index.ps1 style)
    for (const l of text.matchAll(/^[-*]\s+\[[^\]]*\]\(([^)]+)\)\s*(?::|-)\s*(.+)$/gm)) {
      const desc = l[2].replace(/\s*·\s*(human-reviewed|machine-confirmed|unverified|STALE)\s*$/, '').trim();
      descriptions.set(path.normalize(path.join(path.dirname(file), l[1])), desc);
    }
  }
  // Pass 2: concepts.
  for (const file of files) {
    const base = path.basename(file).toLowerCase();
    if (base === 'index.md' || base === 'log.md') continue;
    const text = fs.readFileSync(file, 'utf8');
    const { fm, body, verifiedBy } = parseFrontmatter(text);
    const title = (/^#\s+(.+)$/m.exec(body)?.[1] ?? path.basename(file, '.md')).trim();
    const aliases = (fm['aliases'] ?? '').replace(/^\[|\]$/g, '').split(',').map(s => s.trim().replace(/^["']|["']$/g, '').toLowerCase()).filter(Boolean);
    concepts.push({
      file, rel: path.relative(root, file).replace(/\\/g, '/'), type: fm['type'] ?? 'Document', id: fm['id'],
      title, status: fm['status'], trust: trustOf(fm, verifiedBy), description: descriptions.get(path.normalize(file)), aliases, body,
    });
  }
  return concepts;
}

export function scoreConcept(c: Concept, query: string): number {
  const q = query.toLowerCase();
  const terms = q.split(/\s+/).filter(Boolean);
  let s = 0;
  if (c.id && c.id.toLowerCase() === q) s += 100;
  if (path.basename(c.rel, '.md').toLowerCase() === q) s += 90;
  if (c.title.toLowerCase().includes(q)) s += 40;
  if (c.aliases.includes(q)) s += 60;
  for (const t of terms) {
    if (c.title.toLowerCase().includes(t)) s += 8;
    if (c.aliases.some(a => a.includes(t))) s += 8;
    if ((c.description ?? '').toLowerCase().includes(t)) s += 6;
    if (c.rel.toLowerCase().includes(t)) s += 4;
    if (c.body.toLowerCase().includes(t)) s += 1;
  }
  return s;
}

/** Return one `## heading` section (or the text before the first `##`) - progressive disclosure, not the whole file. */
export function section(body: string, heading?: string): string {
  const parts = body.split(/^(?=##\s)/m);
  if (!heading) return parts[0].trim();
  const h = heading.toLowerCase();
  return (parts.find(p => p.toLowerCase().startsWith('## ' + h) || p.toLowerCase().startsWith('## ' + h.replace(/\s+/g, ' '))) ?? parts[0]).trim();
}

/** Grep-like row filter over the generated Markdown tables; returns header + matching rows. */
export function mapRows(mapFile: string, query: string): string[] {
  if (!fs.existsSync(mapFile)) return [];
  const lines = fs.readFileSync(mapFile, 'utf8').split(/\r?\n/);
  const header = lines.find(l => l.startsWith('|')) ?? '';
  const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
  const rows = lines.filter(l => l.startsWith('|') && l !== header && !/^\|\s*-+/.test(l) && terms.every(t => l.toLowerCase().includes(t)));
  return rows.length ? [header, header.replace(/[^|]+/g, '---'), ...rows] : [];
}

export function clip(text: string, max: number): string {
  return text.length <= max ? text : text.slice(0, max - 40) + `\n... [truncated, ${text.length - max} more chars]`;
}

// --- architectural graph (generated/graph/graph.json from scripts/gen-graph.ps1) --------------

export interface GraphNode { id: string; kind: string; label: string; community: string; repo: string; location?: string; note?: string; rank?: number; degree?: number }
export interface GraphLink { from: string; to: string; rel: string; source?: string }
export interface Graph { nodes: GraphNode[]; edges: GraphLink[]; byId: Map<string, GraphNode>; adj: Map<string, GraphLink[]> }

export function loadGraph(file: string): Graph | undefined {
  if (!fs.existsSync(file)) return undefined;
  const raw = JSON.parse(fs.readFileSync(file, 'utf8')) as { nodes: GraphNode[]; edges: GraphLink[] };
  const byId = new Map(raw.nodes.map(n => [n.id, n]));
  const adj = new Map<string, GraphLink[]>();
  for (const e of raw.edges) {
    (adj.get(e.from) ?? adj.set(e.from, []).get(e.from)!).push(e);
    (adj.get(e.to) ?? adj.set(e.to, []).get(e.to)!).push(e);
  }
  return { nodes: raw.nodes, edges: raw.edges, byId, adj };
}

/** Resolve an id, a substring, or a repo-relative file path to graph nodes. */
export function resolveNodes(g: Graph, query: string): GraphNode[] {
  if (g.byId.has(query)) return [g.byId.get(query)!];
  const q = query.replace(/\\/g, '/').toLowerCase();
  const byPath = g.nodes.filter(n => n.location && (n.location.split(':')[0].toLowerCase() === q || q.endsWith('/' + n.location.split(':')[0].toLowerCase())));
  if (byPath.length) return byPath;
  return g.nodes.filter(n => n.id.toLowerCase().includes(q) || n.label.toLowerCase().includes(q));
}

/** Undirected BFS; returns nodes grouped by depth and the touched edges - the blast radius. */
export function impact(g: Graph, start: GraphNode[], depth: number): { levels: GraphNode[][]; edges: GraphLink[] } {
  const dist = new Map<string, number>(start.map(n => [n.id, 0]));
  const queue = start.map(n => n.id);
  const touched = new Set<GraphLink>();
  while (queue.length) {
    const c = queue.shift()!;
    const d = dist.get(c)!;
    if (d >= depth) continue;
    for (const e of g.adj.get(c) ?? []) {
      touched.add(e);
      const o = e.from === c ? e.to : e.from;
      if (!dist.has(o)) { dist.set(o, d + 1); queue.push(o); }
    }
  }
  const levels: GraphNode[][] = [];
  for (const [id, d] of dist) { (levels[d] ??= []).push(g.byId.get(id) ?? { id, kind: 'unknown', label: id, community: '?', repo: '?' }); }
  levels.forEach(l => l.sort((a, b) => a.id.localeCompare(b.id)));
  return { levels, edges: [...touched].sort((a, b) => (a.rel + a.from + a.to).localeCompare(b.rel + b.from + b.to)) };
}

export function renderImpact(res: { levels: GraphNode[][]; edges: GraphLink[] }): string {
  const fmt = (n: GraphNode) => `- \`${n.id}\` [${n.community}]${n.location ? ` - \`${n.location}\`` : ''}${n.note ? ` - ${n.note}` : ''}`;
  const out: string[] = [];
  res.levels.forEach((l, d) => { if (l?.length) out.push(`#### depth ${d}`, ...l.map(fmt)); });
  out.push('#### edges', ...res.edges.map(e => `- \`${e.from}\` -${e.rel}-> \`${e.to}\`${e.source && e.source !== 'regex-map' ? ` (${e.source})` : ''}`));
  const specs = res.levels.flat().filter(n => n.id.startsWith('spec:')).map(n => n.id);
  out.push(`#### specs in blast radius: ${specs.length ? specs.join(', ') : 'none - check @docs tags'}`);
  return out.join('\n');
}
