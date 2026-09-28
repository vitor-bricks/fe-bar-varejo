# Databricks notebook source
# MAGIC %md
# MAGIC # LojaBR · Centro de Abastecimento — Agente de Reposição (tool-calling)
# MAGIC
# MAGIC A real tool-calling agent on the Databricks **Foundation Model API**
# MAGIC (`databricks-claude-sonnet-5`, OpenAI-compatible `tools`). For the highest-value items in
# MAGIC the action queue it **checks the facts with tools** and then confirms or changes the action
# MAGIC the rule engine proposed, writing a grounded rationale in Portuguese.
# MAGIC
# MAGIC | Tool | What it returns |
# MAGIC |---|---|
# MAGIC | `get_item_position` | stock, velocity, days of cover, open order + expected ETA, recent stockouts |
# MAGIC | `find_donor_stores` | nearby stores (≤ 450 km) with spare units of the same item |
# MAGIC | `get_supplier_history` | on-time rate and typical delay of the supplier |
# MAGIC | `submit_decision` | final decision (action, units, source, confidence, rationale) |
# MAGIC
# MAGIC Items not reviewed by the agent keep a rule-based rationale, labelled as such.
# MAGIC Output: `gold_replenishment_queue_final`, `gold_agent_runs`.

# COMMAND ----------

import json, time
import numpy as np, pandas as pd
from datetime import datetime, timezone
from databricks.sdk import WorkspaceClient

C = "serverless_stable_xpbmim_catalog"
S, G = f"{C}.fe_bar_varejo_silver", f"{C}.fe_bar_varejo_gold"
ENDPOINT = "databricks-claude-sonnet-5"
TOP_N = 12
MAX_STEPS = 8
w = WorkspaceClient()

queue = spark.table(f"{G}.gold_replenishment_queue").toPandas().sort_values("priority")
pos = spark.table(f"{G}.gold_current_position").toPandas().set_index(["store_id", "sku"])
otif = spark.table(f"{G}.gold_supplier_otif").toPandas().set_index("supplier_id")
coords = spark.table(f"{S}.silver_dim_store").select("store_id", "store_name", "lat", "lon").toPandas().set_index("store_id")
print(f"queue {len(queue)} actions · agent reviews top {TOP_N} by R$ protected")

# COMMAND ----------

# MAGIC %md ## Tools

# COMMAND ----------

def km(a, b):
    la1, lo1, la2, lo2 = map(np.radians, [coords.at[a, "lat"], coords.at[a, "lon"], coords.at[b, "lat"], coords.at[b, "lon"]])
    h = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return round(float(6371 * 2 * np.arcsin(np.sqrt(h))))


def get_item_position(store_id, sku):
    r = pos.loc[(store_id, sku)]
    return {"loja": r["store_name"], "produto": r["product_name"], "estoque_un": int(r["on_hand_units"]),
            "venda_media_dia": round(float(r["avg_units_28d"]), 1), "cobertura_dias": float(r["days_of_cover"]),
            "rupturas_ultimos_28d": int(r["stockout_days_28d"]), "pedido_a_caminho_un": int(r["inbound_units"]),
            "dias_ate_chegada_prevista": None if pd.isna(r["days_until_inbound"]) else int(r["days_until_inbound"]),
            "fornecedor": otif.at[r["supplier_id"], "supplier_name"], "supplier_id": r["supplier_id"],
            "lead_time_dias": int(r["lead_time_days"]), "preco": float(r["unit_price"])}


def find_donor_stores(sku, store_id):
    out = []
    for (s, k), r in pos.loc[pos.index.get_level_values("sku") == sku].iterrows():
        if s == store_id:
            continue
        spare = int(np.floor(r["on_hand_units"] - max(r["avg_units_28d"], 0.1) * 10))
        d = km(store_id, s)
        if d <= 450 and r["days_of_cover"] >= 12 and spare >= 3:
            out.append({"loja": r["store_name"], "store_id": s, "distancia_km": d,
                        "cobertura_dias": float(r["days_of_cover"]), "excedente_un": spare})
    return sorted(out, key=lambda x: x["distancia_km"])[:4] or [{"resultado": "nenhuma loja a até 450 km com excedente"}]


def get_supplier_history(supplier_id):
    r = otif.loc[supplier_id]
    return {"fornecedor": r["supplier_name"], "pedidos_recebidos": int(r["orders_received"]),
            "pontualidade": float(r["on_time_rate"]), "atraso_medio_quando_atrasa_dias": float(r["avg_delay_when_late"] or 0)}


TOOLS = [
    {"type": "function", "function": {"name": "get_item_position", "description": "Posição atual do item na loja: estoque, venda média, cobertura, pedido a caminho e chegada prevista.",
        "parameters": {"type": "object", "properties": {"store_id": {"type": "string"}, "sku": {"type": "string"}}, "required": ["store_id", "sku"]}}},
    {"type": "function", "function": {"name": "find_donor_stores", "description": "Lojas a até 450 km com excedente do mesmo item (mantendo 10 dias de cobertura própria).",
        "parameters": {"type": "object", "properties": {"sku": {"type": "string"}, "store_id": {"type": "string"}}, "required": ["sku", "store_id"]}}},
    {"type": "function", "function": {"name": "get_supplier_history", "description": "Pontualidade histórica do fornecedor e atraso típico.",
        "parameters": {"type": "object", "properties": {"supplier_id": {"type": "string"}}, "required": ["supplier_id"]}}},
    {"type": "function", "function": {"name": "submit_decision", "description": "Registra a decisão final. Chame exatamente uma vez.",
        "parameters": {"type": "object", "properties": {
            "action_type": {"type": "string", "enum": ["TRANSFER", "EXPEDITE", "URGENT_ORDER"]},
            "from_id": {"type": "string", "description": "store_id doadora (TRANSFER) ou supplier_id"},
            "units": {"type": "integer"}, "confidence": {"type": "string", "enum": ["alta", "média", "baixa"]},
            "rationale": {"type": "string", "description": "2-3 frases em português, com os números verificados"}},
            "required": ["action_type", "from_id", "units", "confidence", "rationale"]}}},
]
IMPL = {"get_item_position": get_item_position, "find_donor_stores": find_donor_stores,
        "get_supplier_history": get_supplier_history}

SYSTEM = ("Você é o Agente de Reposição da LojaBR, rede de supermercados. Para o item informado, "
          "VERIFIQUE os fatos com as ferramentas antes de decidir: posição do item, lojas doadoras "
          "próximas e histórico do fornecedor. Regras: prefira TRANSFER quando houver loja próxima com "
          "excedente (é mais rápido); use EXPEDITE quando já existe pedido a caminho que chega depois "
          "de a gôndola esvaziar; use URGENT_ORDER quando não há alternativa. Confirme a proposta do "
          "motor ou mude, se os fatos indicarem. Finalize chamando submit_decision exatamente uma vez, "
          "com justificativa em português para o gerente de loja: no máximo 2 frases (≈45 palavras), "
          "citando apenas números obtidos pelas ferramentas. Use nomes de lojas, produtos e fornecedores; "
          "NUNCA cite códigos internos (SKU, store_id, supplier_id) nem nomes de campos.")

# COMMAND ----------

# MAGIC %md ## Agent loop

# COMMAND ----------

REQUIRED = ["action_type", "from_id", "units", "confidence", "rationale"]


def chat(messages):
    return w.api_client.do("POST", f"/serving-endpoints/{ENDPOINT}/invocations",
                           body={"messages": messages, "tools": TOOLS, "max_tokens": 1200})


def review(item):
    msgs = [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": (
                f"Item: {item['product_name']} (sku {item['sku']}) na loja {item['store_name']} (store_id {item['store_id']}). "
                f"Modelo: risco de ruptura em 7 dias = {item['risk_probability']:.0%}; R$ em risco ≈ {item['revenue_at_risk']:.0f}. "
                f"Proposta do motor: {item['action_type']} de {item['units']} un"
                + (f" a partir de {item['from_store_name']}." if item['action_type'] == 'TRANSFER' else f" (fornecedor {item['supplier_id']}).")
                + " Verifique e decida.")}]
    tools_used, t0 = [], time.time()
    for _ in range(MAX_STEPS):
        resp = chat(msgs)
        msg = resp["choices"][0]["message"]
        calls = msg.get("tool_calls") or []
        if not calls:
            break
        msgs.append({"role": "assistant", "content": msg.get("content") or None, "tool_calls": calls})
        fact_calls = [c for c in calls if c["function"]["name"] != "submit_decision"]
        for c in calls:   # every tool_call id must get a tool result
            name = c["function"]["name"]
            try:
                args = json.loads(c["function"]["arguments"] or "{}")
            except json.JSONDecodeError:
                args = {}
            if name == "submit_decision":
                missing = [k for k in REQUIRED if k not in args]
                if fact_calls:
                    # decided in the same turn as fact-finding → not grounded yet; ask again
                    result = {"erro": "Decisão prematura: aguarde os resultados das ferramentas e chame submit_decision de novo."}
                elif missing:
                    result = {"erro": f"Campos obrigatórios faltando: {missing}"}
                else:
                    tools_used.append(name)
                    return {**args, "tools_used": tools_used, "latency_ms": int((time.time() - t0) * 1000)}
            else:
                tools_used.append(name)
                try:
                    result = IMPL[name](**args)
                except Exception as e:
                    result = {"erro": str(e)}
            msgs.append({"role": "tool", "tool_call_id": c["id"], "content": json.dumps(result, ensure_ascii=False, default=str)})
    return {"error": "agent ended without submit_decision", "tools_used": tools_used,
            "latency_ms": int((time.time() - t0) * 1000)}


decisions = {}
for _, it in queue.head(TOP_N).iterrows():
    try:
        d = review(it)
    except Exception as e:
        d = {"error": str(e)[:300], "tools_used": []}
    decisions[it["action_id"]] = d
    ok = "error" not in d
    print(f"#{it['priority']:>3} {it['store_name']:<24} {it['product_name'][:34]:<34} motor={it['action_type']:<12} "
          f"agente={d.get('action_type', 'ERRO'):<12} tools={','.join(d.get('tools_used', []))}")
    print(f"      → {d['rationale'] if ok else d['error']}")

# COMMAND ----------

# MAGIC %md ## Rule-based rationale for the rest of the queue (labelled as such)

# COMMAND ----------

def rule_rationale(r):
    base = (f"{r['product_name']} em {r['store_name']}: {r['days_of_cover']:.1f} dias de cobertura e "
            f"{r['risk_probability']:.0%} de risco de ruptura em 7 dias.")
    if r["action_type"] == "TRANSFER":
        return base + (f" {r['from_store_name']} ({int(r['transfer_km'])} km) tem {r['donor_days_of_cover']:.0f} dias de "
                       f"cobertura — transferir {r['units']} un, chegada em {r['eta_days']} dia(s).")
    sup = otif.at[r["supplier_id"], "supplier_name"]
    if r["action_type"] == "EXPEDITE":
        return base + (f" O pedido de {r['inbound_units']} un de {sup} chega só em ~{r['eta_adjusted_days']:.0f} dias "
                       f"(pontualidade {r['supplier_on_time_rate']:.0%}) — cobrar antecipação para {r['eta_days']} dia(s).")
    return base + f" Sem pedido a caminho nem loja próxima com excedente — pedido emergencial de {r['units']} un a {sup}."


rows = []
for _, r in queue.iterrows():
    d = decisions.get(r["action_id"])
    row = r.to_dict()
    row["supplier_name"] = otif.at[r["supplier_id"], "supplier_name"]
    if d and "error" not in d:
        changed = d["action_type"] != r["action_type"]
        row.update(rationale=d["rationale"], rationale_source="AGENTE", agent_confidence=d["confidence"],
                   agent_changed_action=changed, agent_tools=",".join(d["tools_used"]),
                   agent_latency_ms=d.get("latency_ms"))
        if changed:   # the agent's decision wins; keep the engine's risk economics
            row["action_type"] = d["action_type"]
            row["from_id"] = d["from_id"]
            if d["action_type"] == "TRANSFER" and d["from_id"] in coords.index:
                row["from_store_name"] = coords.at[d["from_id"], "store_name"]
                row["transfer_km"] = km(r["store_id"], d["from_id"])
                row["eta_days"] = 1 if row["transfer_km"] <= 150 else 2
            else:
                row["from_store_name"], row["from_city"], row["transfer_km"], row["donor_days_of_cover"] = None, None, None, None
        row["units"] = int(d["units"])
    else:
        row.update(rationale=rule_rationale(r), rationale_source="REGRA", agent_confidence=None,
                   agent_changed_action=False, agent_tools=None, agent_latency_ms=None)
    rows.append(row)

final = pd.DataFrame(rows)
spark.createDataFrame(final).write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{G}.gold_replenishment_queue_final")

reviewed = [d for d in decisions.values() if "error" not in d]
run = pd.DataFrame([{"run_at": datetime.now(timezone.utc).isoformat(), "model_endpoint": ENDPOINT,
                     "items_reviewed": len(reviewed), "errors": len(decisions) - len(reviewed),
                     "actions_changed": int(final["agent_changed_action"].sum()),
                     "avg_tool_calls": float(np.mean([len(d["tools_used"]) for d in reviewed])) if reviewed else 0.0,
                     "avg_latency_ms": float(np.mean([d["latency_ms"] for d in reviewed])) if reviewed else 0.0}])
spark.createDataFrame(run).write.mode("append").option("mergeSchema", "true").saveAsTable(f"{G}.gold_agent_runs")
print("\nAGENT RUN:", run.to_dict("records")[0])
