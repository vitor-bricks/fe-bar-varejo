# Databricks notebook source
# MAGIC %md
# MAGIC # LojaBR · Centro de Abastecimento — Lakebase Operational Serving (v2)
# MAGIC
# MAGIC Publishes the gold serving tables to **Lakebase (Postgres)**, database `retail`:
# MAGIC
# MAGIC | Schema | Owner | Tables | Refresh |
# MAGIC |---|---|---|---|
# MAGIC | `serving` | this job | store_network, replenishment_queue, position, kpi_daily, supplier_otif, model_card, journey_status | replaced **atomically** each run (one transaction) |
# MAGIC | `app` | the app | replenishment_actions (approvals, with author), genie_interactions | created once, **never dropped** |
# MAGIC
# MAGIC The job mints its own short-lived Lakebase OAuth credential (`/api/2.0/postgres/credentials`);
# MAGIC no token is passed as a parameter. The app's service principal gets read on `serving` and
# MAGIC read/write on `app`.

# COMMAND ----------

# MAGIC %pip install -q pg8000

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import json, ssl
from datetime import datetime, timezone
import pg8000.dbapi          # pure-Python driver: no native libpq/OpenSSL (psycopg2-binary aborted once with SIGABRT)
from databricks.sdk import WorkspaceClient

dbutils.widgets.text("job_run_id", "")
JOB_RUN_ID = dbutils.widgets.get("job_run_id")
ENDPOINT = "projects/fe-bar-varejo/branches/production/endpoints/primary"
HOST = "ep-royal-silence-d24b1cks.database.us-east-1.cloud.databricks.com"
APP_SP = "4f387a6d-76c2-49f8-bd49-d98039ff024d"     # fe-bar-varejo-tower service principal
PIPELINE_ID = "733e5172-5f51-404b-a790-b40cce95f015"
GENIE_SPACE = "01f1b906cf2d15b4b1c72c3b25ddb2f0"
C = "serverless_stable_xpbmim_catalog"
G = f"{C}.fe_bar_varejo_gold"

w = WorkspaceClient()
USER = w.current_user.me().user_name
token = w.api_client.do("POST", "/api/2.0/postgres/credentials", body={"endpoint": ENDPOINT})["token"]


def connect(db="retail"):
    return pg8000.dbapi.connect(host=HOST, port=5432, database=db, user=USER, password=token,
                                ssl_context=ssl.create_default_context())


def run(cur, script):
    """pg8000 uses the extended protocol: one statement per execute."""
    for stmt in [x.strip() for x in script.split(";") if x.strip()]:
        cur.execute(stmt)


def insert_rows(cur, table, cols, rows, chunk=400):
    """Multi-row INSERT in chunks (fast, parameterized)."""
    for i in range(0, len(rows), chunk):
        part = rows[i:i + chunk]
        ph = ", ".join("(" + ", ".join(["%s"] * len(cols)) + ")" for _ in part)
        cur.execute(f"INSERT INTO {table} ({', '.join(cols)}) VALUES {ph}", [v for r in part for v in r])

print(f"minted Lakebase credential for {USER} · endpoint {ENDPOINT}")

# COMMAND ----------

# MAGIC %md ## Journey status — what each stage really did in this run

# COMMAND ----------

upd = w.pipelines.get(PIPELINE_ID).latest_updates[0]
versions = [v.version for v in w.model_versions.list(f"{G}.stockout_early_warning")]
metrics = spark.table(f"{G}.gold_model_metrics").toPandas().iloc[0].to_dict()
agent = spark.sql(f"SELECT * FROM {G}.gold_agent_runs ORDER BY run_at DESC LIMIT 1").toPandas().iloc[0].to_dict()
n_tables = spark.sql(f"SELECT count(*) n FROM {C}.information_schema.tables WHERE table_schema LIKE 'fe_bar_varejo%' "
                     f"AND table_name NOT LIKE '\\_\\_%' AND table_name NOT LIKE 'event_log%'").first()["n"]
now = datetime.now(timezone.utc)
journey = [
    ("01", "Ingestão", "Lakeflow · Auto Loader", "ok", "7 feeds brutos (POS, estoque, pedidos, cadastros) no Volume landing"),
    ("02", "Medallion", "Lakeflow Declarative Pipelines", str(upd.state.value).lower(),
     f"bronze → silver → gold · update {upd.update_id[:8]}"),
    ("03", "Governança", "Unity Catalog", "ok", f"3 schemas · {n_tables} tabelas · lineage + expectations"),
    ("04", "Modelo", "MLflow · UC Model Registry", "ok",
     f"stockout_early_warning v{max(versions)} · AUC {metrics['test_auc']:.2f}"),
    ("05", "Agente", "Foundation Model API · tool-calling", "ok",
     f"{int(agent['items_reviewed'])} itens revisados · {agent['avg_tool_calls']:.1f} ferramentas/item"),
    ("06", "Serving", "Lakebase · Postgres", "ok", "worklist, rede e aprovações em Postgres"),
    ("07", "Linguagem natural", "Genie", "ok", "espaço curado · 5 SQL certificados · entity matching"),
]

# COMMAND ----------

# MAGIC %md ## Publish `serving` atomically + ensure `app`

# COMMAND ----------

SERVING = {
    "store_network": f"SELECT store_id, store_name, city, uf, region, store_format, lat, lon, stockout_rate_7d, lost_revenue_7d, revenue_7d FROM {G}.gold_store_network",
    "replenishment_queue": f"""SELECT action_id, CAST(snapshot_date AS STRING) snapshot_date, priority, action_type, severity,
        store_id, store_name, city, uf, region, sku, product_name, category, from_id, from_store_name, from_city,
        transfer_km, donor_days_of_cover, units, eta_days, on_hand_units, days_of_cover, inbound_units,
        eta_adjusted_days, supplier_id, supplier_name, supplier_on_time_rate, risk_probability, units_at_risk,
        revenue_at_risk, revenue_protected, rationale, rationale_source, agent_confidence, agent_changed_action,
        agent_tools FROM {G}.gold_replenishment_queue_final""",
    "position": f"""SELECT p.store_id, p.sku, p.store_name, p.product_name, p.category, p.on_hand_units,
        round(p.avg_units_28d, 2) avg_units_28d, p.days_of_cover, p.inbound_units, p.days_until_inbound,
        p.stockout_days_28d, p.unit_price, s.risk_probability, s.revenue_at_risk
        FROM {G}.gold_current_position p LEFT JOIN {G}.gold_stockout_predictions s USING (store_id, sku)""",
    "kpi_daily": f"SELECT CAST(snapshot_date AS STRING) snapshot_date, stockout_rate, lost_units, lost_revenue, revenue FROM {G}.gold_kpi_daily",
    "supplier_otif": f"SELECT supplier_id, supplier_name, orders_received, on_time_rate, avg_delay_days, avg_delay_when_late FROM {G}.gold_supplier_otif",
}
PG_TYPE = {"string": "TEXT", "int": "INTEGER", "bigint": "BIGINT", "double": "DOUBLE PRECISION",
           "float": "DOUBLE PRECISION", "boolean": "BOOLEAN", "date": "DATE", "timestamp": "TIMESTAMPTZ"}

conn = connect(); cur = conn.cursor()
run(cur, "CREATE SCHEMA IF NOT EXISTS serving; CREATE SCHEMA IF NOT EXISTS app")
run(cur, """
CREATE TABLE IF NOT EXISTS app.replenishment_actions (
    id BIGSERIAL PRIMARY KEY, action_id TEXT NOT NULL, snapshot_date TEXT, decision TEXT NOT NULL,
    action_type TEXT, store_id TEXT, sku TEXT, units INTEGER, revenue_protected DOUBLE PRECISION,
    decided_by TEXT, decided_at TIMESTAMPTZ NOT NULL DEFAULT now(), note TEXT);
CREATE INDEX IF NOT EXISTS ix_actions_action ON app.replenishment_actions(action_id);
CREATE TABLE IF NOT EXISTS app.genie_interactions (
    id BIGSERIAL PRIMARY KEY, asked_at TIMESTAMPTZ NOT NULL DEFAULT now(), user_email TEXT, question TEXT,
    answer TEXT, sql_query TEXT, row_count INTEGER, status TEXT, duration_ms INTEGER);
""")
counts = {}
for table, sql in SERVING.items():
    df = spark.sql(sql)
    cols = [(f.name, PG_TYPE.get(f.dataType.simpleString(), "TEXT")) for f in df.schema.fields]
    # pandas-origin NaN must become SQL NULL (otherwise the app would render "NaN")
    rows = [tuple(None if isinstance(x, float) and x != x else x for x in r) for r in df.collect()]
    cur.execute(f"DROP TABLE IF EXISTS serving.{table}")
    cur.execute(f"CREATE TABLE serving.{table} ({', '.join(f'{c} {t}' for c, t in cols)})")
    insert_rows(cur, f"serving.{table}", [c for c, _ in cols], rows)
    counts[table] = len(rows)
# model card + journey status
run(cur, "DROP TABLE IF EXISTS serving.model_card; CREATE TABLE serving.model_card (metric TEXT, value DOUBLE PRECISION)")
insert_rows(cur, "serving.model_card", ["metric", "value"],
            [(k, float(v)) for k, v in metrics.items() if isinstance(v, (int, float))])
run(cur, """DROP TABLE IF EXISTS serving.journey_status; CREATE TABLE serving.journey_status
    (step TEXT, stage TEXT, product TEXT, status TEXT, detail TEXT, job_run_id TEXT, updated_at TIMESTAMPTZ)""")
insert_rows(cur, "serving.journey_status", ["step", "stage", "product", "status", "detail", "job_run_id", "updated_at"],
            [(*j, JOB_RUN_ID, now) for j in journey])
run(cur, "CREATE INDEX ON serving.replenishment_queue(priority); CREATE INDEX ON serving.position(store_id)")
# app service principal: read serving, read/write app state
run(cur, f'''
GRANT USAGE ON SCHEMA serving, app TO "{APP_SP}";
GRANT SELECT ON ALL TABLES IN SCHEMA serving TO "{APP_SP}";
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA app TO "{APP_SP}";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA app TO "{APP_SP}";
''')
# v1 leftovers (my own tables from the first build)
for t in ["stockout_predictions", "current_availability", "kpi_daily", "reorder_rationale"]:
    cur.execute(f"DROP TABLE IF EXISTS public.{t}")
conn.commit()      # one transaction: readers see the old serving tables until this commit
cur.close(); conn.close()
print("published to Lakebase:", counts)

# COMMAND ----------

# MAGIC %md ## Verify from Postgres (what the app will read)

# COMMAND ----------

conn = connect(); cur = conn.cursor()
cur.execute("SELECT version()"); print(cur.fetchone()[0].split(",")[0])
for t in list(SERVING) + ["model_card", "journey_status"]:
    cur.execute(f"SELECT count(*) FROM serving.{t}"); print(f"serving.{t:22s} {cur.fetchone()[0]:>6,} rows")
cur.execute("SELECT count(*) FROM app.replenishment_actions"); print(f"app.replenishment_actions      {cur.fetchone()[0]:>6,} rows (kept across runs)")
print("\ntop of the worklist:")
cur.execute("""SELECT priority, action_type, store_name, product_name, units, round(revenue_protected::numeric, 0)
               FROM serving.replenishment_queue ORDER BY priority LIMIT 5""")
for r in cur.fetchall(): print("  ", r)
print("\njourney status:")
cur.execute("SELECT step, stage, product, status, detail FROM serving.journey_status ORDER BY step")
for r in cur.fetchall(): print("  ", r)
cur.close(); conn.close()
