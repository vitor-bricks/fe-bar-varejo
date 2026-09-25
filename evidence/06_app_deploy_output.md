# S6 — Databricks App (Control Tower) — Execution Evidence

**App:** `fe-bar-varejo-tower` · **URL:** https://fe-bar-varejo-tower-7474654865387615.aws.databricksapps.com
**Stack:** FastAPI backend + React (CDN/htm, build-free) frontend
**Deploy:** `App started successfully` (state SUCCEEDED)
**Data path:** reads **Lakebase (Postgres)** operationally, with SQL-warehouse fallback; Genie tab proxies the Genie Space.
**Auth:** app service principal `4f387a6d-76c2-49f8-bd49-d98039ff024d` granted a Lakebase Postgres role (SELECT), warehouse CAN_USE, gold SELECT, and Genie space CAN_RUN.

All responses below are **live** from the deployed app (called with a bearer token).

## `GET /api/health`
```json
{"ok":true,"source":"lakebase","latency_ms":646.4}
```

## `GET /api/kpis` — reads from Lakebase
```json
{"source":"lakebase","latest_date":"2026-09-24","stockout_rate":0.05,
 "lost_revenue_today":28063.14,"revenue_today":681174.49,
 "lost_revenue_period":3260885.74,"revenue_period":82717301.09,
 "lost_revenue_annualized":9918527.0,"items_at_risk":2393,"days":120}
```

## `GET /api/worklist?limit=3` — priority reorder list from Lakebase
```
source lakebase
  1 L119 SKU10029 Bebidas    risk 0.9976 lost 8511.61
  2 L108 SKU10055 Bebidas    risk 0.9999 lost 6246.88
  3 L108 SKU10090 Laticinios risk 0.9995 lost 6035.94
```

## `GET /api/regions` — expected 7-day lost revenue by region
```json
[{"region":"Nordeste","expected_lost_revenue_7d":343690.3,"items":1500},
 {"region":"Sudeste","expected_lost_revenue_7d":267954.45,"items":1250},
 {"region":"Centro-Oeste","expected_lost_revenue_7d":164135.55,"items":1000},
 {"region":"Sul","expected_lost_revenue_7d":137934.41,"items":1000}, ...]
```

## `GET /api/rationale` — GenAI reorder rationale (from Lakebase)
```
source lakebase | items 10
  L119 SKU10029 -> "O SKU10029 está com estoque zerado na loja L119, mas vende em média 87 un/dia — a ruptura está confirmada (100%)..."
```

## `POST /api/genie {"question":"Quantos itens estao em risco agora?"}` — live Genie
```
answer: "Há 5.000 itens ... em gold_stockout_predictions ... risk_probability > 0 ..."
sql:    SELECT COUNT(*) AS itens_em_risco_agora FROM ...gold_stockout_predictions WHERE snapshot_date = (SELECT MAX(...
```

## Static SPA served
```
GET /                 -> http=200  text/html  561 bytes  (<title>LojaBR Varejo · Torre de Controle</title>)
GET /static/app.js    -> http=200  text/javascript  11248 bytes  (parses with no syntax errors)
GET /static/styles.css-> http=200  4741 bytes
```

The app surfaces the whole journey to the business: KPI tiles, stockout-rate trend, region
risk, the ranked reorder worklist (ML), the AI rationale (GenAI), and a live natural-language
Genie tab — all reading the governed data, served operationally from Lakebase.

## UI validation (browser, Chrome DevTools)

Validated interactively in a browser. Result: **no JavaScript/React errors**; all elements
render — 4 KPI tiles (5,0% · R$ 3.260.886 · 2.393 · R$ 82.717.301), the stockout-rate SVG
trend, the region bars, the reorder worklist table, and the AI rationale cards. The
"Pergunte ao Genie" tab returns a live answer + generated SQL + result table
(*"Atualmente há 2.393 itens com risk_flag = 1…"*).

> Fixed during validation: `style` was passed to htm as a string, which React rejects
> (React error #62). Converted all inline styles to objects via a small CSS-string→object
> helper; redeployed and re-validated clean.
