# Databricks App — live checks against the deployed app

App: https://fe-bar-varejo-tower-7474654865387615.aws.databricksapps.com · executed 2026-09-28 09:44 -03

### GET /api/overview (KPIs read from Lakebase `serving`)

`HTTP 200` · 617 ms (laptop → app round trip)

```json
{
 "as_of": "2026-09-27",
 "days": 120,
 "lost_revenue_period": 784391.39,
 "lost_share": 0.0412,
 "lost_revenue_annualized": 2385857.0,
 "lost_revenue_7d": 60330.37,
 "stockout_rate_today": 0.0822,
 "stockout_rate_7d": 0.0653,
 "queue_size": 188,
 "queue_critical": 72,
 "revenue_at_risk_7d": 16843.39,
 "revenue_protectable_7d": 16174.77,
 "action_mix": [
  {
   "type": "EXPEDITE",
   "n": 142,
   "rs": 12884.07
  },
  {
   "type": "TRANSFER",
   "n": 39,
   "rs": 2866.94
  },
  {
   "type": "URGENT_ORDER",
   "n": 7,
   "rs": 423.76
  }
 ],
 "protected_today": 0.0,
 "approved_today": 0,
 "rejected_today": 0,
 "stores_in_alert": 3,
 "stores_total": 20,
 "trend": "120 daily points"
}
```

### GET /api/journey (status of each stage, written by the job's last run)

`HTTP 200` · 577 ms (laptop → app round trip)

```json
[
 {
  "step": "01",
  "stage": "Ingestão",
  "product": "Lakeflow · Auto Loader",
  "status": "ok",
  "detail": "7 feeds brutos (POS, estoque, pedidos, cadastros) no Volume landing",
  "job_run_id": "204235693781766",
  "updated_at": "2026-09-28T12:41:50.099463+00:00"
 },
 {
  "step": "02",
  "stage": "Medallion",
  "product": "Lakeflow Declarative Pipelines",
  "status": "completed",
  "detail": "bronze → silver → gold · update 22ab32bf",
  "job_run_id": "204235693781766",
  "updated_at": "2026-09-28T12:41:50.099463+00:00"
 },
 {
  "step": "03",
  "stage": "Governança",
  "product": "Unity Catalog",
  "status": "ok",
  "detail": "3 schemas · 28 tabelas · lineage + expectations",
  "job_run_id": "204235693781766",
  "updated_at": "2026-09-28T12:41:50.099463+00:00"
 },
 {
  "step": "04",
  "stage": "Modelo",
  "product": "MLflow · UC Model Registry",
  "status": "ok",
  "detail": "stockout_early_warning v6 · AUC 0.85",
  "job_run_id": "204235693781766",
  "updated_at": "2026-09-28T12:41:50.099463+00:00"
 },
 {
  "step": "05",
  "stage": "Agente",
  "product": "Foundation Model API · tool-calling",
  "status": "ok",
  "detail": "12 itens revisados · 4.0 ferramentas/item",
  "job_run_id": "204235693781766",
  "updated_at": "2026-09-28T12:41:50.099463+00:00"
 },
 {
  "step": "06",
  "stage": "Serving",
  "product": "Lakebase · Postgres",
  "status": "ok",
  "detail": "worklist, rede e aprovações em Postgres",
  "job_run_id": "204235693781766",
  "updated_at": "2026-09-28T12:41:50.099463+00:00"
 },
 {
  "step": "07",
  "stage": "Linguagem natural",
  "product": "Genie",
  "status": "ok",
  "detail": "espaço curado · 5 SQL certificados · entity matching",
  "job_run_id": "204235693781766",
  "updated_at": "2026-09-28T12:41:50.099463+00:00"
 }
]
```

### GET /api/queue?limit=3 (ranked action queue)

`HTTP 200` · 574 ms (laptop → app round trip)

```json
[
 {
  "priority": 1,
  "action_type": "EXPEDITE",
  "severity": "HIGH",
  "store_name": "LojaBR Moema",
  "product_name": "Sabão em Pó Omo Lavagem Perfeita 1,6kg",
  "from_store_name": null,
  "units": 26,
  "eta_days": 5,
  "risk_probability": 0.9693,
  "revenue_protected": 579.64,
  "rationale_source": "AGENTE",
  "rationale": "A loja Moema tem apenas 5 unidades em estoque, com venda média de 3,7 por dia e cobertura de 1,3 dias, enquanto o pedido de 26 unidades já em trânsito só chega em 5 dias; não há lojas doadoras a até 450 km. Recomendo expedir esse pedido, mesmo com o fornecedor Limpa Mais Distribuidora tendo pontualidade de 62,7% e atraso médio de 3,91 dias."
 },
 {
  "priority": 2,
  "action_type": "TRANSFER",
  "severity": "CRITICAL",
  "store_name": "LojaBR Campinas",
  "product_name": "Café Torrado e Moído Pilão 500g",
  "from_store_name": "LojaBR Ribeirão Preto",
  "units": 46,
  "eta_days": 2,
  "risk_probability": 0.8419,
  "revenue_protected": 429.62,
  "rationale_source": "AGENTE",
  "rationale": "A loja Campinas tem apenas 9 unidades em estoque, cobertura de 0,6 dia e o pedido do fornecedor Atacado Central (95 unidades) só chega em 2 dias, com esse fornecedor apresentando 83% de pontualidade e atraso médio de 2 dias quando falha. A loja Ribeirão Preto tem excedente de 61 unidades e 18,2 dias de cobertura, permitindo transferir 46 unidades rapidamente e evitar a ruptura iminente."
 },
 {
  "priority": 3,
  "action_type": "EXPEDITE",
  "severity": "HIGH",
  "store_name": "LojaBR Tatuapé",
  "product_name": "Picanha Bovina Resfriada (kg)",
  "from_store_name": null,
  "units": 10,
  "eta_days": 3,
  "risk_probability": 0.8765,
  "revenue_protected": 420.19,
  "rationale_source": "AGENTE",
  "rationale": "Não há loja doadora em até 450 km, mas já existe um pedido de 10 unidades a caminho da Frios Paraná Logística, previsto para chegar em 4 dias — tempo maior que a cobertura atual de apenas 1,2 dias com estoque de 2 unidades. Como o fornecedor tem 74,8% de pontualidade e atraso médio de 2,48 dias quando falha, recomenda-se expedir esse pedido para evitar ruptura antes da chegada."
 }
]
```

### POST /api/queue/ACT-976b4c378651/decide → write to Lakebase `app.replenishment_actions`

`HTTP 200` · 610 ms (laptop → app round trip)

```json
{
 "action_id": "ACT-976b4c378651",
 "decision": "APPROVED",
 "decided_by": "vitor.jardim@databricks.com",
 "revenue_protected": 579.64
}
```

### Effect of the approval

```text
protected_today: R$ 0.00  →  R$ 579.64
approved_today : 0  →  1
```

```text
queue item #1 status: APPROVED by vitor.jardim@databricks.com
```

### POST /api/genie/ask (Genie space via the app's service principal; turn logged to Lakebase)

`HTTP 200` · 41054 ms (laptop → app round trip)

```json
{
 "status": "COMPLETED",
 "answer": "Há **39 transferências recomendadas** entre lojas nesta fila, ordenadas pelo maior valor protegido. Alguns exemplos são:\n- **LojaBR Ribeirão Preto → LojaBR Campinas**: **46 unidades** de **Café Torrado e Moído Pilão 500g**, protegendo **R$ 429,62** (**207 km**)\n- **LojaBR Ribeirão Preto → LojaBR Tatuapé**: **20 unidades** de **Creme Dental Colgate Total 12 90g**, protegendo **R$ 177,28** (**292 km**)\n- **LojaBR Tatuapé → LojaBR Niterói**: **15 unidades** de **Arroz Branco Tipo 1 Tio João 5kg**, protegendo **R$ 131,14** (**362 km**)\n- **LojaBR Barra da Tijuca → LojaBR Moema**: **18 unidades** de **Achocolatado em Pó Nescau 400g**, protegendo **R$ 123,75** (**344 km**)\n- **LojaBR Santos → LojaBR Barra da Tijuca**: **25 unidades** de **Feijão Preto Kicaldo 1kg**, protegendo **R$ 114,11** (**321 km**)\nAs recomendações variam de **14 km a 392 km** e de **R$ 17,59 a R$ 429,62** em receita protegida, mostrando que há tanto transferências curtas quanto de longa distância na fila.",
 "sql": "SELECT from_store_name, store_name, product_name, units, transfer_km, revenue_protected\nFROM serverless_stable_xpbmim_catalog.fe_bar_varejo_gold.gold_replenishment_queue_final\nWHERE action_type = 'TRANSFER'\nORDER BY revenue_protected DESC",
 "columns": [
  "from_store_name",
  "store_name",
  "product_name",
  "units",
  "transfer_km",
  "revenue_protected"
 ],
 "rows": [
  [
   "LojaBR Ribeirão Preto",
   "LojaBR Campinas",
   "Café Torrado e Moído Pilão 500g",
   "46",
   "207.0",
   "429.62"
  ],
  [
   "LojaBR Ribeirão Preto",
   "LojaBR Tatuapé",
   "Creme Dental Colgate Total 12 90g",
   "20",
   "292.0",
   "177.28"
  ],
  [
   "LojaBR Tatuapé",
   "LojaBR Niterói",
   "Arroz Branco Tipo 1 Tio João 5kg",
   "15",
   "362.0",
   "131.14"
  ],
  [
   "LojaBR Barra da Tijuca",
   "LojaBR Moema",
   "Achocolatado em Pó Nescau 400g",
   "18",
   "344.0",
   "123.75"
  ],
  [
   "LojaBR Santos",
   "LojaBR Barra da Tijuca",
   "Feijão Preto Kicaldo 1kg",
   "25",
   "321.0",
   "114.11"
  ]
 ],
 "duration_ms": 40482
}
```

### GET /api/lakebase/status (connection, tables, measured read latency INSIDE the app, recent writes)

`HTTP 200` · 572 ms (laptop → app round trip)

```json
{
 "host": "ep-royal-silence-d24b1cks.database.us-east-1.cloud.databricks.com",
 "database": "retail",
 "postgres": "PostgreSQL 17.11 (8a81ecb) on x86_64-pc-linux-gnu",
 "connected_as": "4f387a6d-76c2-49f8-bd49-d98039ff024d",
 "latency": {
  "calls": 39,
  "p50": 3.3,
  "p95": 6.6,
  "p99": 7.8,
  "min": 2.6,
  "max": 7.8,
  "mean": 3.6
 },
 "tables": [
  {
   "table_schema": "app",
   "table_name": "genie_interactions",
   "rows": 1
  },
  {
   "table_schema": "app",
   "table_name": "replenishment_actions",
   "rows": 1
  },
  {
   "table_schema": "serving",
   "table_name": "journey_status",
   "rows": 7
  },
  {
   "table_schema": "serving",
   "table_name": "kpi_daily",
   "rows": 120
  },
  {
   "table_schema": "serving",
   "table_name": "model_card",
   "rows": 17
  },
  {
   "table_schema": "serving",
   "table_name": "position",
   "rows": 2580
  },
  {
   "table_schema": "serving",
   "table_name": "replenishment_queue",
   "rows": 188
  },
  {
   "table_schema": "serving",
   "table_name": "store_network",
   "rows": 20
  },
  {
   "table_schema": "serving",
   "table_name": "supplier_otif",
   "rows": 9
  }
 ],
 "recent_actions": [
  {
   "decision": "APPROVED",
   "decided_by": "vitor.jardim@databricks.com",
   "decided_at": "2026-09-28T12:44:53.521672+00:00",
   "revenue_protected": 579.64,
   "product_name": "Sabão em Pó Omo Lavagem Perfeita 1,6kg",
   "store_name": "LojaBR Moema"
  }
 ],
 "recent_genie": [
  {
   "asked_at": "2026-09-28T12:45:35.747814+00:00",
   "user_email": "vitor.jardim@databricks.com",
   "question": "Quais transferências entre lojas estão recomendadas?",
   "row_count": 39,
   "duration_ms": 40482,
   "status": "COMPLETED"
  }
 ]
}
```
