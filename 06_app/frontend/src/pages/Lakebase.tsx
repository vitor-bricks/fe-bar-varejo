import { Database, PenLine, Table2 } from 'lucide-react';
import { api, usePoll } from '../lib/api';
import { brl, dec1, num, whenBR } from '../lib/format';
import { ErrorBox, Kpi, Loading, PageTitle, Panel, ProductTag } from '../components/ui';

function Sla({ label, v, target }: { label: string; v?: number; target: number }) {
  const ok = (v ?? 0) <= target;
  const w = Math.min(100, ((v ?? 0) / (target * 2)) * 100);
  return (
    <div>
      <div className="flex justify-between text-[12.5px]"><span className="text-zinc-300">{label}</span><span className="font-mono text-zinc-100">{v == null ? '—' : dec1(v)} ms</span></div>
      <div className="h-1.5 rounded-full bg-zinc-800 mt-1.5 overflow-hidden"><div className={`h-full rounded-full ${ok ? 'bg-emerald-500' : 'bg-amber-500'}`} style={{ width: `${w}%` }} /></div>
      <div className="flex justify-between text-[10px] text-zinc-500 mt-0.5"><span>alvo ≤ {target} ms</span><span>{ok ? 'dentro do alvo' : 'acima do alvo'}</span></div>
    </div>
  );
}

export default function Lakebase() {
  const [s, , err] = usePoll(api.lakebase, 5000);
  if (!s) return <><ErrorBox err={err} /><Loading /></>;
  const serving = s.tables.filter((t) => t.table_schema === 'serving');
  const app = s.tables.filter((t) => t.table_schema === 'app');
  return (
    <div className="space-y-6">
      <PageTitle kicker="Lakebase · Postgres operacional" tone="teal" title="Serving operacional ao vivo"
        sub="a fila, a rede de lojas e cada aprovação vivem em Postgres gerenciado — leitura em milissegundos, escrita transacional, governado pelo Databricks"
        right={<div className="text-right font-mono text-[11px] text-zinc-500 leading-relaxed"><span className="text-teal-300">●</span> {s.host.split('.')[0]}<div>{s.database} · serving + app</div><div>{s.postgres}</div></div>} />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Kpi label="leituras medidas" value={num(s.latency.calls)} sub="janela móvel desta instância do app" />
        <Kpi tone="emerald" label="latência p50" value={s.latency.p50 == null ? '—' : `${dec1(s.latency.p50)} ms`} sub="leitura real do app" />
        <Kpi tone="amber" label="latência p95" value={s.latency.p95 == null ? '—' : `${dec1(s.latency.p95)} ms`} sub={`máx ${s.latency.max == null ? '—' : dec1(s.latency.max)} ms`} />
        <Kpi label="conectado como" value={<span className="text-[13px] break-all">{s.connected_as.length > 20 ? s.connected_as.slice(0, 8) + '…' : s.connected_as}</span>} sub={s.connected_as.includes('@') ? 'usuário (execução local) · OAuth' : 'service principal do app · OAuth'} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Panel title={<span className="inline-flex items-center gap-2"><Table2 className="w-3.5 h-3.5 text-teal-300" />serving · publicado pelo job</span>}
          hint="trocado de forma atômica a cada run (uma transação)" right={<ProductTag>leitura</ProductTag>}>
          <div className="grid grid-cols-2 gap-2">
            {serving.map((t) => (
              <div key={t.table_name} className="rounded-lg border border-zinc-800 bg-zinc-950/60 px-3 py-2">
                <div className="text-[12px] font-mono text-zinc-200">{t.table_name}</div><div className="text-[11px] text-zinc-500 font-mono">{num(t.rows)} linhas</div>
              </div>
            ))}
          </div>
        </Panel>
        <Panel title={<span className="inline-flex items-center gap-2"><PenLine className="w-3.5 h-3.5 text-amber-300" />app · estado do aplicativo</span>}
          hint="criado uma vez, nunca apagado pelo job — é aqui que as decisões ficam" right={<ProductTag>leitura + escrita</ProductTag>}>
          <div className="grid grid-cols-2 gap-2 mb-5">
            {app.map((t) => (
              <div key={t.table_name} className="rounded-lg border border-amber-500/25 bg-amber-500/[0.05] px-3 py-2">
                <div className="text-[12px] font-mono text-zinc-200">{t.table_name}</div><div className="text-[11px] text-zinc-500 font-mono">{num(t.rows)} linhas</div>
              </div>
            ))}
          </div>
          <div className="space-y-4">
            <Sla label="mediana (p50)" v={s.latency.p50} target={50} />
            <Sla label="cauda (p95)" v={s.latency.p95} target={100} />
            <Sla label="cauda (p99)" v={s.latency.p99} target={200} />
          </div>
        </Panel>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Panel title="Escritas recentes · aprovações" hint="app.replenishment_actions" right={<ProductTag>atualiza a cada 5 s</ProductTag>} pad={false}>
          {s.recent_actions.length === 0 && <div className="px-5 py-6 text-[12px] text-zinc-500">Nenhuma aprovação ainda — aprove uma ação na Fila e ela aparece aqui.</div>}
          {s.recent_actions.map((r, i) => (
            <div key={i} className="px-5 py-2.5 border-b border-zinc-800/60 flex items-center gap-3 text-[12px]">
              <span className="font-mono text-zinc-500 w-[88px] shrink-0">{whenBR(r.decided_at)}</span>
              <span className={r.decision === 'APPROVED' ? 'text-emerald-300' : 'text-zinc-500'}>{r.decision === 'APPROVED' ? 'INSERT ✓' : 'INSERT ✕'}</span>
              <span className="flex-1 text-zinc-300 truncate">{r.product_name} · {r.store_name?.replace('LojaBR ', '')}</span>
              <span className="font-mono text-emerald-300">{r.decision === 'APPROVED' ? brl(r.revenue_protected) : ''}</span>
            </div>
          ))}
        </Panel>
        <Panel title={<span className="inline-flex items-center gap-2"><Database className="w-3.5 h-3.5 text-teal-300" />Escritas recentes · Genie</span>} hint="app.genie_interactions — cada pergunta fica auditável" pad={false}>
          {s.recent_genie.length === 0 && <div className="px-5 py-6 text-[12px] text-zinc-500">Pergunte algo ao Genie (botão âmbar) e a interação aparece aqui.</div>}
          {s.recent_genie.map((g, i) => (
            <div key={i} className="px-5 py-2.5 border-b border-zinc-800/60 text-[12px]">
              <div className="flex justify-between"><span className="text-zinc-300 truncate pr-3">{g.question}</span><span className="font-mono text-zinc-500">{whenBR(g.asked_at)}</span></div>
              <div className="text-[10.5px] text-zinc-500">{g.user_email} · {g.row_count} linhas · {(g.duration_ms / 1000).toFixed(1)} s</div>
            </div>
          ))}
        </Panel>
      </div>
    </div>
  );
}
