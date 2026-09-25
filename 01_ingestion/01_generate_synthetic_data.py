# Databricks notebook source
# MAGIC %md
# MAGIC # LojaBR · Centro de Abastecimento — Synthetic Data Generation (v2)
# MAGIC
# MAGIC Generates a realistic Brazilian supermarket chain dataset for the **stockout / on-shelf
# MAGIC availability** use case and lands it as raw CSV in the Unity Catalog Volume
# MAGIC `serverless_stable_xpbmim_catalog.fe_bar_varejo_bronze.landing` (Lakeflow Auto Loader source).
# MAGIC
# MAGIC **What makes it realistic**
# MAGIC - 20 real Brazilian cities/neighbourhoods with coordinates; 3 store formats.
# MAGIC - ~170 real-looking supermarket items (name, brand, pack size) across 8 categories.
# MAGIC - A day-by-day **inventory simulation**: Poisson demand with weekday seasonality and promos,
# MAGIC   a reorder policy, supplier lead times **and supplier-specific delays**. Stockouts emerge
# MAGIC   from the dynamics — they are not labelled at random.
# MAGIC - Every purchase order is recorded (expected vs actual arrival) → supplier on-time rate.
# MAGIC - Store-level stocking policies differ, so some stores carry **excess** of an item while
# MAGIC   others run short → inter-store transfers are a real option.
# MAGIC
# MAGIC **100% synthetic — no customer data.**

# COMMAND ----------

import os, shutil
import numpy as np
import pandas as pd

SEED = 42
N_DAYS = 120
END_DATE = np.datetime64("2026-09-24")
START_DATE = END_DATE - (N_DAYS - 1)
LANDING = "/Volumes/serverless_stable_xpbmim_catalog/fe_bar_varejo_bronze/landing"
rng = np.random.default_rng(SEED)
print(f"period {START_DATE} .. {END_DATE} ({N_DAYS} days) · seed {SEED}")

# COMMAND ----------

# MAGIC %md ## Stores — 20 real locations

# COMMAND ----------

STORES = [
    # store_id, name, city, uf, region, format, lat, lon, traffic
    ("SP-PIN", "LojaBR Pinheiros",        "São Paulo",      "SP", "Sudeste",      "Supermercado", -23.566, -46.692, 1.35),
    ("SP-MOE", "LojaBR Moema",            "São Paulo",      "SP", "Sudeste",      "Supermercado", -23.600, -46.665, 1.25),
    ("SP-TAT", "LojaBR Tatuapé",          "São Paulo",      "SP", "Sudeste",      "Hipermercado", -23.540, -46.576, 1.90),
    ("SP-CPS", "LojaBR Campinas",         "Campinas",       "SP", "Sudeste",      "Hipermercado", -22.907, -47.063, 1.70),
    ("SP-STS", "LojaBR Santos",           "Santos",         "SP", "Sudeste",      "Supermercado", -23.961, -46.334, 1.05),
    ("SP-RPO", "LojaBR Ribeirão Preto",   "Ribeirão Preto", "SP", "Sudeste",      "Supermercado", -21.178, -47.810, 0.95),
    ("RJ-BAR", "LojaBR Barra da Tijuca",  "Rio de Janeiro", "RJ", "Sudeste",      "Hipermercado", -23.000, -43.365, 1.80),
    ("RJ-TIJ", "LojaBR Tijuca",           "Rio de Janeiro", "RJ", "Sudeste",      "Express",      -22.925, -43.235, 0.60),
    ("RJ-NIT", "LojaBR Niterói",          "Niterói",        "RJ", "Sudeste",      "Supermercado", -22.883, -43.103, 0.95),
    ("MG-BHZ", "LojaBR Savassi",          "Belo Horizonte", "MG", "Sudeste",      "Supermercado", -19.938, -43.935, 1.15),
    ("PR-CWB", "LojaBR Batel",            "Curitiba",       "PR", "Sul",          "Supermercado", -25.443, -49.290, 1.10),
    ("RS-POA", "LojaBR Moinhos",          "Porto Alegre",   "RS", "Sul",          "Supermercado", -30.026, -51.201, 1.00),
    ("SC-FLN", "LojaBR Florianópolis",    "Florianópolis",  "SC", "Sul",          "Express",      -27.595, -48.548, 0.55),
    ("BA-SSA", "LojaBR Pituba",           "Salvador",       "BA", "Nordeste",     "Hipermercado", -13.005, -38.458, 1.60),
    ("PE-REC", "LojaBR Boa Viagem",       "Recife",         "PE", "Nordeste",     "Supermercado", -8.119,  -34.903, 1.05),
    ("CE-FOR", "LojaBR Aldeota",          "Fortaleza",      "CE", "Nordeste",     "Supermercado", -3.737,  -38.498, 1.00),
    ("DF-BSB", "LojaBR Asa Sul",          "Brasília",       "DF", "Centro-Oeste", "Hipermercado", -15.815, -47.895, 1.55),
    ("GO-GYN", "LojaBR Setor Bueno",      "Goiânia",        "GO", "Centro-Oeste", "Supermercado", -16.707, -49.271, 0.90),
    ("AM-MAO", "LojaBR Adrianópolis",     "Manaus",         "AM", "Norte",        "Supermercado", -3.097,  -60.013, 0.85),
    ("PA-BEL", "LojaBR Umarizal",         "Belém",          "PA", "Norte",        "Express",      -1.448,  -48.489, 0.50),
]
dim_store = pd.DataFrame(STORES, columns=["store_id", "store_name", "city", "uf", "region",
                                          "store_format", "lat", "lon", "traffic_index"])
print(dim_store[["store_id", "store_name", "city", "uf", "store_format"]].to_string(index=False))

# COMMAND ----------

# MAGIC %md ## Suppliers — each with its own reliability (on-time behaviour)

# COMMAND ----------

SUPPLIERS = [
    # supplier_id, name, p_delay, delay_min, delay_max
    ("FOR-CD",  "CD LojaBR Cajamar (próprio)",       0.06, 1, 2),
    ("FOR-ATC", "Atacado Central Distribuidora",     0.18, 1, 3),
    ("FOR-TRP", "Distribuidora Tropical Bebidas",    0.22, 1, 4),
    ("FOR-VVD", "Hortifruti Vale Verde",             0.12, 1, 1),
    ("FOR-SAZ", "Laticínios Serra Azul",             0.30, 1, 3),
    ("FOR-PAN", "Panificação LojaBR (própria)",      0.04, 1, 1),
    ("FOR-LMP", "Limpa Mais Distribuidora",          0.38, 2, 6),
    ("FOR-HIG", "Higiene & Cia Distribuidora",       0.34, 2, 5),
    ("FOR-FRZ", "Frios Paraná Logística",            0.26, 1, 4),
]
dim_supplier = pd.DataFrame(SUPPLIERS, columns=["supplier_id", "supplier_name", "p_delay",
                                                "delay_min", "delay_max"])
sup_idx = {s[0]: i for i, s in enumerate(SUPPLIERS)}

# COMMAND ----------

# MAGIC %md ## Products — ~170 real-looking supermarket items

# COMMAND ----------

# category -> (supplier options, lead_time_min, lead_time_max, base_daily_demand, gross_margin)
CAT = {
    "Mercearia":   (["FOR-CD", "FOR-ATC"], 3, 5, 5.0, 0.24),
    "Bebidas":     (["FOR-TRP", "FOR-CD"], 2, 4, 7.0, 0.28),
    "Hortifruti":  (["FOR-VVD"],           1, 2, 9.0, 0.35),
    "Laticínios":  (["FOR-SAZ", "FOR-CD"], 2, 3, 6.0, 0.22),
    "Padaria":     (["FOR-PAN"],           1, 1, 8.0, 0.45),
    "Limpeza":     (["FOR-LMP", "FOR-CD"], 4, 7, 3.0, 0.30),
    "Higiene":     (["FOR-HIG", "FOR-CD"], 4, 7, 2.8, 0.33),
    "Congelados":  (["FOR-FRZ"],           3, 5, 2.6, 0.27),
}
ITEMS = {
    "Mercearia": [("Arroz Branco Tipo 1 Tio João 5kg", 27.90, 1.4), ("Arroz Branco Tipo 1 Camil 5kg", 25.50, 1.2),
        ("Feijão Carioca Camil 1kg", 8.90, 1.5), ("Feijão Preto Kicaldo 1kg", 9.50, 0.9),
        ("Açúcar Refinado União 1kg", 4.99, 1.3), ("Café Torrado e Moído Pilão 500g", 18.90, 1.4),
        ("Café Extraforte Melitta 500g", 19.50, 1.0), ("Óleo de Soja Liza 900ml", 7.89, 1.3),
        ("Macarrão Espaguete Renata 500g", 4.59, 1.1), ("Macarrão Parafuso Barilla 500g", 7.99, 0.7),
        ("Molho de Tomate Heinz 340g", 5.29, 1.0), ("Extrato de Tomate Elefante 340g", 6.49, 0.7),
        ("Farinha de Trigo Dona Benta 1kg", 5.99, 0.8), ("Sal Refinado Cisne 1kg", 2.99, 0.6),
        ("Leite Condensado Moça 395g", 7.99, 1.0), ("Achocolatado em Pó Nescau 400g", 9.99, 0.9),
        ("Biscoito Recheado Oreo 90g", 3.99, 1.1), ("Biscoito Cream Cracker Piraquê 200g", 4.49, 0.8),
        ("Azeite Extra Virgem Gallo 500ml", 39.90, 0.5), ("Atum em Óleo Gomes da Costa 170g", 9.79, 0.7),
        ("Maionese Hellmann's 500g", 11.90, 0.9), ("Aveia em Flocos Quaker 200g", 6.49, 0.5),
        ("Milho Verde em Conserva Quero 200g", 3.99, 0.6), ("Sardinha em Óleo Coqueiro 125g", 6.89, 0.5),
        ("Granola Tradicional Mãe Terra 800g", 24.90, 0.3)],
    "Bebidas": [("Cerveja Skol Lata 350ml", 3.49, 2.2), ("Cerveja Heineken Long Neck 330ml", 6.99, 1.6),
        ("Cerveja Brahma Duplo Malte Lata 350ml", 3.99, 1.5), ("Refrigerante Coca-Cola 2L", 10.99, 1.8),
        ("Refrigerante Guaraná Antarctica 2L", 8.49, 1.4), ("Refrigerante Coca-Cola Zero Lata 350ml", 4.29, 1.0),
        ("Água Mineral Crystal sem Gás 1,5L", 2.99, 1.5), ("Água com Gás São Lourenço 300ml", 3.49, 0.6),
        ("Suco de Uva Del Valle 1L", 8.99, 0.7), ("Suco de Laranja Natural One 900ml", 14.90, 0.5),
        ("Energético Red Bull 250ml", 9.99, 0.6), ("Chá Matte Leão Limão 1,5L", 6.99, 0.5),
        ("Isotônico Gatorade Limão 500ml", 5.99, 0.6), ("Vinho Tinto Casillero del Diablo 750ml", 59.90, 0.25),
        ("Espumante Chandon Brut 750ml", 99.90, 0.12), ("Água de Coco Kero Coco 1L", 12.90, 0.5),
        ("Cerveja Stella Artois Long Neck 330ml", 6.49, 0.9), ("Refrigerante Fanta Laranja 2L", 8.99, 0.8),
        ("Cerveja Amstel Lata 350ml", 3.79, 1.1), ("Suco em Pó Tang Laranja 18g", 1.29, 0.7)],
    "Hortifruti": [("Banana Prata (kg)", 6.99, 1.6), ("Tomate Italiano (kg)", 8.49, 1.3),
        ("Batata Inglesa (kg)", 5.99, 1.2), ("Cebola (kg)", 4.99, 1.1), ("Alface Crespa (un)", 3.49, 0.9),
        ("Maçã Gala (kg)", 9.99, 0.9), ("Laranja Pera (kg)", 4.49, 1.0), ("Limão Tahiti (kg)", 5.99, 0.8),
        ("Cenoura (kg)", 4.99, 0.8), ("Mamão Formosa (kg)", 6.49, 0.6), ("Abacate (kg)", 9.99, 0.4),
        ("Morango Bandeja 250g", 8.99, 0.5), ("Uva Thompson sem Semente 500g", 12.90, 0.4),
        ("Manga Palmer (kg)", 7.99, 0.5), ("Brócolis Ninja (un)", 7.49, 0.4), ("Pimentão Verde (kg)", 9.99, 0.4),
        ("Alho Nacional 200g", 6.99, 0.6), ("Melancia (kg)", 2.99, 0.6)],
    "Laticínios": [("Leite Integral Italac 1L", 5.49, 1.9), ("Leite Integral Piracanjuba 1L", 5.89, 1.5),
        ("Leite Desnatado Parmalat 1L", 5.99, 0.8), ("Iogurte Grego Vigor 100g", 3.49, 0.9),
        ("Iogurte Morango Danone 170g", 3.99, 0.8), ("Requeijão Cremoso Catupiry 200g", 9.99, 0.7),
        ("Manteiga com Sal Aviação 200g", 14.90, 0.6), ("Queijo Mussarela Fatiado (kg)", 49.90, 0.8),
        ("Queijo Prato Fatiado (kg)", 54.90, 0.5), ("Creme de Leite Nestlé 200g", 3.99, 0.9),
        ("Leite Fermentado Yakult 6un", 12.90, 0.5), ("Margarina Qualy 500g", 8.99, 0.8),
        ("Cream Cheese Philadelphia 150g", 12.90, 0.3), ("Petit Suisse Danoninho 320g", 9.49, 0.5),
        ("Queijo Parmesão Ralado Faixa Azul 50g", 7.99, 0.4)],
    "Padaria": [("Pão Francês (kg)", 16.90, 2.0), ("Pão de Forma Pullman 500g", 9.99, 1.2),
        ("Pão de Forma Integral Wickbold 500g", 11.90, 0.7), ("Bisnaguinha Seven Boys 300g", 8.99, 0.8),
        ("Bolo de Fubá Caseiro (un)", 14.90, 0.4), ("Croissant Manteiga (un)", 5.99, 0.6),
        ("Torrada Tradicional Bauducco 142g", 6.49, 0.5), ("Sonho de Creme (un)", 4.99, 0.5),
        ("Pão Integral Artesanal (un)", 12.90, 0.4), ("Baguete Tradicional (un)", 7.99, 0.6),
        ("Rosca Doce de Coco (un)", 9.99, 0.3), ("Bolo de Chocolate Fatia (un)", 6.99, 0.4)],
    "Limpeza": [("Sabão em Pó Omo Lavagem Perfeita 1,6kg", 29.90, 1.0), ("Detergente Ypê Neutro 500ml", 2.49, 1.6),
        ("Amaciante Comfort Concentrado 1L", 14.90, 0.7), ("Água Sanitária Qboa 2L", 6.99, 0.9),
        ("Desinfetante Pinho Sol Original 1L", 9.99, 0.6), ("Esponja Scotch-Brite 3un", 5.99, 0.8),
        ("Papel Toalha Snob 2 Rolos", 7.99, 0.6), ("Limpador Multiuso Veja 500ml", 7.49, 0.7),
        ("Saco de Lixo Dover Roll 50L", 12.90, 0.5), ("Sabão em Barra Ypê 5un", 9.49, 0.5),
        ("Tira Manchas Vanish 450ml", 16.90, 0.3), ("Lustra Móveis Poliflor 200ml", 10.90, 0.2),
        ("Lava Roupas Líquido Brilhante 3L", 34.90, 0.4)],
    "Higiene": [("Papel Higiênico Neve Folha Dupla 12un", 24.90, 1.4), ("Papel Higiênico Personal 12un", 18.90, 0.9),
        ("Creme Dental Colgate Total 12 90g", 8.99, 1.2), ("Sabonete Dove Original 90g", 3.99, 1.1),
        ("Shampoo Pantene Restauração 400ml", 22.90, 0.5), ("Condicionador Seda 325ml", 12.90, 0.5),
        ("Desodorante Rexona Aerosol 150ml", 15.90, 0.8), ("Fralda Pampers Confort Sec G 36un", 69.90, 0.4),
        ("Absorvente Always Noturno 8un", 12.90, 0.5), ("Escova Dental Oral-B 2un", 14.90, 0.4),
        ("Aparelho Gillette Prestobarba 3un", 19.90, 0.3), ("Sabonete Líquido Protex 250ml", 14.90, 0.3),
        ("Hidratante Nivea Milk 400ml", 24.90, 0.3), ("Fio Dental Colgate 50m", 7.49, 0.3)],
    "Congelados": [("Pão de Queijo Forno de Minas 400g", 16.90, 0.9), ("Pizza Mussarela Sadia 460g", 21.90, 0.7),
        ("Lasanha Bolonhesa Seara 600g", 19.90, 0.6), ("Hambúrguer Bovino Sadia 672g", 24.90, 0.5),
        ("Batata Palito McCain 720g", 22.90, 0.6), ("Sorvete Napolitano Kibon 1,5L", 29.90, 0.5),
        ("Empanado de Frango Seara Nuggets 300g", 14.90, 0.7), ("Peito de Frango Congelado Sadia (kg)", 24.90, 0.8),
        ("Açaí com Guaraná Frooty 1L", 27.90, 0.4), ("Legumes Congelados Pratigel 300g", 9.99, 0.3),
        ("Picanha Bovina Resfriada (kg)", 79.90, 0.3), ("Coxinha de Frango Congelada 1kg", 29.90, 0.3)],
}
rows = []
for cat, items in ITEMS.items():
    sup_opts, lt_lo, lt_hi, base, marg = CAT[cat]
    for i, (name, price, pop) in enumerate(items):
        sku = f"{cat[:3].upper()}-{i + 1:03d}"
        sup = sup_opts[i % len(sup_opts)]
        m = marg * rng.uniform(0.85, 1.15)
        rows.append(dict(sku=sku, product_name=name, category=cat, supplier_id=sup,
                         unit_price=price, unit_cost=round(price * (1 - m), 2),
                         lead_time_days=int(rng.integers(lt_lo, lt_hi + 1)),
                         base_demand=base * pop))
dim_product = pd.DataFrame(rows)
N_PRODUCTS, N_STORES = len(dim_product), len(dim_store)
print(f"{N_PRODUCTS} products · {N_STORES} stores · {N_PRODUCTS * N_STORES:,} store×sku combos")
display(dim_product.drop(columns=["base_demand"]).head(10))

# COMMAND ----------

# MAGIC %md ## Day-by-day inventory simulation

# COMMAND ----------

N = N_STORES * N_PRODUCTS
si = np.repeat(np.arange(N_STORES), N_PRODUCTS)
pi = np.tile(np.arange(N_PRODUCTS), N_STORES)

traffic = dim_store["traffic_index"].to_numpy()
fmt = dim_store["store_format"].to_numpy()
lam = np.maximum(0.2, dim_product["base_demand"].to_numpy()[pi] * traffic[si] * rng.uniform(0.8, 1.2, N))
lt = dim_product["lead_time_days"].to_numpy()[pi]
sup_of = np.array([sup_idx[s] for s in dim_product["supplier_id"]])[pi]
p_delay = dim_supplier["p_delay"].to_numpy()[sup_of]
d_min = dim_supplier["delay_min"].to_numpy()[sup_of]
d_max = dim_supplier["delay_max"].to_numpy()[sup_of]

# Shelf capacity and store-specific stocking policy. `policy` > 1 → the store over-orders
# this item (excess stock = potential transfer donor); < 1 → runs lean (stockout-prone).
cap = np.maximum(8, np.round(lam * np.where(fmt[si] == "Express", 5, 9))).astype(int)
policy = rng.choice([0.75, 1.0, 1.0, 1.0, 1.6, 2.4], size=N)
safety = np.where(policy >= 1.6, 1.5, np.where(policy < 1.0, 0.8, 1.15))
reorder_point = np.maximum(3, np.round(lam * (lt + 1) * safety)).astype(int)
order_qty = np.maximum(cap * 0.6, np.round(lam * 8 * policy)).astype(int)

weekday = np.array([0.90, 0.85, 0.90, 1.00, 1.20, 1.45, 1.15])  # Mon..Sun
dates = START_DATE + np.arange(N_DAYS)
dow = (dates.astype(int) + 3) % 7  # 1970-01-01 = Thursday -> Mon=0

on_hand = (cap * rng.uniform(0.6, 1.0, N)).astype(float)
pend_qty = np.zeros(N); pend_eta = np.full(N, -1); pend_placed = np.full(N, -1); pend_exp = np.full(N, -1)
sales_parts, inv_parts, po_rows = [], [], []

for t in range(N_DAYS):
    d = str(dates[t])
    promo = rng.random(N) < 0.035
    boost = np.where(promo, rng.uniform(1.4, 2.1, N), 1.0)
    arrive = pend_eta == t
    if arrive.any():
        idx = np.where(arrive)[0]
        for k in idx:
            po_rows.append((int(si[k]), int(pi[k]), int(pend_placed[k]), int(pend_exp[k]), t, int(pend_qty[k])))
        on_hand[arrive] += pend_qty[arrive]
        pend_qty[arrive] = 0; pend_eta[arrive] = -1
    demand = rng.poisson(lam * weekday[dow[t]] * (1 + 0.0012 * t) * boost)
    sold = np.minimum(demand, on_hand).astype(int)
    lost = (demand - sold).astype(int)
    on_hand -= sold
    stockout = ((on_hand <= 0) | (lost > 0)).astype(int)
    need = (on_hand <= reorder_point) & (pend_eta < 0)
    late = rng.random(N) < p_delay
    delay = np.where(late, rng.integers(d_min, d_max + 1), 0)
    eta = t + lt + delay
    pend_qty[need] = order_qty[need]; pend_eta[need] = eta[need]
    pend_placed[need] = t; pend_exp[need] = (t + lt)[need]

    sales_parts.append(pd.DataFrame({"store_id": dim_store["store_id"].to_numpy()[si],
        "sku": dim_product["sku"].to_numpy()[pi], "sale_date": d, "units_sold": sold,
        "unit_price": dim_product["unit_price"].to_numpy()[pi], "promo_flag": promo.astype(int)}))
    inv_parts.append(pd.DataFrame({"store_id": dim_store["store_id"].to_numpy()[si],
        "sku": dim_product["sku"].to_numpy()[pi], "snapshot_date": d,
        "on_hand_units": np.maximum(0, on_hand).astype(int), "reorder_point": reorder_point,
        "shelf_capacity_units": cap, "lost_sales_units": lost, "stockout_flag": stockout}))

fact_sales = pd.concat(sales_parts, ignore_index=True)
fact_sales["revenue"] = (fact_sales["units_sold"] * fact_sales["unit_price"]).round(2)
fact_inventory = pd.concat(inv_parts, ignore_index=True)

sid, sk = dim_store["store_id"].to_numpy(), dim_product["sku"].to_numpy()
fact_purchase_orders = pd.DataFrame(po_rows, columns=["s", "p", "placed", "expected", "actual", "qty"])
fact_purchase_orders = pd.DataFrame({
    "po_id": [f"PO-{i:07d}" for i in range(len(fact_purchase_orders))],
    "store_id": sid[fact_purchase_orders["s"]], "sku": sk[fact_purchase_orders["p"]],
    "supplier_id": dim_product["supplier_id"].to_numpy()[fact_purchase_orders["p"]],
    "order_date": [str(dates[x]) for x in fact_purchase_orders["placed"]],
    "expected_arrival": [str(START_DATE + x) for x in fact_purchase_orders["expected"]],
    "actual_arrival": [str(dates[x]) for x in fact_purchase_orders["actual"]],
    "qty_units": fact_purchase_orders["qty"]})

# orders still open at the end of the period (the "pedido a caminho"). The planner only knows
# the EXPECTED arrival (order date + lead time); an expected date in the past = a late order.
open_mask = pend_eta >= 0
fact_open_orders = pd.DataFrame({
    "store_id": sid[si[open_mask]], "sku": sk[pi[open_mask]],
    "supplier_id": dim_product["supplier_id"].to_numpy()[pi[open_mask]],
    "order_date": [str(START_DATE + x) for x in pend_placed[open_mask]],
    "eta_date": [str(START_DATE + x) for x in pend_exp[open_mask]],
    "qty_units": pend_qty[open_mask].astype(int)})
print(f"sales {len(fact_sales):,} · inventory {len(fact_inventory):,} · purchase orders {len(fact_purchase_orders):,} · open orders {len(fact_open_orders):,}")

# COMMAND ----------

# MAGIC %md ## Land raw CSV into the Unity Catalog Volume (clean re-land)

# COMMAND ----------

tables = {
    "dim_store": dim_store.drop(columns=["traffic_index"]),
    "dim_product": dim_product.drop(columns=["base_demand"]),
    "dim_supplier": dim_supplier[["supplier_id", "supplier_name"]],
    "fact_sales_daily": fact_sales,
    "fact_inventory_daily": fact_inventory,
    "fact_purchase_orders": fact_purchase_orders,
    "fact_open_orders": fact_open_orders,
}
for sub in os.listdir(LANDING):
    shutil.rmtree(f"{LANDING}/{sub}", ignore_errors=True)
print("=" * 72)
for name, df in tables.items():
    os.makedirs(f"{LANDING}/{name}", exist_ok=True)
    df.to_csv(f"{LANDING}/{name}/{name}.csv", index=False)
    print(f"{name:22s} rows={len(df):>8,}  cols={df.shape[1]:>2}  -> landing/{name}/")
print("=" * 72)

# COMMAND ----------

# MAGIC %md ## Execution evidence

# COMMAND ----------

inv = fact_inventory.merge(dim_product[["sku", "category", "unit_price"]], on="sku")
lost_rev = (inv["lost_sales_units"] * inv["unit_price"]).sum()
rev = fact_sales["revenue"].sum()
print(f"stockout rate (store×sku×day): {inv['stockout_flag'].mean():.2%}")
print(f"lost revenue {N_DAYS}d: R$ {lost_rev:,.0f}  ·  revenue: R$ {rev:,.0f}  ·  lost share {lost_rev / (rev + lost_rev):.2%}")
po = fact_purchase_orders.copy()
po["late"] = pd.to_datetime(po["actual_arrival"]) > pd.to_datetime(po["expected_arrival"])
print("\nsupplier on-time rate:")
print((1 - po.groupby("supplier_id")["late"].mean()).round(3).sort_values().to_string())
print("\nstockout rate by category:")
print(inv.groupby("category")["stockout_flag"].mean().sort_values(ascending=False).round(4).to_string())
