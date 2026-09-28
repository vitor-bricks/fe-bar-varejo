"""Início: outcome KPIs, stockout trend and the live status of each journey stage."""
from fastapi import APIRouter

from .. import lakebase as lb

router = APIRouter()

LATEST_DECISION = """
    SELECT DISTINCT ON (action_id) action_id, decision, decided_by, decided_at, revenue_protected
    FROM app.replenishment_actions ORDER BY action_id, decided_at DESC"""


@router.get("/api/overview")
def overview():
    kpi = lb.query("SELECT snapshot_date, stockout_rate, lost_revenue, revenue FROM serving.kpi_daily ORDER BY snapshot_date")
    q = lb.query("""SELECT count(*) n, coalesce(sum(revenue_at_risk),0) at_risk, coalesce(sum(revenue_protected),0) protectable,
                           count(*) FILTER (WHERE severity='CRITICAL') critical
                    FROM serving.replenishment_queue""")[0]
    mix = lb.query("SELECT action_type, count(*) n, sum(revenue_protected) rs FROM serving.replenishment_queue GROUP BY 1 ORDER BY 2 DESC")
    today = lb.query(f"""WITH d AS ({LATEST_DECISION})
        SELECT count(*) FILTER (WHERE decision='APPROVED') approved, count(*) FILTER (WHERE decision='REJECTED') rejected,
               coalesce(sum(revenue_protected) FILTER (WHERE decision='APPROVED'), 0) protected
        FROM d WHERE decided_at >= date_trunc('day', now())""")[0]
    stores = lb.query("SELECT count(*) FILTER (WHERE stockout_rate_7d >= 0.075) alert, count(*) total FROM serving.store_network")[0]
    lost_total = sum(float(r["lost_revenue"]) for r in kpi)
    rev_total = sum(float(r["revenue"]) for r in kpi)
    last7 = kpi[-7:]
    return {
        "as_of": kpi[-1]["snapshot_date"] if kpi else None,
        "days": len(kpi),
        "lost_revenue_period": round(lost_total, 2),
        "lost_share": round(lost_total / (rev_total + lost_total), 4) if rev_total else 0,
        "lost_revenue_annualized": round(lost_total * 365 / max(len(kpi), 1), 0),
        "lost_revenue_7d": round(sum(float(r["lost_revenue"]) for r in last7), 2),
        "stockout_rate_today": float(kpi[-1]["stockout_rate"]) if kpi else 0,
        "stockout_rate_7d": round(sum(float(r["stockout_rate"]) for r in last7) / max(len(last7), 1), 4),
        "queue_size": int(q["n"]), "queue_critical": int(q["critical"]),
        "revenue_at_risk_7d": round(float(q["at_risk"]), 2), "revenue_protectable_7d": round(float(q["protectable"]), 2),
        "action_mix": [{"type": m["action_type"], "n": int(m["n"]), "rs": round(float(m["rs"]), 2)} for m in mix],
        "protected_today": round(float(today["protected"]), 2),
        "approved_today": int(today["approved"]), "rejected_today": int(today["rejected"]),
        "stores_in_alert": int(stores["alert"]), "stores_total": int(stores["total"]),
        "trend": [{"date": r["snapshot_date"], "stockout_rate": float(r["stockout_rate"]),
                   "lost_revenue": float(r["lost_revenue"])} for r in kpi],
    }


@router.get("/api/journey")
def journey():
    steps = lb.query("SELECT step, stage, product, status, detail, job_run_id, updated_at FROM serving.journey_status ORDER BY step")
    card = {r["metric"]: r["value"] for r in lb.query("SELECT metric, value FROM serving.model_card")}
    return {"steps": [{**s, "updated_at": s["updated_at"].isoformat() if s["updated_at"] else None} for s in steps],
            "model": card}
