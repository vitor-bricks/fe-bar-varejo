import { Link } from 'react-router-dom';
import { Area, Bar, CartesianGrid, ComposedChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { ArrowUpRight, CheckCircle2, Database, GitBranch, Layers, Bot, Brain, Sparkles, ShieldCheck, Workflow } from 'lucide-react';
import { api, usePoll, type Journey, type Overview } from '../lib/api';
import { brl, dateBR, pct, num, dec1, timeBR } from '../lib/format';
import { ACTION, ErrorBox, Kpi, Loading, Panel, ProductTag } from '../components/ui';

const STEP_ICON = [Workflow, GitBranch, ShieldCheck, Brain, Bot, Database, Sparkles];

function JourneyStrip({ j }: { j: Journey }) {
  const run = j.steps[0];
  return (
    <Panel title="A jornada de dados · um único job"
      hint="do dado bruto à decisão aprovada — cada estágio abaixo mostra o que realmente rodou no último run"
      right={run && <div className="text-right text-[10.5px] font-mono text-zinc-500">job run {run.job_run_id}<div>{dateBR(run.updated_at)} · {timeBR(run.updated_at)}</div></div>}>
      <div className="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-7 gap-3">
        {j.steps.map((s, i) => {
          const Icon = STEP_ICON[i] ?? Layers;
          return (
            <div key={s.step} className="relative">
              {i < j.steps.length - 1 && (
                <div className="hidden xl:block absolute top-6 -right-3 w-3 h-px bg-zinc-700 overflow-visible">
                  <span className="flow-dot absolute -top-[2px] w-1.5 h-1.5 rounded-full bg-amber-400" style={{ animationDelay: `${i * 0.35}s` }} />
                </div>
              )}
              <div className="h-full rounded-lg border border-zinc-800 bg-zinc-950/60 p-3">
                <div className="flex items-center justify-between">
                  <div className="w-7 h-7 rounded-md bg-amber-500/10 border border-amber-500/30 grid place-items-center"><Icon className="w-3.5 h-3.5 text-amber-300" /></div>
                  <CheckCircle2 className={`w-3.5 h-3.5 ${['ok', 'completed'].includes(s.status) ? 'text-emerald-400' : 'text-amber-400'}`} />
                </div>
                <div className="text-[12.5px] font-semibold text-zinc-100 mt-2">{s.stage}</div>
                <ProductTag>{s.product}</ProductTag>
                <div className="text-[11px] text-zinc-400 mt-1.5 leading-snug">{s.detail}</div>
              </div>
            </div>
          );
        })}
      </div>
    </Panel>
  );
}

function Trend({ o }: { o: Overview }) {
  const data = o.trend.map((t) => ({ ...t, d: dateBR(t.date), rate: +(t.stockout_rate * 100).toFixed(2) }));
  return (
    <Panel title="Ruptura na rede" hint={`taxa diária de ruptura (%) e receita perdida · ${o.days} dias`} right={<ProductTag>Lakeflow · gold_kpi_daily</ProductTag>}>
      <div className="h-[230px]">
        <ResponsiveContainer>
          <ComposedChart data={data} margin={{ top: 6, right: 6, bottom: 0, left: -18 }}>
            <defs><linearGradient id="gr" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#f59e0b" stopOpacity={0.45} /><stop offset="100%" stopColor="#f59e0b" stopOpacity={0} /></linearGradient></defs>
            <CartesianGrid stroke="#27272a" vertical={false} />
            <XAxis dataKey="d" tick={{ fill: '#71717a', fontSize: 10 }} interval={14} tickLine={false} axisLine={{ stroke: '#3f3f46' }} />
            <YAxis yAxisId="r" tick={{ fill: '#71717a', fontSize: 10 }} tickFormatter={(v) => `${v}%`} tickLine={false} axisLine={false} />
            <YAxis yAxisId="l" orientation="right" hide />
            <Tooltip contentStyle={{ background: '#09090b', border: '1px solid #3f3f46', borderRadius: 8, fontSize: 12 }}
              formatter={(v: number, k: string) => (k === 'rate' ? [`${dec1(v)}%`, 'ruptura'] : [brl(v), 'receita perdida'])} />
            <Bar yAxisId="l" dataKey="lost_revenue" fill="#ef4444" fillOpacity={0.25} barSize={3} />
            <Area yAxisId="r" type="monotone" dataKey="rate" stroke="#f59e0b" strokeWidth={2} fill="url(#gr)" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <div className="text-[11px] text-zinc-500 mt-2">picos em sábados e domingos (demanda maior) e em categorias com fornecedores impontuais — limpeza e higiene.</div>
    </Panel>
  );
}

function Mix({ o }: { o: Overview }) {
  const max = Math.max(1, ...o.action_mix.map((m) => m.rs));
  return (
    <Panel title="Como a fila é resolvida" hint="a ação certa por item — mais rápida e barata primeiro" right={<ProductTag>modelo + agente</ProductTag>}>
      <div className="space-y-4">
        {o.action_mix.map((m) => {
          const A = ACTION[m.type];
          return (
            <div key={m.type}>
              <div className="flex items-center justify-between text-[12px]">
                <span className={`inline-flex items-center gap-2 font-semibold ${A.tone}`}><A.icon className="w-4 h-4" />{A.label}</span>
                <span className="font-mono text-zinc-300">{m.n} ações · <span className="text-emerald-300">{brl(m.rs)}</span></span>
              </div>
              <div className="h-1.5 rounded-full bg-zinc-800 mt-1.5 overflow-hidden"><div className="h-full rounded-full bg-gradient-to-r from-amber-400 to-orange-500" style={{ width: `${(m.rs / max) * 100}%` }} /></div>
            </div>
          );
        })}
      </div>
      <Link to="/fila" className="mt-5 flex items-center justify-center gap-2 w-full py-2 rounded-lg border border-amber-500/40 bg-amber-500/10 text-amber-300 text-[12px] font-bold uppercase tracking-wider hover:bg-amber-500/20">
        abrir fila de ação <ArrowUpRight className="w-4 h-4" />
      </Link>
    </Panel>
  );
}

function ModelCard({ m }: { m: Record<string, number> }) {
  const items = [
    ['AUC (teste, datas futuras)', dec1((m.test_auc ?? 0) * 100) + '%', 'separa bem quem vai romper de quem não vai'],
    ['Acerto no top-K diário', pct(m.precision_at_k_daily, 0), `vs ${pct(m.naive_precision, 0)} da regra "cobertura < lead time"`],
    ['Antecedência do alerta', `${dec1(m.avg_warning_lead_days)} dias`, `${pct(m.share_warned_2plus_days, 0)} dos alertas com ≥ 2 dias`],
    ['Fila / sortimento', pct(m.queue_share_of_assortment, 1), `${num(m.queue_size)} de ${num(m.in_stock_scored)} itens em gôndola`],
  ];
  return (
    <Panel title="Por que confiar no alerta" hint="modelo de alerta antecipado · só itens AINDA em gôndola · validação temporal" right={<ProductTag>MLflow · UC Model Registry</ProductTag>}>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {items.map(([k, v, s]) => (
          <div key={k}><div className="text-[10px] uppercase tracking-[0.18em] text-zinc-500">{k}</div>
            <div className="font-mono text-xl text-zinc-100 font-bold mt-1">{v}</div><div className="text-[11px] text-zinc-500 mt-0.5">{s}</div></div>
        ))}
      </div>
    </Panel>
  );
}

export default function Home() {
  const [o, , e1] = usePoll(api.overview, 15000);
  const [j, , e2] = usePoll(api.journey, 60000);
  return (
    <div className="space-y-6">
      <section className="flex items-end justify-between gap-8 flex-wrap pt-2">
        <div className="max-w-3xl">
          <div className="text-[10px] uppercase tracking-[0.3em] text-amber-400 font-bold">LojaBR · abastecimento preditivo</div>
          <h1 className="text-5xl md:text-6xl font-bold tracking-tight leading-[1.02] mt-3">
            Centro de <span className="bg-gradient-to-r from-amber-300 via-amber-400 to-orange-500 bg-clip-text text-transparent">Abastecimento</span>
          </h1>
          <p className="text-[17px] text-zinc-400 mt-4 leading-relaxed">
            Antecipamos a <span className="text-zinc-100 font-medium">ruptura antes da gôndola esvaziar</span> e colocamos a ação certa — <span className="text-zinc-100 font-medium">transferir, antecipar ou pedir</span> — na mão de quem decide. Tudo nativo no Databricks.
          </p>
        </div>
        <div className="text-right shrink-0">
          <div className="text-[9px] uppercase tracking-[0.25em] text-zinc-500 font-semibold mb-1">powered by</div>
          <div className="text-[13px] tracking-wide text-zinc-300 font-semibold">DATABRICKS · MOSAIC AI</div>
          <div className="text-[11px] uppercase tracking-[0.18em] text-zinc-500 mt-0.5">unity catalog · lakeflow · lakebase · genie</div>
        </div>
      </section>

      <ErrorBox err={e1 || e2} />
      {!o ? <Loading /> : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <Kpi tone="red" label="Venda perdida por ruptura · ano" value={brl(o.lost_revenue_annualized)}
            sub={`${pct(o.lost_share)} da venda · medido em ${o.days} dias`} />
          <Kpi tone="amber" label="Em risco · próximos 7 dias" value={brl(o.revenue_at_risk_7d)}
            sub={`${num(o.queue_size)} itens na fila · ${num(o.queue_critical)} críticos`} />
          <Kpi tone="emerald" label="Protegido hoje" value={brl(o.protected_today)}
            sub={`${o.approved_today} ações aprovadas · de ${brl(o.revenue_protectable_7d)} possíveis`} />
          <Kpi label="Lojas em alerta" value={<>{o.stores_in_alert}<span className="text-zinc-500 text-lg"> / {o.stores_total}</span></>}
            sub={`ruptura hoje ${pct(o.stockout_rate_today)} · 7d ${pct(o.stockout_rate_7d)}`} />
        </div>
      )}
      {j && <JourneyStrip j={j} />}
      {o && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2"><Trend o={o} /></div>
          <Mix o={o} />
        </div>
      )}
      {j && <ModelCard m={j.model} />}
    </div>
  );
}
