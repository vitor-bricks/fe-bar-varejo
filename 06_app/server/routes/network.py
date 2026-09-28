"""Rede de lojas: map data (stores + transfer routes) and the per-store drill-down."""
from fastapi import APIRouter, HTTPException

from .. import lakebase as lb
from .overview import LATEST_DECISION

router = APIRouter()


@router.get("/api/network")
def network():
    stores = lb.query("""
        SELECT s.store_id, s.store_name, s.city, s.uf, s.region, s.store_format, s.lat, s.lon,
               s.stockout_rate_7d, s.lost_revenue_7d, s.revenue_7d,
               coalesce(q.n, 0) queue_n, coalesce(q.crit, 0) queue_critical, coalesce(q.rs, 0) revenue_at_risk
        FROM serving.store_network s
        LEFT JOIN (SELECT store_id, count(*) n, count(*) FILTER (WHERE severity='CRITICAL') crit, sum(revenue_at_risk) rs
                   FROM serving.replenishment_queue GROUP BY 1) q USING (store_id)
        ORDER BY coalesce(q.rs, 0) DESC""")
    routes = lb.query(f"""WITH d AS ({LATEST_DECISION})
        SELECT q.action_id, q.from_id, q.store_id, q.product_name, q.units, q.transfer_km, q.revenue_protected,
               q.severity, d.decision
        FROM serving.replenishment_queue q LEFT JOIN d USING (action_id)
        WHERE q.action_type = 'TRANSFER' ORDER BY q.revenue_protected DESC""")
    return {"stores": stores, "routes": routes}


@router.get("/api/stores/{store_id}")
def store_detail(store_id: str):
    s = lb.query("SELECT * FROM serving.store_network WHERE store_id = %s", (store_id,))
    if not s:
        raise HTTPException(404, "loja não encontrada")
    actions = lb.query(f"""WITH d AS ({LATEST_DECISION})
        SELECT q.*, d.decision, d.decided_by FROM serving.replenishment_queue q LEFT JOIN d USING (action_id)
        WHERE q.store_id = %s ORDER BY q.priority""", (store_id,))
    at_risk = lb.query("""SELECT product_name, category, on_hand_units, avg_units_28d, days_of_cover, inbound_units,
                                 days_until_inbound, risk_probability, revenue_at_risk
                          FROM serving.position WHERE store_id = %s AND risk_probability IS NOT NULL
                          ORDER BY revenue_at_risk DESC NULLS LAST LIMIT 8""", (store_id,))
    return {"store": s[0], "actions": actions, "at_risk": at_risk}
