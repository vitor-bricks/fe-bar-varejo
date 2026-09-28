# Executed pipeline — Lakeflow Declarative Pipeline `fe_bar_varejo_pipeline`

Task `02_lakeflow_medallion` of job run `204235693781766` (job `fe_bar_varejo_e2e`), full refresh.
Source: `02_lakeflow/02_lakeflow_medallion_pipeline.py`. Queried after the run via the Databricks API and SQL.

## Pipeline update
```text
pipeline fe_bar_varejo_pipeline | latest update 22ab32bf-c075-4e89-a2e4-26cfafa9d167 COMPLETED 2026-09-28T12:34:17.153Z
```

## Row counts per medallion layer (Unity Catalog)
```text
t | n
silver.silver_open_orders | 1344
bronze.bronze_sales | 309600
bronze.bronze_inventory | 309600
bronze.bronze_purchase_orders | 37882
silver.silver_sales | 309600
silver.silver_inventory | 309600
silver.silver_purchase_orders | 37882
gold.gold_daily_store_sku | 309600
gold.gold_current_position | 2580
gold.gold_supplier_otif | 9
gold.gold_store_network | 20
gold.gold_kpi_daily | 120
```

## Data-quality expectations — results of this update (from the pipeline event log)
```text
dataset | expectation | passed | failed
silver_dim_product | valid_price | 129 | 0
silver_dim_store | store_id_present | 20 | 0
silver_inventory | non_negative_onhand | 309600 | 0
silver_open_orders | positive_qty | 1344 | 0
silver_purchase_orders | arrival_after_order | 37882 | 0
silver_sales | has_date | 309600 | 0
silver_sales | non_negative_units | 309600 | 0
```

Query used: `explode(details:flow_progress.data_quality.expectations)` on the UC event-log table
`fe_bar_varejo_gold.event_log_733e5172_...` filtered by this update id.
