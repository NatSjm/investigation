// Precise FE graph export using the TypeScript compiler API - `typescript` is already a devDependency in any
// TS React repo, so this adds no library. Complements the regex maps (gen-codebase-map.py) with exact
// import edges and resolved API URLs: openapi-fetch calls such as `api.GET('/session/product1/overview', ...)`
// (method from the member name, literal contract path), plus fetch/axios with template literals and
// `const BASE = '...'` constants.
//
// Layout: read from scripts/docs/docs-gen.json (same file as the Python generators): `pages_dir` (one `feature:` node
// per page folder, folders in `not_pages` become their own node, e.g. `shared`), `exclude_paths` (generated clients
// are never parsed), everything else is `fe-app`.
//
// Output: docs/_generated/graph-export-fe.json, consumed by docs repo scripts/gen-graph.py (edges source=export).
//
// Run:   npx tsc -p scripts/docs/tsconfig.gen.json && node scripts/docs/out/gen-graph-fe.js [srcDir] [outFile]
// or     npx ts-node scripts/docs/gen-graph-fe.ts            (if ts-node is already present)
import * as fs from 'fs';
import * as path from 'path';
import * as ts from 'typescript';
import { fileURLToPath } from 'url';

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

interface Node { id: string; kind: string; label: string; community: string; repo: string; location: string; note: string }
interface Edge { from: string; to: string; rel: string }
const nodes = new Map<string, Node>();
const edges = new Set<string>();
const addNode = (n: Node) => { if (!nodes.has(n.id)) nodes.set(n.id, n); };
const addEdge = (from: string, to: string, rel: string) => edges.add(JSON.stringify({ from, to, rel }));
const rel = (f: string) => path.relative(repoRoot, f).replace(/\\/g, '/');
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

const files = listFiles(srcDir);
const program = ts.createProgram(files, { allowJs: false, jsx: ts.JsxEmit.Preserve, module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020, noResolve: false });
const checker = program.getTypeChecker();

for (const sf of program.getSourceFiles()) {
  if (sf.isDeclarationFile || !files.includes(path.resolve(sf.fileName))) continue;
  const feature = featureOf(sf.fileName);
  addNode({ id: `feature:${feature}`, kind: 'feature', label: feature, community: feature, repo: 'fe', location: feature === 'fe-app' ? '' : entryOf(feature), note: '' });
  const consts = new Map<string, string>();  // string constants in this file, for template-literal URLs

  // Exported declarations become nodes: components (PascalCase function returning JSX), hooks (use*), others skipped.
  const declNode = (name: string, line: number): string | undefined => {
    const kind = /^use[A-Z]/.test(name) ? 'hook' : /^[A-Z][A-Za-z0-9]*[a-z][A-Za-z0-9]*$/.test(name) ? 'component' : undefined;  // ALL_CAPS consts are not components
    if (!kind) return undefined;
    const id = `${kind}:${name}`;
    addNode({ id, kind, label: name, community: feature, repo: 'fe', location: `${rel(sf.fileName)}:${line}`, note: '' });
    addEdge(`feature:${feature}`, id, 'contains');
    return id;
  };
  const line = (n: ts.Node) => sf.getLineAndCharacterOfPosition(n.getStart(sf)).line + 1;

  const visit = (n: ts.Node, owner?: string) => {
    if (ts.isVariableStatement(n)) {
      for (const d of n.declarationList.declarations) {
        if (ts.isIdentifier(d.name) && d.initializer) {
          if (ts.isStringLiteral(d.initializer) || ts.isNoSubstitutionTemplateLiteral(d.initializer)) consts.set(d.name.text, d.initializer.text);
          const id = declNode(d.name.text, line(d));
          if (id) { ts.forEachChild(d.initializer, c => visit(c, id)); continue; }
        }
      }
    }
    if (ts.isFunctionDeclaration(n) && n.name) {
      const id = declNode(n.name.text, line(n));
      if (id) { n.body && ts.forEachChild(n.body, c => visit(c, id)); return; }
    }
    // fetch(...) / axios.get(...) / apiClient.post(...) -> first argument is the URL
    if (ts.isCallExpression(n) && owner) {
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
      if (ts.isIdentifier(n.expression) && /^use[A-Z]/.test(n.expression.text)) {
        const sym = checker.getSymbolAtLocation(n.expression);
        const real = sym && (sym.flags & ts.SymbolFlags.Alias ? checker.getAliasedSymbol(sym) : sym);
        const target = real?.declarations?.[0]?.getSourceFile();
        if (target && files.includes(path.resolve(target.fileName))) addEdge(owner, `hook:${n.expression.text}`, 'uses');
      }
    }
    if (ts.isJsxOpeningLikeElement(n) && owner && ts.isIdentifier(n.tagName) && /^[A-Z]/.test(n.tagName.text)) {
      const sym = checker.getSymbolAtLocation(n.tagName);
      const decl = sym && ((sym.flags & ts.SymbolFlags.Alias ? checker.getAliasedSymbol(sym) : sym).declarations?.[0]);
      if (decl && files.includes(path.resolve(decl.getSourceFile().fileName))) addEdge(owner, `component:${n.tagName.text}`, 'renders');
    }
    ts.forEachChild(n, c => visit(c, owner));
  };

  const urlOf = (a: ts.Expression): string | undefined => {
    if (ts.isStringLiteral(a) || ts.isNoSubstitutionTemplateLiteral(a)) return a.text;
    if (ts.isTemplateExpression(a)) {
      let s = a.head.text;
      for (const span of a.templateSpans) {
        const e = span.expression;
        s += ts.isIdentifier(e) && consts.has(e.text) ? consts.get(e.text) : '{*}';
        s += span.literal.text;
      }
      return s;
    }
    if (ts.isIdentifier(a) && consts.has(a.text)) return consts.get(a.text);
    return undefined;
  };
  const methodFromInit = (a?: ts.Expression): string | undefined => {
    if (!a || !ts.isObjectLiteralExpression(a)) return undefined;
    for (const p of a.properties) if (ts.isPropertyAssignment(p) && p.name.getText(sf) === 'method' && ts.isStringLiteral(p.initializer)) return p.initializer.text.toUpperCase();
    return undefined;
  };

  // cross-page imports (relative or '@/' alias) -> depends-on between pages / shared / fe-app
  for (const st of sf.statements) {
    if (ts.isImportDeclaration(st) && ts.isStringLiteral(st.moduleSpecifier)) {
      const spec = st.moduleSpecifier.text;
      const target = spec.startsWith('.') ? path.resolve(path.dirname(sf.fileName), spec) : spec.startsWith('@/') ? path.join(srcDir, spec.slice(2)) : '';
      if (!target) continue;
      const tf = featureOf(target + '/');
      if (tf !== feature) addEdge(`feature:${feature}`, `feature:${tf}`, 'depends-on');
    }
  }
  ts.forEachChild(sf, c => visit(c));
}

fs.mkdirSync(path.dirname(outFile), { recursive: true });
const json = { generated: { by: 'process:graph-export-fe' }, nodes: [...nodes.values()], edges: [...edges].map(e => JSON.parse(e) as Edge) };
fs.writeFileSync(outFile, JSON.stringify(json, null, 2) + '\n', 'utf8');
console.log(`graph-export-fe: ${nodes.size} nodes, ${edges.size} edges -> ${outFile}`);
