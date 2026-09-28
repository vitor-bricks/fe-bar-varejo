# Databricks notebook source
# MAGIC %md
# MAGIC # LojaBR · Centro de Abastecimento — Stockout Early-Warning Model + Action Engine (v2)
# MAGIC
# MAGIC **Question the model answers:** *for an item that is still on the shelf today, will it
# MAGIC stock out in the next 7 days?* Items already at zero are excluded — predicting those is
# MAGIC trivial and useless for prevention.
# MAGIC
# MAGIC 1. Point-in-time features (velocity, variability, days of cover, the purchase order that
# MAGIC    was open **on that day** with its *expected* arrival, supplier on-time history).
# MAGIC 2. Time-based split; gradient boosting vs. the naive planner rule *"cover < lead time"*.
# MAGIC 3. Model logged to MLflow and registered in Unity Catalog.
# MAGIC 4. Score today's in-stock items → estimate shortfall and R$ at risk → pick an action per item:
# MAGIC    **transfer from a store with excess** or **urgent purchase order**.
# MAGIC
# MAGIC Outputs: `gold_stockout_predictions`, `gold_replenishment_queue`, `gold_model_metrics`.

# COMMAND ----------

# MAGIC %pip install -q mlflow scikit-learn

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import hashlib
import mlflow, mlflow.sklearn
import numpy as np, pandas as pd
from pyspark.sql import functions as F, Window as W
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, precision_score, recall_score

C = "serverless_stable_xpbmim_catalog"
S, G = f"{C}.fe_bar_varejo_silver", f"{C}.fe_bar_varejo_gold"
H = 7                      # prediction horizon (days)
mlflow.set_registry_uri("databricks-uc")

# COMMAND ----------

# MAGIC %md ## 1 · Point-in-time features and label

# COMMAND ----------

d = spark.table(f"{G}.gold_daily_store_sku")
w = W.partitionBy("store_id", "sku").orderBy("snapshot_date")
fwd = w.rowsBetween(1, H)

feat = (d
    .withColumn("avg_units_7d", F.avg("units_sold").over(w.rowsBetween(-6, 0)))
    .withColumn("avg_units_28d", F.avg("units_sold").over(w.rowsBetween(-27, 0)))
    .withColumn("std_units_28d", F.coalesce(F.stddev("units_sold").over(w.rowsBetween(-27, 0)), F.lit(0.0)))
    .withColumn("stockout_days_28d", F.sum("stockout_flag").over(w.rowsBetween(-27, 0)))
    .withColumn("days_of_cover", F.col("on_hand_units") / F.greatest(F.col("avg_units_28d"), F.lit(0.1)))
    .withColumn("onhand_to_rop", F.col("on_hand_units") / F.greatest(F.col("reorder_point"), F.lit(1)))
    .withColumn("dow", F.dayofweek("snapshot_date"))
    .withColumn("label", F.when(F.max("stockout_flag").over(fwd) > 0, 1).otherwise(0))
    .withColumn("fwd_rows", F.count("stockout_flag").over(fwd))
    # measured (not estimated) lead: days until the first stockout inside the horizon
    .withColumn("day_idx", F.datediff("snapshot_date", F.lit("2026-01-01")))
    .withColumn("days_to_first_stockout",
                F.min(F.when(F.col("stockout_flag") == 1, F.col("day_idx"))).over(fwd) - F.col("day_idx")))

# The purchase order open on each day, with the arrival the planner EXPECTED (not the actual one).
po = spark.table(f"{S}.silver_purchase_orders").select(
    "store_id", "sku", "order_date", "expected_arrival", "actual_arrival", F.col("qty_units").alias("po_units"))
f_alias, p_alias = feat.alias("f"), po.alias("p")
open_po = (f_alias.join(p_alias,
            (F.col("f.store_id") == F.col("p.store_id")) & (F.col("f.sku") == F.col("p.sku")) &
            (F.col("p.order_date") <= F.col("f.snapshot_date")) & (F.col("p.actual_arrival") > F.col("f.snapshot_date")),
            "left")
           .select("f.*", F.coalesce("p.po_units", F.lit(0)).alias("inbound_units"),
                   F.datediff("p.expected_arrival", "f.snapshot_date").alias("days_until_inbound")))
otif = spark.table(f"{G}.gold_supplier_otif").select("supplier_id", "on_time_rate", "avg_delay_when_late")
feat = (open_po.join(otif, "supplier_id", "left")
        .withColumn("days_until_inbound", F.coalesce("days_until_inbound", F.lit(99)))
        .withColumn("inbound_cover_days", F.col("inbound_units") / F.greatest(F.col("avg_units_28d"), F.lit(0.1))))

NUM = ["on_hand_units", "reorder_point", "lead_time_days", "avg_units_7d", "avg_units_28d", "std_units_28d",
       "stockout_days_28d", "days_of_cover", "onhand_to_rop", "inbound_units", "days_until_inbound",
       "inbound_cover_days", "on_time_rate", "avg_delay_when_late", "unit_price", "promo_flag", "dow"]
CAT = ["category", "store_format", "region"]

# Train only on items that are ON THE SHELF (on_hand > 0, no stockout today) with a full horizon.
labeled = (feat.filter((F.col("on_hand_units") > 0) & (F.col("stockout_flag") == 0) & (F.col("fwd_rows") == H))
           .filter(F.col("snapshot_date") >= F.date_add(F.lit("2026-05-28"), 28))   # full 28d history
           .select(*NUM, *CAT, "snapshot_date", "label", "days_to_first_stockout").toPandas())
labeled["avg_delay_when_late"] = labeled["avg_delay_when_late"].fillna(0)
print(f"labeled in-stock rows: {len(labeled):,} · positive rate: {labeled['label'].mean():.2%}")

# COMMAND ----------

# MAGIC %md ## 2 · Time-based split, model vs. naive rule

# COMMAND ----------

X = pd.get_dummies(labeled[NUM + CAT], columns=CAT, dtype=float)
y = labeled["label"].to_numpy()
dates = pd.to_datetime(labeled["snapshot_date"])
cutoff = dates.quantile(0.75)
tr, te = (dates <= cutoff).to_numpy(), (dates > cutoff).to_numpy()
print(f"train {tr.sum():,} rows (≤ {cutoff.date()}) · test {te.sum():,} rows")

# Naive planner rule: flag when days of cover < supplier lead time
naive = (labeled["days_of_cover"] < labeled["lead_time_days"]).astype(int).to_numpy()

with mlflow.start_run(run_name="stockout_early_warning_hgb") as run:
    clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06, max_depth=6,
                                         l2_regularization=1.0, random_state=42)
    clf.fit(X[tr], y[tr])
    p = clf.predict_proba(X[te])[:, 1]
    yt = y[te]
    k = int(0.05 * te.sum() / labeled.loc[te, "snapshot_date"].nunique())  # 5% of daily in-stock items
    # precision@K computed per test day, then averaged (what the ops team sees each morning)
    te_df = pd.DataFrame({"d": labeled.loc[te, "snapshot_date"].to_numpy(), "p": p, "y": yt})
    prec_at_k = te_df.groupby("d").apply(lambda g: g.nlargest(k, "p")["y"].mean()).mean()
    thr = float(np.quantile(p, 0.90))    # alert on the top decile of risk
    pred = (p >= thr).astype(int)
    m = {
        "test_auc": roc_auc_score(yt, p), "test_avg_precision": average_precision_score(yt, p),
        "precision_top_decile": precision_score(yt, pred), "recall_top_decile": recall_score(yt, pred),
        "precision_at_k_daily": float(prec_at_k), "k_daily": k, "positive_rate": float(yt.mean()),
        "naive_precision": precision_score(yt, naive[te]), "naive_recall": recall_score(yt, naive[te]),
        "naive_flag_rate": float(naive[te].mean()),
    }
    mlflow.log_params({"horizon_days": H, "max_iter": 300, "learning_rate": 0.06, "max_depth": 6})
    mlflow.log_metrics(m)
    sig = mlflow.models.infer_signature(X[tr].head(50), clf.predict_proba(X[tr].head(50))[:, 1])
    mlflow.sklearn.log_model(clf, artifact_path="model", signature=sig, serialization_format="cloudpickle",
                             registered_model_name=f"{G}.stockout_early_warning")
    run_id = run.info.run_id

print("=" * 64)
print("EARLY-WARNING MODEL — test set (later dates, in-stock items only)")
print("=" * 64)
for key in ["test_auc", "test_avg_precision", "precision_top_decile", "recall_top_decile",
            "precision_at_k_daily", "positive_rate"]:
    print(f"{key:24s} {m[key]:.4f}")
print(f"{'k_daily':24s} {k}")
print("-" * 64)
print("NAIVE RULE (days_of_cover < lead_time)")
print(f"{'naive_precision':24s} {m['naive_precision']:.4f}")
print(f"{'naive_recall':24s} {m['naive_recall']:.4f}")
print(f"{'naive_flag_rate':24s} {m['naive_flag_rate']:.4f}   (share of items it would flag)")
print("registered:", f"{G}.stockout_early_warning", "| run:", run_id)

# COMMAND ----------

# MAGIC %md ## 3 · Lead time of the warning (true alerts only)

# COMMAND ----------

te_rows = labeled.loc[te].copy()
te_rows["p"] = p
hits = te_rows[(te_rows["p"] >= thr) & (te_rows["label"] == 1)]
lead = hits["days_to_first_stockout"].astype(int)     # measured from the actual future stockout
m["avg_warning_lead_days"] = float(lead.mean())
m["share_warned_2plus_days"] = float((lead >= 2).mean())
print(f"true alerts: {len(hits):,} · avg warning lead: {lead.mean():.1f} days · warned ≥2 days ahead: {(lead >= 2).mean():.0%}")

# COMMAND ----------

# MAGIC %md ## 4 · Score today's in-stock items and build the action queue

# COMMAND ----------

today = feat.agg(F.max("snapshot_date")).first()[0]
cur = (feat.filter((F.col("snapshot_date") == F.lit(today)) & (F.col("on_hand_units") > 0))
       .select("store_id", "store_name", "city", "uf", "region", "store_format", "sku", "product_name",
               "category", "supplier_id", *[c for c in NUM if c not in ("unit_price",)], "unit_price",
               "unit_cost").toPandas())
cur["avg_delay_when_late"] = cur["avg_delay_when_late"].fillna(0)

# Orders still open today are not in the received-PO history, so the historical reconstruction
# would show "nothing inbound". Use the real open orders (expected ETA) BEFORE scoring.
opn = spark.table(f"{G}.gold_current_position").select("store_id", "sku", "inbound_units", "days_until_inbound").toPandas()
cur = cur.drop(columns=["inbound_units", "days_until_inbound"]).merge(opn, on=["store_id", "sku"], how="left")
cur["inbound_units"] = cur["inbound_units"].fillna(0)
cur["days_until_inbound"] = cur["days_until_inbound"].fillna(99)
v = np.maximum(cur["avg_units_28d"], 0.1)
cur["inbound_cover_days"] = cur["inbound_units"] / v

Xc = pd.get_dummies(cur[NUM + CAT], columns=CAT, dtype=float).reindex(columns=X.columns, fill_value=0)
cur["risk_probability"] = clf.predict_proba(Xc)[:, 1].round(4)

# Expected arrival adjusted by the supplier's lateness history; an order already past its
# expected date is assumed to land after the supplier's typical delay.
dui = cur["days_until_inbound"]
late_hist = (1 - cur["on_time_rate"].fillna(1)) * cur["avg_delay_when_late"]
eta_adj = np.where(dui < 0, cur["avg_delay_when_late"].clip(lower=1), dui + late_hist)
eta_adj = pd.Series(np.where(cur["inbound_units"] > 0, eta_adj, 99), index=cur.index)
inbound_in_window = np.where(eta_adj <= H, cur["inbound_units"], 0)
cur["days_of_cover"] = (cur["on_hand_units"] / v).round(1)
cur["eta_adjusted_days"] = eta_adj.round(1)
cur["shortfall_units"] = np.maximum(0, np.ceil(v * H - cur["on_hand_units"] - inbound_in_window)).astype(int)
# Units lost before the inbound order lands (if it arrives after the shelf empties)
gap_days = np.where(cur["inbound_units"] > 0, np.clip(eta_adj - cur["days_of_cover"], 0, H), np.clip(H - cur["days_of_cover"], 0, H))
cur["units_at_risk"] = np.maximum(cur["shortfall_units"], np.ceil(v * gap_days)).astype(int)
cur["revenue_at_risk"] = (cur["risk_probability"] * cur["units_at_risk"] * cur["unit_price"]).round(2)

pred_cols = ["store_id", "store_name", "city", "uf", "region", "sku", "product_name", "category", "supplier_id",
             "on_hand_units", "avg_units_28d", "days_of_cover", "inbound_units", "days_until_inbound",
             "eta_adjusted_days", "on_time_rate", "lead_time_days", "unit_price", "risk_probability",
             "shortfall_units", "units_at_risk", "revenue_at_risk"]
preds = cur[pred_cols].copy(); preds["snapshot_date"] = today
spark.createDataFrame(preds).write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{G}.gold_stockout_predictions")
print(f"scored {len(preds):,} in-stock store×sku rows as of {today}")

# COMMAND ----------

# Queue = items the model flags (top risk decile threshold from test) with real money at stake
q = cur[(cur["risk_probability"] >= thr) & (cur["units_at_risk"] > 0) & (cur["revenue_at_risk"] >= 20)].copy()
# A donor store keeps 10 days of its own cover and only offers the rest; transfers only make
# sense between nearby stores (road distance proxy: great-circle ≤ 450 km).
coords = spark.table(f"{S}.silver_dim_store").select("store_id", "lat", "lon").toPandas().set_index("store_id")
def km(a, b):
    la1, lo1, la2, lo2 = map(np.radians, [coords.at[a, "lat"], coords.at[a, "lon"], coords.at[b, "lat"], coords.at[b, "lon"]])
    h = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return float(6371 * 2 * np.arcsin(np.sqrt(h)))
MAX_TRANSFER_KM = 450
donors_pool = cur.assign(spare=lambda x: np.floor(x["on_hand_units"] - np.maximum(x["avg_units_28d"], 0.1) * 10))
donors_pool = donors_pool[(donors_pool["days_of_cover"] >= 12) & (donors_pool["spare"] >= 3)]

actions = []
for _, r in q.iterrows():
    need = int(max(r["units_at_risk"], np.ceil(r["avg_units_28d"] * 3)))
    cand = donors_pool[(donors_pool["sku"] == r["sku"]) & (donors_pool["store_id"] != r["store_id"])].copy()
    if len(cand):
        cand["km"] = [km(r["store_id"], s) for s in cand["store_id"]]
        cand = cand[cand["km"] <= MAX_TRANSFER_KM].sort_values(["km", "spare"], ascending=[True, False])
    dist_km = None
    if len(cand):
        dnr = cand.iloc[0]
        units = int(min(need, dnr["spare"]))
        dist_km = round(float(dnr["km"]))
        kind, eta = "TRANSFER", (1 if dist_km <= 150 else 2)
        frm_id, frm_name, frm_city, frm_cover = dnr["store_id"], dnr["store_name"], dnr["city"], float(dnr["days_of_cover"])
    elif r["inbound_units"] > 0:
        # an order is already on the way but lands after the shelf empties → pull it forward
        units, kind = int(r["inbound_units"]), "EXPEDITE"
        eta = int(max(1, np.ceil(r["eta_adjusted_days"]) - 2))
        frm_id, frm_name, frm_city, frm_cover = r["supplier_id"], None, None, None
    else:
        units, kind = need, "URGENT_ORDER"
        eta = int(max(1, r["lead_time_days"] - 1))
        frm_id, frm_name, frm_city, frm_cover = r["supplier_id"], None, None, None
    covered = min(units, r["units_at_risk"])
    protected = round(float(r["risk_probability"] * covered * r["unit_price"]), 2)
    sev = "CRITICAL" if r["days_of_cover"] < 2 else ("HIGH" if r["days_of_cover"] < 4 else "MEDIUM")
    aid = hashlib.sha1(f"{today}|{r['store_id']}|{r['sku']}|{kind}".encode()).hexdigest()[:12]
    actions.append(dict(action_id=f"ACT-{aid}", snapshot_date=today, action_type=kind, severity=sev,
        store_id=r["store_id"], store_name=r["store_name"], city=r["city"], uf=r["uf"], region=r["region"],
        sku=r["sku"], product_name=r["product_name"], category=r["category"],
        from_id=frm_id, from_store_name=frm_name, from_city=frm_city, donor_days_of_cover=frm_cover,
        transfer_km=dist_km,
        units=int(units), eta_days=int(eta), on_hand_units=int(r["on_hand_units"]),
        days_of_cover=float(r["days_of_cover"]), inbound_units=int(r["inbound_units"]),
        eta_adjusted_days=float(r["eta_adjusted_days"]) if r["inbound_units"] > 0 else None,
        supplier_id=r["supplier_id"], supplier_on_time_rate=float(r["on_time_rate"]),
        risk_probability=float(r["risk_probability"]), units_at_risk=int(r["units_at_risk"]),
        revenue_at_risk=float(r["revenue_at_risk"]), revenue_protected=protected))
queue = pd.DataFrame(actions).sort_values("revenue_protected", ascending=False).reset_index(drop=True)
queue["priority"] = np.arange(1, len(queue) + 1)
spark.createDataFrame(queue).write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{G}.gold_replenishment_queue")

m.update({"queue_size": int(len(queue)), "in_stock_scored": int(len(cur)),
          "queue_share_of_assortment": float(len(queue) / (cur.shape[0] or 1)),
          "revenue_protected_total": float(queue["revenue_protected"].sum()), "alert_threshold": thr,
          "run_id": run_id})
spark.createDataFrame(pd.DataFrame([{k: (float(v) if isinstance(v, (int, float, np.floating)) and k != "run_id" else v) for k, v in m.items()}])) \
    .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{G}.gold_model_metrics")

print("=" * 64)
mix = queue["action_type"].value_counts().to_dict()
print(f"queue: {len(queue)} actions = {len(queue) / len(cur):.1%} of in-stock items · mix {mix}")
print(f"R$ at stake protected if approved: R$ {queue['revenue_protected'].sum():,.0f} (next 7 days)")
print("=" * 64)
print(queue.head(10)[["priority", "severity", "action_type", "store_name", "product_name", "from_store_name",
                      "units", "days_of_cover", "risk_probability", "revenue_protected"]].to_string(index=False))
