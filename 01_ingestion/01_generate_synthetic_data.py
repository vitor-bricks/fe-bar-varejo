# Databricks notebook source
# MAGIC %md
# MAGIC # FE Bar Varejo — Synthetic Data Generation
# MAGIC
# MAGIC Generates a realistic multi-store retail dataset for the **On-Shelf Availability /
# MAGIC stockout** use case and lands it as raw CSV in the Unity Catalog Volume
# MAGIC `serverless_stable_xpbmim_catalog.fe_bar_varejo_bronze.landing` (the Lakeflow
# MAGIC Auto Loader source).
# MAGIC
# MAGIC Inventory dynamics come from a **path-dependent simulation** (Poisson demand,
# MAGIC reorder policy with lead time + supplier delay) so stockouts emerge organically and
# MAGIC carry genuine predictive signal. **100% synthetic — no customer data.**
# MAGIC
# MAGIC | Table | Rows | Grain |
# MAGIC |---|---|---|
# MAGIC | `dim_store` | ~20 | store master |
# MAGIC | `dim_product` | ~250 | product master |
# MAGIC | `fact_sales_daily` | ~600K | store × sku × day (POS) |
# MAGIC | `fact_inventory_daily` | ~600K | store × sku × day (inventory snapshot) |
# MAGIC | `fact_shelf_audit` | ~40K | periodic shelf-gap audits |

# COMMAND ----------

import numpy as np
import pandas as pd
import os

SEED = 42
N_STORES = 20
N_PRODUCTS = 250
N_DAYS = 120
END_DATE = np.datetime64("2026-09-24")
START_DATE = END_DATE - (N_DAYS - 1)
LANDING = "/Volumes/serverless_stable_xpbmim_catalog/fe_bar_varejo_bronze/landing"

rng = np.random.default_rng(SEED)
print(f"period: {START_DATE} .. {END_DATE} ({N_DAYS} days) | seed={SEED}")

# COMMAND ----------

# MAGIC %md ## Dimensions: stores & products

# COMMAND ----------

REGIONS = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]
REGION_W = np.array([40, 22, 20, 12, 6], dtype=float)
CITIES = {
    "Sudeste": ["Sao Paulo", "Rio de Janeiro", "Belo Horizonte", "Campinas"],
    "Sul": ["Curitiba", "Porto Alegre", "Florianopolis"],
    "Nordeste": ["Recife", "Salvador", "Fortaleza"],
    "Centro-Oeste": ["Brasilia", "Goiania"],
    "Norte": ["Manaus", "Belem"],
}
FORMATS = ["Hipermercado", "Supermercado", "Express"]
FORMAT_W = np.array([25, 50, 25], dtype=float)
FORMAT_TRAFFIC = {"Hipermercado": 1.8, "Supermercado": 1.0, "Express": 0.5}

store_ids = np.array([f"L{100 + i}" for i in range(N_STORES)])
store_regions = rng.choice(REGIONS, size=N_STORES, p=REGION_W / REGION_W.sum())
store_cities = np.array([rng.choice(CITIES[r]) for r in store_regions])
store_formats = rng.choice(FORMATS, size=N_STORES, p=FORMAT_W / FORMAT_W.sum())
store_traffic = np.array([FORMAT_TRAFFIC[f] for f in store_formats]) * rng.uniform(0.8, 1.2, N_STORES)
store_sqm = np.where(store_formats == "Hipermercado", rng.integers(4000, 8000, N_STORES),
             np.where(store_formats == "Supermercado", rng.integers(1200, 3500, N_STORES),
                      rng.integers(200, 800, N_STORES)))

dim_store = pd.DataFrame({
    "store_id": store_ids,
    "store_name": [f"LojaBR {c} {i:02d}" for i, c in enumerate(store_cities)],
    "region": store_regions, "city": store_cities, "store_format": store_formats,
    "size_sqm": store_sqm, "open_date": ["2019-01-01"] * N_STORES,
})

CATEGORIES = {
    "Mercearia":  (6.0, 3.0, 35.0, 0.28, 2, 5), "Bebidas":   (8.0, 2.5, 18.0, 0.32, 2, 4),
    "Hortifruti": (10.0, 1.5, 15.0, 0.35, 1, 2), "Limpeza":   (4.0, 4.0, 40.0, 0.30, 3, 7),
    "Higiene":    (3.5, 3.0, 45.0, 0.34, 3, 7),  "Padaria":   (7.0, 2.0, 25.0, 0.40, 1, 2),
    "Laticinios": (6.5, 3.5, 30.0, 0.26, 1, 3),  "Congelados": (3.0, 6.0, 50.0, 0.29, 3, 6),
}
BRANDS = ["MarcaA", "MarcaB", "MarcaC", "MarcaPropria", "Premium", "Regional"]
cat_names = list(CATEGORIES.keys())
prod_cat = rng.choice(cat_names, size=N_PRODUCTS)
skus = np.array([f"SKU{10000 + i}" for i in range(N_PRODUCTS)])
popularity = rng.lognormal(0.0, 0.6, N_PRODUCTS)
price_lo = np.array([CATEGORIES[c][1] for c in prod_cat])
price_hi = np.array([CATEGORIES[c][2] for c in prod_cat])
unit_price = np.round(rng.uniform(price_lo, price_hi), 2)
margin = np.array([CATEGORIES[c][3] for c in prod_cat]) * rng.uniform(0.85, 1.15, N_PRODUCTS)
unit_cost = np.round(unit_price * (1 - margin), 2)
lead_lo = np.array([CATEGORIES[c][4] for c in prod_cat])
lead_hi = np.array([CATEGORIES[c][5] for c in prod_cat])
lead_time = rng.integers(lead_lo, lead_hi + 1)
base_demand_prod = np.array([CATEGORIES[c][0] for c in prod_cat]) * popularity
shelf_capacity = np.maximum(8, np.round(base_demand_prod * rng.uniform(6, 12, N_PRODUCTS))).astype(int)

dim_product = pd.DataFrame({
    "sku": skus,
    "product_name": [f"{prod_cat[i]} {BRANDS[i % len(BRANDS)]} {i:03d}" for i in range(N_PRODUCTS)],
    "category": prod_cat, "brand": [BRANDS[i % len(BRANDS)] for i in range(N_PRODUCTS)],
    "unit_cost": unit_cost, "unit_price": unit_price,
    "shelf_capacity_units": shelf_capacity, "lead_time_days": lead_time,
    "supplier_id": [f"FORN{200 + (i % 15)}" for i in range(N_PRODUCTS)],
})
print("dim_store:", dim_store.shape, "| dim_product:", dim_product.shape)
display(dim_product.head(8))

# COMMAND ----------

# MAGIC %md ## Inventory + sales simulation (path-dependent, day-by-day)

# COMMAND ----------

N = N_STORES * N_PRODUCTS
si = np.repeat(np.arange(N_STORES), N_PRODUCTS)
pi = np.tile(np.arange(N_PRODUCTS), N_STORES)

lam = np.maximum(0.1, base_demand_prod[pi] * store_traffic[si])
cap = np.maximum(6, (shelf_capacity[pi] * np.where(store_formats[si] == "Express", 0.5, 1.0))).astype(int)
reorder_point = np.maximum(3, np.round(lam * (lead_time[pi] + 1) * 1.2)).astype(int)
order_qty = np.maximum(cap, np.round(lam * 10)).astype(int)
lt = lead_time[pi]
unreliable = rng.random(N) < 0.18

weekday_factor = np.array([0.9, 0.85, 0.9, 1.0, 1.25, 1.5, 1.2])  # Mon..Sun
dates = START_DATE + np.arange(N_DAYS)
dow = (dates.astype("datetime64[D]").astype(int) - 4) % 7

on_hand = cap.astype(float).copy()
pending_qty = np.zeros(N); pending_day = np.full(N, -1)
sales_rows, inv_rows = [], []

for t in range(N_DAYS):
    date_t = str(dates[t]); wf = weekday_factor[dow[t]]; trend = 1.0 + 0.0015 * t
    promo = rng.random(N) < 0.04
    promo_boost = np.where(promo, rng.uniform(1.4, 2.2, N), 1.0)
    arriving = pending_day == t
    on_hand[arriving] += pending_qty[arriving]; pending_qty[arriving] = 0; pending_day[arriving] = -1
    demand = rng.poisson(lam * wf * trend * promo_boost)
    sales = np.minimum(demand, on_hand).astype(int)
    lost = (demand - sales).astype(int)
    on_hand -= sales
    stockout = ((on_hand <= 0) | (lost > 0)).astype(int)
    need_order = (on_hand <= reorder_point) & (pending_day < 0)
    r = rng.random(N)
    delay = np.where(unreliable & (r < 0.5), rng.integers(2, 7, N),
             np.where(~unreliable & (r < 0.2), rng.integers(1, 3, N), 0))
    arrival = t + lt + delay
    place = need_order & (arrival < N_DAYS + 30)
    pending_qty[place] = order_qty[place]; pending_day[place] = arrival[place]
    on_order = (pending_day >= 0).astype(int)
    days_to_arrival = np.where(pending_day >= 0, pending_day - t, -1)

    sales_rows.append(pd.DataFrame({
        "store_id": store_ids[si], "sku": skus[pi], "sale_date": date_t,
        "units_sold": sales, "unit_price": unit_price[pi],
        "revenue": np.round(sales * unit_price[pi], 2), "promo_flag": promo.astype(int)}))
    inv_rows.append(pd.DataFrame({
        "store_id": store_ids[si], "sku": skus[pi], "snapshot_date": date_t,
        "on_hand_units": np.maximum(0, on_hand).astype(int),
        "on_order_units": (pending_qty * on_order).astype(int),
        "reorder_point": reorder_point, "shelf_capacity_units": cap,
        "lead_time_days": lt, "days_to_arrival": days_to_arrival,
        "lost_sales_units": lost, "stockout_flag": stockout}))

fact_sales = pd.concat(sales_rows, ignore_index=True)
fact_inventory = pd.concat(inv_rows, ignore_index=True)
print("fact_sales:", fact_sales.shape, "| fact_inventory:", fact_inventory.shape)

# COMMAND ----------

# MAGIC %md ## Shelf audits (periodic, correlated with stockouts)

# COMMAND ----------

audit_frames = []
inv_by_date = {d: g for d, g in fact_inventory.groupby("snapshot_date")}
for t in range(N_DAYS):
    mask = ((si + pi + t) % 14 == 0)
    if not mask.any():
        continue
    idx = np.where(mask)[0]; date_t = str(dates[t])
    g = inv_by_date[date_t].reset_index(drop=True)
    oh = g["on_hand_units"].to_numpy()[idx]
    facings_expected = np.maximum(1, np.round(cap[idx] / 8)).astype(int)
    gap = (oh == 0) | (rng.random(len(idx)) < 0.05)
    facings_actual = np.where(gap, np.maximum(0, facings_expected - rng.integers(1, 3, len(idx))), facings_expected)
    audit_frames.append(pd.DataFrame({
        "store_id": store_ids[si[idx]], "sku": skus[pi[idx]], "audit_date": date_t,
        "facings_expected": facings_expected,
        "facings_actual": np.maximum(0, facings_actual).astype(int),
        "shelf_gap_flag": gap.astype(int)}))
fact_shelf_audit = pd.concat(audit_frames, ignore_index=True)
print("fact_shelf_audit:", fact_shelf_audit.shape)

# COMMAND ----------

# MAGIC %md ## Land raw CSV to the Unity Catalog Volume

# COMMAND ----------

tables = {"dim_store": dim_store, "dim_product": dim_product,
          "fact_sales_daily": fact_sales, "fact_inventory_daily": fact_inventory,
          "fact_shelf_audit": fact_shelf_audit}
print("=" * 66)
for name, df in tables.items():
    folder = f"{LANDING}/{name}"
    os.makedirs(folder, exist_ok=True)
    df.to_csv(f"{folder}/{name}.csv", index=False)
    print(f"{name:24s} rows={len(df):>8,}  cols={df.shape[1]}  -> {folder}/{name}.csv")
print("=" * 66)

# COMMAND ----------

# MAGIC %md ## Headline stats (execution evidence)

# COMMAND ----------

so = fact_inventory["stockout_flag"].mean()
m = fact_inventory.merge(dim_product[["sku", "unit_price"]], on="sku")
lost_rev = (m["lost_sales_units"] * m["unit_price"]).sum()
print("EVIDENCE ---------------------------------------------------------")
print(f"overall stockout rate (row-level): {so:6.2%}")
print(f"total lost-sales revenue (period): R$ {lost_rev:,.2f}")
print(f"store x sku combos: {N:,} | days: {N_DAYS}")
print(f"sales rows: {len(fact_sales):,} | inventory rows: {len(fact_inventory):,} | audit rows: {len(fact_shelf_audit):,}")
so_by_cat = (fact_inventory.merge(dim_product[["sku", "category"]], on="sku")
             .groupby("category")["stockout_flag"].mean().sort_values(ascending=False))
print("\nstockout rate by category:")
print(so_by_cat.to_string())
print("------------------------------------------------------------------")
