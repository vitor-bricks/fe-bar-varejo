import { useMemo, useState } from 'react';
import { geoMercator, geoPath } from 'd3-geo';
import brazil from '../lib/brazil.geo.json';
import type { Route, Store } from '../lib/api';
import { brl, pct } from '../lib/format';

const W = 720, H = 640;

export function healthColor(rate: number) {
  if (rate >= 0.075) return { fill: '#ef4444', ring: 'rgba(239,68,68,0.35)' };
  if (rate >= 0.06) return { fill: '#f59e0b', ring: 'rgba(245,158,11,0.3)' };
  return { fill: '#10b981', ring: 'rgba(16,185,129,0.3)' };
}


const IW = 700, IH = 330;
/** Zoomed view of the dense Sudeste cluster (São Paulo / Rio / BH), with every store labelled. */
function SudesteInset({ stores, routes, selected, onSelect }: { stores: Store[]; routes: Route[]; selected?: string | null; onSelect: (id: string) => void }) {
  const sud = stores.filter((s) => s.region === 'Sudeste');
  const { path, pts, labels } = useMemo(() => {
    const proj = geoMercator().fitExtent([[90, 34], [IW - 90, IH - 30]], { type: 'MultiPoint', coordinates: sud.map((s) => [s.lon, s.lat]) } as any);
    const maxRisk = Math.max(1, ...sud.map((s) => s.revenue_at_risk));
    const placed: { id: string; x: number; y: number; r: number; s: Store }[] = [];
    [...sud].sort((a, b) => b.revenue_at_risk - a.revenue_at_risk).forEach((s) => {
      let [x, y] = proj([s.lon, s.lat]) as [number, number];
      const r = 6 + 10 * Math.sqrt(s.revenue_at_risk / maxRisk);
      for (let k = 0; k < 10; k++) {
        const hit = placed.find((p) => Math.hypot(p.x - x, p.y - y) < p.r + r + 3);
        if (!hit) break;
        const ang = (k * 137.5 * Math.PI) / 180;
        x = hit.x + Math.cos(ang) * (hit.r + r + 4); y = hit.y + Math.sin(ang) * (hit.r + r + 4);
      }
      placed.push({ id: s.store_id, x, y, r, s });
    });
    // greedy label placement: try 8 spots around the bubble; if all collide, push out with a leader line
    type Box = { x0: number; y0: number; x1: number; y1: number };
    const boxes: Box[] = placed.map((p) => ({ x0: p.x - p.r, y0: p.y - p.r, x1: p.x + p.r, y1: p.y + p.r }));
    const hit = (b: Box) => b.x0 < 2 || b.x1 > IW - 2 || b.y0 < 18 || b.y1 > IH - 2 || boxes.some((o) => b.x0 < o.x1 && b.x1 > o.x0 && b.y0 < o.y1 && b.y1 > o.y0);
    type Label = { id: string; text: string; tx: number; ty: number; anchor: 'start' | 'end' | 'middle'; leader: boolean; ax: number; ay: number; lx: number; ly: number };
    const labels = placed.map((p): Label => {
      const text = p.s.store_name.replace('LojaBR ', '');
      const w = text.length * 6.9, h = 14, g = p.r + 4;
      const spots: [number, number, 'start' | 'end' | 'middle'][] = [
        [p.x + g, p.y + 4, 'start'], [p.x - g, p.y + 4, 'end'], [p.x, p.y - g - 2, 'middle'], [p.x, p.y + g + 11, 'middle'],
        [p.x + g, p.y - g, 'start'], [p.x + g, p.y + g + 8, 'start'], [p.x - g, p.y - g, 'end'], [p.x - g, p.y + g + 8, 'end']];
      const boxOf = (tx: number, ty: number, a: string): Box => {
        const x0 = a === 'start' ? tx : a === 'end' ? tx - w : tx - w / 2;
        return { x0, y0: ty - 11, x1: x0 + w, y1: ty + 3 };
      };
      for (const [tx, ty, anchor] of spots) {
        const b = boxOf(tx, ty, anchor);
        if (!hit(b)) { boxes.push(b); return { id: p.id, text, tx, ty, anchor, leader: false, ax: 0, ay: 0, lx: 0, ly: 0 }; }
      }
      for (let k = 1; k < 30; k++) {           // spiral outwards until free, then draw a leader line
        const ang = (k * 47 * Math.PI) / 180, d = g + 10 + k * 5;
        const tx = p.x + Math.cos(ang) * d, ty = p.y + Math.sin(ang) * d;
        const anchor: 'start' | 'end' = Math.cos(ang) >= 0 ? 'start' : 'end';
        const b = boxOf(tx, ty, anchor);
        if (!hit(b)) { boxes.push(b); return { id: p.id, text, tx, ty, anchor, leader: true, ax: p.x, ay: p.y, lx: tx, ly: ty - 4 }; }
      }
      return { id: p.id, text, tx: p.x + g, ty: p.y + 4, anchor: 'start' as const, leader: false, ax: 0, ay: 0, lx: 0, ly: 0 };
    });
    return { path: geoPath(proj)(brazil as any) || '', pts: Object.fromEntries(placed.map((p) => [p.id, p])), labels };
  }, [stores]);
  return (
    <div className="mt-4 rounded-lg border border-zinc-800 bg-zinc-950/70 overflow-hidden">
      <div className="px-3 pt-2.5 text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-semibold">zoom · Sudeste · {sud.length} lojas · clique para abrir</div>
      <svg viewBox={`0 0 ${IW} ${IH}`} className="w-full h-auto">
        <defs><clipPath id="inset-clip"><rect width={IW} height={IH} /></clipPath></defs>
        <path d={path} fill="#1c1c20" stroke="#3f3f46" strokeWidth={1} clipPath="url(#inset-clip)" />
        {routes.map((r) => {
          const a = pts[r.from_id], b = pts[r.store_id];
          if (!a || !b) return null;
          const done = r.decision === 'APPROVED';
          return <line key={r.action_id} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={done ? '#34d399' : '#fbbf24'} strokeOpacity={done ? 0.9 : 0.5} strokeWidth={done ? 1.8 : 1.1} className={done ? '' : 'route-flow'} />;
        })}
        {Object.values(pts).map(({ id, x, y, r, s }) => {
          const c = healthColor(s.stockout_rate_7d); const sel = selected === id;
          return <circle key={id} onClick={() => onSelect(id)} className="cursor-pointer" cx={x} cy={y} r={r} fill={c.fill} fillOpacity={0.9} stroke={sel ? '#fde68a' : '#09090b'} strokeWidth={sel ? 2 : 1} />;
        })}
        {labels.map((l) => (
          <g key={l.id} onClick={() => onSelect(l.id)} className="cursor-pointer">
            {l.leader && <line x1={l.ax} y1={l.ay} x2={l.lx} y2={l.ly} stroke="#52525b" strokeWidth={0.8} />}
            <text x={l.tx} y={l.ty} textAnchor={l.anchor} fill={selected === l.id ? '#fde68a' : '#a1a1aa'} fontSize={12.5} fontWeight={selected === l.id ? 700 : 500}>{l.text}</text>
          </g>
        ))}
      </svg>
    </div>
  );
}

export default function BrazilMap({ stores, routes, selected, onSelect }: {
  stores: Store[]; routes: Route[]; selected?: string | null; onSelect: (id: string) => void;
}) {
  const [hover, setHover] = useState<string | null>(null);
  const { path, pts } = useMemo(() => {
    const proj = geoMercator().fitExtent([[20, 20], [W - 20, H - 20]], brazil as any);
    const path = geoPath(proj)(brazil as any) || '';
    const maxRisk = Math.max(1, ...stores.map((s) => s.revenue_at_risk));
    // project, then nudge stores that would sit on top of each other (São Paulo, Rio clusters)
    const placed: { id: string; x: number; y: number; r: number; s: Store }[] = [];
    [...stores].sort((a, b) => b.revenue_at_risk - a.revenue_at_risk).forEach((s) => {
      let [x, y] = proj([s.lon, s.lat]) as [number, number];
      const r = 4 + 9 * Math.sqrt(s.revenue_at_risk / maxRisk);
      for (let k = 0; k < 12; k++) {
        const hit = placed.find((p) => Math.hypot(p.x - x, p.y - y) < p.r + r + 2);
        if (!hit) break;
        const ang = (k * 137.5 * Math.PI) / 180;
        x = hit.x + Math.cos(ang) * (hit.r + r + 3);
        y = hit.y + Math.sin(ang) * (hit.r + r + 3);
      }
      placed.push({ id: s.store_id, x, y, r, s });
    });
    return { path, pts: Object.fromEntries(placed.map((p) => [p.id, p])) };
  }, [stores]);

  const tip = hover ? pts[hover] : null;

  return (
    <>
    <div className="relative">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto">
        <defs>
          <radialGradient id="land" cx="45%" cy="40%" r="75%">
            <stop offset="0%" stopColor="#27272a" /><stop offset="100%" stopColor="#18181b" />
          </radialGradient>
        </defs>
        <path d={path} fill="url(#land)" stroke="#3f3f46" strokeWidth={1} />
        {routes.map((r) => {
          const a = pts[r.from_id], b = pts[r.store_id];
          if (!a || !b) return null;
          const done = r.decision === 'APPROVED';
          return (
            <line key={r.action_id} x1={a.x} y1={a.y} x2={b.x} y2={b.y}
              stroke={done ? '#34d399' : '#fbbf24'} strokeOpacity={done ? 0.9 : 0.55} strokeWidth={done ? 2 : 1.4}
              className={done ? '' : 'route-flow'} />
          );
        })}
        {Object.values(pts).map(({ id, x, y, r, s }) => {
          const c = healthColor(s.stockout_rate_7d);
          const sel = selected === id;
          return (
            <g key={id} onMouseEnter={() => setHover(id)} onMouseLeave={() => setHover(null)} onClick={() => onSelect(id)} className="cursor-pointer">
              <circle cx={x} cy={y} r={r + 6} fill={c.ring} opacity={sel || hover === id ? 1 : 0.55} />
              <circle cx={x} cy={y} r={r} fill={c.fill} fillOpacity={0.85} stroke={sel ? '#fde68a' : '#09090b'} strokeWidth={sel ? 2.5 : 1.2} />
              {(hover === id || (sel && s.region !== 'Sudeste')) && (
                <text x={x + r + 6} y={y + 4} fill="#d4d4d8" fontSize={12} fontWeight={600} className="pointer-events-none">{s.store_name.replace('LojaBR ', '')}</text>
              )}
            </g>
          );
        })}
      </svg>
      {tip && (
        <div className="absolute pointer-events-none rounded-lg border border-zinc-700 bg-zinc-950/95 px-3 py-2 text-[11.5px] shadow-xl"
          style={{ left: `${(tip.x / W) * 100}%`, top: `${(tip.y / H) * 100}%`, transform: 'translate(12px, -110%)' }}>
          <div className="text-zinc-100 font-semibold">{tip.s.store_name}</div>
          <div className="text-zinc-500">{tip.s.city} · {tip.s.uf} · {tip.s.store_format}</div>
          <div className="mt-1 font-mono text-zinc-300">ruptura 7d {pct(tip.s.stockout_rate_7d)} · em risco {brl(tip.s.revenue_at_risk)}</div>
          <div className="font-mono text-zinc-400">{tip.s.queue_n} ações na fila</div>
        </div>
      )}
      <div className="absolute left-3 bottom-3 rounded-lg border border-zinc-800 bg-zinc-950/90 px-3 py-2 text-[10.5px] text-zinc-400 space-y-1">
        <div className="text-[9.5px] uppercase tracking-[0.2em] text-zinc-500 font-semibold mb-1">Legenda</div>
        <div className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> ruptura 7d &lt; 6%</div>
        <div className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> 6% – 7,5%</div>
        <div className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-red-500" /> ≥ 7,5% · em alerta</div>
        <div className="flex items-center gap-2"><span className="w-4 border-t-2 border-dashed border-amber-400" /> transferência sugerida</div>
        <div className="flex items-center gap-2"><span className="w-4 border-t-2 border-emerald-400" /> transferência aprovada</div>
        <div className="text-zinc-600">tamanho = R$ em risco (7 dias)</div>
      </div>
    </div>
    <SudesteInset stores={stores} routes={routes} selected={selected} onSelect={onSelect} />
    </>
  );
}
