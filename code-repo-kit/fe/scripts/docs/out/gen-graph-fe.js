"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
// Precise FE graph export using the TypeScript compiler API - `typescript` is already a devDependency in any
// TS React repo, so this adds no library. Complements the regex maps (gen-codebase-map.ps1) with exact
// import edges and resolved API URLs: openapi-fetch calls such as `api.GET('/session/product1/overview', ...)`
// (method from the member name, literal contract path), plus fetch/axios with template literals and
// `const BASE = '...'` constants.
//
// Output: docs/_generated/graph-export-fe.json, consumed by docs repo scripts/gen-graph.ps1 (edges source=export).
//
// Run:   npx tsc -p scripts/docs/tsconfig.gen.json && node scripts/docs/out/gen-graph-fe.js [srcDir] [outFile]
// or     npx ts-node scripts/docs/gen-graph-fe.ts            (if ts-node is already present)
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const ts = __importStar(require("typescript"));
const srcDir = path.resolve(process.argv[2] ?? 'src');
const outFile = path.resolve(process.argv[3] ?? 'docs/_generated/graph-export-fe.json');
const nodes = new Map();
const edges = new Set();
const addNode = (n) => { if (!nodes.has(n.id))
    nodes.set(n.id, n); };
const addEdge = (from, to, rel) => edges.add(JSON.stringify({ from, to, rel }));
const rel = (f) => path.relative(path.dirname(srcDir), f).replace(/\\/g, '/');
const featureOf = (f) => /src\/features\/([^/]+)\//.exec(rel(f))?.[1] ?? 'fe-app';
function listFiles(dir) {
    const out = [];
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
        const p = path.join(dir, e.name);
        if (e.isDirectory()) {
            if (!['node_modules', 'dist', 'build', '__tests__'].includes(e.name))
                out.push(...listFiles(p));
        }
        else if (/\.(ts|tsx)$/.test(e.name) && !/\.(test|spec|stories|d)\.tsx?$/.test(e.name))
            out.push(p);
    }
    return out;
}
const files = listFiles(srcDir);
const program = ts.createProgram(files, { allowJs: false, jsx: ts.JsxEmit.Preserve, module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020, noResolve: false });
const checker = program.getTypeChecker();
for (const sf of program.getSourceFiles()) {
    if (sf.isDeclarationFile || !files.includes(path.resolve(sf.fileName)))
        continue;
    const feature = featureOf(sf.fileName);
    addNode({ id: `feature:${feature}`, kind: 'feature', label: feature, community: feature, repo: 'fe', location: feature === 'fe-app' ? '' : `src/features/${feature}/index.ts`, note: '' });
    const consts = new Map(); // string constants in this file, for template-literal URLs
    // Exported declarations become nodes: components (PascalCase function returning JSX), hooks (use*), others skipped.
    const declNode = (name, line) => {
        const kind = /^use[A-Z]/.test(name) ? 'hook' : /^[A-Z][A-Za-z0-9]*[a-z][A-Za-z0-9]*$/.test(name) ? 'component' : undefined; // ALL_CAPS consts are not components
        if (!kind)
            return undefined;
        const id = `${kind}:${name}`;
        addNode({ id, kind, label: name, community: feature, repo: 'fe', location: `${rel(sf.fileName)}:${line}`, note: '' });
        addEdge(`feature:${feature}`, id, 'contains');
        return id;
    };
    const line = (n) => sf.getLineAndCharacterOfPosition(n.getStart(sf)).line + 1;
    const visit = (n, owner) => {
        if (ts.isVariableStatement(n)) {
            for (const d of n.declarationList.declarations) {
                if (ts.isIdentifier(d.name) && d.initializer) {
                    if (ts.isStringLiteral(d.initializer) || ts.isNoSubstitutionTemplateLiteral(d.initializer))
                        consts.set(d.name.text, d.initializer.text);
                    const id = declNode(d.name.text, line(d));
                    if (id) {
                        ts.forEachChild(d.initializer, c => visit(c, id));
                        continue;
                    }
                }
            }
        }
        if (ts.isFunctionDeclaration(n) && n.name) {
            const id = declNode(n.name.text, line(n));
            if (id) {
                n.body && ts.forEachChild(n.body, c => visit(c, id));
                return;
            }
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
                if (target && files.includes(path.resolve(target.fileName)))
                    addEdge(owner, `hook:${n.expression.text}`, 'uses');
            }
        }
        if (ts.isJsxOpeningLikeElement(n) && owner && ts.isIdentifier(n.tagName) && /^[A-Z]/.test(n.tagName.text)) {
            const sym = checker.getSymbolAtLocation(n.tagName);
            const decl = sym && ((sym.flags & ts.SymbolFlags.Alias ? checker.getAliasedSymbol(sym) : sym).declarations?.[0]);
            if (decl && files.includes(path.resolve(decl.getSourceFile().fileName)))
                addEdge(owner, `component:${n.tagName.text}`, 'renders');
        }
        ts.forEachChild(n, c => visit(c, owner));
    };
    const urlOf = (a) => {
        if (ts.isStringLiteral(a) || ts.isNoSubstitutionTemplateLiteral(a))
            return a.text;
        if (ts.isTemplateExpression(a)) {
            let s = a.head.text;
            for (const span of a.templateSpans) {
                const e = span.expression;
                s += ts.isIdentifier(e) && consts.has(e.text) ? consts.get(e.text) : '{*}';
                s += span.literal.text;
            }
            return s;
        }
        if (ts.isIdentifier(a) && consts.has(a.text))
            return consts.get(a.text);
        return undefined;
    };
    const methodFromInit = (a) => {
        if (!a || !ts.isObjectLiteralExpression(a))
            return undefined;
        for (const p of a.properties)
            if (ts.isPropertyAssignment(p) && p.name.getText(sf) === 'method' && ts.isStringLiteral(p.initializer))
                return p.initializer.text.toUpperCase();
        return undefined;
    };
    // cross-feature imports -> depends-on between features
    for (const st of sf.statements) {
        if (ts.isImportDeclaration(st) && ts.isStringLiteral(st.moduleSpecifier) && st.moduleSpecifier.text.startsWith('.')) {
            const target = path.resolve(path.dirname(sf.fileName), st.moduleSpecifier.text);
            const tf = featureOf(target + '/');
            if (tf !== feature)
                addEdge(`feature:${feature}`, `feature:${tf}`, 'depends-on');
        }
    }
    ts.forEachChild(sf, c => visit(c));
}
fs.mkdirSync(path.dirname(outFile), { recursive: true });
const json = { generated: { by: 'process:graph-export-fe' }, nodes: [...nodes.values()], edges: [...edges].map(e => JSON.parse(e)) };
fs.writeFileSync(outFile, JSON.stringify(json, null, 2) + '\n', 'utf8');
console.log(`graph-export-fe: ${nodes.size} nodes, ${edges.size} edges -> ${outFile}`);
