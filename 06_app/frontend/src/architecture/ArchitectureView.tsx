/** "Arquitetura ao vivo": the data journey in an overlay, opened from the glowing header button.
 *  Every stage deep-links into the real object in the Databricks workspace. */
import { useEffect, useState } from 'react';
import { ArrowUpRight, X } from 'lucide-react';
import { api, type Journey, type Resources } from '../lib/api';
import { dateBR, timeBR } from '../lib/format';
import { Loading } from '../components/ui';
import JourneyDiagram from './JourneyDiagram';

export default function ArchitectureView({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [j, setJ] = useState<Journey | null>(null);
  const [res, setRes] = useState<Resources>({});
  useEffect(() => {
    if (!open) return;
    api.journey().then(setJ);
    api.resources().then(setRes).catch(() => setRes({}));   // no links → inert tiles, same diagram
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open]); // eslint-disable-line react-hooks/exhaustive-deps
  if (!open) return null;

  const run = j?.steps[0];
  const job = res.job?.url;
  const chip = 'inline-flex items-center gap-1 rounded-md border border-zinc-700 px-2 py-1 text-[10.5px] font-mono text-zinc-300 hover:border-[#EF5B3F]/60 hover:text-orange-200';
  return (
    <div className="fixed inset-0 z-[3000] overflow-y-auto bg-black/70 backdrop-blur-sm p-4 sm:p-8" onClick={onClose}>
      <div role="dialog" aria-modal="true" aria-label="Arquitetura ao vivo" onClick={(e) => e.stopPropagation()}
        className="mx-auto mt-6 w-full max-w-[1320px] rounded-2xl border border-[#EF5B3F]/30 bg-zinc-950 shadow-[0_0_80px_-20px_rgba(239,91,63,0.45)]">
        <header className="flex items-start justify-between gap-4 border-b border-zinc-800/80 px-6 py-5">
          <div>
            <div className="text-[10px] uppercase tracking-[0.28em] font-bold text-[#EF5B3F]">arquitetura ao vivo · databricks</div>
            <h2 className="mt-1 text-xl font-semibold text-zinc-100">A jornada de dados: um único job, do dado bruto à decisão aprovada</h2>
            <p className="mt-1 text-[12.5px] text-zinc-400">
              O selo verde marca o que rodou no último run. Clique num estágio para abrir o objeto real no workspace:
              notebook, pipeline, Unity Catalog, modelo, Lakebase, Genie ou o app.
            </p>
          </div>
          <div className="flex items-start gap-2 shrink-0">
            {run && (
              <div className="flex flex-col items-end gap-1.5">
                <div className="flex gap-1.5">
                  {job && <a className={chip} href={job} target="_blank" rel="noopener noreferrer">job diário · 06:00 <ArrowUpRight className="w-3 h-3" /></a>}
                  {job && <a className={chip} href={`${job}/runs/${run.job_run_id}`} target="_blank" rel="noopener noreferrer">run {run.job_run_id} <ArrowUpRight className="w-3 h-3" /></a>}
                </div>
                <span className="text-[10.5px] font-mono text-zinc-500">último run · {dateBR(run.updated_at)} · {timeBR(run.updated_at)}</span>
              </div>
            )}
            <button onClick={onClose} aria-label="Fechar" className="ml-2 rounded-md border border-zinc-800 p-1.5 text-zinc-400 hover:text-zinc-100 hover:border-zinc-600"><X className="w-4 h-4" /></button>
          </div>
        </header>
        {j ? <JourneyDiagram j={j} res={res} /> : <div className="p-10"><Loading /></div>}
        <footer className="flex flex-wrap items-center gap-x-5 gap-y-1 border-t border-zinc-800/80 px-6 py-3 text-[10.5px] text-zinc-500">
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> rodou no último run</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#EF5B3F] shadow-[0_0_8px_#EF5B3F]" /> abre no workspace</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#EF5B3F]/70" /> ponto em movimento = o dado fluindo entre estágios</span>
          <span className="ml-auto">Esc para fechar</span>
        </footer>
      </div>
    </div>
  );
}
