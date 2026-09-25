# S4 — Lakebase Operational Serving — Execution Evidence

**Lakebase project:** `projects/fe-bar-varejo` (Autoscaling tier, Postgres 16)
**Endpoint host:** `ep-royal-silence-d24b1cks.database.us-east-1.cloud.databricks.com`
**Database:** `retail` · served tables: `stockout_predictions`, `current_availability`, `kpi_daily`, `reorder_rationale`
**Loader:** `04_lakebase/04_lakebase_sync.py` (serverless notebook, psycopg2) — job **SUCCESS**
**Verification below:** run independently from a local `psql` client against the live endpoint.

## Row counts (queried from Lakebase Postgres)

```
          t           | count
----------------------+-------
 current_availability |  5000
 kpi_daily            |   120
 reorder_rationale    |    10
 stockout_predictions |  5000
(4 rows)
```

## Operational query — reorder worklist (what the app reads)

```
 store_id |   sku    |  category  | on_hand_units | suggested_order_units | expected_lost_revenue_7d
----------+----------+------------+---------------+-----------------------+--------------------------
 L119     | SKU10029 | Bebidas    |             0 |                     0 |                  8511.61
 L108     | SKU10055 | Bebidas    |             0 |                   133 |                  6246.88
 L108     | SKU10090 | Laticinios |            18 |                    31 |                  6035.94
 L105     | SKU10143 | Higiene    |            30 |                   101 |                  5188.13
 L112     | SKU10054 | Padaria    |            42 |                     3 |                  4915.87
(5 rows)
```

## Indexed point lookup

```sql
SELECT count(*) FROM stockout_predictions WHERE store_id='L108' AND risk_probability>0.8;
 count
-------
    24
Time: 147.950 ms   (round trip from a laptop over the public internet; in-region app reads are single-digit ms)
```

Indexes were created on `risk_rank`, `store_id` (predictions) and `store_id` (availability), so
the Control Tower app serves per-store reorder worklists at operational latency — decoupled from
the analytics warehouse used by Genie and dashboards.
