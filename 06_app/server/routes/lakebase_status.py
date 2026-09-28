"""Lakebase ao vivo: connection facts, served tables, real read latency and the app's writes."""
from fastapi import APIRouter

from .. import lakebase as lb
from ..config import LAKEBASE_DB, LAKEBASE_HOST

router = APIRouter()


@router.get("/api/lakebase/status")
def status():
    info = lb.query("SELECT version() v, current_user u")[0]
    tables = lb.query("""SELECT table_schema, table_name FROM information_schema.tables
                         WHERE table_schema IN ('serving', 'app') ORDER BY 1, 2""")
    if tables:   # one round trip for all counts
        union = " UNION ALL ".join(f"SELECT '{t['table_schema']}.{t['table_name']}' k, count(*) n FROM {t['table_schema']}.\"{t['table_name']}\""
                                   for t in tables)
        counts = {r["k"]: r["n"] for r in lb.query(union)}
        for t in tables:
            t["rows"] = counts[f"{t['table_schema']}.{t['table_name']}"]
    actions = lb.query("""SELECT a.decision, a.decided_by, a.decided_at, a.revenue_protected, q.product_name, q.store_name
                          FROM app.replenishment_actions a LEFT JOIN serving.replenishment_queue q USING (action_id)
                          ORDER BY a.decided_at DESC LIMIT 8""")
    genie = lb.query("""SELECT asked_at, user_email, question, row_count, duration_ms, status
                        FROM app.genie_interactions ORDER BY asked_at DESC LIMIT 6""")
    for r in actions:
        r["decided_at"] = r["decided_at"].isoformat()
    for r in genie:
        r["asked_at"] = r["asked_at"].isoformat()
    return {"host": LAKEBASE_HOST, "database": LAKEBASE_DB, "postgres": info["v"].split(",")[0],
            "connected_as": info["u"], "tables": tables, "latency": lb.latency_stats(),
            "recent_actions": actions, "recent_genie": genie}
