/**
 * The data journey, drawn with the databricks-arch-diagram kit (<Pipeline>).
 * Generated from ./journey.spec.json (validated with the skill's validator): one step per spec
 * entry, 1:1 props. Two additions ride on the `icon` prop, so the primitives stay untouched:
 *  - a status badge (green = the stage ran fine in the job's last run, from /api/journey);
 *  - the skill's "glowing dot" deep-link: when /api/resources has a url for the stage, the whole
 *    stage (tile + labels) opens the real object in the Databricks workspace.
 */
import type { ReactNode } from 'react';
import { ArrowUpRight, Check } from 'lucide-react';
import { Pipeline, type PipelineStep } from './diagrams';
import { AppsIcon, GenieIcon, LakebaseIcon, LakeflowIcon, LakehouseIcon, UCIcon } from './icons';
import { FoundationModelIcon, MLflowRegistryIcon } from './icons-extra';
import './theme.css';
import type { Journey, Resources } from '../lib/api';

type Link = [key: string, label: string];

// journey.spec.json → steps (the first 7 map to the job's stages, in order; the last is this app).
// `links[0]` is what a click on the stage opens; the rest are listed under the strip.
const SPEC: { icon: ReactNode; name: string; sub: string; links: Link[]; detail?: string }[] = [
  { icon: <LakeflowIcon />, name: 'Ingestão', sub: 'Auto Loader', links: [['nb_ingest', 'notebook'], ['volume', 'Volume landing']] },
  { icon: <LakehouseIcon />, name: 'Medallion', sub: 'bronze → gold', links: [['pipeline', 'pipeline'], ['nb_pipeline', 'notebook']] },
  { icon: <UCIcon />, name: 'Governança', sub: 'Unity Catalog', links: [['catalog', 'schema gold']] },
  { icon: <MLflowRegistryIcon />, name: 'Modelo', sub: 'MLflow · UC', links: [['model', 'modelo no UC'], ['nb_model', 'notebook']] },
  { icon: <FoundationModelIcon />, name: 'Agente', sub: 'FMAPI · tools', links: [['nb_agent', 'notebook']] },
  { icon: <LakebaseIcon />, name: 'Serving', sub: 'Lakebase', links: [['lakebase', 'projeto Lakebase'], ['nb_sync', 'notebook de sync']] },
  { icon: <GenieIcon />, name: 'Linguagem natural', sub: 'Genie', links: [['genie', 'espaço Genie']] },
  { icon: <AppsIcon />, name: 'Decisão', sub: 'este app', links: [['app', 'app no workspace']],
    detail: 'o gerente aprova; a decisão é gravada na Lakebase com o usuário' },
];

const OK = ['ok', 'success', 'succeeded', 'completed'];
const isOk = (s?: string) => OK.includes(String(s).toLowerCase());

/** Product icon + status badge (top-right) + glowing deep-link dot (top-left) and click area. */
function Tile({ status, url, label, children }: { status?: string; url?: string; label: string; children: ReactNode }) {
  return (
    <span style={{ position: 'relative', display: 'block', width: '100%', height: '100%' }}>
      {children}
      {status && (
        <span title={isOk(status) ? 'rodou no último run' : status}
          className={`absolute -top-[14px] -right-[14px] w-4 h-4 rounded-full grid place-items-center ring-2 ring-zinc-950 ${isOk(status) ? 'bg-emerald-500' : 'bg-amber-500'}`}>
          <Check className="w-2.5 h-2.5 text-zinc-950" strokeWidth={4} />
        </span>
      )}
      {url && (
        <>
          <span className="absolute -top-[13px] -left-[13px] w-3 h-3">
            <span className="absolute inset-0 rounded-full bg-[#EF5B3F] animate-ping opacity-60" />
            <span className="absolute inset-0 rounded-full bg-[#EF5B3F] ring-2 ring-zinc-950 shadow-[0_0_10px_#EF5B3F]" />
          </span>
          {/* covers the tile and its two label lines below (labels sit ~34px under the tile) */}
          <a href={url} target="_blank" rel="noopener noreferrer" title={`Abrir no workspace: ${label}`} aria-label={`Abrir no workspace: ${label}`}
            className="absolute z-10 rounded-xl transition hover:bg-[#EF5B3F]/[0.06] hover:ring-1 hover:ring-[#EF5B3F]/60"
            style={{ inset: '-9px -42px -46px -42px' }} />
        </>
      )}
    </span>
  );
}

export default function JourneyDiagram({ j, res = {} }: { j: Journey; res?: Resources }) {
  const url = (k: string) => res[k]?.url || '';
  const steps: PipelineStep[] = SPEC.map((s, i) => ({
    name: s.name, sub: s.sub,
    icon: <Tile status={j.steps[i]?.status} url={url(s.links[0][0])} label={`${s.name} · ${s.links[0][1]}`}>{s.icon}</Tile>,
  }));
  return (
    <div className="db-arch">
      <Pipeline steps={steps} connectorWidth={96} />
      {/* what each stage did in the last run + every workspace link (subs in the strip stay short) */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-x-6 gap-y-4 border-t border-zinc-800/80 px-5 py-4">
        {SPEC.map((s, i) => {
          const st = j.steps[i];
          return (
            <div key={s.name} className="flex gap-2.5 text-[11.5px] leading-snug">
              <span className={`mt-[4px] w-1.5 h-1.5 rounded-full shrink-0 ${!st || isOk(st.status) ? 'bg-emerald-400' : 'bg-amber-400'}`} />
              <div className="min-w-0">
                <span className="font-semibold text-zinc-200">{st?.stage ?? s.name}</span>
                <span className="text-zinc-500"> · {st?.product ?? 'Databricks Apps'}</span>
                <div className="text-zinc-400">{st?.detail ?? s.detail}</div>
                <div className="mt-1.5 flex flex-wrap gap-1.5">
                  {s.links.filter(([k]) => url(k)).map(([k, label]) => (
                    <a key={k} href={url(k)} target="_blank" rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 rounded-md border border-[#EF5B3F]/30 bg-[#EF5B3F]/[0.07] px-1.5 py-0.5 text-[10.5px] font-medium text-orange-200 hover:border-[#EF5B3F]/70 hover:bg-[#EF5B3F]/15">
                      {label} <ArrowUpRight className="w-3 h-3" />
                    </a>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
