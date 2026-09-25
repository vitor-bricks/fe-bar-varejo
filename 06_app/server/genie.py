"""Genie natural-language proxy — forwards a question to the LojaBR Varejo Genie Space."""
import os, time, requests
from .config import get_oauth_token, get_workspace_host

SPACE = os.environ.get("GENIE_SPACE_ID", "")


def _headers():
    return {"Authorization": f"Bearer {get_oauth_token()}", "Content-Type": "application/json"}


def ask(question: str):
    host = get_workspace_host()
    base = f"{host}/api/2.0/genie/spaces/{SPACE}"
    r = requests.post(f"{base}/start-conversation", headers=_headers(),
                      json={"content": question}, timeout=30).json()
    cid = r.get("conversation_id") or r.get("conversation", {}).get("id")
    mid = r.get("message_id") or r.get("message", {}).get("id")
    if not (cid and mid):
        return {"error": "could not start conversation", "raw": r}
    msg = {}
    for _ in range(40):
        msg = requests.get(f"{base}/conversations/{cid}/messages/{mid}", headers=_headers(), timeout=30).json()
        if msg.get("status") in ("COMPLETED", "FAILED", "CANCELLED"):
            break
        time.sleep(2)
    out = {"status": msg.get("status"), "answer": None, "sql": None, "columns": None, "rows": None}
    for att in msg.get("attachments", []) or []:
        if att.get("text"):
            out["answer"] = att["text"].get("content")
        if att.get("query"):
            out["sql"] = att["query"].get("query")
            aid = att.get("attachment_id")
            qr = requests.get(f"{base}/conversations/{cid}/messages/{mid}/attachments/{aid}/query-result",
                              headers=_headers(), timeout=30).json()
            sr = qr.get("statement_response", {})
            out["columns"] = [c["name"] for c in sr.get("manifest", {}).get("schema", {}).get("columns", [])]
            out["rows"] = sr.get("result", {}).get("data_array") or []
    return out
