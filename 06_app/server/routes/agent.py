"""Agente de Reposição: what the tool-calling agent reviewed and decided in the last run."""
from fastapi import APIRouter

from .. import lakebase as lb
from .overview import LATEST_DECISION

router = APIRouter()


@router.get("/api/agent")
def agent():
    items = lb.query(f"""WITH d AS ({LATEST_DECISION})
        SELECT q.*, d.decision, d.decided_by FROM serving.replenishment_queue q LEFT JOIN d USING (action_id)
        WHERE q.rationale_source = 'AGENTE' ORDER BY q.priority""")
    step = lb.query("SELECT detail, updated_at FROM serving.journey_status WHERE step = '05'")
    suppliers = lb.query("SELECT supplier_name, orders_received, on_time_rate, avg_delay_when_late FROM serving.supplier_otif ORDER BY on_time_rate")
    tools = {}
    for it in items:
        for t in (it.get("agent_tools") or "").split(","):
            if t:
                tools[t] = tools.get(t, 0) + 1
    return {"items": items, "run_detail": step[0]["detail"] if step else None,
            "run_at": step[0]["updated_at"].isoformat() if step and step[0]["updated_at"] else None,
            "tool_usage": tools, "changed": sum(1 for i in items if i.get("agent_changed_action")),
            "suppliers": suppliers}
