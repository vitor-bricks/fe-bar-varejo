# Databricks notebook source
# MAGIC %md
# MAGIC # FE Bar Varejo — Lakebase Operational Serving
# MAGIC
# MAGIC Syncs the gold serving tables into a **Lakebase (Postgres)** database `retail` so the
# MAGIC Control Tower app reads the reorder worklist, current availability and KPIs at
# MAGIC **operational low latency** (single-digit ms), decoupled from the analytics warehouse.
# MAGIC
# MAGIC Served tables: `stockout_predictions`, `current_availability`, `kpi_daily`, `reorder_rationale`.
# MAGIC
# MAGIC Connection params are passed as job parameters (host / OAuth token / user).

# COMMAND ----------

# MAGIC %pip install -q psycopg2-binary

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import psycopg2
from psycopg2.extras import execute_values

dbutils.widgets.text("pg_host", "")
dbutils.widgets.text("pg_token", "")
dbutils.widgets.text("pg_user", "")
HOST = dbutils.widgets.get("pg_host")
TOKEN = dbutils.widgets.get("pg_token")
USER = dbutils.widgets.get("pg_user")
C = "serverless_stable_xpbmim_catalog"
GOLD = f"{C}.fe_bar_varejo_gold"

def connect(db):
    return psycopg2.connect(host=HOST, port=5432, dbname=db, user=USER, password=TOKEN, sslmode="require")

# COMMAND ----------

# MAGIC %md ## Create database `retail`

# COMMAND ----------

conn = connect("postgres"); conn.autocommit = True
cur = conn.cursor()
cur.execute("SELECT 1 FROM pg_database WHERE datname='retail'")
if not cur.fetchone():
    cur.execute("CREATE DATABASE retail")
    print("created database retail")
else:
    print("database retail already exists")
cur.close(); conn.close()

# COMMAND ----------

# MAGIC %md ## Create tables + load from gold (full refresh)

# COMMAND ----------

DDL = """
DROP TABLE IF EXISTS stockout_predictions;
CREATE TABLE stockout_predictions (
    store_id TEXT, sku TEXT, category TEXT, brand TEXT, region TEXT, city TEXT, store_format TEXT,
    on_hand_units INT, on_order_units INT, reorder_point INT, lead_time_days INT,
    avg_units_7d DOUBLE PRECISION, stockout_7d INT, unit_price DOUBLE PRECISION,
    risk_probability DOUBLE PRECISION, suggested_order_units INT,
    expected_lost_revenue_7d DOUBLE PRECISION, risk_rank INT, snapshot_date DATE
);
DROP TABLE IF EXISTS current_availability;
CREATE TABLE current_availability (
    store_id TEXT, sku TEXT, category TEXT, region TEXT, store_format TEXT,
    on_hand_units INT, reorder_point INT, stockout_days_7d INT,
    avg_daily_units_7d DOUBLE PRECISION, risk_flag INT, snapshot_date DATE
);
DROP TABLE IF EXISTS kpi_daily;
CREATE TABLE kpi_daily (
    snapshot_date DATE, stockout_rate DOUBLE PRECISION, lost_units INT,
    lost_revenue DOUBLE PRECISION, revenue DOUBLE PRECISION, active_combos INT
);
DROP TABLE IF EXISTS reorder_rationale;
CREATE TABLE reorder_rationale (
    store_id TEXT, sku TEXT, category TEXT, risk_probability DOUBLE PRECISION,
    expected_lost_revenue_7d DOUBLE PRECISION, suggested_order_units INT, reorder_rationale TEXT
);
CREATE INDEX idx_pred_rank ON stockout_predictions(risk_rank);
CREATE INDEX idx_pred_store ON stockout_predictions(store_id);
CREATE INDEX idx_avail_store ON current_availability(store_id);
"""
conn = connect("retail"); conn.autocommit = True; cur = conn.cursor()
cur.execute(DDL)
print("tables created")

def load(table, select_sql, cols):
    rows = [tuple(r) for r in spark.sql(select_sql).collect()]
    execute_values(cur, f"INSERT INTO {table} ({','.join(cols)}) VALUES %s", rows, page_size=1000)
    print(f"{table:24s} loaded {len(rows):,} rows")

load("stockout_predictions",
     f"SELECT store_id,sku,category,brand,region,city,store_format,on_hand_units,on_order_units,reorder_point,lead_time_days,avg_units_7d,stockout_7d,unit_price,risk_probability,suggested_order_units,expected_lost_revenue_7d,risk_rank,snapshot_date FROM {GOLD}.gold_stockout_predictions",
     ["store_id","sku","category","brand","region","city","store_format","on_hand_units","on_order_units","reorder_point","lead_time_days","avg_units_7d","stockout_7d","unit_price","risk_probability","suggested_order_units","expected_lost_revenue_7d","risk_rank","snapshot_date"])

load("current_availability",
     f"SELECT store_id,sku,category,region,store_format,on_hand_units,reorder_point,stockout_days_7d,avg_daily_units_7d,risk_flag,snapshot_date FROM {GOLD}.gold_current_availability",
     ["store_id","sku","category","region","store_format","on_hand_units","reorder_point","stockout_days_7d","avg_daily_units_7d","risk_flag","snapshot_date"])

load("kpi_daily",
     f"SELECT snapshot_date,stockout_rate,lost_units,lost_revenue,revenue,active_combos FROM {GOLD}.gold_kpi_daily",
     ["snapshot_date","stockout_rate","lost_units","lost_revenue","revenue","active_combos"])

load("reorder_rationale",
     f"SELECT store_id,sku,category,risk_probability,expected_lost_revenue_7d,suggested_order_units,reorder_rationale FROM {GOLD}.gold_reorder_rationale",
     ["store_id","sku","category","risk_probability","expected_lost_revenue_7d","suggested_order_units","reorder_rationale"])

cur.close(); conn.close()

# COMMAND ----------

# MAGIC %md ## Verify (row counts + sample operational query)

# COMMAND ----------

conn = connect("retail"); cur = conn.cursor()
for t in ["stockout_predictions", "current_availability", "kpi_daily", "reorder_rationale"]:
    cur.execute(f"SELECT count(*) FROM {t}")
    print(f"{t:24s} {cur.fetchone()[0]:,} rows")
print("\nTop 5 reorder worklist (operational query):")
cur.execute("SELECT store_id, sku, category, on_hand_units, suggested_order_units, expected_lost_revenue_7d FROM stockout_predictions ORDER BY risk_rank LIMIT 5")
for r in cur.fetchall():
    print("  ", r)
cur.close(); conn.close()
