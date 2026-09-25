#!/usr/bin/env python3
"""
FE Bar Varejo — Genie natural-language Q&A driver.

Sends a set of business questions (PT-BR) to the LojaBR Varejo Genie Space, waits for each
answer, and prints the natural-language question, the SQL Genie generated, and the result rows.
Used to produce the S5 execution evidence. Auth via the local Databricks CLI OAuth (profile).

Usage:  python3 05_genie/genie_qa.py
"""
import json, subprocess, sys, time

PROFILE = "fevm-stable"
SPACE = "01f1b906cf2d15b4b1c72c3b25ddb2f0"
BASE = f"/api/2.0/genie/spaces/{SPACE}"

QUESTIONS = [
    "Qual foi a taxa de ruptura media dos ultimos 7 dias e a receita perdida total no periodo?",
    "Quais as 5 lojas com maior receita perdida por ruptura no total do periodo?",
    "Quais categorias tem a maior taxa de ruptura?",
    "Quantos itens estao atualmente em risco de ruptura (risk_flag = 1)?",
    "Liste os 5 itens com maior receita perdida esperada nos proximos 7 dias, com a loja e o pedido sugerido.",
    "Qual a receita perdida por regiao no total do periodo?",
]

def api(method, path, body=None):
    cmd = ["databricks", "api", method.lower(), path, "--profile", PROFILE]
    if body is not None:
        cmd += ["--json", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(out.stdout)
    except Exception:
        return {"_raw": out.stdout, "_err": out.stderr}

def ask(question):
    r = api("POST", f"{BASE}/start-conversation", {"content": question})
    cid = r.get("conversation_id") or r.get("conversation", {}).get("id")
    mid = r.get("message_id") or r.get("message", {}).get("id")
    if not (cid and mid):
        return {"error": r}
    # poll
    for _ in range(40):
        m = api("GET", f"{BASE}/conversations/{cid}/messages/{mid}")
        status = m.get("status")
        if status in ("COMPLETED", "FAILED", "CANCELLED"):
            break
        time.sleep(3)
    result = {"status": status, "text": None, "sql": None, "rows": None, "cols": None}
    for att in m.get("attachments", []) or []:
        if att.get("text"):
            result["text"] = att["text"].get("content")
        if att.get("query"):
            result["sql"] = att["query"].get("query")
            aid = att.get("attachment_id")
            qr = api("GET", f"{BASE}/conversations/{cid}/messages/{mid}/attachments/{aid}/query-result")
            sr = qr.get("statement_response", {})
            result["cols"] = [c["name"] for c in sr.get("manifest", {}).get("schema", {}).get("columns", [])]
            result["rows"] = sr.get("result", {}).get("data_array")
    return result

def main():
    for i, q in enumerate(QUESTIONS, 1):
        print("=" * 90)
        print(f"Q{i}: {q}")
        r = ask(q)
        if r.get("error"):
            print("  ERROR:", r["error"]); continue
        if r.get("text"):
            print("\nGenie:", r["text"])
        if r.get("sql"):
            print("\nSQL gerado:\n  " + r["sql"].replace("\n", "\n  "))
        if r.get("cols"):
            print("\nResultado:")
            print("  " + " | ".join(r["cols"]))
            for row in (r["rows"] or [])[:12]:
                print("  " + " | ".join("" if x is None else str(x) for x in row))
    print("=" * 90)

if __name__ == "__main__":
    main()
