import React, { useState, useEffect } from "https://esm.sh/react@18.2.0";
import { createRoot } from "https://esm.sh/react-dom@18.2.0/client";
import htm from "https://esm.sh/htm@3.1.1";
const html = htm.bind(React.createElement);

// htm passes attributes straight to React.createElement, and React requires `style` to be an
// OBJECT, not a string. s() turns a CSS string into a React style object.
const s = (str) => Object.fromEntries(
  str.split(";").filter((x) => x.trim()).map((kv) => {
    const i = kv.indexOf(":");
    const k = kv.slice(0, i).trim().replace(/-([a-z])/g, (_, c) => c.toUpperCase());
    return [k, kv.slice(i + 1).trim()];
  })
);

const brl = (v) => "R$ " + Number(v || 0).toLocaleString("pt-BR", { maximumFractionDigits: 0 });
const pct = (v) => (Number(v || 0) * 100).toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + "%";
const api = (p, o) => fetch(p, o).then((r) => r.json());

function Source({ src }) {
  return html`<span class="src"><span class="pip"></span>fonte: ${src === "lakebase" ? "Lakebase (Postgres)" : "SQL Warehouse"}</span>`;
}

function KPIs({ k }) {
  if (!k) return html`<div class="loading">Carregando KPIs…</div>`;
  return html`<div class="kpis">
    <div class="kpi alert"><div class="label">Taxa de ruptura (hoje)</div>
      <div class="val">${pct(k.stockout_rate)}</div>
      <div class="foot">${k.latest_date}</div></div>
    <div class="kpi"><div class="label">Receita perdida (período)</div>
      <div class="val mono">${brl(k.lost_revenue_period)}</div>
      <div class="foot">≈ ${brl(k.lost_revenue_annualized)} / ano</div></div>
    <div class="kpi alert"><div class="label">Itens em risco agora</div>
      <div class="val">${(k.items_at_risk || 0).toLocaleString("pt-BR")}</div>
      <div class="foot">SKUs × loja com risco elevado</div></div>
    <div class="kpi"><div class="label">Receita (período)</div>
      <div class="val mono">${brl(k.revenue_period)}</div>
      <div class="foot">${k.days} dias monitorados</div></div>
  </div>`;
}

function TrendChart({ data }) {
  if (!data || !data.length) return null;
  const W = 640, H = 190, pad = 34;
  const rates = data.map((d) => d.stockout_rate);
  const maxR = Math.max(...rates) * 1.15 || 0.1;
  const x = (i) => pad + (i * (W - pad * 2)) / (data.length - 1);
  const y = (v) => H - pad - (v / maxR) * (H - pad * 2);
  const line = rates.map((v, i) => `${i === 0 ? "M" : "L"}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
  const area = `${line} L${x(data.length - 1).toFixed(1)},${H - pad} L${x(0).toFixed(1)},${H - pad} Z`;
  const ticks = [0, Math.floor(data.length / 2), data.length - 1];
  return html`<svg viewBox="0 0 ${W} ${H}" style=${s("width:100%;height:auto")}>
    <defs><linearGradient id="g" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stopColor="#ff3621" stopOpacity="0.35"/>
      <stop offset="100%" stopColor="#ff3621" stopOpacity="0"/></linearGradient></defs>
    ${[0, maxR / 2, maxR].map((v) => html`<g key=${v}>
      <line x1=${pad} x2=${W - pad} y1=${y(v)} y2=${y(v)} stroke="#2b3340"/>
      <text x=${4} y=${y(v) + 4} fill="#9aa7b4" fontSize="10">${(v * 100).toFixed(0)}%</text></g>`)}
    <path d=${area} fill="url(#g)"/>
    <path d=${line} fill="none" stroke="#ff3621" strokeWidth="2"/>
    ${ticks.map((i) => html`<text key=${i} x=${x(i)} y=${H - 10} fill="#9aa7b4" fontSize="10" textAnchor="middle">${data[i].date.slice(5)}</text>`)}
  </svg>`;
}

function RegionBars({ rows }) {
  if (!rows || !rows.length) return null;
  const max = Math.max(...rows.map((r) => r.expected_lost_revenue_7d)) || 1;
  return html`<div>${rows.map((r) => html`<div key=${r.region} style=${s("margin-bottom:10px")}>
    <div style=${s("display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px")}>
      <span>${r.region}</span><span class="mono">${brl(r.expected_lost_revenue_7d)}</span></div>
    <div style=${s("height:8px;background:#1c2230;border-radius:6px;overflow:hidden")}>
      <div style=${{ width: (r.expected_lost_revenue_7d / max) * 100 + "%", height: "100%", background: "linear-gradient(90deg,#ff3621,#ff6b35)" }}></div></div>
  </div>`)}</div>`;
}

function Worklist({ stores }) {
  const [store, setStore] = useState("");
  const [d, setD] = useState(null);
  useEffect(() => { api(`/api/worklist?limit=20${store ? "&store=" + store : ""}`).then(setD); }, [store]);
  return html`<div class="card">
    <div style=${s("display:flex;align-items:center;gap:12px;margin-bottom:10px")}>
      <div style=${s("flex:1")}><h3>Worklist de reposição — priorizado por receita em risco</h3>
        <div class="hint">Ranking do modelo de risco de ruptura (próximos 7 dias) com pedido sugerido</div></div>
      <select value=${store} onChange=${(e) => setStore(e.target.value)}>
        <option value="">Todas as lojas</option>
        ${(stores || []).map((st) => html`<option key=${st} value=${st}>${st}</option>`)}
      </select>
    </div>
    ${!d ? html`<div class="loading">Carregando…</div>` : html`<table>
      <thead><tr><th>#</th><th>Loja</th><th>SKU</th><th>Categoria</th><th class="num">Estoque</th>
        <th class="num">Risco</th><th class="num">Pedido</th><th class="num">Perda esp. 7d</th></tr></thead>
      <tbody>${d.items.map((it) => html`<tr key=${it.store_id + it.sku}>
        <td class="mono">${it.risk_rank}</td><td>${it.store_id}</td><td class="mono">${it.sku}</td>
        <td>${it.category}</td><td class="num">${it.on_hand_units}</td>
        <td class="num"><span class=${"badge " + (it.risk_probability >= 0.8 ? "hi" : "md")}>${pct(it.risk_probability)}</span></td>
        <td class="num">${it.suggested_order_units}</td>
        <td class="num">${brl(it.expected_lost_revenue_7d)}</td></tr>`)}</tbody>
    </table>`}
  </div>`;
}

function Rationale() {
  const [d, setD] = useState(null);
  useEffect(() => { api("/api/rationale").then(setD); }, []);
  return html`<div class="card">
    <h3>Recomendação de reposição — gerada por IA</h3>
    <div class="hint">Justificativa em linguagem natural (Foundation Model API · Claude Sonnet)</div>
    ${!d ? html`<div class="loading">Carregando…</div>` : d.items.slice(0, 5).map((r) => html`
      <div class="rationale" key=${r.store_id + r.sku}>
        <div class="meta">${r.store_id} · ${r.sku} · ${r.category} · risco ${pct(r.risk_probability)} · perda esp. ${brl(r.expected_lost_revenue_7d)} · pedido ${r.suggested_order_units} un</div>
        <div class="txt">${r.reorder_rationale}</div></div>`)}
  </div>`;
}

function Roadmap() {
  const items = [
    { t: "Disponibilidade em gôndola", d: "Previsão de ruptura + reposição priorizada", tag: "ATIVO", live: true },
    { t: "Previsão de demanda", d: "Forecast por SKU×loja alimentando o pedido", tag: "Módulo", live: false },
    { t: "Markdown / preço", d: "Remarcação para queimar excesso protegendo margem", tag: "Módulo", live: false },
    { t: "Next-best-offer", d: "Personalização sobre o comportamento do cliente", tag: "Módulo", live: false },
  ];
  return html`<div class="card"><h3>Plataforma — uma jornada de dados</h3>
    <div class="hint">Herói ativo hoje; módulos conectados na mesma base governada (Unity Catalog)</div>
    <div class="roadmap">${items.map((i) => html`<div key=${i.t} class=${"rm " + (i.live ? "live" : "")}>
      <div class=${"tag " + (i.live ? "" : "soon")}>${i.tag}</div>
      <div class="t">${i.t}</div><div class="d">${i.d}</div></div>`)}</div></div>`;
}

function Dashboard() {
  const [k, setK] = useState(null); const [tr, setTr] = useState(null);
  const [rg, setRg] = useState(null); const [stores, setStores] = useState([]);
  useEffect(() => {
    api("/api/kpis").then(setK); api("/api/trend").then(setTr);
    api("/api/regions").then(setRg); api("/api/stores").then(setStores);
  }, []);
  return html`<div>
    <${KPIs} k=${k} />
    <div class="grid2">
      <div class="card"><h3>Taxa de ruptura — tendência diária</h3>
        <div class="hint">Picos coincidem com fins de semana (maior demanda)</div>
        <${TrendChart} data=${tr} /></div>
      <div class="card"><h3>Receita em risco por região (7d)</h3>
        <div class="hint">Onde a perda esperada se concentra agora</div>
        <${RegionBars} rows=${rg} /></div>
    </div>
    <${Worklist} stores=${stores} />
    <${Rationale} />
    <${Roadmap} />
  </div>`;
}

function GenieTab() {
  const [q, setQ] = useState("Quais categorias têm a maior taxa de ruptura?");
  const [busy, setBusy] = useState(false); const [res, setRes] = useState(null);
  const suggestions = [
    "Qual a taxa de ruptura média dos últimos 7 dias?",
    "Quais as 5 lojas com maior receita perdida?",
    "Quantos itens estão em risco agora?",
    "Qual a receita perdida por região?",
  ];
  const ask = (question) => {
    setBusy(true); setRes(null);
    api("/api/genie", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question }) })
      .then(setRes).finally(() => setBusy(false));
  };
  return html`<div class="card">
    <h3>Pergunte ao Genie — em linguagem natural</h3>
    <div class="hint">Genie Space governado sobre as tabelas gold · responde em português com o SQL gerado</div>
    <div style=${s("display:flex;gap:8px;margin:12px 0")}>
      <input class="q" value=${q} onChange=${(e) => setQ(e.target.value)}
        onKeyDown=${(e) => e.key === "Enter" && ask(q)} placeholder="Ex.: quais lojas perderam mais receita?" />
      <button class="primary" disabled=${busy} onClick=${() => ask(q)}>${busy ? "Perguntando…" : "Perguntar"}</button>
    </div>
    <div style=${s("display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px")}>
      ${suggestions.map((sg) => html`<span key=${sg} class="chip" style=${s("cursor:pointer")} onClick=${() => { setQ(sg); ask(sg); }}>${sg}</span>`)}
    </div>
    ${busy && html`<div class="loading">Genie está gerando o SQL e consultando os dados…</div>`}
    ${res && res.answer && html`<div class="answer">${res.answer}</div>`}
    ${res && res.sql && html`<div><div class="hint">SQL gerado pelo Genie</div><pre class="sql">${res.sql}</pre></div>`}
    ${res && res.columns && html`<table style=${s("margin-top:12px")}><thead><tr>${res.columns.map((c) => html`<th key=${c}>${c}</th>`)}</tr></thead>
      <tbody>${(res.rows || []).slice(0, 10).map((row, i) => html`<tr key=${i}>${row.map((v, j) => html`<td key=${j}>${v}</td>`)}</tr>`)}</tbody></table>`}
    ${res && res.error && html`<div class="loading">Não foi possível responder: ${res.error}</div>`}
  </div>`;
}

function App() {
  const [tab, setTab] = useState("torre");
  const [health, setHealth] = useState(null);
  useEffect(() => { api("/api/health").then(setHealth); }, []);
  return html`<div>
    <header class="top"><div class="wrap">
      <div class="brand"><div class="dot"></div>
        <div><h1>LojaBR Varejo · Torre de Controle</h1>
          <div class="sub">Disponibilidade em gôndola — prever e prevenir ruptura de estoque</div></div>
        ${health && html`<${Source} src=${health.source} />`}
      </div>
      <div class="tabs">
        <div class=${"tab " + (tab === "torre" ? "active" : "")} onClick=${() => setTab("torre")}>Torre de Controle</div>
        <div class=${"tab " + (tab === "genie" ? "active" : "")} onClick=${() => setTab("genie")}>Pergunte ao Genie</div>
      </div>
    </div></header>
    <div class="wrap" style=${s("padding-top:8px;border-left:1px solid #2b3340;border-right:1px solid #2b3340")}>
      ${tab === "torre" ? html`<${Dashboard} />` : html`<${GenieTab} />`}
    </div>
  </div>`;
}

createRoot(document.getElementById("root")).render(html`<${App} />`);
