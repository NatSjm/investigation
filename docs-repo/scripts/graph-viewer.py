#!/usr/bin/env python3
"""Writes a self-contained HTML page that draws generated/graph/graph.json: one community at a time (dropdown), text filter,
optional direct neighbours from other communities, click a node for its location, note and edges; drag, wheel to zoom.
Standard library only; the page needs nothing but a browser (open the file directly, no server).

Examples:
  python3 scripts/graph-viewer.py                      -> .context/graph-viewer.html (git-ignored), first community selected
  python3 scripts/graph-viewer.py --community stress --out /tmp/graph.html"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import repo_root  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--graph', default='', help='graph.json (default: generated/graph/graph.json)')
    ap.add_argument('--out', default='', help='output page (default: .context/graph-viewer.html)')
    ap.add_argument('--community', default='', help='community selected when the page opens (default: the first)')
    a = ap.parse_args()
    root = repo_root(__file__)
    src = a.graph or os.path.join(root, 'generated', 'graph', 'graph.json')
    out = a.out or os.path.join(root, '.context', 'graph-viewer.html')
    if not os.path.isfile(src):
        raise SystemExit(f'{src} missing: run scripts/gen-graph.py first')
    with open(src, encoding='utf-8') as fh:
        g = json.load(fh)
    start = a.community or (g['communities'][0]['id'] if g.get('communities') else '*')
    data = json.dumps({'communities': g['communities'], 'nodes': g['nodes'], 'edges': g['edges'], 'start': start})
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as fh:
        fh.write(HTML.replace('__DATA__', data))
    print(f"graph viewer: {len(g['nodes'])} node(s), {len(g['edges'])} edge(s) -> {out} (open it in a browser)")


HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>Architecture graph</title>
<style>
 body{margin:0;font:13px system-ui,sans-serif;background:#fafafa;color:#222;display:flex;height:100vh}
 #side{width:230px;flex:none;padding:10px;border-right:1px solid #ddd;overflow:auto;background:#fff}
 canvas{flex:1;display:block}
 select,input{width:100%;margin:4px 0 10px;padding:4px}
 .legend span{display:inline-block;padding:2px 6px;margin:2px;border-radius:3px;color:#fff;font-size:11px}
 #info{margin-top:10px;white-space:pre-wrap;word-break:break-all;font-family:ui-monospace,monospace;font-size:11px;background:#f3f3f3;padding:8px;border-radius:4px;min-height:80px}
 h3{margin:8px 0 4px;font-size:13px}
</style></head><body>
<div id="side">
 <h3>Community</h3><select id="community"></select>
 <h3>Filter nodes by text</h3><input id="filter" placeholder="e.g. Stress">
 <label><input type="checkbox" id="ext"> include direct neighbours from other communities</label>
 <h3>Kinds</h3><div class="legend" id="legend"></div>
 <h3>Selected node</h3><div id="info">click a node; drag to move; wheel to zoom</div>
 <h3>Edges of the selection</h3><div id="edges" style="font-size:11px"></div>
</div>
<canvas id="c"></canvas>
<script>
const DATA = __DATA__;
const COLORS = {context:'#222',feature:'#1f77b4',route:'#17becf',hook:'#9467bd',component:'#c5b0d5',endpoint:'#2ca02c',
  class:'#ff7f0e',table:'#8c564b',topic:'#d62728',channel:'#e377c2',spec:'#bcbd22',calculation:'#7f7f7f'};
const byId = Object.fromEntries(DATA.nodes.map(n=>[n.id,n]));
const sel = document.getElementById('community'), filt = document.getElementById('filter'), ext = document.getElementById('ext');
const legend = document.getElementById('legend');
for (const [k,c] of Object.entries(COLORS)) legend.insertAdjacentHTML('beforeend', `<span style="background:${c}">${k}</span>`);
for (const c of DATA.communities) sel.insertAdjacentHTML('beforeend', `<option value="${c.id}">${c.id} (${c.nodes} nodes, ${c.repo})</option>`);
sel.insertAdjacentHTML('afterbegin', `<option value="*">all communities (${DATA.nodes.length} nodes)</option>`);
sel.value = DATA.communities.some(c=>c.id===DATA.start) ? DATA.start : '*';
const canvas = document.getElementById('c'), ctx = canvas.getContext('2d');
let nodes=[], edges=[], scale=1, ox=0, oy=0, drag=null, selected=null, raf=0;
function build(){
  const com = sel.value, q = filt.value.trim().toLowerCase();
  let ids = new Set(DATA.nodes.filter(n => com==='*' || n.community===com).map(n=>n.id));
  if (ext.checked && com!=='*') { const base = new Set(ids); for (const e of DATA.edges) { if (base.has(e.from)) ids.add(e.to); else if (base.has(e.to)) ids.add(e.from); } }
  if (q) { const keep = new Set([...ids].filter(id => id.toLowerCase().includes(q)));
    for (const e of DATA.edges) { if (keep.has(e.from) && ids.has(e.to)) keep.add(e.to); if (keep.has(e.to) && ids.has(e.from)) keep.add(e.from); }
    ids = keep; }
  const W = canvas.width, H = canvas.height;
  nodes = [...ids].map(id => byId[id]).filter(Boolean).map(n => Object.assign({x: W/2 + (Math.random()-.5)*W*.6, y: H/2 + (Math.random()-.5)*H*.6, vx:0, vy:0}, n));
  const pos = Object.fromEntries(nodes.map(n=>[n.id,n]));
  edges = DATA.edges.filter(e => pos[e.from] && pos[e.to]).map(e => ({...e, a: pos[e.from], b: pos[e.to]}));
  scale=1; ox=0; oy=0; selected=null; document.getElementById('info').textContent = nodes.length + ' nodes, ' + edges.length + ' edges';
  document.getElementById('edges').textContent=''; ticks = 0; loop();
}
let ticks = 0;
function step(){
  const k = 0.012, rep = 2600, W = canvas.width, H = canvas.height;
  for (const n of nodes) { n.vx += (W/2 - n.x) * 0.002; n.vy += (H/2 - n.y) * 0.002; }
  for (let i=0;i<nodes.length;i++) for (let j=i+1;j<nodes.length;j++) {
    const a=nodes[i], b=nodes[j]; let dx=b.x-a.x, dy=b.y-a.y, d2=dx*dx+dy*dy+0.01; if (d2>90000) continue;
    const f = rep/d2; const d=Math.sqrt(d2); dx/=d; dy/=d; a.vx-=dx*f; a.vy-=dy*f; b.vx+=dx*f; b.vy+=dy*f; }
  for (const e of edges) { const dx=e.b.x-e.a.x, dy=e.b.y-e.a.y, d=Math.sqrt(dx*dx+dy*dy)+0.01, f=(d-70)*k; e.a.vx+=dx/d*f; e.a.vy+=dy/d*f; e.b.vx-=dx/d*f; e.b.vy-=dy/d*f; }
  for (const n of nodes) { if (n===drag) continue; n.vx*=0.82; n.vy*=0.82; n.x+=n.vx; n.y+=n.vy; }
}
function draw(){
  const W = canvas.width, H = canvas.height; ctx.setTransform(1,0,0,1,0,0); ctx.clearRect(0,0,W,H); ctx.setTransform(scale,0,0,scale,ox,oy);
  ctx.lineWidth = 1/scale;
  for (const e of edges) { const hi = selected && (e.from===selected.id || e.to===selected.id);
    ctx.strokeStyle = hi ? '#d62728' : '#bbb'; ctx.beginPath(); ctx.moveTo(e.a.x,e.a.y); ctx.lineTo(e.b.x,e.b.y); ctx.stroke();
    if (hi || scale>1.6) { ctx.fillStyle='#666'; ctx.font = (10/scale)+'px sans-serif'; ctx.fillText(e.rel, (e.a.x+e.b.x)/2, (e.a.y+e.b.y)/2); } }
  for (const n of nodes) { const r = n.kind==='context' ? 9 : 5 + Math.min(6, (n.degree||1)/3);
    ctx.fillStyle = COLORS[n.kind] || '#999'; ctx.beginPath(); ctx.arc(n.x,n.y,r,0,7); ctx.fill();
    if (n===selected) { ctx.strokeStyle='#d62728'; ctx.lineWidth=3/scale; ctx.stroke(); ctx.lineWidth=1/scale; }
    if (scale>0.8 || n.kind==='context' || n===selected) { ctx.fillStyle='#222'; ctx.font = (11/scale)+'px sans-serif'; ctx.fillText(n.label, n.x+r+2, n.y+4); } }
}
function loop(){ cancelAnimationFrame(raf); const f=()=>{ if (ticks++ < 400 || drag) step(); draw(); raf=requestAnimationFrame(f); }; f(); }
function resize(){ canvas.width = window.innerWidth-251; canvas.height = window.innerHeight; }
window.addEventListener('resize', ()=>{resize(); draw();}); resize();
function pick(ev){ const x=(ev.offsetX-ox)/scale, y=(ev.offsetY-oy)/scale; return nodes.find(n => (n.x-x)**2+(n.y-y)**2 < 100/scale); }
canvas.addEventListener('mousedown', ev => { const n = pick(ev); if (n) { drag = n; selected = n; show(n); } else drag = {pan:true, x:ev.offsetX, y:ev.offsetY}; });
canvas.addEventListener('mousemove', ev => { if (!drag) return; if (drag.pan) { ox += ev.offsetX-drag.x; oy += ev.offsetY-drag.y; drag.x=ev.offsetX; drag.y=ev.offsetY; } else { drag.x=(ev.offsetX-ox)/scale; drag.y=(ev.offsetY-oy)/scale; ticks=0; } });
window.addEventListener('mouseup', ()=> drag=null);
canvas.addEventListener('wheel', ev => { ev.preventDefault(); const f = ev.deltaY<0 ? 1.15 : 1/1.15; ox = ev.offsetX - (ev.offsetX-ox)*f; oy = ev.offsetY - (ev.offsetY-oy)*f; scale*=f; }, {passive:false});
function show(n){ document.getElementById('info').textContent = `${n.id}\\nkind: ${n.kind}   community: ${n.community}   repo: ${n.repo}\\nlocation: ${n.location||'-'}\\nnote: ${n.note||'-'}\\nrank ${n.rank}  degree ${n.degree}`;
  const out = edges.filter(e => e.from===n.id).map(e => `→ ${e.rel} → ${e.to}`), inn = edges.filter(e => e.to===n.id).map(e => `← ${e.rel} ← ${e.from}`);
  document.getElementById('edges').innerHTML = [...out, ...inn].map(s => `<div>${s}</div>`).join(''); }
sel.onchange = build; filt.oninput = build; ext.onchange = build; build();
</script></body></html>"""

if __name__ == '__main__':
    main()
