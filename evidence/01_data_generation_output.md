# S1 — Synthetic Data Generation — Execution Evidence

**Notebook:** `01_ingestion/01_generate_synthetic_data.py`
**Executed on:** Databricks serverless (job run `fe_bar_varejo_S1_datagen`) — result **SUCCESS**
**Landing zone:** `/Volumes/serverless_stable_xpbmim_catalog/fe_bar_varejo_bronze/landing/`
**Period:** 2026-05-28 .. 2026-09-24 (120 days) · seed = 42 · 100% synthetic

## Row counts (queried from landed CSV via `read_files`)

```
t                    | n
dim_product          | 250
dim_store            | 20
fact_inventory_daily | 600000
fact_sales_daily     | 600000
fact_shelf_audit     | 42859
```

## Stockout signal (the whole point of the use case)

```
stockout_rate | total_lost_units
0.055         | 207191
```

Overall **5.5% stockout rate** and **207,191 lost units** over the period — in line with the
retail industry benchmark of 5–10% on-shelf unavailability.

## Stockout rate by category (genuine, structured signal)

```
category    | stockout_rate | lost_units
Higiene     | 0.0758        | 18291
Limpeza     | 0.0668        | 19074
Congelados  | 0.0613        | 18067
Mercearia   | 0.0582        | 21519
Bebidas     | 0.0523        | 41778
Laticinios  | 0.0449        | 19490
Hortifruti  | 0.0433        | 46672
Padaria     | 0.0405        | 22300
```

Categories with longer supplier lead times (Higiene, Limpeza, Congelados) show the highest
stockout rates — exactly the pattern the ML model in S3 will learn to predict. High-velocity
categories (Bebidas, Hortifruti) drive the largest absolute lost-unit volume.

## Sample rows

See `data/samples/` for the first rows of each table (`dim_store.csv`, `dim_product.csv`,
`fact_*_sample.csv`).
