# LojaBR · Centro de Abastecimento — stop stockouts before the shelf empties

> **FE Bar submission · Industry: Retail (supermarkets).** 100% synthetic data.

## The outcome

A Brazilian supermarket chain (20 stores) loses sales every day to **stockouts**: the product is
missing from the shelf, the shopper buys elsewhere. Replenishment teams find out *after* the shelf
is empty.

**Measured on the chain's data:** stockouts cost **R$ 2.39 M/year** on this 129-item high-turnover
sample, which is **4.1% of sales**, in line with the ~4% retail benchmark.

The **Centro de Abastecimento** predicts which items *still on the shelf* will run out in the next
7 days (≈ **2.9 days of warning**). For each item it proposes the cheapest fix: **transfer from a
nearby store with excess, expedite the order already in transit, or place an urgent order**. A
manager approves it in one click; the decision is stored with the approver's name and "R$
protected today" moves on screen.

| Buyer KPI | Today | With the Centro de Abastecimento |
|---|---|---|
| Stockout rate (store × item × day) | 6.5% (last 7 days) | target **< 4.5%** |
| Sales lost to stockouts | R$ 2.39 M/yr (4.1% of sales) | recover **~⅓ ≈ R$ 0.8 M/yr** on this sample |
| Warning before the shelf empties | none (reactive) | **~2.9 days** |
| Work list | intuition, whole assortment | **8% of items**, ranked by R$ |

**Assumptions:** the queue from the evidence run (data through 2026-09-27) protects R$ 16.2 k over
the next 7 days (risk-weighted expected value), ≈ 27% of the R$ 60 k lost last week. Annualized and at full approval this is ≈ R$ 0.84 M/yr,
≈ 35% of the loss. **Rule of thumb for the full chain:** every R$ 100 M of sales carries ~R$ 4 M of
stockout loss; recovering a third is **~R$ 1.4 M per R$ 100 M of sales**.

## The integrated journey (one job, one run id)

```
raw feeds ──▶ Lakeflow ──▶ Unity Catalog ──▶ ML model ──▶ AI agent ──▶ Lakebase ──▶ Databricks App
(POS, stock,   Auto Loader   bronze/silver/gold  early warning  tool-calling   serving +     approve →
 POs, masters) + medallion   + expectations      (MLflow, UC)   (FMAPI)        app state     persisted
                                    └────────────▶ Genie (natural language, curated)
```

| Stage | What it does | Code |
|---|---|---|
| **Lakeflow** | Auto Loader ingests 7 raw feeds; declarative medallion with 7 data-quality expectations | `01_ingestion/`, `02_lakeflow/` |
| **Unity Catalog** | 3 governed schemas, lineage, comments, registered model, least-privilege grants | throughout |
| **ML** | Stockout early warning for in-stock items; beats the planner rule (precision@K 0.84 vs 0.38) | `03_ml_genai/03_early_warning_model.py` |
| **GenAI agent** | Tool-calling agent checks position, nearby donors and supplier history, then decides and explains | `03_ml_genai/04_replenishment_agent.py` |
| **Lakebase** | `serving` (atomic publish) + `app` (approvals, Genie log); the app reads and writes here | `04_lakebase/05_lakebase_sync.py` |
| **Genie** | Curated space: entity matching, metric definitions, certified SQL | `05_genie/` |
| **App** | React + Vite + TS + Tailwind / FastAPI — home, store network map, action queue, agent room, Lakebase live, and a live architecture view whose stages open the real notebooks, pipeline, UC objects, Lakebase and Genie in the workspace | `06_app/` |
| **Orchestration** | Job `fe_bar_varejo_e2e`, 5 tasks, daily 06:00 BRT | `07_orchestration/job_e2e.json` |

## Live resources

| Resource | Identifier |
|---|---|
| App | https://fe-bar-varejo-tower-7474654865387615.aws.databricksapps.com |
| Job | `fe_bar_varejo_e2e` (id `384370635751593`) — evidence run `204235693781766` |
| Lakeflow pipeline | `fe_bar_varejo_pipeline` (`733e5172-5f51-404b-a790-b40cce95f015`) |
| UC schemas | `serverless_stable_xpbmim_catalog.fe_bar_varejo_{bronze,silver,gold}` |
| Model | `…fe_bar_varejo_gold.stockout_early_warning` |
| Agent LLM | `databricks-claude-sonnet-5` (Foundation Model API) |
| Lakebase | project `fe-bar-varejo`, database `retail`, schemas `serving` / `app` |
| Genie space | `01f1b906cf2d15b4b1c72c3b25ddb2f0` |

The job re-runs every morning and the data always closes yesterday, so the live app's queue and
stores in alert change from day to day. The headline loss stays at 4.1–4.2% of sales (R$ 2.37–2.45
M/yr). Figures in this README and the deck come from the evidence run. `deck/demo_prep.py` prints
the current day's figures from the deployed app.

## Read the evidence

Everything ran: see **[`evidence/README.md`](evidence/README.md)**. It contains executed notebooks
exported **with their cell outputs**, pipeline expectation results, Postgres read-backs, Genie Q&A
with generated SQL, and live app API responses, all as text.

## More

- **[`DECISIONS.md`](DECISIONS.md)**: trade-offs, including a correction to this build's first version.
- **[`AI_USAGE.md`](AI_USAGE.md)**: how AI was used as a teammate (planner / generator / evaluator).
- **[`deck/`](deck/)**: business deck and roleplay prep.

Isolation: everything uses the `fe_bar_varejo` / `fe-bar-varejo` prefix; no pre-existing asset in
the workspace was modified.
