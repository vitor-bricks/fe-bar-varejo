/**
 * diagrams.tsx — GENERIC, data-driven versions of the three architecture
 * diagrams from the reference demo. This is the heart of the template: the
 * three original components (IngestionFlow / AgentLoopFlow / PlatformDiagram)
 * had their narrative HARDCODED in JSX. Here that narrative is lifted into
 * props, so a new app renders its own story by passing a spec — no SVG or
 * layout editing.
 *
 * Depends on the sibling files (copy all three into the app):
 *   - ./Flow      → Stage, Connector, Fork, FlowKeyframes  (primitives)
 *   - ./icons     → the Databricks product icon set
 *   - theme.css   → the CSS vars (--foreground, --accent, …) these read
 *
 * Three exports:
 *   <Pipeline steps=[…] />                 → horizontal A → B → C flow strip
 *   <AgentLoop … />                        → operator → analysis → propose → fork
 *   <PlatformStack rows=[…] sources=[…] /> → the layered platform panel
 *
 * Every icon is passed in by the caller (import what you need from ./icons,
 * or pass a custom SVG), so the diagrams are not tied to any one product set.
 */

import { useEffect, useState, type ReactNode } from 'react';
import { Connector, FlowKeyframes, Fork, Stage } from './Flow';
import { RtBadge } from './icons';

/* ──────────────────────────────────────────────────────────────────────────
 * 1. <Pipeline> — a horizontal "A → B → C → …" flow strip.
 *    Reference: IngestionFlow (Data → Zerobus → Pipeline → Lakebase → App).
 *    Generic: pass any ordered list of steps. First step can be `bare` (no
 *    white tile) to read as raw input. Optional lead-in caption above.
 * ──────────────────────────────────────────────────────────────────────── */

export type PipelineStep = {
  icon: ReactNode;
  /** bold one-liner under the tile */
  name: string;
  /** muted mono sub-line under the name */
  sub?: string;
  /** render the icon with no white tile (raw-input look). Usually only step 0. */
  bare?: boolean;
};

export function Pipeline({
  steps,
  caption,
  tileSize = 44,
  iconSize = 30,
  connectorWidth = 48,
}: {
  steps: PipelineStep[];
  /** optional caption rendered above the strip; ReactNode so you can bold words */
  caption?: ReactNode;
  tileSize?: number;
  iconSize?: number;
  connectorWidth?: number;
}) {
  return (
    <section
      className="rounded-xl border border-border bg-card p-4 sm:p-5"
      aria-label="Pipeline flow"
    >
      <FlowKeyframes />
      {caption && (
        <p className="text-sm text-muted-foreground mb-3 leading-relaxed">{caption}</p>
      )}
      {/* overflowX:auto lets a wide strip scroll horizontally on narrow
          screens; overflowY:hidden + paddingBottom stops the browser from
          also showing a spurious VERTICAL scrollbar (overflow-x:auto forces
          overflow-y to compute as auto, and Stage renders its labels ~34px
          BELOW the tile via position:absolute — that would overflow). */}
      <div style={{ overflowX: 'auto', overflowY: 'hidden', paddingTop: 8, paddingBottom: 44 }}>
        <div className="inline-flex items-start justify-center" style={{ gap: 2, minWidth: '100%' }}>
          {steps.map((s, i) => (
            <FlowSegment key={i} first={i === 0} width={connectorWidth}>
              <Stage
                bare={s.bare}
                icon={s.icon}
                name={s.name}
                sub={s.sub}
                tileSize={tileSize}
                iconSize={iconSize}
              />
            </FlowSegment>
          ))}
        </div>
      </div>
    </section>
  );
}

/** Prepends a <Connector> before every segment except the first. */
function FlowSegment({
  first,
  width,
  children,
}: {
  first: boolean;
  width: number;
  children: ReactNode;
}) {
  return (
    <>
      {!first && <Connector width={width} />}
      {children}
    </>
  );
}

/* ──────────────────────────────────────────────────────────────────────────
 * 1b. <TrainingLoop> — a horizontal flow strip that CLOSES BACK on itself with
 *     a labeled return arc over the top. Not in the reference set — composed
 *     from the same <Stage> primitive plus a bespoke SVG arc, to show the
 *     primitives generalize to closed-loop (MLOps / feedback) architectures.
 *
 *     e.g. Features → Train → Registry → Serving → Monitor  ⟲ retrain
 * ──────────────────────────────────────────────────────────────────────── */

export function TrainingLoop({
  steps,
  caption,
  loopLabel = 'retrain on drift',
  tileSize = 46,
  iconSize = 30,
  gap = 66,
}: {
  steps: PipelineStep[];
  caption?: ReactNode;
  /** text shown on the return arc that loops from last stage back to first */
  loopLabel?: string;
  tileSize?: number;
  iconSize?: number;
  /** horizontal gap between stages (px) */
  gap?: number;
}) {
  return (
    <section className="rounded-xl border border-border bg-card p-4 sm:p-6" aria-label="Training feedback loop">
      <FlowKeyframes />
      {caption && <p className="text-sm text-muted-foreground mb-3 leading-relaxed">{caption}</p>}
      <style>{`
        @keyframes tl-arc-dot { 0%{opacity:0} 10%{opacity:1} 90%{opacity:1} 100%{opacity:0} }
        .tl-arc-dot{fill:${'#EF5B3F'};filter:drop-shadow(0 0 4px #EF5B3F);animation:tl-arc-dot 3s linear infinite}
      `}</style>
      {/* extra top padding leaves room for the return arc */}
      <div className="flex justify-center" style={{ marginTop: 34, marginBottom: 40 }}>
        <div className="relative inline-flex items-start" style={{ gap }}>
          {/* the return arc: spans the full width, rises above the row */}
          <ReturnArc label={loopLabel} />
          {steps.map((s, i) => (
            <div key={i} style={{ position: 'relative' }}>
              {i > 0 && (
                <span
                  aria-hidden
                  style={{ position: 'absolute', top: tileSize / 2 - 4, right: '100%', width: gap, height: 8,
                    ['--db-flow-w' as string]: `${gap}px` }}
                >
                  <svg viewBox={`0 0 ${gap} 8`} preserveAspectRatio="none" width={gap} height={8} style={{ overflow: 'visible' }}>
                    <line x1="0" y1="4" x2={gap} y2="4" style={{ stroke: 'var(--muted-foreground)', strokeWidth: 1.4, opacity: 0.5 }} />
                    <circle className="db-flow-dot-animate" cx="0" cy="4" r="2.4" />
                  </svg>
                </span>
              )}
              <Stage bare={s.bare} icon={s.icon} name={s.name} sub={s.sub} tileSize={tileSize} iconSize={iconSize} />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/** The curved return arc drawn above a TrainingLoop, last stage → first, with
 *  a centered label and an animated dot riding the curve. */
function ReturnArc({ label }: { label: string }) {
  return (
    <div aria-hidden style={{ position: 'absolute', left: 0, right: 0, top: -30, height: 40, pointerEvents: 'none' }}>
      <svg width="100%" height="40" viewBox="0 0 100 40" preserveAspectRatio="none" style={{ overflow: 'visible' }}>
        <path id="tl-arc" d="M97 34 C97 6 3 6 3 34" fill="none"
              stroke="var(--accent)" strokeWidth="1.4" strokeDasharray="4 3" opacity="0.7"
              vectorEffect="non-scaling-stroke" />
        {/* arrowhead landing on the first stage */}
        <path d="M3 34 l3 -5 M3 34 l4 1" stroke="var(--accent)" strokeWidth="1.4" fill="none"
              vectorEffect="non-scaling-stroke" />
        <circle className="tl-arc-dot" r="2.6"><animateMotion dur="3s" repeatCount="indefinite"><mpath href="#tl-arc" /></animateMotion></circle>
      </svg>
      <div style={{ position: 'absolute', top: -4, left: '50%', transform: 'translateX(-50%)',
        font: "600 10px 'DM Mono', monospace", letterSpacing: '.12em', textTransform: 'uppercase',
        color: 'var(--accent)', background: 'var(--card)', padding: '0 8px', whiteSpace: 'nowrap' }}>
        ⟲ {label}
      </div>
    </div>
  );
}

/* ──────────────────────────────────────────────────────────────────────────
 * 2. <AgentLoop> — operator → [analysis box] → propose → fork{ outcomes }.
 *    Reference: AgentLoopFlow ("How the agent works").
 *    Generic: the operator label, the analysis-box rows, the propose label,
 *    the two fork outcomes, and the "governed by" chips are all props.
 * ──────────────────────────────────────────────────────────────────────── */

export type LabeledIcon = { icon: ReactNode; label: string; sub?: string };

export function AgentLoop({
  kicker = 'How the agent works',
  intro,
  operator,
  analysisTitle = 'Agentic analysis',
  analysis,
  propose,
  outcomes,
  governedBy,
}: {
  kicker?: string;
  /** intro paragraph; ReactNode so you can bold words */
  intro: ReactNode;
  operator: { name: string; sub?: string; icon: ReactNode };
  analysisTitle?: string;
  /** the stacked mini-tiles inside the analysis box (e.g. Agent Bricks / Genie / Lakebase) */
  analysis: LabeledIcon[];
  propose: { name: string; sub?: string; icon: ReactNode };
  /** exactly two outcomes → top + bottom fork branches */
  outcomes: [{ name: string; sub?: string; icon: ReactNode }, { name: string; sub?: string; icon: ReactNode }];
  /** optional footer chips, e.g. Unity Catalog + AI Gateway */
  governedBy?: LabeledIcon[];
}) {
  return (
    <section className="rounded-xl border border-border bg-card p-5 sm:p-6 overflow-hidden">
      <FlowKeyframes />

      <div className="flex items-center gap-2 mb-1">
        <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
          {kicker}
        </span>
      </div>
      <p className="text-sm text-muted-foreground leading-relaxed mb-5">{intro}</p>

      {/* desktop */}
      <div className="hidden md:flex items-center justify-center" style={{ gap: 0, paddingTop: 8, paddingBottom: 34, overflowX: 'auto', overflowY: 'hidden' }}>
        <Stage tileSize={50} iconSize={32} icon={operator.icon} name={operator.name} sub={operator.sub} />
        <Connector width={56} centered />

        <div
          className="rounded-xl border bg-background"
          style={{ display: 'flex', flexDirection: 'column', gap: 8, padding: '12px 14px', borderColor: 'var(--border)' }}
        >
          <div className="text-[10.5px] font-mono uppercase tracking-[0.16em] text-muted-foreground">
            {analysisTitle}
          </div>
          {analysis.map((a, i) => (
            <MiniTile key={i} icon={a.icon} label={a.label} />
          ))}
        </div>

        <Connector width={56} centered />
        <Stage tileSize={50} iconSize={32} icon={propose.icon} name={propose.name} sub={propose.sub} />
        {/* 172px column: tall enough that the TOP outcome's sub-label clears
            the BOTTOM tile (≈ 2·tileSize + 70). Fork height matches. */}
        <Fork height={172} tileSize={50} idPrefix="db-fork-agent" />
        <div className="flex flex-col" style={{ height: 172, justifyContent: 'space-between', flexShrink: 0 }}>
          <Stage tileSize={50} iconSize={32} icon={outcomes[0].icon} name={outcomes[0].name} sub={outcomes[0].sub} />
          <Stage tileSize={50} iconSize={32} icon={outcomes[1].icon} name={outcomes[1].name} sub={outcomes[1].sub} />
        </div>
      </div>

      {/* mobile: stacked, no animated connectors */}
      <ol className="md:hidden flex flex-col gap-3 mt-2 mb-2">
        <MobileStep icon={operator.icon} label={operator.name} sub={operator.sub} />
        <li className="rounded-xl border border-border bg-background p-3 flex flex-col gap-2">
          <div className="text-[10.5px] font-mono uppercase tracking-[0.16em] text-muted-foreground">{analysisTitle}</div>
          {analysis.map((a, i) => (
            <MiniTile key={i} icon={a.icon} label={a.label} />
          ))}
        </li>
        <MobileStep icon={propose.icon} label={propose.name} sub={propose.sub} />
        <MobileStep icon={outcomes[0].icon} label={outcomes[0].name} sub={outcomes[0].sub} />
        <MobileStep icon={outcomes[1].icon} label={outcomes[1].name} sub={outcomes[1].sub} />
      </ol>

      {governedBy && governedBy.length > 0 && (
        <div className="flex flex-wrap items-center justify-center gap-3 sm:gap-6 mt-1 pt-2 border-t border-border">
          <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            Governed by
          </span>
          {governedBy.map((g, i) => (
            <span key={i} className="inline-flex items-center gap-1.5">
              <span style={{ width: 22, height: 22 }}>{g.icon}</span>
              <span className="text-sm font-semibold">{g.label}</span>
            </span>
          ))}
        </div>
      )}
    </section>
  );
}

function MiniTile({ icon, label }: { icon: ReactNode; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <div
        className="grid place-items-center"
        style={{ width: 38, height: 38, borderRadius: 9, background: '#fff', boxShadow: '0 2px 8px rgba(0,0,0,.15)' }}
      >
        <div style={{ width: 28, height: 28 }}>{icon}</div>
      </div>
      <span className="text-[13px] font-semibold text-foreground whitespace-nowrap">{label}</span>
    </div>
  );
}

function MobileStep({ icon, label, sub }: { icon: ReactNode; label: string; sub?: string }) {
  return (
    <li className="flex items-center gap-3">
      <div
        className="grid place-items-center shrink-0"
        style={{ width: 40, height: 40, borderRadius: 10, background: '#fff', boxShadow: '0 2px 10px rgba(0,0,0,.18)' }}
      >
        <div style={{ width: 26, height: 26 }}>{icon}</div>
      </div>
      <div className="text-sm font-semibold">
        {label}
        {sub && <span className="font-normal text-muted-foreground"> {sub}</span>}
      </div>
    </li>
  );
}

/* ──────────────────────────────────────────────────────────────────────────
 * 3. <PlatformStack> — the layered "Running X on the Databricks Platform"
 *    panel. Reference: PlatformDiagram.
 *    Generic: hero text, the layer rows, and the datasource strip are props.
 *    Each product tile takes an optional `resourceKey` — if the resources map
 *    (from /api/resources) has a non-empty url for that key, the tile becomes
 *    a clickable "glowing dot" deep-link; otherwise it renders inert.
 *
 *    Pass `resources` yourself (fetch once at a higher level) OR let the
 *    component fetch `/api/resources` itself by passing `fetchResources`.
 * ──────────────────────────────────────────────────────────────────────── */

export type ResourceMap = Record<string, { id: string; url: string }>;

export type PlatformProduct = {
  icon: ReactNode;
  title: string;
  sub: string;
  /** key into the ResourceMap; when its url is non-empty the tile deep-links */
  resourceKey?: string;
  /** show the ⚡RT badge next to the title */
  rt?: boolean;
  /** extra chips/nodes rendered inline after the title (e.g. ONE / AGENTS / CODE) */
  after?: ReactNode;
  /** replace the `sub` line with medallion-style stage labels, e.g.
   *  ['bronze','silver','gold'] renders "bronze › silver › gold" in mono. */
  medallion?: string[];
};

export type PlatformRow = {
  title: string;
  sub: string;
  tint?: 'orange' | 'navy';
  products: PlatformProduct[];
  /** Layout of the products area:
   *  - undefined/'flat' → tiles laid out in a row (or 2-col grid if exactly 2)
   *  - 'fork' → first product on the left, a Y-fork, then the remaining
   *    products stacked on the right (the pipeline visibly serves both stores).
   *    Matches the reference "Agentic Data" row (Lakeflow → Lakehouse+Lakebase). */
  layout?: 'flat' | 'fork';
};

export type PlatformSource = { icon: ReactNode; title: string; sub: string };

const PD_CSS = `
.pds-root{position:relative;color:var(--foreground);font-family:'DM Sans',sans-serif;border-radius:16px;overflow:hidden;margin-bottom:48px;background:var(--card)}
.pds-wrap{position:relative;z-index:1;max-width:1480px;margin:0 auto;padding:24px clamp(14px,2.5vw,28px) 20px}
.pds-hero{position:relative;text-align:center;margin:0 0 16px;padding:6px 24px 4px}
.pds-hero .pds-kick{font:600 12px 'DM Mono',monospace;letter-spacing:.26em;text-transform:uppercase;color:var(--accent)}
.pds-hero h2{margin:6px 0 0;font-size:clamp(22px,2.4vw,28px);font-weight:800;letter-spacing:-.015em;line-height:1.15;color:var(--foreground)}
.pds-hero h2 .pds-hl{color:var(--accent)}
.pds-hero .pds-brand{position:absolute;top:8px;right:12px;font:600 12px 'DM Mono',monospace;letter-spacing:.04em;color:var(--muted-foreground)}
.pds-plat{border:1px solid var(--border);border-radius:14px;overflow:hidden;background:var(--background);box-shadow:0 8px 28px rgba(15,23,42,.06), 0 1px 0 rgba(15,23,42,.04) inset}
.pds-row{display:grid;grid-template-columns:200px 1fr;gap:14px;align-items:center;padding:14px 18px;border-top:1px solid var(--border)}
.pds-row:first-child{border-top:none}
.pds-row.pds-tint-orange{background:color-mix(in srgb, var(--accent) 5%, transparent)}
.pds-row.pds-tint-navy{background:color-mix(in srgb, var(--primary) 4%, transparent)}
.pds-row .pds-lbl b{display:block;font-size:17px;font-weight:800;letter-spacing:-.01em;color:var(--foreground)}
.pds-row .pds-lbl span{display:block;font-size:13px;color:var(--muted-foreground);line-height:1.4;margin-top:3px}
.pds-row .pds-items{display:flex;gap:24px;align-items:center;flex-wrap:wrap}
.pds-row .pds-items.pds-two{display:grid;grid-template-columns:1fr 1fr;align-items:center;gap:20px}
.pds-prod{display:flex;align-items:center;gap:11px;text-decoration:none;color:inherit;min-width:0;padding:4px 7px;margin:-4px -7px;border-radius:10px;transition:.15s ease}
a.pds-prod:hover{background:color-mix(in srgb, var(--accent) 10%, transparent)}
.pds-tile{width:50px;height:50px;flex:none;background:#fff;border-radius:12px;display:grid;place-items:center;box-shadow:0 2px 10px rgba(15,23,42,.10);border:1px solid var(--border)}
.pds-tile svg{width:36px;height:36px}
.pds-tx b{display:flex;align-items:center;font-size:16.5px;font-weight:800;letter-spacing:-.01em;white-space:nowrap;color:var(--foreground)}
.pds-tx .pds-sub{display:block;font-size:13px;color:var(--muted-foreground);line-height:1.35;margin-top:2px}
.pds-live{width:6px;height:6px;border-radius:99px;background:var(--accent);box-shadow:0 0 7px color-mix(in srgb, var(--accent) 80%, transparent);display:inline-block;margin-left:7px;flex:none}
.pds-chip{display:inline-flex;align-items:center;gap:5px;background:#fff;color:#11171C;border:1px solid var(--border);border-radius:99px;padding:5px 11px;margin-left:8px;font:800 11.5px 'DM Sans',sans-serif;letter-spacing:.04em;box-shadow:0 1px 4px rgba(15,23,42,.08);white-space:nowrap}
.pds-chip svg{width:14px;height:14px;flex:none}
/* medallion stage labels (bronze › silver › gold) under a product title */
.pds-medlbls{display:flex;align-items:center;gap:6px;margin-top:4px;font:600 10px 'DM Mono',monospace;letter-spacing:.10em;color:var(--muted-foreground);text-transform:uppercase;white-space:nowrap}
.pds-medlbls .pds-medsep{color:var(--accent)}
/* fork-layout row: trunk product on left, Y-fork, stacked products on right */
.pds-story{display:flex;align-items:center;justify-content:center;gap:18px;width:100%;flex-wrap:nowrap}
.pds-fork-dest{display:flex;flex-direction:column;height:150px;justify-content:space-between;flex-shrink:0;min-width:0}
@media (max-width:980px){.pds-story{flex-wrap:wrap;gap:14px}.pds-fork-dest{height:auto;gap:14px}}
.pds-infra{display:flex;align-items:center;gap:18px;padding:9px 18px;border-top:1px solid var(--border);background:color-mix(in srgb, var(--muted) 60%, transparent)}
.pds-infra b{font-size:14.5px;font-weight:800;color:var(--foreground)}
.pds-infra .pds-ofdl{font:600 12px 'DM Mono',monospace;letter-spacing:.10em;color:var(--muted-foreground);text-transform:uppercase}
.pds-infra .pds-logos{margin-left:auto;display:flex;align-items:center;gap:22px}
.pds-flows{position:relative;height:58px;display:grid;grid-template-columns:repeat(var(--pds-n,4),1fr);max-width:880px;margin:6px auto 0}
.pds-fl{position:relative}
.pds-fl::before{content:'';position:absolute;left:50%;top:0;bottom:0;width:2px;margin-left:-1px;background:linear-gradient(180deg, color-mix(in srgb, var(--accent) 60%, transparent), color-mix(in srgb, var(--accent) 10%, transparent))}
.pds-fl i{position:absolute;left:50%;width:6px;height:6px;margin-left:-3px;border-radius:99px;background:var(--accent);box-shadow:0 0 8px color-mix(in srgb, var(--accent) 80%, transparent);animation:pds-rise 2.1s linear infinite}
.pds-fl i:nth-child(2){animation-delay:1.05s}
@keyframes pds-rise{0%{top:calc(100% - 4px);opacity:0}12%{opacity:1}88%{opacity:1}100%{top:-4px;opacity:0}}
.pds-zb{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);z-index:2;display:inline-flex;align-items:center;gap:6px;white-space:nowrap;background:var(--card);border:1px solid var(--border);border-radius:99px;padding:6px 13px;text-decoration:none;color:var(--foreground);font:700 13px 'DM Sans',sans-serif;box-shadow:0 4px 14px rgba(15,23,42,.10)}
.pds-zb svg{width:13px;height:13px;color:var(--accent)}
/* dual-path: Zerobus pill shifts to the left quarter, upload pill to the right */
.pds-zb.pds-dual{left:25%}
.pds-zb.pds-up{left:87.5%}
a.pds-zb:hover{border-color:var(--accent);background:color-mix(in srgb, var(--accent) 8%, transparent)}
.pds-sources{display:grid;grid-template-columns:repeat(var(--pds-n,4),1fr);gap:10px;max-width:880px;margin:0 auto}
.pds-src{display:flex;align-items:center;gap:10px;justify-content:center}
.pds-src .pds-tile{width:44px;height:44px;border-radius:11px}
.pds-src .pds-tile svg{width:28px;height:28px}
.pds-src .pds-tx b{display:block;font-size:14px;font-weight:800;white-space:nowrap}
.pds-src .pds-tx span{display:block;font-size:12.5px;color:var(--muted-foreground);white-space:nowrap}
.pds-foot{margin-top:14px;text-align:center;font-size:12px;color:var(--muted-foreground)}
.pds-foot .pds-dot{display:inline-block;width:5px;height:5px;border-radius:99px;background:var(--accent);box-shadow:0 0 6px color-mix(in srgb, var(--accent) 80%, transparent);vertical-align:middle;margin:0 4px 1px 0}
@media (max-width:980px){.pds-row{grid-template-columns:1fr}.pds-row .pds-items.pds-two{grid-template-columns:1fr}.pds-flows{display:none}.pds-sources{grid-template-columns:1fr 1fr}}
`;

function ProdTile({ p, resources }: { p: PlatformProduct; resources: ResourceMap }) {
  const url = p.resourceKey ? resources[p.resourceKey]?.url : undefined;
  const body = (
    <>
      <span className="pds-tile">{p.icon}</span>
      <span className="pds-tx">
        <b>
          {p.title}
          {p.rt ? <RtBadge /> : null}
          {url ? <span className="pds-live" /> : null}
          {p.after}
        </b>
        {p.medallion ? (
          <span className="pds-medlbls">
            {p.medallion.map((m, i) => (
              <span key={i}>
                {i > 0 && <span className="pds-medsep">›</span>}
                {m}
              </span>
            ))}
          </span>
        ) : (
          <span className="pds-sub">{p.sub}</span>
        )}
      </span>
    </>
  );
  return url ? (
    <a className="pds-prod" href={url} target="_blank" rel="noopener noreferrer"
       title="Opens the live resource in the Databricks workspace">{body}</a>
  ) : (
    <div className="pds-prod">{body}</div>
  );
}

export function PlatformStack({
  kicker,
  titlePrefix,
  titleHighlight,
  brand = 'Databricks Platform',
  rows,
  sources,
  ingestLabel,
  ingestUpload,
  infraLabel = 'Open Format Data Lake',
  infraLogos,
  resources,
  fetchResources,
}: {
  /** small uppercase eyebrow above the title, e.g. "LuxeBeauty · Returns Intelligence" */
  kicker: string;
  /** title text before the highlighted part, e.g. "Running LuxeBeauty Returns on the " */
  titlePrefix: string;
  /** highlighted (accent-colored) tail of the title, e.g. "Databricks Platform" */
  titleHighlight: string;
  /** top-right brand tag */
  brand?: string;
  rows: PlatformRow[];
  /** the datasource strip at the bottom (Order POS / CS Tickets / …) */
  sources: PlatformSource[];
  /** pill label on the ingest flow between sources and the box, e.g. "Zerobus · real-time ingest" */
  ingestLabel?: string;
  /** optional SECOND ingest pill (e.g. "Upload · file on Volume") shown on the
   *  right; when present the ingestLabel pill shifts left to make room, matching
   *  the reference diagram's dual-path ingest. `resourceKey` deep-links it. */
  ingestUpload?: { label: ReactNode; icon?: ReactNode; resourceKey?: string };
  infraLabel?: string;
  /** e.g. [<DeltaLogo/>, <IcebergLogo/>] */
  infraLogos?: ReactNode[];
  /** pass a resolved resource map… */
  resources?: ResourceMap;
  /** …or a fetcher (e.g. () => fetch('/api/resources').then(r=>r.json())) to load at mount */
  fetchResources?: () => Promise<ResourceMap>;
}) {
  const [R, setR] = useState<ResourceMap>(resources ?? {});
  useEffect(() => {
    if (resources) { setR(resources); return; }
    if (!fetchResources) return;
    let alive = true;
    void fetchResources()
      .then((r) => { if (alive) setR(r); })
      .catch((e) => console.error('[platform-stack] resources fetch failed', e));
    return () => { alive = false; };
  }, [resources, fetchResources]);

  return (
    <section className="pds-root" aria-label="Platform panel">
      <style>{PD_CSS}</style>
      <div className="pds-wrap">
        <div className="pds-hero">
          <div className="pds-brand">{brand}</div>
          <div className="pds-kick">{kicker}</div>
          <h2>{titlePrefix}<span className="pds-hl">{titleHighlight}</span></h2>
        </div>

        <div className="pds-plat">
          {rows.map((row, i) => (
            <div key={i} className={`pds-row${row.tint ? ` pds-tint-${row.tint}` : ''}`}>
              <div className="pds-lbl"><b>{row.title}</b><span>{row.sub}</span></div>
              {row.layout === 'fork' ? (
                /* trunk product → Y-fork → remaining products stacked right */
                <div className="pds-story">
                  <FlowKeyframes />
                  <ProdTile p={row.products[0]} resources={R} />
                  <Fork height={150} tileSize={50} idPrefix={`db-fork-pd-${i}`} />
                  <div className="pds-fork-dest">
                    {row.products.slice(1).map((p, j) => (
                      <ProdTile key={j} p={p} resources={R} />
                    ))}
                  </div>
                </div>
              ) : (
                <div className={`pds-items${row.products.length === 2 ? ' pds-two' : ''}`}>
                  {row.products.map((p, j) => (
                    <ProdTile key={j} p={p} resources={R} />
                  ))}
                </div>
              )}
            </div>
          ))}

          {infraLogos && (
            <div className="pds-infra">
              <b>Open Infrastructure</b>
              <span className="pds-ofdl">{infraLabel}</span>
              <span className="pds-logos">{infraLogos.map((l, i) => <span key={i}>{l}</span>)}</span>
            </div>
          )}
        </div>

        {sources.length > 0 && (
          <>
            <div className="pds-flows" style={{ ['--pds-n' as string]: sources.length }}>
              {sources.map((_, i) => (
                <div key={i} className="pds-fl"><i style={{ animationDelay: `${(i * 0.4).toFixed(2)}s` }} /><i /></div>
              ))}
              {ingestLabel && (
                <span className={`pds-zb${ingestUpload ? ' pds-dual' : ''}`}>{ingestLabel}</span>
              )}
              {ingestUpload && (() => {
                const url = ingestUpload.resourceKey ? R[ingestUpload.resourceKey]?.url : undefined;
                const inner = <>{ingestUpload.icon}{ingestUpload.label}</>;
                return url ? (
                  <a className="pds-zb pds-up" href={url} target="_blank" rel="noopener noreferrer">{inner}</a>
                ) : (
                  <span className="pds-zb pds-up">{inner}</span>
                );
              })()}
            </div>
            <div className="pds-sources" style={{ ['--pds-n' as string]: sources.length }}>
              {sources.map((s, i) => (
                <div key={i} className="pds-src">
                  <span className="pds-tile">{s.icon}</span>
                  <span className="pds-tx"><b>{s.title}</b><span>{s.sub}</span></span>
                </div>
              ))}
            </div>
          </>
        )}

        <div className="pds-foot">
          <span className="pds-dot" />
          glowing dot = opens the real object in the Databricks workspace
        </div>
      </div>
    </section>
  );
}
