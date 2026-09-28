"""Genie drawer: ask in Portuguese, get the answer + the SQL Genie wrote + the rows.
Every turn is logged to Lakebase `app.genie_interactions` (a blip there never breaks the chat)."""
import logging
import time
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from .. import lakebase as lb
from ..config import GENIE_SPACE_ID, get_current_user_email, get_workspace_client

log = logging.getLogger(__name__)
router = APIRouter()
BASE = f"/api/2.0/genie/spaces/{GENIE_SPACE_ID}"


class Ask(BaseModel):
    question: str
    conversation_id: Optional[str] = None


def _do(method, path, body=None):
    return get_workspace_client().api_client.do(method, path, body=body)


@router.post("/api/genie/ask")
def ask(body: Ask, request: Request):
    q = (body.question or "").strip()
    if not q:
        raise HTTPException(400, "pergunta vazia")
    t0 = time.monotonic()
    if body.conversation_id:
        r = _do("POST", f"{BASE}/conversations/{body.conversation_id}/messages", {"content": q})
        cid, mid = body.conversation_id, r.get("id") or r.get("message_id")
    else:
        r = _do("POST", f"{BASE}/start-conversation", {"content": q})
        cid, mid = r.get("conversation_id"), r.get("message_id")
    msg = {}
    for _ in range(60):
        msg = _do("GET", f"{BASE}/conversations/{cid}/messages/{mid}")
        if (msg.get("status") or "").upper() in {"COMPLETED", "FAILED", "CANCELLED", "EXECUTING_QUERY_FAILED"}:
            break
        time.sleep(1)
    out = {"conversation_id": cid, "status": msg.get("status"), "answer": None, "sql": None, "columns": [], "rows": []}
    for att in msg.get("attachments") or []:
        if att.get("text"):
            out["answer"] = att["text"].get("content")
        if att.get("query"):
            out["sql"] = att["query"].get("query")
            out["description"] = att["query"].get("description")
            res = _do("GET", f"{BASE}/conversations/{cid}/messages/{mid}/attachments/{att.get('attachment_id')}/query-result")
            sr = res.get("statement_response") or {}
            out["columns"] = [c["name"] for c in (sr.get("manifest") or {}).get("schema", {}).get("columns", [])]
            out["rows"] = ((sr.get("result") or {}).get("data_array") or [])[:50]
    out["duration_ms"] = int((time.monotonic() - t0) * 1000)
    try:
        lb.execute("""INSERT INTO app.genie_interactions (user_email, question, answer, sql_query, row_count, status, duration_ms)
                      VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                   (get_current_user_email(request), q, out["answer"], out["sql"], len(out["rows"]), out["status"], out["duration_ms"]))
    except Exception as exc:
        log.warning("genie log to Lakebase failed: %s", exc)
    return out
