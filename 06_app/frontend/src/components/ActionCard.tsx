import { useState } from 'react';
import { ArrowRight, Check, Loader2, Sparkles, X } from 'lucide-react';
import { api, type QueueItem } from '../lib/api';
import { brl, dec1, num, pct } from '../lib/format';
import { ActionLabel, SEV, SeverityBadge } from './ui';

function Route({ it }: { it: QueueItem }) {
  const chip = 'px-2 py-0.5 rounded-md border text-[11px] whitespace-nowrap';
  const origin = it.action_type === 'TRANSFER'
    ? <span className={`${chip} border-teal-500/30 bg-teal-500/10 text-teal-200`}>{it.from_store_name?.replace('LojaBR ', '')} <span className="text-teal-400/70">({dec1(it.donor_days_of_cover)} d)</span></span>
    : <span className={`${chip} border-zinc-700 bg-zinc-800/60 text-zinc-300`}>{it.supplier_name}</span>;
  return (
    <div className="flex items-center gap-2 flex-wrap">
      {origin}
      <ArrowRight className="w-3.5 h-3.5 text-zinc-500" />
      <span className={`${chip} border-red-500/30 bg-red-500/10 text-red-200`}>{it.store_name.replace('LojaBR ', '')} <span className="text-red-300/70">({dec1(it.days_of_cover)} d)</span></span>
      {it.action_type === 'TRANSFER' && it.transfer_km != null && <span className="text-[10.5px] text-zinc-500 font-mono">{num(it.transfer_km)} km</span>}
    </div>
  );
}

export default function ActionCard({ it, onDecided, compact = false }: { it: QueueItem; onDecided?: () => void; compact?: boolean }) {
  const [busy, setBusy] = useState<null | 'APPROVED' | 'REJECTED'>(null);
  const [local, setLocal] = useState<{ decision: string; by: string } | null>(null);
  const decision = local?.decision ?? it.decision;
  const by = local?.by ?? it.decided_by;

  const decide = async (d: 'APPROVED' | 'REJECTED') => {
    setBusy(d);
    try {
      const r = await api.decide(it.action_id, d);
      setLocal({ decision: r.decision, by: r.decided_by });
      onDecided?.();
    } finally { setBusy(null); }
  };

  const agent = it.rationale_source === 'AGENTE';
  const inbound = it.inbound_units > 0
    ? `${num(it.inbound_units)} un a caminho${it.eta_adjusted_days != null ? ` · chega em ~${Math.round(it.eta_adjusted_days)} d` : ''}`
    : 'nada a caminho';

  return (
    <article className={`rounded-xl border border-zinc-800 border-l-4 ${SEV[it.severity].bar} bg-zinc-900/70 p-4 flex flex-col gap-3 ${decision ? 'opacity-80' : ''}`}>
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <SeverityBadge s={it.severity} />
          <span className="text-[10px] uppercase tracking-[0.2em] text-zinc-500">{it.category}</span>
        </div>
        <span className="text-[10px] font-mono text-zinc-600">#{it.priority}</span>
      </div>
      <div>
        <ActionLabel t={it.action_type} />
        <h3 className="text-[15px] font-semibold text-zinc-100 mt-1 leading-snug">{it.product_name}</h3>
      </div>
      <Route it={it} />
      <div className="grid grid-cols-3 gap-2 text-[11px]">
        <div><div className="text-zinc-500">risco 7 dias</div><div className="font-mono text-zinc-200 tabular-nums">{pct(it.risk_probability, 0)}</div></div>
        <div><div className="text-zinc-500">{it.action_type === 'EXPEDITE' ? 'antecipar' : 'mover'}</div><div className="font-mono text-amber-300 font-bold tabular-nums">{num(it.units)} un</div></div>
        <div><div className="text-zinc-500">chegada</div><div className="font-mono text-zinc-200 tabular-nums">{it.eta_days} dia{it.eta_days > 1 ? 's' : ''}</div></div>
      </div>
      {!compact && <div className="text-[10.5px] text-zinc-500">estoque {num(it.on_hand_units)} un · {inbound} · pontualidade do fornecedor {pct(it.supplier_on_time_rate, 0)}</div>}
      <div className={`rounded-lg px-3 py-2.5 text-[12px] leading-relaxed ${agent ? 'border border-amber-500/25 bg-amber-500/[0.06] text-zinc-300' : 'border border-zinc-800 bg-zinc-800/30 text-zinc-400'}`}>
        <div className={`text-[9.5px] uppercase tracking-[0.2em] font-bold mb-1 flex items-center gap-1.5 ${agent ? 'text-amber-400' : 'text-zinc-500'}`}>
          {agent ? <><Sparkles className="w-3 h-3" /> agente de reposição · verificou {it.agent_tools?.split(',').filter((t) => t !== 'submit_decision').length} fontes</> : 'regra do motor de ação'}
        </div>
        {it.rationale}
      </div>
      <div className="flex items-center justify-between gap-3 mt-auto">
        <div>
          <div className="text-[10px] uppercase tracking-[0.18em] text-zinc-500">protege</div>
          <div className="font-mono text-emerald-300 font-bold tabular-nums text-[15px]">{brl(it.revenue_protected)}</div>
        </div>
        {decision ? (
          <div className={`text-[11px] font-semibold text-right ${decision === 'APPROVED' ? 'text-emerald-300' : 'text-zinc-500'}`}>
            {decision === 'APPROVED' ? '✓ aprovada' : '✕ rejeitada'}<div className="text-[10px] text-zinc-500 font-normal">{by}</div>
          </div>
        ) : (
          <div className="flex gap-2">
            <button onClick={() => decide('REJECTED')} disabled={!!busy} title="Rejeitar"
              className="px-2.5 py-1.5 rounded-md border border-zinc-700 text-zinc-400 hover:text-zinc-200 hover:border-zinc-500 disabled:opacity-50">
              {busy === 'REJECTED' ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <X className="w-3.5 h-3.5" />}
            </button>
            <button onClick={() => decide('APPROVED')} disabled={!!busy}
              className="px-3 py-1.5 rounded-md text-[11px] font-bold uppercase tracking-wider bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 hover:bg-emerald-500/25 hover:text-emerald-200 transition-colors disabled:opacity-50 inline-flex items-center gap-1.5">
              {busy === 'APPROVED' ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />} Aprovar
            </button>
          </div>
        )}
      </div>
    </article>
  );
}
