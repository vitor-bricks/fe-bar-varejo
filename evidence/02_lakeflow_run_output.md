# S2 — Lakeflow Declarative Pipeline (Medallion) — Execution Evidence

**Notebook:** `02_lakeflow/02_lakeflow_medallion_pipeline.py`
**Pipeline:** `fe_bar_varejo_pipeline` (id `733e5172-5f51-404b-a790-b40cce95f015`), serverless, UC direct-publishing
**Last update:** `cd2347c0-dcd7-40bb-ad0c-946b8f07c4b2` — state **COMPLETED**
**Flow:** Auto Loader (`cloudFiles`) → bronze → silver (`@dlt.expect`) → gold, across 3 schemas

## Row counts across all medallion layers

```
t                              | n
bronze.bronze_inventory        | 600000
bronze.bronze_sales            | 600000
silver.silver_inventory        | 600000
silver.silver_sales            | 600000
gold.gold_daily_store_sku      | 600000
gold.gold_current_availability | 5000     (= 20 stores × 250 SKUs)
gold.gold_kpi_daily            | 120      (one row per day)
```

## Current availability — at-risk classification (gold_current_availability)

```
risk_flag | combos
0         | 2607
1         | 2393
```

## Top at-risk SKUs by velocity (sample)

```
store_id | sku      | category   | region       | on_hand | reorder_pt | stockout_days_7d | avg7d | risk_flag
L108     | SKU10029 | Bebidas    | Sudeste      | 220     | 254        | 0                | 89.4  | 1
L119     | SKU10029 | Bebidas    | Nordeste     | 0       | 289        | 1                | 87.0  | 1
L105     | SKU10008 | Hortifruti | Norte        | 184     | 222        | 0                | 80.0  | 1
L105     | SKU10233 | Bebidas    | Norte        | 153     | 186        | 0                | 75.7  | 1
L113     | SKU10029 | Bebidas    | Centro-Oeste | 9       | 182        | 0                | 66.3  | 1
```

## Daily KPIs — last 7 days (gold_kpi_daily)

```
snapshot_date | stockout_rate | lost_units | lost_revenue | revenue
2026-09-24    | 0.0500        | 1804       | 28063.14     | 681174.49
2026-09-23    | 0.0574        | 1620       | 24731.62     | 623391.71
2026-09-22    | 0.0598        | 1581       | 24605.99     | 572984.32
2026-09-21    | 0.0776        | 2293       | 35344.68     | 602280.32
2026-09-20    | 0.0878        | 3030       | 46369.78     | 812678.60   (Sunday — weekend demand spike)
2026-09-19    | 0.0742        | 3246       | 49917.49     | 1010690.05  (Saturday)
2026-09-18    | 0.0562        | 2222       | 34677.10     | 853518.88
```

## Business case headline (period totals)

```
lost_rev_120d | rev_120d      | lost_share | lost_rev_annualized
3,260,885.74  | 82,717,301.09 | 3.79%      | 9,918,527  (≈ R$ 9.9M / year)
```

**~R$ 9.9M/year in lost sales** from stockouts. Recovering even half is a **~R$ 5M/year**
prize — the quantified outcome the deck and roleplay lead with.

## Governance (Unity Catalog)

All tables are UC-managed with column-typed schemas, table comments, and silver-layer data
quality expectations (`@dlt.expect_or_drop("non_negative_units", ...)`). Lineage bronze→silver→gold
is captured automatically by the pipeline.
