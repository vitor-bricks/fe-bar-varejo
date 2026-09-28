#!/usr/bin/env python3
"""Configure the LojaBR · Centro de Abastecimento Genie space (tables, entity matching, metric
definitions and certified example SQL). Idempotent: full replacement of the serialized space.

Usage: python3 05_genie/configure_genie_space.py
"""
import json, subprocess, uuid

PROFILE, SPACE, WAREHOUSE = "fevm-stable", "01f1b906cf2d15b4b1c72c3b25ddb2f0", "38762a7d9e9e5b33"
G = "serverless_stable_xpbmim_catalog.fe_bar_varejo_gold"

# column entity matching: lets users type "Asa Sul", "papel higiênico", "Limpa Mais"...
MATCH = {
    "gold_replenishment_queue_final": ["store_name", "city", "product_name", "category", "action_type", "severity", "supplier_name", "from_store_name", "region"],
    "gold_store_network": ["store_name", "city", "uf", "region", "store_format"],
    "gold_current_position": ["store_name", "product_name", "category", "region"],
    "gold_daily_store_sku": ["store_name", "product_name", "category", "region", "city"],
    "gold_supplier_otif": ["supplier_name"],
    "gold_stockout_predictions": ["store_name", "product_name", "category"],
    "gold_kpi_daily": [],
}

INSTRUCTIONS = """Você é o assistente de dados do Centro de Abastecimento da LojaBR (rede de 20 supermercados no Brasil). Responda SEMPRE em português. Valores monetários em R$ (R$ 1.234,56); frações exibidas como percentual (0,053 → 5,3%).

DATAS: os dados vão até a data mais recente de snapshot_date (2026-09-24). "Hoje", "agora" e "últimos N dias" são SEMPRE relativos a (SELECT max(snapshot_date) FROM gold_kpi_daily) — NUNCA use current_date().

DEFINIÇÕES:
- Ruptura = stockout_flag = 1 (item indisponível no dia). Taxa de ruptura = avg(stockout_flag) ou stockout_rate / stockout_rate_7d (já é fração).
- Receita perdida = sum(lost_revenue) (vendas que não aconteceram por falta do produto).
- Fila de ação / itens em risco / ações recomendadas = linhas de gold_replenishment_queue_final (uma ação por loja×item, snapshot mais recente). "Quantos itens em risco" = count(*) dessa tabela. NÃO use gold_stockout_predictions para contar itens em risco (ela contém TODOS os itens pontuados).
- action_type: TRANSFER = transferência de outra loja (from_store_name, transfer_km); EXPEDITE = antecipar pedido já a caminho; URGENT_ORDER = pedido emergencial ao fornecedor.
- revenue_protected = R$ protegido se a ação for executada (próximos 7 dias). revenue_at_risk = R$ em risco. risk_probability = probabilidade de ruptura em 7 dias.
- days_of_cover = dias de cobertura (estoque ÷ venda média diária de 28 dias).
- Pontualidade do fornecedor = on_time_rate (gold_supplier_otif).
- Lojas: use store_name (ex.: "LojaBR Asa Sul") e city; regiões Sudeste, Sul, Nordeste, Centro-Oeste, Norte."""

EXAMPLES = [
    ("Quantos itens estão na fila de ação agora?",
     f"SELECT count(*) AS itens_na_fila, round(sum(revenue_protected), 2) AS rs_protegido FROM {G}.gold_replenishment_queue_final"),
    ("Qual foi a receita perdida por ruptura nos últimos 7 dias?",
     f"SELECT round(sum(lost_revenue), 2) AS receita_perdida_7d, round(avg(stockout_rate), 4) AS taxa_ruptura_media FROM {G}.gold_kpi_daily "
     f"WHERE snapshot_date > date_sub((SELECT max(snapshot_date) FROM {G}.gold_kpi_daily), 7)"),
    ("Quais fornecedores atrasam mais?",
     f"SELECT supplier_name, orders_received, on_time_rate, avg_delay_when_late FROM {G}.gold_supplier_otif ORDER BY on_time_rate ASC"),
    ("Quais lojas têm a maior taxa de ruptura na última semana?",
     f"SELECT store_name, city, uf, stockout_rate_7d, lost_revenue_7d FROM {G}.gold_store_network ORDER BY stockout_rate_7d DESC LIMIT 10"),
    ("Quais transferências entre lojas estão recomendadas?",
     f"SELECT from_store_name, store_name, product_name, units, transfer_km, revenue_protected FROM {G}.gold_replenishment_queue_final "
     f"WHERE action_type = 'TRANSFER' ORDER BY revenue_protected DESC"),
]


def space(with_examples: bool):
    tables = []
    for t in sorted(MATCH):
        entry = {"identifier": f"{G}.{t}"}
        if MATCH[t]:
            entry["column_configs"] = [{"column_name": c, "enable_format_assistance": True, "enable_entity_matching": True}
                                       for c in sorted(MATCH[t])]
        tables.append(entry)
    ins = {"text_instructions": [{"id": uuid.uuid4().hex, "content": [INSTRUCTIONS]}]}
    if with_examples:
        ins["example_question_sqls"] = sorted(
            [{"id": uuid.uuid4().hex, "question": [q], "sql": [s]} for q, s in EXAMPLES], key=lambda x: x["id"])
    return {"version": 2, "data_sources": {"tables": tables}, "instructions": ins}


def update(ss):
    return subprocess.run(["databricks", "genie", "update-space", SPACE, "--serialized-space", json.dumps(ss, ensure_ascii=False),
                           "--title", "LojaBR · Centro de Abastecimento (Genie)", "--warehouse-id", WAREHOUSE,
                           "--description", "Pergunte em português sobre ruptura, fila de ação, transferências, lojas e fornecedores.",
                           "-p", PROFILE, "-o", "json"], capture_output=True, text=True)


r = update(space(with_examples=True))
if r.returncode != 0:
    print("example SQL not accepted by this API version, falling back to text instructions:", r.stderr.strip()[:300])
    r = update(space(with_examples=False))
print("OK" if r.returncode == 0 else f"FAILED: {r.stderr.strip()[:500]}")
