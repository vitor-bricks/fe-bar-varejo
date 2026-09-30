import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, MapPin } from 'lucide-react';
import { api, usePoll, type Store, type StoreDetail } from '../lib/api';
import { brl, dec1, num, pct } from '../lib/format';
import BrazilMap, { healthColor } from '../components/BrazilMap';
import ActionCard from '../components/ActionCard';
import { ErrorBox, Kpi, Loading, PageTitle, Panel, ProductTag } from '../components/ui';

const SHOWN_ACTIONS = 6;

function Stat({ label, value, tone = 'text-zinc-100' }: { label: string; value: string; tone?: string }) {
  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-950/60 px-3 py-2">
      <div className="text-[9.5px] uppercase tracking-[0.18em] text-zinc-500 font-semibold">{label}</div>
      <div className={`font-mono text-[15px] font-bold mt-0.5 ${tone}`}>{value}</div>
    </div>
  );
}

/** Selected store: identity, headline numbers and the items most at risk. Sits next to the map. */
function StoreSummary({ s, d }: { s: Store; d: StoreDetail }) {
  return (
    <div className="space-y-4">
      <div>
        <div className="text-lg font-semibold text-zinc-100">{s.store_name}</div>
        <div className="text-[11px] text-zinc-500">{s.city} · {s.uf} · {s.store_format} · {s.region}</div>
      </div>
      <div className="grid grid-cols-3 gap-2">
        <Stat label="ruptura 7d" value={pct(s.stockout_rate_7d)} tone={s.stockout_rate_7d >= 0.075 ? 'text-red-300' : 'text-zinc-100'} />
        <Stat label="em risco 7d" value={brl(s.revenue_at_risk)} tone="text-amber-300" />
        <Stat label="ações na fila" value={`${s.queue_n}${s.queue_critical ? ` · ${s.queue_critical} crít.` : ''}`} />
      </div>
      <div>
        <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-semibold mb-2">itens com maior R$ em risco</div>
        <table className="w-full text-[11.5px]">
            <thead className="text-zinc-500"><tr><th className="text-left font-medium pb-1">produto</th><th className="text-right font-medium">cob.</th><th className="text-right font-medium">a caminho</th><th className="text-right font-medium">risco</th></tr></thead>
            <tbody>{d.at_risk.map((r) => (
              <tr key={r.product_name} className="border-t border-zinc-800/80">
                <td className="py-1.5 text-zinc-300 pr-2">{r.product_name}</td>
                <td className="text-right font-mono text-zinc-300">{dec1(r.days_of_cover)} d</td>
                <td className="text-right font-mono text-zinc-400">{r.inbound_units ? `${num(r.inbound_units)} un` : '—'}</td>
                <td className={`text-right font-mono ${r.risk_probability >= 0.5 ? 'text-red-300' : 'text-zinc-400'}`}>{pct(r.risk_probability, 0)}</td>
              </tr>))}</tbody>
        </table>
      </div>
    </div>
  );
}

export default function Network() {
  const [n, reload, err] = usePoll(api.network, 20000);
  const [sel, setSel] = useState<string | null>(null);
  const [detail, setDetail] = useState<StoreDetail | null>(null);
  useEffect(() => { if (n && !sel && n.stores.length) setSel(n.stores[0].store_id); }, [n, sel]);
  // the previous store stays on screen (dimmed) until the next one arrives: no layout jump, and
  // everything shown belongs to the same store. Stale replies are ignored.
  useEffect(() => {
    if (!sel) return;
    let live = true;
    api.store(sel).then((x) => { if (live) setDetail(x); });
    return () => { live = false; };
  }, [sel]);
  const onDecided = () => { reload(); if (sel) api.store(sel).then(setDetail); };

  if (!n) return <><ErrorBox err={err} /><Loading /></>;
  const alert = n.stores.filter((s) => s.stockout_rate_7d >= 0.075);
  const risk = n.stores.reduce((a, s) => a + s.revenue_at_risk, 0);
  const crit = n.stores.reduce((a, s) => a + s.queue_critical, 0);
  const pending = n.routes.filter((r) => !r.decision).length;
  const store = n.stores.find((s) => s.store_id === detail?.store.store_id);
  const loading = sel !== detail?.store.store_id;

  return (
    <div className="space-y-6">
      <PageTitle kicker="Rede LojaBR" title="Rede de lojas" sub={`${n.stores.length} lojas · ${brl(risk)} em risco nos próximos 7 dias · ${n.routes.length} transferências sugeridas`} />

      <section className="rounded-xl border border-red-500/30 bg-gradient-to-r from-red-500/[0.12] via-red-500/[0.05] to-transparent p-5 flex items-center gap-6 flex-wrap">
        <div className="w-14 h-14 rounded-xl border border-red-500/40 bg-red-500/10 grid place-items-center"><AlertTriangle className="w-6 h-6 text-red-300" /></div>
        <div className="flex-1 min-w-[260px]">
          <div className="text-[10px] uppercase tracking-[0.25em] text-red-300 font-bold">status da rede</div>
          <div className="text-xl font-semibold text-zinc-100 mt-1">{alert.length} lojas com ruptura acima de 7,5% na semana · {crit} ações críticas</div>
          <div className="text-[13px] text-zinc-400 mt-1">Aprovar as {pending} transferências pendentes move estoque parado para onde a gôndola vai esvaziar — sem esperar o fornecedor.</div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Kpi tone="amber" label="em risco 7d" value={brl(risk)} />
          <Kpi tone="red" label="lojas em alerta" value={`${alert.length}/${n.stores.length}`} />
        </div>
      </section>

      {/* Row 1: map | selected store + ranking. The right column is pinned to the map's height,
          the ranking absorbs the remaining space and scrolls, so both columns end on the same line. */}
      <div className="grid grid-cols-1 xl:grid-cols-[1.35fr_1fr] gap-6">
        <Panel title="Mapa operacional" hint="clique numa loja · linhas = transferências sugeridas" right={<ProductTag>Lakebase · serving.store_network</ProductTag>}>
          <BrazilMap stores={n.stores} routes={n.routes} selected={sel} onSelect={setSel} />
        </Panel>
        <div className="relative">
          <div className="flex flex-col gap-6 xl:absolute xl:inset-0">
            <Panel className={`shrink-0 transition-opacity ${loading ? 'opacity-50' : ''}`} title={<span className="inline-flex items-center gap-2"><MapPin className="w-3.5 h-3.5 text-amber-400" />Loja selecionada</span>}>
              {store && detail ? <StoreSummary s={store} d={detail} /> : <Loading />}
            </Panel>
            <Panel className="flex-1 min-h-0 flex flex-col" bodyClassName="flex-1 min-h-0 overflow-y-auto scrollbar-thin max-h-[360px] xl:max-h-none" title="Lojas por R$ em risco" hint="próximos 7 dias · clique para selecionar" pad={false}>
              {n.stores.map((s, i) => (
                <button key={s.store_id} onClick={() => setSel(s.store_id)}
                  className={`w-full flex items-center gap-3 px-5 py-2.5 text-left border-b border-zinc-800/60 hover:bg-zinc-800/40 ${sel === s.store_id ? 'bg-amber-500/[0.07]' : ''}`}>
                  <span className="text-[10px] font-mono text-zinc-600 w-6">#{i + 1}</span>
                  <span className="w-2 h-2 rounded-full" style={{ background: healthColor(s.stockout_rate_7d).fill }} />
                  <span className="flex-1 min-w-0"><span className="block text-[13px] text-zinc-100 truncate">{s.store_name.replace('LojaBR ', '')}</span>
                    <span className="block text-[10.5px] text-zinc-500">{s.city} · {s.uf} · {s.queue_n} ações</span></span>
                  <span className="text-right"><span className="block font-mono text-[12.5px] text-amber-300 font-bold">{brl(s.revenue_at_risk)}</span>
                    <span className="block text-[10px] text-zinc-500 font-mono">ruptura {pct(s.stockout_rate_7d)}</span></span>
                </button>
              ))}
            </Panel>
          </div>
        </div>
      </div>

      {/* Row 2: the selected store's actions, full width */}
      {store && detail && (
        <Panel className={`transition-opacity ${loading ? 'opacity-50' : ''}`} title={`Ações para ${store.store_name}`} hint="ordenadas por R$ protegido · aprovar grava a decisão na Lakebase com o seu usuário"
          right={store.queue_n > SHOWN_ACTIONS && <Link to={`/fila?loja=${store.store_id}`} className="text-[11px] uppercase tracking-[0.18em] text-amber-300 hover:text-amber-200 whitespace-nowrap">ver as {store.queue_n} na fila →</Link>}>
          {!detail.actions.length ? (
            <div className="text-[12px] text-zinc-500">Nenhuma ação pendente: estoque saudável nesta loja.</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {detail.actions.slice(0, SHOWN_ACTIONS).map((a) => <ActionCard key={a.action_id} it={a} onDecided={onDecided} />)}
            </div>
          )}
        </Panel>
      )}
    </div>
  );
}
