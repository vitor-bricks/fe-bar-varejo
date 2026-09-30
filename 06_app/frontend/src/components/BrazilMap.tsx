import { useEffect, useMemo, useState } from 'react';
import { createPortal } from 'react-dom';
import { CircleMarker, GeoJSON, MapContainer, Pane, Polyline, TileLayer, Tooltip, useMap, useMapEvents } from 'react-leaflet';
import { DomEvent, latLngBounds, type LatLngBoundsExpression, type Map as LMap } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './map.css';
import brazil from '../lib/brazil.geo.json';
import type { Route, Store } from '../lib/api';
import { brl, pct } from '../lib/format';

export function healthColor(rate: number) {
  if (rate >= 0.075) return { fill: '#ef4444', ring: 'rgba(239,68,68,0.35)' };
  if (rate >= 0.06) return { fill: '#f59e0b', ring: 'rgba(245,158,11,0.3)' };
  return { fill: '#10b981', ring: 'rgba(16,185,129,0.3)' };
}

// Dark basemap with labels on their own layer (same idea as the reference app). CARTO's basemaps
// now answer "API KEY REQUIRED", so this uses Esri's key-free Dark Gray Canvas.
const ESRI = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas';
const TILES = `${ESRI}/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}`;
const LABELS = `${ESRI}/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}`;
const ATTRIBUTION = 'Tiles &copy; Esri &mdash; Esri, HERE, Garmin, &copy; OpenStreetMap';
const BRASIL: LatLngBoundsExpression = [[-33.8, -73.9], [5.3, -34.8]];

/** Pans to the selected store when it is off-screen (e.g. picked in the ranking while zoomed in). */
function FollowSelection({ focus }: { focus: [number, number] | null }) {
  const map = useMap();
  useEffect(() => {
    if (focus && !map.getBounds().pad(-0.08).contains(focus)) map.flyTo(focus, Math.max(map.getZoom(), 6), { duration: 0.8 });
  }, [focus?.[0], focus?.[1]]); // eslint-disable-line react-hooks/exhaustive-deps
  return null;
}

/** Store names next to the bubbles, placed greedily so they never overlap a bubble or each other
 *  (selected store first, then by R$ at risk); names that do not fit are left to the hover tooltip.
 *  They live in their own map pane: above the bubbles, BELOW the hover tooltips, and they travel with
 *  the map while dragging. Re-placed after each move, hidden during the zoom animation. */
function StoreLabels({ stores, selected, radius, onSelect }: { stores: Store[]; selected?: string | null; radius: (s: Store) => number; onSelect: (id: string) => void }) {
  const map = useMap();
  const pane = useMemo(() => {
    const el = map.getPane('storeLabels') ?? map.createPane('storeLabels');
    el.style.zIndex = '620';            // markers 600 < labels < tooltips 650
    el.style.pointerEvents = 'none';
    DomEvent.disableClickPropagation(el);
    return el;
  }, [map]);
  const [, redraw] = useState(0);
  const [zooming, setZooming] = useState(false);
  useMapEvents({ moveend: () => redraw((n) => n + 1), zoomstart: () => setZooming(true), zoomend: () => { setZooming(false); redraw((n) => n + 1); }, resize: () => redraw((n) => n + 1) });
  if (zooming) return null;
  const { x: W, y: H } = map.getSize();
  type Box = { x0: number; y0: number; x1: number; y1: number };
  const pts = stores.map((s) => ({ s, p: map.latLngToContainerPoint([s.lat, s.lon]), r: radius(s) }));
  const taken: Box[] = pts.map(({ p, r }) => ({ x0: p.x - r - 2, y0: p.y - r - 2, x1: p.x + r + 2, y1: p.y + r + 2 }));
  const free = (b: Box) => b.x0 > 4 && b.y0 > 4 && b.x1 < W - 4 && b.y1 < H - 4 && !taken.some((o) => b.x0 < o.x1 && b.x1 > o.x0 && b.y0 < o.y1 && b.y1 > o.y0);
  const order = [...pts].sort((a, b) => (a.s.store_id === selected ? -1 : b.s.store_id === selected ? 1 : b.s.revenue_at_risk - a.s.revenue_at_risk));
  const labels: { id: string; text: string; x: number; y: number; sel: boolean }[] = [];
  for (const { s, p, r } of order) {
    const text = s.store_name.replace('LojaBR ', ''), sel = s.store_id === selected;
    const w = text.length * (sel ? 7 : 6.3) + 6, h = 15, g = r + 5;
    const spots = [[p.x + g, p.y - h / 2], [p.x - g - w, p.y - h / 2], [p.x - w / 2, p.y - g - h], [p.x - w / 2, p.y + g]];
    for (const [x, y] of spots) {
      const b = { x0: x, y0: y, x1: x + w, y1: y + h };
      if (free(b)) { taken.push(b); const lp = map.containerPointToLayerPoint([x, y]); labels.push({ id: s.store_id, text, x: lp.x, y: lp.y, sel }); break; }
    }
  }
  return createPortal(
    <>
      {labels.map((l) => (
        <button key={l.id} onClick={() => onSelect(l.id)} style={{ left: l.x, top: l.y }}
          className={`absolute pointer-events-auto whitespace-nowrap leading-[15px] px-[3px] tracking-[0.01em] [text-shadow:0_0_2px_#09090b,0_0_5px_#09090b,0_0_9px_#09090b] ${
            l.sel ? 'text-[12px] font-semibold text-amber-200' : 'text-[11px] font-medium text-zinc-300 hover:text-amber-200'}`}>
          {l.text}
        </button>
      ))}
    </>,
    pane,
  );
}

export default function BrazilMap({ stores, routes, selected, onSelect }: {
  stores: Store[]; routes: Route[]; selected?: string | null; onSelect: (id: string) => void;
}) {
  const [map, setMap] = useState<LMap | null>(null);
  const byId = useMemo(() => Object.fromEntries(stores.map((s) => [s.store_id, s])), [stores]);
  const maxRisk = Math.max(1, ...stores.map((s) => s.revenue_at_risk));
  const radius = (s: Store) => 5 + 10 * Math.sqrt(s.revenue_at_risk / maxRisk);
  const sudeste = useMemo(() => latLngBounds(stores.filter((s) => s.region === 'Sudeste').map((s) => [s.lat, s.lon] as [number, number])), [stores]);
  const sel = selected ? byId[selected] : null;
  // draw the biggest bubbles first so small ones stay clickable on top; the selected store last
  const ordered = [...stores].sort((a, b) => (a.store_id === selected ? 1 : b.store_id === selected ? -1 : b.revenue_at_risk - a.revenue_at_risk));

  return (
    <>
    <div className="relative h-[560px] xl:h-[740px]">
      <MapContainer ref={setMap} className="lb-map h-full w-full" bounds={BRASIL} boundsOptions={{ padding: [36, 36] }} scrollWheelZoom={false}
        minZoom={3} maxZoom={12} zoomSnap={0.25} zoomDelta={0.5} worldCopyJump={false}>
        {/* fallback outline under the tiles: only visible if the basemap cannot load */}
        <Pane name="fallback" style={{ zIndex: 150 }}>
          <GeoJSON data={brazil as any} style={{ color: '#3f3f46', weight: 1, fillColor: '#27272a', fillOpacity: 1 }} interactive={false} />
        </Pane>
        <TileLayer url={TILES} attribution={ATTRIBUTION} maxNativeZoom={16} />
        {/* place names above the land, below the stores (overlay pane = 400). Hidden at country
            zoom, where the store bubbles already mark the cities and would cut the names in half. */}
        <Pane name="labels" style={{ zIndex: 350, pointerEvents: 'none' }}>
          <TileLayer url={LABELS} maxNativeZoom={16} minZoom={6} opacity={0.8} />
        </Pane>

        {routes.map((r) => {
          const a = byId[r.from_id], b = byId[r.store_id];
          if (!a || !b) return null;
          const done = r.decision === 'APPROVED';
          const mine = !!selected && (r.store_id === selected || r.from_id === selected);
          return (
            // className must be a top-level prop: react-leaflet only applies pathOptions through setStyle
            <Polyline key={`${r.action_id}-${done}`} positions={[[a.lat, a.lon], [b.lat, b.lon]]} interactive={false}
              className={done ? undefined : 'route-flow'}
              pathOptions={{ color: done ? '#34d399' : '#fbbf24', weight: done ? 2.5 : mine ? 2.2 : 1.4,
                opacity: done ? 0.95 : selected && !mine ? 0.28 : 0.75 }} />
          );
        })}

        {ordered.map((s) => {
          const c = healthColor(s.stockout_rate_7d);
          const r = radius(s);
          const isSel = s.store_id === selected;
          return [
            <CircleMarker key={`${s.store_id}-halo`} center={[s.lat, s.lon]} radius={r + 6} interactive={false}
              pathOptions={{ stroke: false, fillColor: c.fill, fillOpacity: isSel ? 0.35 : 0.18 }} />,
            isSel && <CircleMarker key={`${s.store_id}-pulse`} center={[s.lat, s.lon]} radius={r + 4} interactive={false}
              className="lb-pulse" pathOptions={{ color: '#fde68a', fill: false }} />,
            <CircleMarker key={`${s.store_id}-${isSel}`} center={[s.lat, s.lon]} radius={r} eventHandlers={{ click: () => onSelect(s.store_id) }}
              pathOptions={{ color: isSel ? '#fde68a' : '#09090b', weight: isSel ? 2.5 : 1.2, fillColor: c.fill, fillOpacity: 0.9 }}>
              {!isSel && (
                <Tooltip direction="top" offset={[0, -r - 2]} className="lb-tip" opacity={1}>
                  <div className="text-[12.5px] font-semibold text-zinc-100">{s.store_name}</div>
                  <div className="text-[11px] text-zinc-500">{s.city} · {s.uf} · {s.store_format}</div>
                  <div className="mt-2 flex gap-5 text-[9.5px] uppercase tracking-[0.14em] text-zinc-500">
                    <span>ruptura 7d<b className="block font-mono text-[12px] normal-case tracking-normal text-zinc-100">{pct(s.stockout_rate_7d)}</b></span>
                    <span>em risco<b className="block font-mono text-[12px] normal-case tracking-normal text-amber-300">{brl(s.revenue_at_risk)}</b></span>
                    <span>na fila<b className="block font-mono text-[12px] normal-case tracking-normal text-zinc-100">{s.queue_n} ações</b></span>
                  </div>
                </Tooltip>
              )}
            </CircleMarker>,
          ];
        })}
        <FollowSelection focus={sel ? [sel.lat, sel.lon] : null} />
        <StoreLabels stores={stores} selected={selected} radius={radius} onSelect={onSelect} />
      </MapContainer>

      {/* view presets (replace the old static Sudeste inset: the map itself zooms). They move the
          camera on every click, so they still work after the user has dragged or zoomed. */}
      <div className="absolute right-3 top-3 z-[1000] flex gap-1 rounded-lg border border-zinc-700 bg-zinc-950/90 p-1 shadow-xl">
        {([['Brasil', BRASIL], [`Sudeste · ${stores.filter((s) => s.region === 'Sudeste').length} lojas`, sudeste]] as const).map(([label, b]) => (
          <button key={label} onClick={() => map?.flyToBounds(b, { padding: [36, 36], duration: 0.8 })}
            className="px-3 py-1.5 rounded-md text-[10.5px] font-bold uppercase tracking-[0.16em] text-zinc-300 hover:bg-amber-400/15 hover:text-amber-300 transition-colors">
            {label}
          </button>
        ))}
      </div>

    </div>
    {/* legend below the map, so it never covers a store */}
    <div className="flex flex-wrap items-center gap-x-5 gap-y-1.5 px-5 py-3 border-t border-zinc-800 text-[10.5px] text-zinc-400">
      <span className="text-[9.5px] uppercase tracking-[0.2em] text-zinc-500 font-semibold">Legenda</span>
      <span className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> ruptura 7d &lt; 6%</span>
      <span className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> 6% – 7,5%</span>
      <span className="flex items-center gap-2"><span className="w-2.5 h-2.5 rounded-full bg-red-500" /> ≥ 7,5% · em alerta</span>
      <span className="flex items-center gap-2"><span className="w-4 border-t-2 border-dashed border-amber-400" /> transferência sugerida</span>
      <span className="flex items-center gap-2"><span className="w-4 border-t-2 border-emerald-400" /> aprovada</span>
      <span className="text-zinc-600">tamanho = R$ em risco (7 dias)</span>
    </div>
    </>
  );
}
