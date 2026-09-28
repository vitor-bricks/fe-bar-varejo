import { ArrowRight, Bot, Boxes, ClipboardCheck, MapPinned, Truck } from 'lucide-react';
import { api, usePoll } from '../lib/api';
import { brl, dateBR, pct, timeBR } from '../lib/format';
import ActionCard from '../components/ActionCard';
import { ErrorBox, Loading, PageTitle, Panel, ProductTag } from '../components/ui';

const TOOLS = [
  { key: 'get_item_position', label: 'Posição do item', desc: 'estoque, venda média, cobertura, pedido a caminho', icon: Boxes },
  { key: 'find_donor_stores', label: 'Lojas doadoras', desc: 'excedente do mesmo item a até 450 km', icon: MapPinned },
  { key: 'get_supplier_history', label: 'Histórico do fornecedor', desc: 'pontualidade e atraso típico', icon: Truck },
  { key: 'submit_decision', label: 'Decisão', desc: 'confirma ou muda a ação + justificativa', icon: ClipboardCheck },
];

export default function Agent() {
  const [a, reload, err] = usePoll(api.agent, 30000);
  if (!a) return <><ErrorBox err={err} /><Loading /></>;
  const [lead, ...rest] = a.items;
  return (
    <div className="space-y-6">
      <PageTitle kicker="Sala do agente · Mosaic AI" title="Seu analista de abastecimento, trabalhando agora"
        sub={`agente de tool-calling na Foundation Model API · ${a.run_detail ?? ''} · último run ${dateBR(a.run_at)} ${timeBR(a.run_at)}`} />

      <section className="rounded-xl border border-amber-500/30 bg-gradient-to-r from-amber-500/[0.08] to-transparent p-5 flex items-center gap-5 flex-wrap">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-amber-300 to-orange-500 grid place-items-center animate-agent-glow"><Bot className="w-8 h-8 text-zinc-950" /></div>
        <div className="flex-1 min-w-[240px]">
          <div className="flex items-center gap-2"><span className="text-lg font-semibold text-amber-300">Agente de Reposição</span>
            <span className="text-[10px] uppercase tracking-widest text-emerald-400 font-semibold inline-flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />ativo</span></div>
          <div className="text-[13px] text-zinc-400 mt-1">Revisa os itens de maior valor da fila, <span className="text-zinc-200">verifica os fatos com ferramentas</span> antes de decidir e escreve a justificativa para o gerente. Decisão sem consulta é rejeitada pelo próprio loop.</div>
        </div>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div><div className="font-mono text-2xl font-bold text-zinc-100">{a.items.length}</div><div className="text-[10px] uppercase tracking-[0.18em] text-zinc-500">revisados</div></div>
          <div><div className="font-mono text-2xl font-bold text-zinc-100">{a.changed}</div><div className="text-[10px] uppercase tracking-[0.18em] text-zinc-500">ações alteradas</div></div>
          <div><div className="font-mono text-2xl font-bold text-emerald-300">{brl(a.items.reduce((s, i) => s + i.revenue_protected, 0))}</div><div className="text-[10px] uppercase tracking-[0.18em] text-zinc-500">em jogo</div></div>
        </div>
      </section>

      <Panel title="Como ele decide" hint="ferramentas chamadas nesta rodada (contagem real do loop)" right={<ProductTag>databricks-claude-sonnet-5 · tools</ProductTag>}>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 items-stretch">
          {TOOLS.map((t, i) => (
            <div key={t.key} className="relative rounded-lg border border-zinc-800 bg-zinc-950/60 p-3">
              {i < TOOLS.length - 1 && <ArrowRight className="hidden md:block absolute -right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-600 z-10" />}
              <div className="flex items-center justify-between"><t.icon className="w-4 h-4 text-amber-300" /><span className="font-mono text-[11px] text-zinc-400">{a.tool_usage[t.key] ?? 0}×</span></div>
              <div className="text-[13px] font-semibold text-zinc-100 mt-2">{t.label}</div>
              <div className="text-[11px] text-zinc-500">{t.desc}</div>
              <div className="text-[10px] font-mono text-zinc-600 mt-1">{t.key}()</div>
            </div>
          ))}
        </div>
      </Panel>

      <div className="grid grid-cols-1 xl:grid-cols-[1fr_360px] gap-6">
        <div className="space-y-4">
          {lead && (
            <div>
              <div className="text-[10px] uppercase tracking-[0.25em] text-amber-400 font-bold mb-2">ação em destaque</div>
              <ActionCard it={lead} onDecided={reload} />
            </div>
          )}
          <div className="text-[10px] uppercase tracking-[0.25em] text-zinc-500 font-bold">próximas revisadas pelo agente · {rest.length}</div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">{rest.map((it) => <ActionCard key={it.action_id} it={it} onDecided={reload} compact />)}</div>
        </div>
        <Panel title="Fornecedores sob observação" hint="pontualidade medida nos pedidos recebidos" right={<ProductTag>gold_supplier_otif</ProductTag>}>
          <div className="space-y-3">
            {a.suppliers.map((s) => (
              <div key={s.supplier_name}>
                <div className="flex justify-between text-[12px]"><span className="text-zinc-300">{s.supplier_name}</span>
                  <span className={`font-mono ${s.on_time_rate < 0.75 ? 'text-red-300' : s.on_time_rate < 0.88 ? 'text-amber-300' : 'text-emerald-300'}`}>{pct(s.on_time_rate, 0)}</span></div>
                <div className="h-1.5 rounded-full bg-zinc-800 mt-1 overflow-hidden"><div className={`h-full rounded-full ${s.on_time_rate < 0.75 ? 'bg-red-500' : s.on_time_rate < 0.88 ? 'bg-amber-500' : 'bg-emerald-500'}`} style={{ width: `${s.on_time_rate * 100}%` }} /></div>
                <div className="text-[10.5px] text-zinc-500 mt-0.5">{s.orders_received} pedidos · atraso médio {s.avg_delay_when_late?.toFixed(1)} d quando atrasa</div>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}
