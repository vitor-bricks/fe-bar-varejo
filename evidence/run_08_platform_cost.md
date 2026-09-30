# Platform cost — measured from the workspace's system billing tables

What it costs to run the whole prototype for one day, measured (not estimated) from
`system.billing.usage` and priced with `system.billing.list_prices` (list price, USD).
Day measured: **2026-09-29**, the first day with only the scheduled 06:00 run (run `878776469785234`,
7.7 min); earlier days include development runs. Queried on 2026-09-30.

## 1 · Daily usage per component

```sql
SELECT usage_date,
  round(sum(CASE WHEN usage_metadata.job_id = '384370635751593' THEN usage_quantity END),3) job_dbu,
  round(sum(CASE WHEN usage_metadata.dlt_pipeline_id = '733e5172-5f51-404b-a790-b40cce95f015' THEN usage_quantity END),3) pipeline_dbu,
  round(sum(CASE WHEN billing_origin_product = 'APPS' AND to_json(usage_metadata) like '%fe-bar-varejo%' THEN usage_quantity END),3) app_dbu,
  round(sum(CASE WHEN billing_origin_product = 'LAKEBASE' AND sku_name like '%COMPUTE%'
                  AND (to_json(usage_metadata) like '%fe-bar-varejo%' OR to_json(usage_metadata) like '%2f21f630%') THEN usage_quantity END),3) lakebase_dbu
FROM system.billing.usage WHERE usage_date >= '2026-09-26' GROUP BY 1 ORDER BY 1
```

```text
usage_date | job_dbu | pipeline_dbu | app_dbu | lakebase_dbu
2026-09-26 |         |              | 12.000  | 5.112
2026-09-27 |         |              | 12.000  | 0.250
2026-09-28 | 1.243   | 1.183        | 12.000  | 2.634     (evidence run + development runs)
2026-09-29 | 0.351   | 0.386        | 12.000  | 5.112     (scheduled run only)
2026-09-30 | 0.273   | 0.304        | 4.000   | 2.095     (partial day)
```

## 2 · The agent's LLM usage (Foundation Model API, pay-per-token)

```sql
-- tokens: the agent task window of the 2026-09-29 run
SELECT u.requester, count(*) calls, sum(u.input_token_count) tin, sum(u.output_token_count) tout
FROM system.serving.endpoint_usage u JOIN system.serving.served_entities e ON u.served_entity_id = e.served_entity_id
WHERE e.endpoint_name = 'databricks-claude-sonnet-5'
  AND u.request_time >= '2026-09-29T09:00:00Z' AND u.request_time < '2026-09-29T09:10:00Z'
GROUP BY 1
-- billed DBUs for the same hour
SELECT usage_start_time, sku_name, round(sum(usage_quantity),4) dbu
FROM system.billing.usage
WHERE usage_date = '2026-09-29' AND billing_origin_product = 'MODEL_SERVING'
  AND identity_metadata.run_as = 'vitor.jardim@databricks.com' AND usage_metadata.endpoint_name = 'databricks-claude-sonnet-5'
GROUP BY 1,2
```

```text
requester                    | calls | tin    | tout
vitor.jardim@databricks.com  | 24    | 41,472 | 9,027        (09:04:52 → 09:06:50 UTC, the agent task)

usage_start_time          | sku_name                           | dbu
2026-09-29T09:00:00.000Z  | ENTERPRISE_ANTHROPIC_MODEL_SERVING | 2.7219
```

## 3 · List prices

```sql
SELECT sku_name, pricing.default price_usd FROM system.billing.list_prices
WHERE price_end_time IS NULL AND sku_name IN (...)
```

```text
ENTERPRISE_JOBS_SERVERLESS_COMPUTE_US_EAST_N_VIRGINIA         0.45 USD/DBU   (job + pipeline)
ENTERPRISE_ALL_PURPOSE_SERVERLESS_COMPUTE_US_EAST_N_VIRGINIA  0.95 USD/DBU   (Databricks App)
ENTERPRISE_DATABASE_SERVERLESS_COMPUTE_US_EAST_N_VIRGINIA     0.52 USD/DBU   (Lakebase)
ENTERPRISE_ANTHROPIC_MODEL_SERVING                            0.07 USD/DBU   (agent LLM)
```

## 4 · Result (2026-09-29, list price)

```text
component                          usage            USD/day
job, serverless (4 notebook tasks) 0.351 DBU        0.16
Lakeflow pipeline, serverless      0.386 DBU        0.17
agent LLM (24 calls)               2.722 DBU        0.19
Lakebase (scales to zero)          5.112 DBU        2.66
Databricks App (always on)        12.000 DBU       11.40
------------------------------------------------------------
total                                              14.58 USD/day  ≈ 437 USD / 30 days
daily batch journey (job+pipeline+LLM)              0.52 USD/day  ≈ 16 USD / 30 days
```

Storage (Lakebase 0.111 DSU over 6 days; Delta tables of a few MB) is negligible. Discounts and
committed-use pricing would lower these list-price figures; the pilot measures them at real volume.

## 5 · Where the value comes from (evidence run 204235693781766, `run_07_app_checks.md`)

```text
action        n    R$ protected (7 days)   share   R$ per action
EXPEDITE    142         12,884.07          79.7%        90.73
TRANSFER     39          2,866.94          17.7%        73.51
URGENT        7            423.76           2.6%        60.54
total       188         16,174.77
```

A transfer only pays off if its marginal freight is below the ~R$ 74 it protects, so the pilot
limits transfers to routes that already run (e.g. the DC delivery) or to grouped items per store pair.
