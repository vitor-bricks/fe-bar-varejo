#!/usr/bin/env python3
"""Cola do dia: the numbers and examples to quote in the roleplay, read from the DEPLOYED app.

The daily job (06:00 BRT) regenerates the chain's data, so stores in alert and queue items change
from day to day (headline numbers stay ~stable: 4.1-4.2% of sales). Run this the morning of the
demo and quote what it prints, not the numbers of the evidence run. Read-only: it only GETs.
Usage: python3 deck/demo_prep.py
"""
import json, subprocess, urllib.request

APP = "https://fe-bar-varejo-tower-7474654865387615.aws.databricksapps.com"
TOKEN = json.loads(subprocess.run(["databricks", "auth", "token", "-p", "fevm-stable"], capture_output=True, text=True).stdout)["access_token"]


def get(path):
    req = urllib.request.Request(APP + path, headers={"Authorization": f"Bearer {TOKEN}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def brl(x):
    s = f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


ACTION = {"TRANSFER": "transferir", "EXPEDITE": "antecipar pedido", "URGENT_ORDER": "pedido urgente"}
SEV = {"CRITICAL": "crítico", "HIGH": "alto", "MEDIUM": "médio"}


def mil(x):
    return f"R$ {x / 1e6:.2f} mi".replace(".", ",") if x >= 1e6 else f"R$ {x / 1e3:.1f} mil".replace(".", ",")


o, j, net, q = get("/api/overview"), get("/api/journey"), get("/api/network"), get("/api/queue?limit=200")
stores = {s["store_id"]: s for s in net["stores"]}
alert = sorted((s for s in net["stores"] if s["stockout_rate_7d"] >= 0.075), key=lambda s: -s["stockout_rate_7d"])

y, m, d = o["as_of"].split("-")
print(f"# Cola do dia · dados até {d}/{m}/{y}\n")
bad = [s for s in j["steps"] if str(s.get("status")).lower() not in ("ok", "success", "succeeded", "completed")]
print("Jornada: " + ("todos os estágios OK" if not bad else "ATENÇÃO: " + ", ".join(f"{s['stage']}={s['status']}" for s in bad)))
if o["protected_today"] > 0:
    print(f"ATENÇÃO: 'Protegido hoje' já está em {brl(o['protected_today'])} ({o['approved_today']} aprovações hoje); "
          "o clique ao vivo não vai partir de R$ 0.")
else:
    print("Protegido hoje: R$ 0 (pronto para o clique ao vivo)")

print("\n## Início (os 4 KPIs)")
print(f"- Perda por ruptura: {mil(o['lost_revenue_annualized'])}/ano · {o['lost_share'] * 100:.1f}% da venda".replace(".", ",", 1))
print(f"- Em risco nos próximos 7 dias: {mil(o['revenue_at_risk_7d'])} · protegível {mil(o['revenue_protectable_7d'])}")
print(f"- Fila: {o['queue_size']} itens ({o['queue_critical']} críticos) · mix " +
      ", ".join(f"{m['n']} {ACTION.get(m['type'], m['type'])}" for m in o["action_mix"]))
print(f"- Lojas em alerta: {o['stores_in_alert']} de {o['stores_total']}" +
      (": " + ", ".join(f"{s['store_name'].replace('LojaBR ', '')} ({s['stockout_rate_7d'] * 100:.1f}%)".replace(".", ",") for s in alert) if alert else ""))

print("\n## Rede de lojas")
top_store = max(net["stores"], key=lambda s: s["revenue_at_risk"])
print(f"- Loja para clicar: {top_store['store_name']} ({top_store['city']}) · {mil(top_store['revenue_at_risk'])} em risco · "
      f"{top_store['queue_n']} ações na fila")
if net["routes"]:
    r = net["routes"][0]
    print(f"- Melhor transferência: {stores[r['from_id']]['store_name']} → {stores[r['store_id']]['store_name']} · "
          f"{r['product_name']} · {r['units']} un · {r['transfer_km']:.0f} km · protege {brl(r['revenue_protected'])}")

print("\n## Fila de ação (o card para aprovar ao vivo)")
card = next((x for x in q if x["action_type"] == "TRANSFER" and x["rationale_source"] == "AGENTE" and not x.get("decision")),
            next(x for x in q if not x.get("decision")))
print(f"- #{card['priority']} · {ACTION.get(card['action_type'])} · {SEV.get(card['severity'])} · {card['product_name']} em {card['store_name']}")
print(f"- Protege {brl(card['revenue_protected'])} · risco {card['risk_probability'] * 100:.0f}% · cobertura {card['days_of_cover']:.1f} dia(s)".replace(".", ",", 1))
print(f"- Justificativa ({card['rationale_source']}): \"{card['rationale']}\"")

print("\n## Trocar de altitude (frase de fechamento)")
print(f"\"Na prática, é o que evita perder os {brl(card['revenue_protected'])} do {card['product_name']} "
      f"em {card['store_name'].replace('LojaBR ', '')} nesta semana.\"")
