# Databricks notebook source
# MAGIC %md
# MAGIC # FE Bar Varejo — Lakeflow Declarative Pipeline (Medallion)
# MAGIC
# MAGIC Ingests the raw CSV feeds landed in the Unity Catalog Volume and refines them through
# MAGIC **bronze → silver → gold** across three governed schemas:
# MAGIC
# MAGIC - **bronze** (`fe_bar_varejo_bronze.*`) — raw ingest via Auto Loader (`cloudFiles`)
# MAGIC - **silver** (`fe_bar_varejo_silver.*`) — typed, cleaned, quality-checked (`@dlt.expect`)
# MAGIC - **gold** (`fe_bar_varejo_gold.*`) — business tables: daily store×sku fact, current
# MAGIC   availability with stockout-risk fields, and daily KPIs
# MAGIC
# MAGIC Pipeline default catalog = `serverless_stable_xpbmim_catalog`; tables are written to
# MAGIC their medallion schema via two-part names (direct publishing mode).

# COMMAND ----------

import dlt
from pyspark.sql import functions as F, Window as W

LANDING = "/Volumes/serverless_stable_xpbmim_catalog/fe_bar_varejo_bronze/landing"

def _autoload(subdir):
    return (spark.readStream.format("cloudFiles")
            .option("cloudFiles.format", "csv")
            .option("cloudFiles.inferColumnTypes", "true")
            .option("header", "true")
            .load(f"{LANDING}/{subdir}"))

# ============================================================ BRONZE (raw ingest)
@dlt.table(name="fe_bar_varejo_bronze.bronze_sales", comment="Raw POS sales (Auto Loader)")
def bronze_sales():
    return _autoload("fact_sales_daily").withColumn("_ingested_at", F.current_timestamp())

@dlt.table(name="fe_bar_varejo_bronze.bronze_inventory", comment="Raw inventory snapshots (Auto Loader)")
def bronze_inventory():
    return _autoload("fact_inventory_daily").withColumn("_ingested_at", F.current_timestamp())

@dlt.table(name="fe_bar_varejo_bronze.bronze_shelf_audit", comment="Raw shelf audits (Auto Loader)")
def bronze_shelf_audit():
    return _autoload("fact_shelf_audit").withColumn("_ingested_at", F.current_timestamp())

@dlt.table(name="fe_bar_varejo_bronze.bronze_dim_store", comment="Raw store master")
def bronze_dim_store():
    return spark.read.format("csv").option("header", "true").option("inferSchema", "true").load(f"{LANDING}/dim_store")

@dlt.table(name="fe_bar_varejo_bronze.bronze_dim_product", comment="Raw product master")
def bronze_dim_product():
    return spark.read.format("csv").option("header", "true").option("inferSchema", "true").load(f"{LANDING}/dim_product")

# ============================================================ SILVER (clean + quality)
@dlt.table(name="fe_bar_varejo_silver.silver_dim_store", comment="Cleaned store master")
def silver_dim_store():
    return dlt.read("fe_bar_varejo_bronze.bronze_dim_store").dropDuplicates(["store_id"])

@dlt.table(name="fe_bar_varejo_silver.silver_dim_product", comment="Cleaned product master")
@dlt.expect_or_drop("valid_price", "unit_price > 0")
def silver_dim_product():
    return dlt.read("fe_bar_varejo_bronze.bronze_dim_product").dropDuplicates(["sku"])

@dlt.table(name="fe_bar_varejo_silver.silver_sales", comment="Typed, deduped POS sales")
@dlt.expect_or_drop("non_negative_units", "units_sold >= 0")
@dlt.expect("has_date", "sale_date IS NOT NULL")
def silver_sales():
    return (dlt.read_stream("fe_bar_varejo_bronze.bronze_sales")
            .withColumn("sale_date", F.to_date("sale_date"))
            .dropDuplicates(["store_id", "sku", "sale_date"]))

@dlt.table(name="fe_bar_varejo_silver.silver_inventory", comment="Typed, deduped inventory snapshots")
@dlt.expect_or_drop("non_negative_onhand", "on_hand_units >= 0")
def silver_inventory():
    return (dlt.read_stream("fe_bar_varejo_bronze.bronze_inventory")
            .withColumn("snapshot_date", F.to_date("snapshot_date"))
            .dropDuplicates(["store_id", "sku", "snapshot_date"]))

@dlt.table(name="fe_bar_varejo_silver.silver_shelf_audit", comment="Typed shelf audits")
def silver_shelf_audit():
    return (dlt.read_stream("fe_bar_varejo_bronze.bronze_shelf_audit")
            .withColumn("audit_date", F.to_date("audit_date"))
            .dropDuplicates(["store_id", "sku", "audit_date"]))

# ============================================================ GOLD (business)
@dlt.table(name="fe_bar_varejo_gold.gold_daily_store_sku",
           comment="Daily store×sku fact: inventory + sales + product/store attributes + lost revenue")
def gold_daily_store_sku():
    inv = dlt.read("fe_bar_varejo_silver.silver_inventory")
    sales = dlt.read("fe_bar_varejo_silver.silver_sales").select(
        "store_id", "sku", F.col("sale_date").alias("snapshot_date"),
        "units_sold", "revenue", "promo_flag")
    prod = dlt.read("fe_bar_varejo_silver.silver_dim_product")
    store = dlt.read("fe_bar_varejo_silver.silver_dim_store").select(
        "store_id", "region", "city", "store_format")
    return (inv.join(sales, ["store_id", "sku", "snapshot_date"], "left")
            .join(prod.select("sku", "category", "brand", "unit_cost", "unit_price",
                              "supplier_id"), "sku", "left")
            .join(store, "store_id", "left")
            .withColumn("units_sold", F.coalesce("units_sold", F.lit(0)))
            .withColumn("revenue", F.coalesce("revenue", F.lit(0.0)))
            .withColumn("promo_flag", F.coalesce("promo_flag", F.lit(0)))
            .withColumn("lost_revenue", F.round(F.col("lost_sales_units") * F.col("unit_price"), 2))
            .withColumn("days_of_supply",
                        F.when(F.col("units_sold") > 0, F.round(F.col("on_hand_units") / F.col("units_sold"), 1))
                         .otherwise(F.lit(None))))

@dlt.table(name="fe_bar_varejo_gold.gold_current_availability",
           comment="Latest snapshot per store×sku with stockout-risk fields (serves app, Genie, Lakebase)")
def gold_current_availability():
    g = dlt.read("fe_bar_varejo_gold.gold_daily_store_sku")
    latest = W.partitionBy("store_id", "sku").orderBy(F.col("snapshot_date").desc())
    r7 = (W.partitionBy("store_id", "sku").orderBy("snapshot_date").rowsBetween(-6, 0))
    return (g.withColumn("avg_daily_units_7d", F.avg("units_sold").over(r7))
            .withColumn("stockout_days_7d", F.sum("stockout_flag").over(r7))
            .withColumn("_rn", F.row_number().over(latest))
            .filter(F.col("_rn") == 1).drop("_rn")
            .withColumn("risk_flag",
                        F.when((F.col("on_hand_units") <= F.col("reorder_point")) | (F.col("stockout_days_7d") >= 2), F.lit(1)).otherwise(F.lit(0))))

@dlt.table(name="fe_bar_varejo_gold.gold_kpi_daily",
           comment="Daily chain-wide KPIs for the executive dashboard")
def gold_kpi_daily():
    g = dlt.read("fe_bar_varejo_gold.gold_daily_store_sku")
    return (g.groupBy("snapshot_date").agg(
        F.round(F.avg("stockout_flag"), 4).alias("stockout_rate"),
        F.sum("lost_sales_units").alias("lost_units"),
        F.round(F.sum("lost_revenue"), 2).alias("lost_revenue"),
        F.round(F.sum("revenue"), 2).alias("revenue"),
        F.countDistinct("store_id", "sku").alias("active_combos"))
        .orderBy("snapshot_date"))
