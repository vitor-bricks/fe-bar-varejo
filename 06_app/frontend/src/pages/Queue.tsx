import { useState } from 'react';
import { CheckCheck, Loader2 } from 'lucide-react';
import { api, usePoll, type ActionType, type Severity } from '../lib/api';
import { brl, timeBR } from '../lib/format';
import ActionCard from '../components/ActionCard';
import { ACTION, ErrorBox, Loading, PageTitle, Panel, ProductTag, SEV } from '../components/ui';

const TYPES: (ActionType | '')[] = ['', 'TRANSFER', 'EXPEDITE', 'URGENT_ORDER'];
const SEVS: (Severity | '')[] = ['', 'CRITICAL', 'HIGH', 'MEDIUM'];

export default function Queue() {
  const [type, setType] = useState<ActionType | ''>('');
  const [sev, setSev] = useState<Severity | ''>('');
  const [bulk, setBulk] = useState(false);
  const [limit, setLimit] = useState(24);
  const [items, reload, err] = usePoll(() => api.queue({ action_type: type, severity: sev, limit }), 20000, [type, sev, limit]);
  const [decs, reloadDecs] = usePoll(api.decisions, 20000);
  const refresh = () => { reload(); reloadDecs(); };

  const pendingCritical = (items ?? []).filter((i) => i.severity === 'CRITICAL' && !i.decision);
  const approveCritical = async () => {
    setBulk(true);
    try { await api.approveAll(pendingCritical.slice(0, 20).map((i) => i.action_id)); refresh(); } finally { setBulk(false); }
  };
  const chip = (on: boolean) => `px-3 py-1.5 rounded-full border text-[11px] font-semibold uppercase tracking-wider ${on ? 'border-amber-400/60 bg-amber-400/10 text-amber-300' : 'border-zinc-800 text-zinc-400 hover:text-zinc-200'}`;

  return (
    <div className="space-y-6">
      <PageTitle kicker="Fila de ação" title="Ações priorizadas por R$ protegido"
        sub="modelo de alerta antecipado + agente de reposição · cada aprovação é gravada na Lakebase com o seu usuário"
        right={pendingCritical.length > 0 && (
          <button onClick={approveCritical} disabled={bulk}
            className="px-4 py-2 rounded-lg text-[11px] font-bold uppercase tracking-wider bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 hover:bg-emerald-500/25 inline-flex items-center gap-2 disabled:opacity-50">
            {bulk ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCheck className="w-4 h-4" />} aprovar críticas ({Math.min(20, pendingCritical.length)})
          </button>
        )} />

      <div className="flex flex-wrap gap-2 items-center">
        {TYPES.map((t) => <button key={t || 'all'} onClick={() => setType(t)} className={chip(type === t)}>{t ? ACTION[t].short : 'todas'}</button>)}
        <span className="w-px h-5 bg-zinc-800 mx-1" />
        {SEVS.map((s) => <button key={s || 'all'} onClick={() => setSev(s)} className={chip(sev === s)}>{s ? SEV[s].label : 'qualquer severidade'}</button>)}
      </div>

      <ErrorBox err={err} />
      <div className="grid grid-cols-1 xl:grid-cols-[1fr_320px] gap-6">
        <div>
          {!items ? <Loading /> : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {items.map((it) => <ActionCard key={it.action_id} it={it} onDecided={refresh} />)}
            </div>
          )}
          {items && items.length >= limit && (
            <button onClick={() => setLimit(limit + 24)} className="mt-5 w-full py-2.5 rounded-lg border border-zinc-800 text-[11px] uppercase tracking-[0.18em] text-zinc-400 hover:text-zinc-200 hover:border-zinc-600">carregar mais ações</button>
          )}
        </div>
        <Panel className="xl:sticky xl:top-32 self-start" title="Decisões já tomadas" hint="app.replenishment_actions · Lakebase" right={<ProductTag>escrita</ProductTag>} pad={false}>
          <div className="max-h-[70vh] overflow-y-auto scrollbar-thin">
            {(decs ?? []).length === 0 && <div className="px-5 py-6 text-[12px] text-zinc-500">Nenhuma decisão ainda. Aprove uma ação ao lado.</div>}
            {(decs ?? []).map((d) => (
              <div key={`${d.action_id}-${d.decided_at}`} className="px-5 py-3 border-b border-zinc-800/60">
                <div className="flex items-center justify-between">
                  <span className={`text-[11px] font-bold ${d.decision === 'APPROVED' ? 'text-emerald-300' : 'text-zinc-500'}`}>{d.decision === 'APPROVED' ? '✓ aprovada' : '✕ rejeitada'}</span>
                  <span className="text-[10.5px] font-mono text-zinc-500">{timeBR(d.decided_at)}</span>
                </div>
                <div className="text-[12.5px] text-zinc-200 mt-0.5">{d.product_name}</div>
                <div className="text-[11px] text-zinc-500">{d.store_name}{d.from_store_name ? ` ← ${d.from_store_name}` : ''} · {d.units} un</div>
                <div className="flex items-center justify-between mt-1">
                  <span className="text-[10.5px] text-zinc-500 truncate">{d.decided_by}</span>
                  {d.decision === 'APPROVED' && <span className="text-[11px] font-mono text-emerald-300">{brl(d.revenue_protected)}</span>}
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}
