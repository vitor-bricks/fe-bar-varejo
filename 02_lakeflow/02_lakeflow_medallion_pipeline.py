# Databricks notebook source
# MAGIC %md
# MAGIC # LojaBR · Centro de Abastecimento — Lakeflow Declarative Pipeline (v2)
# MAGIC
# MAGIC Raw CSV feeds (Volume) → **bronze** (Auto Loader) → **silver** (typed, deduped, quality
# MAGIC expectations) → **gold** (business tables) across three governed Unity Catalog schemas.
# MAGIC
# MAGIC | Gold table | Grain | Used by |
# MAGIC |---|---|---|
# MAGIC | `gold_daily_store_sku` | store × sku × day | ML training, Genie |
# MAGIC | `gold_current_position` | store × sku (latest day) | ML scoring, agent, app drill |
# MAGIC | `gold_supplier_otif` | supplier | agent, app, Genie |
# MAGIC | `gold_store_network` | store | app map, Genie |
# MAGIC | `gold_kpi_daily` | day | app, Genie |

# COMMAND ----------

import dlt
from pyspark.sql import functions as F, Window as W

LANDING = "/Volumes/serverless_stable_xpbmim_catalog/fe_bar_varejo_bronze/landing"
B, S, G = "fe_bar_varejo_bronze", "fe_bar_varejo_silver", "fe_bar_varejo_gold"


def autoload(sub):
    return (spark.readStream.format("cloudFiles")
            .option("cloudFiles.format", "csv")
            .option("cloudFiles.inferColumnTypes", "true")
            .option("header", "true")
            .load(f"{LANDING}/{sub}")
            .withColumn("_ingested_at", F.current_timestamp())
            .withColumn("_source_file", F.col("_metadata.file_path")))


def batch(sub):
    return (spark.read.format("csv").option("header", "true").option("inferSchema", "true")
            .load(f"{LANDING}/{sub}"))

# ============================================================ BRONZE
@dlt.table(name=f"{B}.bronze_sales", comment="Raw POS daily sales (Auto Loader)")
def bronze_sales(): return autoload("fact_sales_daily")

@dlt.table(name=f"{B}.bronze_inventory", comment="Raw daily inventory snapshots (Auto Loader)")
def bronze_inventory(): return autoload("fact_inventory_daily")

@dlt.table(name=f"{B}.bronze_purchase_orders", comment="Raw received purchase orders (Auto Loader)")
def bronze_purchase_orders(): return autoload("fact_purchase_orders")

@dlt.table(name=f"{B}.bronze_open_orders", comment="Raw open purchase orders in transit")
def bronze_open_orders(): return batch("fact_open_orders")

@dlt.table(name=f"{B}.bronze_dim_store", comment="Raw store master")
def bronze_dim_store(): return batch("dim_store")

@dlt.table(name=f"{B}.bronze_dim_product", comment="Raw product master")
def bronze_dim_product(): return batch("dim_product")

@dlt.table(name=f"{B}.bronze_dim_supplier", comment="Raw supplier master")
def bronze_dim_supplier(): return batch("dim_supplier")

# ============================================================ SILVER
@dlt.table(name=f"{S}.silver_dim_store", comment="Store master (20 stores, with coordinates)")
@dlt.expect_or_fail("store_id_present", "store_id IS NOT NULL")
def silver_dim_store(): return dlt.read(f"{B}.bronze_dim_store").dropDuplicates(["store_id"])

@dlt.table(name=f"{S}.silver_dim_product", comment="Product master")
@dlt.expect_or_drop("valid_price", "unit_price > 0 AND unit_cost > 0 AND unit_cost < unit_price")
def silver_dim_product(): return dlt.read(f"{B}.bronze_dim_product").dropDuplicates(["sku"])

@dlt.table(name=f"{S}.silver_dim_supplier", comment="Supplier master")
def silver_dim_supplier(): return dlt.read(f"{B}.bronze_dim_supplier").dropDuplicates(["supplier_id"])

@dlt.table(name=f"{S}.silver_sales", comment="Typed, deduped POS daily sales")
@dlt.expect_or_drop("non_negative_units", "units_sold >= 0")
@dlt.expect("has_date", "sale_date IS NOT NULL")
def silver_sales():
    return (dlt.read_stream(f"{B}.bronze_sales").withColumn("sale_date", F.to_date("sale_date"))
            .dropDuplicates(["store_id", "sku", "sale_date"]))

@dlt.table(name=f"{S}.silver_inventory", comment="Typed, deduped daily inventory snapshots")
@dlt.expect_or_drop("non_negative_onhand", "on_hand_units >= 0")
def silver_inventory():
    return (dlt.read_stream(f"{B}.bronze_inventory").withColumn("snapshot_date", F.to_date("snapshot_date"))
            .dropDuplicates(["store_id", "sku", "snapshot_date"]))

@dlt.table(name=f"{S}.silver_purchase_orders", comment="Received purchase orders with delay in days")
@dlt.expect_or_drop("arrival_after_order", "actual_arrival >= order_date")
def silver_purchase_orders():
    return (dlt.read_stream(f"{B}.bronze_purchase_orders")
            .withColumn("order_date", F.to_date("order_date"))
            .withColumn("expected_arrival", F.to_date("expected_arrival"))
            .withColumn("actual_arrival", F.to_date("actual_arrival"))
            .withColumn("delay_days", F.greatest(F.lit(0), F.datediff("actual_arrival", "expected_arrival")))
            .dropDuplicates(["po_id"]))

@dlt.table(name=f"{S}.silver_open_orders", comment="Open purchase orders in transit")
@dlt.expect_or_drop("positive_qty", "qty_units > 0")
def silver_open_orders():
    return (dlt.read(f"{B}.bronze_open_orders")
            .withColumn("order_date", F.to_date("order_date"))
            .withColumn("eta_date", F.to_date("eta_date")))

# ============================================================ GOLD
@dlt.table(name=f"{G}.gold_daily_store_sku",
           comment="Daily store×sku fact: inventory, sales, lost sales (R$), product and store attributes")
def gold_daily_store_sku():
    inv = dlt.read(f"{S}.silver_inventory")
    sales = dlt.read(f"{S}.silver_sales").select("store_id", "sku", F.col("sale_date").alias("snapshot_date"),
                                                 "units_sold", "revenue", "promo_flag")
    prod = dlt.read(f"{S}.silver_dim_product").select("sku", "product_name", "category", "supplier_id",
                                                      "unit_price", "unit_cost", "lead_time_days")
    store = dlt.read(f"{S}.silver_dim_store").select("store_id", "store_name", "city", "uf", "region", "store_format")
    return (inv.join(sales, ["store_id", "sku", "snapshot_date"], "left")
            .join(prod, "sku", "left").join(store, "store_id", "left")
            .fillna({"units_sold": 0, "revenue": 0.0, "promo_flag": 0})
            .withColumn("lost_revenue", F.round(F.col("lost_sales_units") * F.col("unit_price"), 2)))


@dlt.table(name=f"{G}.gold_supplier_otif", comment="Supplier on-time rate and average delay (from received POs)")
def gold_supplier_otif():
    po = dlt.read(f"{S}.silver_purchase_orders")
    sup = dlt.read(f"{S}.silver_dim_supplier")
    return (po.groupBy("supplier_id").agg(
                F.count("*").alias("orders_received"),
                F.round(F.avg(F.when(F.col("delay_days") == 0, 1).otherwise(0)), 4).alias("on_time_rate"),
                F.round(F.avg("delay_days"), 2).alias("avg_delay_days"),
                F.round(F.avg(F.when(F.col("delay_days") > 0, F.col("delay_days"))), 2).alias("avg_delay_when_late"))
            .join(sup, "supplier_id", "left"))


@dlt.table(name=f"{G}.gold_current_position",
           comment="Latest position per store×sku: stock, velocity, days of cover, inbound order, recent stockouts")
def gold_current_position():
    g = dlt.read(f"{G}.gold_daily_store_sku")
    w = W.partitionBy("store_id", "sku").orderBy("snapshot_date")
    hist = (g.withColumn("avg_units_7d", F.avg("units_sold").over(w.rowsBetween(-6, 0)))
             .withColumn("avg_units_28d", F.avg("units_sold").over(w.rowsBetween(-27, 0)))
             .withColumn("std_units_28d", F.stddev("units_sold").over(w.rowsBetween(-27, 0)))
             .withColumn("stockout_days_7d", F.sum("stockout_flag").over(w.rowsBetween(-6, 0)))
             .withColumn("stockout_days_28d", F.sum("stockout_flag").over(w.rowsBetween(-27, 0)))
             .withColumn("lost_revenue_7d", F.sum("lost_revenue").over(w.rowsBetween(-6, 0))))
    last = hist.agg(F.max("snapshot_date").alias("d"))
    cur = hist.join(last, hist.snapshot_date == last.d).drop("d")
    inbound = (dlt.read(f"{S}.silver_open_orders").groupBy("store_id", "sku")
               .agg(F.sum("qty_units").alias("inbound_units"), F.min("eta_date").alias("inbound_eta")))
    otif = dlt.read(f"{G}.gold_supplier_otif").select("supplier_id", "on_time_rate", "avg_delay_when_late")
    return (cur.join(inbound, ["store_id", "sku"], "left").join(otif, "supplier_id", "left")
            .fillna({"inbound_units": 0})
            .withColumn("days_until_inbound", F.datediff("inbound_eta", "snapshot_date"))
            .withColumn("days_of_cover", F.round(F.col("on_hand_units") / F.greatest(F.col("avg_units_28d"), F.lit(0.1)), 1)))


@dlt.table(name=f"{G}.gold_kpi_daily", comment="Daily chain-wide KPIs")
def gold_kpi_daily():
    return (dlt.read(f"{G}.gold_daily_store_sku").groupBy("snapshot_date").agg(
        F.round(F.avg("stockout_flag"), 4).alias("stockout_rate"),
        F.sum("lost_sales_units").alias("lost_units"),
        F.round(F.sum("lost_revenue"), 2).alias("lost_revenue"),
        F.round(F.sum("revenue"), 2).alias("revenue")))


@dlt.table(name=f"{G}.gold_store_network", comment="Store network view: location + last-7-day availability KPIs")
def gold_store_network():
    g = dlt.read(f"{G}.gold_daily_store_sku")
    last = g.agg(F.max("snapshot_date").alias("d"))
    recent = g.join(last, g.snapshot_date >= F.date_sub(last.d, 6))
    k = recent.groupBy("store_id").agg(
        F.round(F.avg("stockout_flag"), 4).alias("stockout_rate_7d"),
        F.round(F.sum("lost_revenue"), 2).alias("lost_revenue_7d"),
        F.round(F.sum("revenue"), 2).alias("revenue_7d"))
    return dlt.read(f"{S}.silver_dim_store").join(k, "store_id", "left")
