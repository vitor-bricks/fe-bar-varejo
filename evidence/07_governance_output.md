# S7 — Unity Catalog Governance — Execution Evidence

**Catalog:** `serverless_stable_xpbmim_catalog` · **Schemas (isolated):** `fe_bar_varejo_bronze`, `fe_bar_varejo_silver`, `fe_bar_varejo_gold`

Every table across the medallion is a UC-managed table with a column-typed schema and a
descriptive comment. Silver applies data-quality expectations; lineage bronze→silver→gold is
captured automatically by the Lakeflow pipeline. Queried from `information_schema.tables`
(internal DLT materialization/event-log tables omitted):

```
table_schema          | table_name                 | comment
fe_bar_varejo_bronze  | bronze_sales               | Raw POS sales (Auto Loader)
fe_bar_varejo_bronze  | bronze_inventory           | Raw inventory snapshots (Auto Loader)
fe_bar_varejo_bronze  | bronze_shelf_audit         | Raw shelf audits (Auto Loader)
fe_bar_varejo_bronze  | bronze_dim_store           | Raw store master
fe_bar_varejo_bronze  | bronze_dim_product         | Raw product master
fe_bar_varejo_silver  | silver_sales               | Typed, deduped POS sales
fe_bar_varejo_silver  | silver_inventory           | Typed, deduped inventory snapshots
fe_bar_varejo_silver  | silver_shelf_audit         | Typed shelf audits
fe_bar_varejo_silver  | silver_dim_store           | Cleaned store master
fe_bar_varejo_silver  | silver_dim_product         | Cleaned product master
fe_bar_varejo_gold    | gold_daily_store_sku       | Daily store×sku fact: inventory + sales + product/store attributes + lost revenue
fe_bar_varejo_gold    | gold_current_availability  | Latest snapshot per store×sku with stockout-risk fields (serves app, Genie, Lakebase)
fe_bar_varejo_gold    | gold_kpi_daily             | Daily chain-wide KPIs for the executive dashboard
fe_bar_varejo_gold    | gold_stockout_predictions  | ML scored risk + suggested reorder (written by S3)
fe_bar_varejo_gold    | gold_reorder_rationale     | GenAI reorder rationale (written by S3)
fe_bar_varejo_gold    | gold_model_metrics         | Model evaluation metrics (written by S3)
```

## Data-quality expectations (silver layer, from the pipeline code)

```python
@dlt.expect_or_drop("valid_price", "unit_price > 0")            # silver_dim_product
@dlt.expect_or_drop("non_negative_units", "units_sold >= 0")    # silver_sales
@dlt.expect("has_date", "sale_date IS NOT NULL")                # silver_sales
@dlt.expect_or_drop("non_negative_onhand", "on_hand_units >= 0")# silver_inventory
```

## Access control (least privilege)

The app service principal (`4f387a6d-76c2-49f8-bd49-d98039ff024d`) was granted only what it
needs: `USE CATALOG`, `USE SCHEMA` + `SELECT` on the gold schema, warehouse `CAN_USE`, a
Lakebase Postgres role with `SELECT`, and Genie space `CAN_RUN`. A registered model
`fe_bar_varejo_gold.stockout_risk` is versioned in UC.

## Isolation guarantee

Nothing pre-existing in the workspace was modified. All assets use the `fe_bar_varejo` /
`fe-bar-varejo` prefix; the `lojabr-warroom` app and existing catalogs are untouched.
