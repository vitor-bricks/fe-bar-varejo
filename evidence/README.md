# Execution evidence (text only)

The FE Bar evaluator reads text, so every stage below is backed by **real output committed as
text** — no screenshots. All of it comes from one orchestrated run of the job
`fe_bar_varejo_e2e` (**run `204235693781766`**, all 5 tasks SUCCESS), plus the Genie and app
checks run against the data that job produced.

| # | Stage | Evidence file | What it proves |
|---|---|---|---|
| 1 | Raw data (synthetic) | [`run_01_generate_raw_data.md`](run_01_generate_raw_data.md) | executed notebook **with cell outputs**: 20 stores, 129 items, 309,600 store×item×day rows, supplier on-time rates, stockout by category |
| 2 | Lakeflow medallion | [`run_02_lakeflow_pipeline.md`](run_02_lakeflow_pipeline.md) | pipeline update COMPLETED, row counts bronze→silver→gold, **7 data-quality expectations, 0 failed records** |
| 3 | ML early warning | [`run_03_early_warning_model.md`](run_03_early_warning_model.md) | executed notebook: AUC 0.85, precision@K 0.84 vs naive rule 0.39, measured warning lead, UC model registration, action queue |
| 4 | GenAI agent | [`run_04_replenishment_agent.md`](run_04_replenishment_agent.md) | executed notebook: tool calls per item and the agent's grounded decisions/rationales |
| 5 | Lakebase serving | [`run_05_lakebase_sync.md`](run_05_lakebase_sync.md) | executed notebook: atomic publish, row counts **read back from Postgres**, journey status |
| 6 | Genie | [`run_06_genie_qa.md`](run_06_genie_qa.md) | 6 PT-BR questions → Genie answer + generated SQL + rows (3 certified, 3 generalisation) |
| 7 | Databricks App | [`run_07_app_checks.md`](run_07_app_checks.md) | live API responses, approve → Lakebase write → KPI change, browser validation |

Re-generate: `python3 evidence/export_run.py <task_run_id> <out.md>` exports any executed
notebook task run with its outputs.
