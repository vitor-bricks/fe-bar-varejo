# Retail Intelligence Control Tower — On-Shelf Availability

> **FE Bar submission — Industry: Retail (Varejo).**
> End-to-end Databricks data journey that predicts and prevents **stockouts / on-shelf
> unavailability** for a multi-store retail chain, and surfaces it to store-ops as a
> live control tower. All data is **synthetic** (no customer data).

---

## The business problem

For a physical retail chain, a product that is **out on the shelf is a lost sale** — and
repeat unavailability pushes shoppers to competitors. Industry benchmarks put **on-shelf
availability (OSA)** gaps at **5–10% of SKUs at any time**, translating to **~4% of annual
revenue** in lost sales. The operational pain: replenishment teams react *after* the shelf
is already empty, using stale reports.

**Our customer — "LojaBR Varejo"** (synthetic), a chain with multiple stores across Brazil —
wants to move from *reactive* to *predictive* replenishment.

### The outcome we drive

| KPI | Baseline | Target with Control Tower |
|-----|----------|---------------------------|
| Stockout rate (SKU×store) | ~8% | **< 4%** |
| Lost sales recovered | — | **R$ (quantified in deck)** |
| Replenishment lead reaction | after empty shelf | **hours ahead (predicted risk)** |
| Sell-through | baseline | **+ via demand-aligned reorders** |

---

## The solution — one integrated journey

A **Retail Intelligence Control Tower** anchored on the stockout hero use case, with
connected modules (demand forecast, markdown, next-best-offer) on the same data journey.

```
Raw synthetic data ──▶ Lakeflow ──▶ Unity Catalog ──▶ ML + GenAI ──▶ Lakebase ──▶ Databricks App
   (POS, stock,        (ingest +     (govern:          (stockout      (operational   (Control Tower
    shelf audits,       medallion     catalog/          risk model +   serving of     + embedded
    product/store)      bronze→gold)  schemas/lineage)  GenAI reason)  reco to app)   Genie)
                                              │
                                              └──▶ Genie Space (natural-language querying)
```

| Stage | What it does | Where |
|-------|--------------|-------|
| **Lakeflow** | Ingest raw synthetic feeds → bronze; declarative medallion bronze→silver→gold | `02_lakeflow/` |
| **Unity Catalog** | Governs the data: catalog `serverless_stable_xpbmim_catalog`, schemas `fe_bar_varejo_{bronze,silver,gold}`, comments, tags, lineage | throughout |
| **ML + GenAI** | Stockout-risk model (per SKU×store) registered in UC/MLflow + GenAI reorder rationale via Foundation Model API | `03_ml_genai/` |
| **Lakebase** | Operational Postgres serving at-risk SKUs + reorder recommendations to the app | `04_lakebase/` |
| **Genie** | Natural-language querying over gold tables | `05_genie/` |
| **Databricks App** | React + FastAPI control tower surfacing it to store-ops | `06_app/` |

---

## Decisions, trade-offs & how it was built

- **[`DECISIONS.md`](DECISIONS.md)** — the key choices and trade-offs (scenario scope, synthetic
  simulation, serverless execution, medallion pipeline, ranking by money, Lakebase + warehouse, …).
- **[`AI_USAGE.md`](AI_USAGE.md)** — how AI (Claude Code + harness engineering) was used as a
  teammate: planner/generator/evaluator roles, the bugs it caught and fixed, and the tooling.

## How to read the execution evidence (for the evaluator)

This build commits **execution output as text**, not screenshots:

- `evidence/` — consolidated run outputs, query results, and model output as `.md`/`.txt`.
- Notebooks under `02_lakeflow/`, `03_ml_genai/` are committed **with cell outputs visible**.
- SQL results and Lakebase query output are committed as text.
- Genie natural-language Q&A committed as text in `05_genie/`.

See [`evidence/README.md`](evidence/README.md) for the index of what ran and where its
output lives.

---

## Live resources (the integrated journey, deployed)

| Stage | Resource | Identifier |
|-------|----------|------------|
| Landing | UC Volume | `serverless_stable_xpbmim_catalog.fe_bar_varejo_bronze.landing` |
| Lakeflow | Declarative Pipeline | `fe_bar_varejo_pipeline` (`733e5172-5f51-404b-a790-b40cce95f015`) |
| Unity Catalog | Schemas | `fe_bar_varejo_{bronze,silver,gold}` |
| ML | UC-registered model | `serverless_stable_xpbmim_catalog.fe_bar_varejo_gold.stockout_risk` |
| GenAI | Foundation Model | `databricks-claude-sonnet-5` |
| Lakebase | Postgres (Autoscaling) | `projects/fe-bar-varejo` · db `retail` |
| Genie | Genie Space | `01f1b906cf2d15b4b1c72c3b25ddb2f0` |
| App | Databricks App | `fe-bar-varejo-tower` |

**App URL:** https://fe-bar-varejo-tower-7474654865387615.aws.databricksapps.com

## Isolation note

This build is **fully isolated** and does not modify any pre-existing asset in the
workspace. All resources use the `fe_bar_varejo` / `fe-bar-varejo` prefix in a
dedicated set of schemas.

## Repository layout

```
01_ingestion/   synthetic data generation
02_lakeflow/    Lakeflow ingestion + medallion pipeline
03_ml_genai/    stockout-risk ML model + GenAI reorder rationale
04_lakebase/    Lakebase (Postgres) operational serving
05_genie/       Genie space setup + example NL Q&A
06_app/         React + FastAPI Databricks App
evidence/       execution evidence (text) index
deck/           business presentation deck
data/           synthetic data schema / samples
```
