"""Fila de ação: the ranked worklist and the human decision (approve / reject), persisted in
Lakebase `app.replenishment_actions` with the signed-in user as author."""
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from .. import lakebase as lb
from ..config import get_current_user_email
from .overview import LATEST_DECISION

router = APIRouter()


@router.get("/api/queue")
def queue(action_type: Optional[str] = None, severity: Optional[str] = None, store_id: Optional[str] = None,
          limit: int = 60):
    where, params = [], []
    for col, val in (("q.action_type", action_type), ("q.severity", severity), ("q.store_id", store_id)):
        if val:
            where.append(f"{col} = %s"); params.append(val)
    sql = f"""WITH d AS ({LATEST_DECISION})
        SELECT q.*, d.decision, d.decided_by, d.decided_at
        FROM serving.replenishment_queue q LEFT JOIN d USING (action_id)
        {"WHERE " + " AND ".join(where) if where else ""}
        ORDER BY q.priority LIMIT %s"""
    rows = lb.query(sql, (*params, min(limit, 200)))
    for r in rows:
        if r.get("decided_at"):
            r["decided_at"] = r["decided_at"].isoformat()
    return rows


class Decision(BaseModel):
    decision: Literal["APPROVED", "REJECTED"]
    note: Optional[str] = None


def _record(action_id: str, decision: str, note: Optional[str], actor: str) -> dict:
    q = lb.query("SELECT snapshot_date, action_type, store_id, sku, units, revenue_protected FROM serving.replenishment_queue WHERE action_id = %s",
                 (action_id,))
    if not q:
        raise HTTPException(404, "ação não encontrada")
    a = q[0]
    lb.execute("""INSERT INTO app.replenishment_actions
                  (action_id, snapshot_date, decision, action_type, store_id, sku, units, revenue_protected, decided_by, note)
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
               (action_id, a["snapshot_date"], decision, a["action_type"], a["store_id"], a["sku"], a["units"],
                a["revenue_protected"] if decision == "APPROVED" else 0, actor, note))
    return {"action_id": action_id, "decision": decision, "decided_by": actor,
            "revenue_protected": a["revenue_protected"] if decision == "APPROVED" else 0}


@router.post("/api/queue/{action_id}/decide")
def decide(action_id: str, body: Decision, request: Request):
    return _record(action_id, body.decision, body.note, get_current_user_email(request))


class Bulk(BaseModel):
    action_ids: list[str]


@router.post("/api/queue/approve-all")
def approve_all(body: Bulk, request: Request):
    actor = get_current_user_email(request)
    return {"approved": [_record(a, "APPROVED", "aprovação em lote", actor) for a in body.action_ids[:50]]}


@router.get("/api/decisions")
def decisions(limit: int = 20):
    rows = lb.query("""SELECT a.action_id, a.decision, a.decided_by, a.decided_at, a.units, a.revenue_protected,
                              coalesce(q.action_type, a.action_type) action_type,
                              coalesce(q.store_name, p.store_name) store_name,
                              coalesce(q.product_name, p.product_name) product_name, q.from_store_name
                       FROM app.replenishment_actions a LEFT JOIN serving.replenishment_queue q USING (action_id)
                       LEFT JOIN serving.position p ON p.store_id = a.store_id AND p.sku = a.sku
                       ORDER BY a.decided_at DESC LIMIT %s""", (min(limit, 100),))
    for r in rows:
        r["decided_at"] = r["decided_at"].isoformat()
    return rows
