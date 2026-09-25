# S3 — Stockout-Risk Model — Execution Evidence

**Notebook:** `03_ml_genai/03_stockout_model_and_genai.py`
**Executed on:** Databricks serverless (job `fe_bar_varejo_S3_ml_genai`) — result **SUCCESS**
**Model:** `HistGradientBoostingClassifier`, logged to MLflow, registered in Unity Catalog as
`serverless_stable_xpbmim_catalog.fe_bar_varejo_gold.stockout_risk` (READY)
**Target:** probability of a stockout in the **next 7 days**, per store×SKU
**Split:** time-based (train ≤ 75th-percentile date, test = later dates)

## Model evaluation (held-out later dates)

```
auc    | avg_precision | precision_05 | recall_05 | precision_at_100 | positive_rate | train_rows | test_rows
0.8558 | 0.7544        | 0.9160       | 0.4321    | 1.0000           | 0.2142        | 425000     | 140000
```

- **AUC 0.856** — strong ranking of at-risk store×SKUs.
- **Precision @ top-100 = 1.00** — every one of the 100 highest-risk items really did stock
  out. This is the operationally relevant number: the replenishment team can act on the
  ranked list with essentially no wasted effort.
- Precision 0.92 / recall 0.43 at the 0.5 threshold — conservative alerting; the app ranks by
  **expected lost revenue** rather than a hard threshold.

## Scored current inventory → `gold_stockout_predictions` (5,000 store×SKU rows)

Top at-risk by expected 7-day lost revenue:

```
store_id | sku      | category   | region   | on_hand | reorder_pt | avg7d | risk_prob | order_units | exp_lost_rev_7d
L119     | SKU10029 | Bebidas    | Nordeste | 0       | 289        | 87.0  | 0.9976    | 0           | 8511.61
L108     | SKU10055 | Bebidas    | Sudeste  | 0       | 114        | 50.0  | 0.9999    | 133         | 6246.88
L108     | SKU10090 | Laticinios | Sudeste  | 18      | 136        | 33.1  | 0.9995    | 31          | 6035.94
L105     | SKU10143 | Higiene    | Norte    | 30      | 107        | 19.9  | 0.9940    | 101         | 5188.13
L112     | SKU10054 | Padaria    | Nordeste | 42      | 91         | 33.0  | 0.9991    | 3           | 4915.87
L108     | SKU10208 | Congelados | Sudeste  | 62      | 93         | 17.6  | 0.9951    | 19          | 4731.88
L105     | SKU10152 | Hortifruti | Norte    | 46      | 107        | 55.4  | 0.9821    | 0           | 4374.51
L103     | SKU10156 | Bebidas    | Nordeste | 57      | 165        | 51.3  | 0.9803    | 111         | 4272.40
```

Each row carries a **suggested_order_units** (demand × (lead time + 7 days) − on-hand −
on-order) and **expected_lost_revenue_7d** (risk × 7-day demand × price) so the business can
prioritize action by money at risk, not just probability.
