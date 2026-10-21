// Precise FE graph export using the TypeScript compiler API - `typescript` is already a devDependency in any
// TS React repo, so this adds no library. Complements the regex maps (gen-codebase-map.py) with exact
// import edges and resolved API URLs: openapi-fetch calls such as `api.GET('/session/product1/overview', ...)`
// (method from the member name, literal contract path), plus fetch/axios with template literals and
// `const BASE = '...'` constants.
//
// Needs TypeScript 7 (the native compiler): the package no longer exports the old `ts.createProgram` API, only
// `typescript/unstable/sync` (a client of the bundled native compiler process) and `typescript/unstable/ast`
// (node classes and `is*` guards). The script opens every source file in that process, which picks the project the
// way the language server does: the nearest tsconfig.json that includes the file (a Vite-style root config that only
// lists `references` hands over to the referenced one), so `@/` paths and other options come from the repository's own
// configuration; a file outside every tsconfig lands in the inferred project (relative imports only). The console line
// names the config(s) used. The API is marked unstable by the TypeScript team - a later 7.x may rename things.
//
// Layout: read from scripts/docs/docs-gen.json (same file as the Python generators): `pages_dir` (one `feature:` node
// per page folder, folders in `not_pages` become their own node, e.g. `shared`), `exclude_paths` (generated clients
// are never parsed), everything else is `fe-app`.
//
// Output: docs/_generated/graph-export-fe.json, consumed by docs repo scripts/gen-graph.py (edges source=export).
//
// Run:   npx tsc -p scripts/docs/tsconfig.gen.json && node scripts/docs/out/gen-graph-fe.js [srcDir] [outFile]
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';
import { API, SymbolFlags, type Checker, type Project } from 'typescript/unstable/sync';
import {
  isCallExpression, isFunctionDeclaration, isIdentifier, isImportDeclaration, isJsxOpeningLikeElement,
  isNoSubstitutionTemplateLiteral, isObjectLiteralExpression, isPropertyAssignment, isStringLiteral,
  isTemplateExpression, isVariableStatement, type Expression, type Identifier, type Node, type SourceFile,
} from 'typescript/unstable/ast';

const srcDir = path.resolve(process.argv[2] ?? 'src');
const outFile = path.resolve(process.argv[3] ?? 'docs/_generated/graph-export-fe.json');
const repoRoot = path.dirname(srcDir);
// ES module output (Vite repos declare "type": "module"); for a CommonJS repo set "module": "CommonJS" in tsconfig.gen.json and use __dirname here
const scriptDir = path.dirname(fileURLToPath(import.meta.url));

interface Layout { pages_dir: string; not_pages: string[]; page_entry: string[]; exclude_paths: string[] }
const layout: Layout = { pages_dir: 'src/pages', not_pages: ['shared'], page_entry: ['<Page>.tsx', 'index.tsx', 'index.ts'], exclude_paths: [] };
for (const cfg of [path.join(repoRoot, 'scripts', 'docs', 'docs-gen.json'), path.join(scriptDir, '..', 'docs-gen.json'), path.join(scriptDir, 'docs-gen.json')]) {
  if (fs.existsSync(cfg)) { Object.assign(layout, JSON.parse(fs.readFileSync(cfg, 'utf8'))); break; }
}
const pagesPrefix = layout.pages_dir.replace(/\\/g, '/').replace(/\/+$/, '') + '/';
const excluded = layout.exclude_paths.map(p => path.resolve(repoRoot, p).toLowerCase());

interface Node_ { id: string; kind: string; label: string; community: string; repo: string; location: string; note: string }
interface Edge { from: string; to: string; rel: string }
const nodes = new Map<string, Node_>();
const edges = new Set<string>();
const addNode = (n: Node_) => { if (!nodes.has(n.id)) nodes.set(n.id, n); };
const addEdge = (from: string, to: string, rel: string) => edges.add(JSON.stringify({ from, to, rel }));
const rel = (f: string) => path.relative(repoRoot, f).replace(/\\/g, '/');
// one spelling for file comparisons: the native compiler reports forward-slash paths, declarations come back as
// canonical (lower-case on Windows) paths
const key = (f: string) => path.resolve(f).replace(/\\/g, '/').toLowerCase();
// page folder of a file: first segment under pages_dir (shared pieces keep their folder name), else fe-app
const featureOf = (f: string) => {
  const r = rel(f);
  return r.startsWith(pagesPrefix) ? r.slice(pagesPrefix.length).split('/')[0] || 'fe-app' : 'fe-app';
};
const entryOf = (page: string) => {
  for (const pat of layout.page_entry) {
    const cand = path.join(repoRoot, layout.pages_dir, page, pat.replace('<Page>', page));
    if (fs.existsSync(cand)) return rel(cand);
  }
  return `${layout.pages_dir}/${page}`;
};
const isExcluded = (f: string) => { const p = path.resolve(f).toLowerCase(); return excluded.some(x => p === x || p.startsWith(x + path.sep)); };

function listFiles(dir: string): string[] {
  const out: string[] = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (isExcluded(p)) continue;
    if (e.isDirectory()) { if (!['node_modules', 'dist', 'build', '__tests__'].includes(e.name)) out.push(...listFiles(p)); }
    else if (/\.(ts|tsx)$/.test(e.name) && !/\.(test|spec|stories|d)\.tsx?$/.test(e.name)) out.push(p);
  }
  return out;
}

const files = listFiles(srcDir).sort();  // deterministic output whatever order the file system lists folders in
const fileKeys = new Set(files.map(key));

// The native compiler process: every listed file is opened, its default project (nearest tsconfig that includes it)
// gives the program and the checker. Files are grouped by project so the console line can name each config once.
const api = new API({ cwd: repoRoot });
const snapshot = api.updateSnapshot({ openFiles: files.map(f => f.replace(/\\/g, '/')) });
const byProject = new Map<Project, string[]>();
const projectName = (p: Project) => p.configFileName && fs.existsSync(p.configFileName) ? rel(p.configFileName) : 'inferred project (no tsconfig.json includes the file)';
for (const f of files) {
  const project = snapshot.getDefaultProjectForFile(f.replace(/\\/g, '/'));
  if (!project) { console.error(`graph-export-fe: no project for ${rel(f)}, skipped`); continue; }
  byProject.set(project, [...(byProject.get(project) ?? []), f]);
}

for (const [project, projectFiles] of byProject) {
  const checker: Checker = project.checker;
  for (const file of projectFiles) {
    const sf: SourceFile | undefined = project.program.getSourceFile(file.replace(/\\/g, '/'));
    if (!sf) { console.error(`graph-export-fe: ${rel(file)} is not in ${projectName(project)}, skipped`); continue; }
    exportFile(sf, checker);
  }
}
api.close();

function exportFile(sf: SourceFile, checker: Checker) {
  const feature = featureOf(sf.fileName);
  addNode({ id: `feature:${feature}`, kind: 'feature', label: feature, community: feature, repo: 'fe', location: feature === 'fe-app' ? '' : entryOf(feature), note: '' });
  const consts = new Map<string, string>();  // string constants in this file, for template-literal URLs
  // identifiers whose declaration file decides whether an edge is ours; resolved in one round trip per file
  const lookups: { ident: Identifier; edge: [string, string, string] }[] = [];

  // Exported declarations become nodes: components (PascalCase function returning JSX), hooks (use*), others skipped.
  const declNode = (name: string, line: number): string | undefined => {
    const kind = /^use[A-Z]/.test(name) ? 'hook' : /^[A-Z][A-Za-z0-9]*[a-z][A-Za-z0-9]*$/.test(name) ? 'component' : undefined;  // ALL_CAPS consts are not components
    if (!kind) return undefined;
    const id = `${kind}:${name}`;
    addNode({ id, kind, label: name, community: feature, repo: 'fe', location: `${rel(sf.fileName)}:${line}`, note: '' });
    addEdge(`feature:${feature}`, id, 'contains');
    return id;
  };
  const line = (n: Node) => sf.getLineAndCharacterOfPosition(n.getStart(sf)).line + 1;

  const visit = (n: Node, owner?: string): void => {
    if (isVariableStatement(n)) {
      for (const d of n.declarationList.declarations) {
        if (isIdentifier(d.name) && d.initializer) {
          if (isStringLiteral(d.initializer) || isNoSubstitutionTemplateLiteral(d.initializer)) consts.set(d.name.text, d.initializer.text);
          const id = declNode(d.name.text, line(d));
          if (id) { d.initializer.forEachChild(c => { visit(c, id); }); continue; }
        }
      }
    }
    if (isFunctionDeclaration(n) && n.name) {
      const id = declNode(n.name.text, line(n));
      if (id) { n.body?.forEachChild(c => { visit(c, id); }); return; }
    }
    // fetch(...) / axios.get(...) / apiClient.post(...) -> first argument is the URL
    if (isCallExpression(n) && owner) {
      const callee = n.expression.getText(sf);
      if (/^(fetch|axios(\.\w+)?|api(Client)?(\.\w+)?|http(\.\w+)?)$/.test(callee) && n.arguments[0]) {
        const url = urlOf(n.arguments[0]);
        if (url) {
          const method = /\.(get|post|put|patch|delete)$/i.exec(callee)?.[1]?.toUpperCase() ?? methodFromInit(n.arguments[1]) ?? 'GET';
          const id = `url:${method} ${url}`;
          addNode({ id, kind: 'url', label: `${method} ${url}`, community: feature, repo: 'fe', location: `${rel(sf.fileName)}:${line(n)}`, note: 'resolved by TS compiler' });
          addEdge(owner, id, 'calls');
        }
      }
      // calls to our own hooks/components -> uses edges (resolved through the checker, so re-exports work)
      if (isIdentifier(n.expression) && /^use[A-Z]/.test(n.expression.text)) lookups.push({ ident: n.expression, edge: [owner, `hook:${n.expression.text}`, 'uses'] });
    }
    if (isJsxOpeningLikeElement(n) && owner && isIdentifier(n.tagName) && /^[A-Z]/.test(n.tagName.text)) lookups.push({ ident: n.tagName, edge: [owner, `component:${n.tagName.text}`, 'renders'] });
    n.forEachChild(c => { visit(c, owner); });
  };

  const urlOf = (a: Expression): string | undefined => {
    if (isStringLiteral(a) || isNoSubstitutionTemplateLiteral(a)) return a.text;
    if (isTemplateExpression(a)) {
      let s = a.head.text;
      for (const span of a.templateSpans) {
        const e = span.expression;
        s += isIdentifier(e) && consts.has(e.text) ? consts.get(e.text) : '{*}';
        s += span.literal.text;
      }
      return s;
    }
    if (isIdentifier(a) && consts.has(a.text)) return consts.get(a.text);
    return undefined;
  };
  const methodFromInit = (a?: Expression): string | undefined => {
    if (!a || !isObjectLiteralExpression(a)) return undefined;
    for (const p of a.properties) if (isPropertyAssignment(p) && p.name.getText(sf) === 'method' && isStringLiteral(p.initializer)) return p.initializer.text.toUpperCase();
    return undefined;
  };

  // cross-page imports (relative or '@/' alias) -> depends-on between pages / shared / fe-app
  for (const st of sf.statements) {
    if (isImportDeclaration(st) && isStringLiteral(st.moduleSpecifier)) {
      const spec = st.moduleSpecifier.text;
      const target = spec.startsWith('.') ? path.resolve(path.dirname(sf.fileName), spec) : spec.startsWith('@/') ? path.join(srcDir, spec.slice(2)) : '';
      if (!target) continue;
      const tf = featureOf(target + '/');
      if (tf !== feature) addEdge(`feature:${feature}`, `feature:${tf}`, 'depends-on');
    }
  }
  sf.forEachChild(c => { visit(c); });

  // an edge counts only when the symbol's declaration is one of the listed files (not node_modules, not a generated client)
  const symbols = checker.getSymbolAtLocation(lookups.map(l => l.ident));
  lookups.forEach((l, i) => {
    const sym = symbols[i];
    const real = sym && (sym.flags & SymbolFlags.Alias ? checker.getAliasedSymbol(sym) : sym);
    const declFile = real?.declarations[0]?.path;
    if (declFile && fileKeys.has(key(declFile))) addEdge(...l.edge);
  });
}

fs.mkdirSync(path.dirname(outFile), { recursive: true });
const json = { generated: { by: 'process:graph-export-fe' }, nodes: [...nodes.values()], edges: [...edges].map(e => JSON.parse(e) as Edge) };
fs.writeFileSync(outFile, JSON.stringify(json, null, 2) + '\n', 'utf8');
const used = [...byProject].map(([p, fs_]) => `${projectName(p)}: ${fs_.length} files`).join(', ');
console.log(`graph-export-fe: ${nodes.size} nodes, ${edges.size} edges (compiler options: ${used}) -> ${outFile}`);
