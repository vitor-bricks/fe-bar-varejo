# Databricks notebook source
# MAGIC %md
# MAGIC # FE Bar Varejo — Stockout-Risk Model + GenAI Reorder Rationale
# MAGIC
# MAGIC **ML:** trains a classifier that predicts, for each store×SKU, the probability of a
# MAGIC **stockout in the next 7 days**, using trailing demand/inventory features built from the
# MAGIC gold layer. Logged to MLflow and registered in **Unity Catalog**.
# MAGIC
# MAGIC **GenAI:** for the top at-risk SKUs, calls a Databricks Foundation Model
# MAGIC (`databricks-claude-sonnet-5`) to write a concise, business-ready **reorder rationale**
# MAGIC in Portuguese — turning a probability into an action a store manager can act on.
# MAGIC
# MAGIC Outputs written to gold: `gold_stockout_predictions`, `gold_reorder_rationale`.

# COMMAND ----------

# MAGIC %pip install -q mlflow scikit-learn

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import mlflow, mlflow.sklearn
import numpy as np, pandas as pd
from pyspark.sql import functions as F, Window as W
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, classification_report, precision_score, recall_score

C = "serverless_stable_xpbmim_catalog"
GOLD = f"{C}.fe_bar_varejo_gold"
mlflow.set_registry_uri("databricks-uc")

# COMMAND ----------

# MAGIC %md ## Feature engineering (trailing windows) + label (stockout in next 7 days)

# COMMAND ----------

g = spark.table(f"{GOLD}.gold_daily_store_sku")
w_key = W.partitionBy("store_id", "sku").orderBy("snapshot_date")
r7 = w_key.rowsBetween(-6, 0)
r14 = w_key.rowsBetween(-13, 0)
lead7 = w_key.rowsBetween(1, 7)

feat = (g
    .withColumn("avg_units_7d", F.avg("units_sold").over(r7))
    .withColumn("avg_units_14d", F.avg("units_sold").over(r14))
    .withColumn("stockout_7d", F.sum("stockout_flag").over(r7))
    .withColumn("stockout_14d", F.sum("stockout_flag").over(r14))
    .withColumn("lost_7d", F.sum("lost_sales_units").over(r7))
    .withColumn("avg_onhand_7d", F.avg("on_hand_units").over(r7))
    .withColumn("onhand_to_reorder", F.round(F.col("on_hand_units") / F.greatest(F.col("reorder_point"), F.lit(1)), 3))
    .withColumn("dow", F.dayofweek("snapshot_date"))
    # label: any stockout in the following 7 days
    .withColumn("label_stockout_next7", F.when(F.max("stockout_flag").over(lead7) > 0, 1).otherwise(0))
    # count of forward rows available (to know when label is complete)
    .withColumn("fwd_rows", F.count("stockout_flag").over(lead7))
)

FEATURES = ["on_hand_units", "on_order_units", "reorder_point", "shelf_capacity_units",
            "lead_time_days", "days_to_arrival", "units_sold", "avg_units_7d", "avg_units_14d",
            "stockout_7d", "stockout_14d", "lost_7d", "avg_onhand_7d", "onhand_to_reorder",
            "unit_price", "dow", "days_of_supply"]
CAT = ["category", "region", "store_format"]

max_date = feat.agg(F.max("snapshot_date")).first()[0]
print("max snapshot_date:", max_date)

# labeled set = rows with a full 7-day forward window
labeled = feat.filter(F.col("fwd_rows") == 7).select(*FEATURES, *CAT, "snapshot_date", "label_stockout_next7")
pdf = labeled.toPandas()
pdf["days_of_supply"] = pdf["days_of_supply"].fillna(999.0)
print("labeled rows:", len(pdf), "| positive rate:", round(pdf["label_stockout_next7"].mean(), 4))

# COMMAND ----------

# MAGIC %md ## Time-based train/test split + model training

# COMMAND ----------

X = pd.get_dummies(pdf[FEATURES + CAT], columns=CAT)
y = pdf["label_stockout_next7"].values
dates = pd.to_datetime(pdf["snapshot_date"])
cutoff = dates.quantile(0.75)
tr, te = dates <= cutoff, dates > cutoff
print(f"train rows: {tr.sum():,} (<= {cutoff.date()}) | test rows: {te.sum():,}")

mlflow.sklearn.autolog(log_models=False)
with mlflow.start_run(run_name="stockout_risk_hgb") as run:
    clf = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.08,
                                         max_depth=6, l2_regularization=1.0, random_state=42)
    clf.fit(X[tr], y[tr])
    proba = clf.predict_proba(X[te])[:, 1]
    pred = (proba >= 0.5).astype(int)
    auc = roc_auc_score(y[te], proba)
    ap = average_precision_score(y[te], proba)
    prec = precision_score(y[te], pred, zero_division=0)
    rec = recall_score(y[te], pred, zero_division=0)
    # precision@top-100 (where the ops team would actually act)
    k = 100
    top_idx = np.argsort(proba)[::-1][:k]
    prec_at_k = y[te].reshape(-1)[top_idx].mean()
    mlflow.log_metrics({"test_auc": auc, "test_ap": ap, "test_precision": prec,
                        "test_recall": rec, "precision_at_100": prec_at_k})

    signature = mlflow.models.infer_signature(X[tr], clf.predict_proba(X[tr])[:, 1])
    mlflow.sklearn.log_model(clf, artifact_path="model", signature=signature,
                             serialization_format="cloudpickle",
                             registered_model_name=f"{GOLD}.stockout_risk")
    run_id = run.info.run_id

print("=" * 60)
print("MODEL EVALUATION (test set, held-out later dates)")
print("=" * 60)
print(f"AUC-ROC          : {auc:.4f}")
print(f"Avg precision    : {ap:.4f}")
print(f"Precision @0.5   : {prec:.4f}")
print(f"Recall @0.5      : {rec:.4f}")
print(f"Precision @top100: {prec_at_k:.4f}   (of the 100 highest-risk, this fraction really stocked out)")
print("-" * 60)
print(classification_report(y[te], pred, target_names=["no_stockout", "stockout_next7"]))

# feature importance (permutation-free: use fitted model's not available for HGB; use simple corr proxy)
print("registered model:", f"{GOLD}.stockout_risk", "| run:", run_id)

# persist metrics so evidence can be pulled via SQL after the job run
metrics_pd = pd.DataFrame([{
    "model": "stockout_risk_hgb", "run_id": run_id,
    "train_rows": int(tr.sum()), "test_rows": int(te.sum()),
    "positive_rate": float(round(pdf["label_stockout_next7"].mean(), 4)),
    "auc": float(round(auc, 4)), "avg_precision": float(round(ap, 4)),
    "precision_05": float(round(prec, 4)), "recall_05": float(round(rec, 4)),
    "precision_at_100": float(round(prec_at_k, 4)),
    "trained_at": pd.Timestamp.utcnow().isoformat()}])
spark.createDataFrame(metrics_pd).write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{GOLD}.gold_model_metrics")

# COMMAND ----------

# MAGIC %md ## Score current combos → gold_stockout_predictions

# COMMAND ----------

cur = feat.filter(F.col("snapshot_date") == F.lit(max_date)).select(
    "store_id", "sku", "category", "brand", "region", "city", "store_format",
    *FEATURES).toPandas()
cur["days_of_supply"] = cur["days_of_supply"].fillna(999.0)
Xcur = pd.get_dummies(cur[FEATURES + CAT], columns=CAT)
Xcur = Xcur.reindex(columns=X.columns, fill_value=0)   # align to training columns
cur["risk_probability"] = clf.predict_proba(Xcur)[:, 1].round(4)
cur["suggested_order_units"] = np.maximum(0,
    np.ceil(cur["avg_units_7d"] * (cur["lead_time_days"] + 7)) - cur["on_hand_units"] - cur["on_order_units"]).astype(int)
cur["expected_lost_revenue_7d"] = (cur["risk_probability"] * cur["avg_units_7d"] * 7 * cur["unit_price"]).round(2)
cur["risk_rank"] = cur["expected_lost_revenue_7d"].rank(ascending=False, method="first").astype(int)
cur["snapshot_date"] = max_date

out_cols = ["store_id", "sku", "category", "brand", "region", "city", "store_format",
            "on_hand_units", "on_order_units", "reorder_point", "lead_time_days",
            "avg_units_7d", "stockout_7d", "unit_price", "risk_probability",
            "suggested_order_units", "expected_lost_revenue_7d", "risk_rank", "snapshot_date"]
sdf = spark.createDataFrame(cur[out_cols])
sdf.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{GOLD}.gold_stockout_predictions")
print(f"wrote {sdf.count():,} scored rows to {GOLD}.gold_stockout_predictions")

top = cur.sort_values("expected_lost_revenue_7d", ascending=False).head(10)
print("\nTOP 10 AT-RISK (by expected 7-day lost revenue):")
print(top[["store_id", "sku", "category", "region", "on_hand_units", "reorder_point",
           "avg_units_7d", "risk_probability", "suggested_order_units", "expected_lost_revenue_7d"]]
      .to_string(index=False))

# COMMAND ----------

# MAGIC %md ## GenAI reorder rationale (Foundation Model API — Claude Sonnet)

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

w = WorkspaceClient()
ENDPOINT = "databricks-claude-sonnet-5"
SYS = ("Voce e um analista de reposicao de uma rede varejista. Escreva uma justificativa "
       "curta (2-3 frases, PT-BR) para o gerente de loja: por que este item esta em risco "
       "de ruptura e qual acao tomar. Seja direto, cite os numeros e o impacto em vendas.")

rationales = []
for _, r in top.iterrows():
    user = (f"Loja {r.store_id} ({r.region}), SKU {r.sku} categoria {r.category}. "
            f"Estoque atual {int(r.on_hand_units)} un, ponto de reposicao {int(r.reorder_point)}, "
            f"venda media 7d {r.avg_units_7d:.1f} un/dia, lead time {int(r.lead_time_days)} dias. "
            f"Probabilidade de ruptura em 7 dias: {r.risk_probability:.0%}. "
            f"Perda de receita esperada: R$ {r.expected_lost_revenue_7d:,.0f}. "
            f"Sugestao de pedido: {int(r.suggested_order_units)} un.")
    try:
        resp = w.serving_endpoints.query(name=ENDPOINT, max_tokens=220,
            messages=[ChatMessage(role=ChatMessageRole.SYSTEM, content=SYS),
                      ChatMessage(role=ChatMessageRole.USER, content=user)])
        content = resp.choices[0].message.content
        if isinstance(content, list):   # Claude returns a list of content blocks
            parts = []
            for p in content:
                if isinstance(p, dict):
                    parts.append(p.get("text", ""))
                elif hasattr(p, "text"):
                    parts.append(p.text or "")
                else:
                    parts.append(str(p))
            txt = " ".join(parts).strip()
        else:
            txt = str(content).strip()
    except Exception as e:
        txt = f"[erro FMAPI: {e}]"
    rationales.append({"store_id": r.store_id, "sku": r.sku, "category": r.category,
                       "risk_probability": float(r.risk_probability),
                       "expected_lost_revenue_7d": float(r.expected_lost_revenue_7d),
                       "suggested_order_units": int(r.suggested_order_units),
                       "reorder_rationale": txt})

rdf = spark.createDataFrame(pd.DataFrame(rationales))
rdf.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{GOLD}.gold_reorder_rationale")
print(f"wrote {len(rationales)} rationales to {GOLD}.gold_reorder_rationale\n")
print("=" * 70)
for x in rationales[:5]:
    print(f"[{x['store_id']} / {x['sku']} / {x['category']}] risk={x['risk_probability']:.0%} "
          f"lost=R${x['expected_lost_revenue_7d']:,.0f} order={x['suggested_order_units']}un")
    print("  ->", x["reorder_rationale"])
    print("-" * 70)
