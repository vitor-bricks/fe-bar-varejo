/**
 * The data journey on the home page, drawn with the databricks-arch-diagram kit (<Pipeline>).
 * Generated from ./journey.spec.json (validated with the skill's validator): one step per spec
 * entry, 1:1 props. The only addition is a status badge on each tile, passed through the `icon`
 * prop, so the primitives stay untouched. Status and details come from /api/journey, which the
 * job's last run writes to Lakebase.
 */
import type { ReactNode } from 'react';
import { Check } from 'lucide-react';
import { Pipeline, type PipelineStep } from './diagrams';
import { AppsIcon, GenieIcon, LakebaseIcon, LakeflowIcon, LakehouseIcon, UCIcon } from './icons';
import { FoundationModelIcon, MLflowRegistryIcon } from './icons-extra';
import './theme.css';
import type { Journey } from '../lib/api';

// journey.spec.json → steps (the first 7 map to the job's stages, in order; the last is this app)
const SPEC: { icon: ReactNode; name: string; sub: string }[] = [
  { icon: <LakeflowIcon />, name: 'Ingestão', sub: 'Auto Loader' },
  { icon: <LakehouseIcon />, name: 'Medallion', sub: 'bronze → gold' },
  { icon: <UCIcon />, name: 'Governança', sub: 'Unity Catalog' },
  { icon: <MLflowRegistryIcon />, name: 'Modelo', sub: 'MLflow · UC' },
  { icon: <FoundationModelIcon />, name: 'Agente', sub: 'FMAPI · tools' },
  { icon: <LakebaseIcon />, name: 'Serving', sub: 'Lakebase' },
  { icon: <GenieIcon />, name: 'Linguagem natural', sub: 'Genie' },
  { icon: <AppsIcon />, name: 'Decisão', sub: 'este app' },
];

const OK = ['ok', 'success', 'succeeded', 'completed'];

/** Product icon + a small status badge on the tile's corner (green = ran fine in the last run). */
function WithStatus({ status, children }: { status?: string; children: ReactNode }) {
  if (!status) return <>{children}</>;
  const ok = OK.includes(status.toLowerCase());
  return (
    <span style={{ position: 'relative', display: 'block', width: '100%', height: '100%' }}>
      {children}
      <span title={ok ? 'rodou no último run' : status}
        className={`absolute -top-[14px] -right-[14px] w-4 h-4 rounded-full grid place-items-center ring-2 ring-zinc-900 ${ok ? 'bg-emerald-500' : 'bg-amber-500'}`}>
        <Check className="w-2.5 h-2.5 text-zinc-950" strokeWidth={4} />
      </span>
    </span>
  );
}

export default function JourneyDiagram({ j }: { j: Journey }) {
  const steps: PipelineStep[] = SPEC.map((s, i) => ({
    ...s,
    icon: <WithStatus status={j.steps[i]?.status}>{s.icon}</WithStatus>,
  }));
  return (
    <div className="db-arch">
      <Pipeline steps={steps} connectorWidth={96} />
      {/* what each stage actually did in the last run (kept out of the strip: subs must stay short) */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-x-6 gap-y-3 border-t border-zinc-800/80 px-5 py-4">
        {j.steps.map((s) => (
          <div key={s.step} className="flex gap-2.5 text-[11.5px] leading-snug">
            <span className={`mt-[3px] w-1.5 h-1.5 rounded-full shrink-0 ${OK.includes(String(s.status).toLowerCase()) ? 'bg-emerald-400' : 'bg-amber-400'}`} />
            <div>
              <span className="font-semibold text-zinc-200">{s.stage}</span>
              <span className="text-zinc-500"> · {s.product}</span>
              <div className="text-zinc-400">{s.detail}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
