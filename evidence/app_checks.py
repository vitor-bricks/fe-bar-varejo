#!/usr/bin/env python3
"""Exercise the DEPLOYED Databricks App end to end and print what it returns (evidence as text).

Calls the app with the signed-in user's OAuth token (the Apps gateway forwards the user's
identity, so an approval is recorded with that user as author).
Usage: python3 evidence/app_checks.py > evidence/run_07_app_checks.md
"""
import json, subprocess, time, urllib.request

APP = "https://fe-bar-varejo-tower-7474654865387615.aws.databricksapps.com"
TOKEN = json.loads(subprocess.run(["databricks", "auth", "token", "-p", "fevm-stable"], capture_output=True, text=True).stdout)["access_token"]


def call(path, body=None):
    req = urllib.request.Request(APP + path, data=None if body is None else json.dumps(body).encode(),
                                 method="GET" if body is None else "POST",
                                 headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read()), r.status, round((time.time() - t0) * 1000)


def show(title, obj, status, ms):
    print(f"\n### {title}\n\n`HTTP {status}` · {ms} ms (laptop → app round trip)\n\n```json")
    print(json.dumps(obj, ensure_ascii=False, indent=1, default=str)[:2500])
    print("```")


print("# Databricks App — live checks against the deployed app\n")
print(f"App: {APP} · executed {time.strftime('%Y-%m-%d %H:%M %Z')}")

o, s, ms = call("/api/overview"); trend = o.pop("trend")
show("GET /api/overview (KPIs read from Lakebase `serving`)", {**o, "trend": f"{len(trend)} daily points"}, s, ms)
before = o["protected_today"]

j, s, ms = call("/api/journey")
show("GET /api/journey (status of each stage, written by the job's last run)", j["steps"], s, ms)

q, s, ms = call("/api/queue?limit=3")
show("GET /api/queue?limit=3 (ranked action queue)", [{k: x[k] for k in ("priority", "action_type", "severity", "store_name", "product_name",
     "from_store_name", "units", "eta_days", "risk_probability", "revenue_protected", "rationale_source", "rationale")} for x in q], s, ms)

target = q[0]
d, s, ms = call(f"/api/queue/{target['action_id']}/decide", {"decision": "APPROVED", "note": "evidence check"})
show(f"POST /api/queue/{target['action_id']}/decide → write to Lakebase `app.replenishment_actions`", d, s, ms)

o2, s, ms = call("/api/overview")
print(f"\n### Effect of the approval\n\n```text\nprotected_today: R$ {before:,.2f}  →  R$ {o2['protected_today']:,.2f}\n"
      f"approved_today : {o['approved_today']}  →  {o2['approved_today']}\n```")
q2, _, _ = call("/api/queue?limit=1")
print(f"\n```text\nqueue item #{q2[0]['priority']} status: {q2[0]['decision']} by {q2[0]['decided_by']}\n```")

g, s, ms = call("/api/genie/ask", {"question": "Quais transferências entre lojas estão recomendadas?"})
show("POST /api/genie/ask (Genie space via the app's service principal; turn logged to Lakebase)",
     {"status": g["status"], "answer": g["answer"], "sql": g["sql"], "columns": g["columns"], "rows": g["rows"][:5], "duration_ms": g["duration_ms"]}, s, ms)

lb, s, ms = call("/api/lakebase/status")
show("GET /api/lakebase/status (connection, tables, measured read latency INSIDE the app, recent writes)",
     {k: lb[k] for k in ("host", "database", "postgres", "connected_as", "latency", "tables", "recent_actions", "recent_genie")}, s, ms)
