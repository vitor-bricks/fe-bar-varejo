# Executed notebook — 5cf75b73-a0f1-46a3-8ae5-39c8394d507c

Job task run `779570241607253` · exported with cell outputs (`databricks jobs export-run`).

# LojaBR · Centro de Abastecimento — Agente de Reposição (tool-calling)

A real tool-calling agent on the Databricks **Foundation Model API**
(`databricks-claude-sonnet-5`, OpenAI-compatible `tools`). For the highest-value items in
the action queue it **checks the facts with tools** and then confirms or changes the action
the rule engine proposed, writing a grounded rationale in Portuguese.

| Tool | What it returns |
|---|---|
| `get_item_position` | stock, velocity, days of cover, open order + expected ETA, recent stockouts |
| `find_donor_stores` | nearby stores (≤ 450 km) with spare units of the same item |
| `get_supplier_history` | on-time rate and typical delay of the supplier |
| `submit_decision` | final decision (action, units, source, confidence, rationale) |

Items not reviewed by the agent keep a rule-based rationale, labelled as such.
Output: `gold_replenishment_queue_final`, `gold_agent_runs`.

```python
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
```

**Output**

```text
queue 188 actions · agent reviews top 12 by R$ protected
```

## Tools

```python
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
```

## Agent loop

```python
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
```

**Output**

```text
#  1 LojaBR Moema             Sabão em Pó Omo Lavagem Perfeita 1 motor=EXPEDITE     agente=EXPEDITE     tools=get_item_position,find_donor_stores,get_supplier_history,submit_decision
      → A loja Moema tem apenas 5 unidades em estoque, com venda média de 3,7 por dia e cobertura de 1,3 dias, enquanto o pedido de 26 unidades já em trânsito só chega em 5 dias; não há lojas doadoras a até 450 km. Recomendo expedir esse pedido, mesmo com o fornecedor Limpa Mais Distribuidora tendo pontualidade de 62,7% e atraso médio de 3,91 dias.
#  2 LojaBR Campinas          Café Torrado e Moído Pilão 500g    motor=TRANSFER     agente=TRANSFER     tools=get_item_position,find_donor_stores,get_supplier_history,submit_decision
      → A loja Campinas tem apenas 9 unidades em estoque, cobertura de 0,6 dia e o pedido do fornecedor Atacado Central (95 unidades) só chega em 2 dias, com esse fornecedor apresentando 83% de pontualidade e atraso médio de 2 dias quando falha. A loja Ribeirão Preto tem excedente de 61 unidades e 18,2 dias de cobertura, permitindo transferir 46 unidades rapidamente e evitar a ruptura iminente.
#  3 LojaBR Tatuapé           Picanha Bovina Resfriada (kg)      motor=EXPEDITE     agente=EXPEDITE     tools=get_item_position,find_donor_stores,get_supplier_history,submit_decision
      → Não há loja doadora em até 450 km, mas já existe um pedido de 10 unidades a caminho da Frios Paraná Logística, previsto para chegar em 4 dias — tempo maior que a cobertura atual de apenas 1,2 dias com estoque de 2 unidades. Como o fornecedor tem 74,8% de pontualidade e atraso médio de 2,48 dias quando falha, recomenda-se expedir esse pedido para evitar ruptura antes da chegada.
#  4 LojaBR Niterói           Café Torrado e Moído Pilão 500g    motor=EXPEDITE     agente=EXPEDITE     tools=get_item_position,find_donor_stores,get_supplier_history,submit_decision
      → Não há lojas doadoras em até 450 km, então a transferência não é viável. O estoque de 13 unidades cobre apenas 1,6 dias de venda, enquanto o pedido de 46 unidades já a caminho só chega em 4 dias; como a Atacado Central Distribuidora tem 83% de pontualidade (atraso médio de 2 dias quando falha), é essencial expedir essa entrega para evitar ruptura.
#  5 LojaBR Pinheiros         Arroz Branco Tipo 1 Camil 5kg      motor=EXPEDITE     agente=EXPEDITE     tools=get_item_position,find_donor_stores,get_supplier_history,submit_decision
      → O estoque atual de 13 unidades cobre apenas 1,5 dia de venda (9 un/dia), enquanto o pedido de 44 unidades da Atacado Central Distribuidora só chega em 3 dias, e não há loja doadora em até 450 km. Como o fornecedor tem 83% de pontualidade e atraso médio de 2 dias, recomenda-se antecipar (expedir) essa entrega para evitar ruptura na gôndola.
#  6 LojaBR Setor Bueno       Café Torrado e Moído Pilão 500g    motor=EXPEDITE     agente=EXPEDITE     tools=get_item_position,find_donor_stores,get_supplier_history,submit_decision
      → Não há loja doadora em até 450 km, e o estoque atual de 10 unidades cobre apenas 1,1 dia de venda (média de 8,9 un/dia), enquanto o pedido de 60 unidades só chega em 3 dias. Como a Atacado Central Distribuidora tem 83% de pontualidade e atraso médio de 2,04 dias, recomenda-se expedir esse pedido para evitar ruptura na gôndola.
#  7 LojaBR Tatuapé           Desodorante Rexona Aerosol 150ml   motor=EXPEDITE     agente=EXPEDITE     tools=get_item_position,find_donor_stores,get_supplier_history,submit_decision
      → Estoque atual é de apenas 2 unidades com cobertura de 0,5 dia e venda média de 3,7 un/dia, e não há lojas doadoras em até 450 km. Já existe um pedido de 23 unidades a caminho da Higiene & Cia Distribuidora, mas como o fornecedor tem só 68% de pontualidade e atraso médio de 3,49 dias, é essencial acelerar essa entrega para evitar a ruptura.
#  8 LojaBR Tatuapé           Sabão em Pó Omo Lavagem Perfeita 1 motor=EXPEDITE     agente=EXPEDITE     tools=get_item_position,find_donor_stores,get_supplier_history,submit_decision
      → Não há lojas doadoras em até 450 km, e o estoque atual de 23 unidades cobre apenas 4 dias, enquanto o pedido de 46 unidades só chegaria em 5 dias - por isso é necessário expedir. Atenção: a Limpa Mais Distribuidora tem apenas 62,7% de pontualidade e atraso médio de 3,9 dias, o que pode agravar a ruptura se não houver acompanhamento.
#  9 LojaBR Pituba            Queijo Prato Fatiado (kg)          motor=EXPEDITE     agente=EXPEDITE     tools=get_item_position,find_donor_stores,get_supplier_history,submit_decision
      → O estoque na loja Pituba está em apenas 2 unidades com cobertura de 0,4 dia, e não há lojas doadoras a até 450 km, portanto transferência não é viável. Já existe um pedido de 29 unidades a caminho do fornecedor Laticínios Serra Azul, com chegada prevista em 1 dia; recomenda-se expedir essa entrega, mas com atenção pois o fornecedor tem 70,6% de pontualidade histórica e atraso médio de cerca de 2 dias quando atrasa.
# 10 LojaBR Pinheiros         Queijo Mussarela Fatiado (kg)      motor=EXPEDITE     agente=EXPEDITE     tools=get_item_position,find_donor_stores,get_supplier_history,submit_decision
      → A loja Pinheiros tem apenas 5 unidades em estoque, cobertura de 0,9 dia e vendas médias de 5,7 un/dia, sem lojas doadoras num raio de 450 km. Já existe pedido de 32 unidades a caminho do CD Cajamar, com chegada prevista em 2 dias e pontualidade histórica de 93,98% (atraso médio de 1,48 dia); por isso, recomenda-se expedir esse pedido para evitar ruptura antes da chegada.
# 11 LojaBR Pituba            Picanha Bovina Resfriada (kg)      motor=EXPEDITE     agente=EXPEDITE     tools=get_item_position,find_donor_stores,get_supplier_history,submit_decision
      → Não há loja doadora em até 450 km com excedente do produto. O estoque atual de 4 unidades cobre apenas 2,7 dias, enquanto o pedido de 9 unidades só chega em 5 dias pela Frios Paraná Logística, fornecedor com 74,79% de pontualidade e atraso médio de 2,48 dias; por isso recomendamos antecipar es
```

## Rule-based rationale for the rest of the queue (labelled as such)

```python
def br(x, d=1):
    """pt-BR number: 6,9 · 1.234"""
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def dias(n):
    n = int(round(n))
    return f"{n} dia" if n == 1 else f"{n} dias"


def rule_rationale(r):
    base = (f"{r['product_name']} em {r['store_name']}: {br(r['days_of_cover'])} dias de cobertura e "
            f"{r['risk_probability']:.0%} de risco de ruptura em 7 dias.")
    if r["action_type"] == "TRANSFER":
        return base + (f" A {r['from_store_name']}, a {int(r['transfer_km'])} km, tem {br(r['donor_days_of_cover'], 0)} dias de "
                       f"cobertura: transferir {r['units']} un, com chegada em {dias(r['eta_days'])}.")
    sup = otif.at[r["supplier_id"], "supplier_name"]
    if r["action_type"] == "EXPEDITE":
        return base + (f" O pedido de {r['inbound_units']} un de {sup} chega só em ~{dias(r['eta_adjusted_days'])} "
                       f"(pontualidade de {r['supplier_on_time_rate']:.0%}): cobrar a antecipação para {dias(r['eta_days'])}.")
    return base + f" Não há pedido a caminho nem loja próxima com excedente: pedido emergencial de {r['units']} un a {sup}."


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
```

**Output**

```text
AGENT RUN: {'run_at': '2026-09-28T12:41:17.153852+00:00', 'model_endpoint': 'databricks-claude-sonnet-5', 'items_reviewed': 12, 'errors': 0, 'actions_changed': 0, 'avg_tool_calls': 4.0, 'avg_latency_ms': 12367.833333333334}
```
