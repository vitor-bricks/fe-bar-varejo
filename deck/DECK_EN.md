# LojaBR · Replenishment Center — business deck (text version)

> PDF: `LojaBR_Replenishment_Center_EN.pdf` · Português: `DECK.md` / `LojaBR_Centro_de_Abastecimento.pdf`
> Audience: **VP of Operations & Supply Chain** (executive sponsor) and **Replenishment Manager** (domain owner).
> 100% synthetic data. Every number comes from the evidence run of 2026-09-28 (`evidence/`). The app UI is in Portuguese.

---

## 1. Win back up to R$ 0.8 M a year in sales that vanish from the shelf today

The Replenishment Center warns **2.9 days ahead** that an item will run out. The cheapest fix for each case comes ready, and the replenishment manager approves it **in one click**.

- **Today:** 4.1% of sales is lost to stockouts, or R$ 2.39 M/yr in the sample.
- **Chain-wide:** ~R$ 1.4 M recoverable per R$ 100 M of sales (⅓ of the loss).
- **The ask:** a 30-day pilot in 4 stores, with 4 control stores.

## 2. Executive summary

| | |
|---|---|
| **The problem** | 4.1% of sales is lost to stockouts: R$ 2.39 M a year on just 129 high-turnover items across 20 stores. The team finds out **after** the shelf is empty. |
| **The solution** | A model flags which in-stock items will run out in the next 7 days. An AI agent checks the facts and proposes the cheapest fix: transfer, expedite or urgent order. The manager approves in one click. |
| **The value** | Up to ⅓ of the loss recovered: R$ 0.4 to 0.8 M a year in the sample, depending on execution. Across the chain, R$ 0.7 to 1.4 M per R$ 100 M of sales. |
| **The ask** | A 30-day pilot in 4 stores, with 4 control stores. The decision to scale comes from LojaBR's own numbers, not from a projection. |

## 3. The problem, in reais

- **4.1%** of sales lost to stockouts, or **R$ 2.39 M/yr** on 129 items × 20 stores.
- On-shelf availability of **93.5%** over the last 7 days (a 6.5% stockout rate, per store × item × day).
- The loss is concentrated. By category (120 days; chain average 5.3%): cleaning 11.3%, personal care 9.2%, frozen 8.1%, grocery 5.2%, beverages 4.5%, dairy 4.2%, produce 1.2% and bakery 0.6%.
- The suppliers of cleaning and personal care deliver on time only **63% and 68%** of the time.

## 4. The buyer's KPIs

| KPI | Today | With the Replenishment Center | Who tracks it |
|---|---|---|---|
| On-shelf availability | 93.5% | ≥ 95.5% | VP of Operations |
| Stockout rate (store × item × day) | 6.5% | < 4.5% | VP and manager |
| Sales lost to stockouts | 4.1% · R$ 2.39 M/yr | up to −⅓ · ≈ R$ 0.8 M/yr back | VP and finance |
| Warning before the shelf empties | none (reactive) | ~2.9 days · 75% ≥ 2 days | Replenishment manager |
| Items to review per day | 29% of assortment · 38% right | 8% · 84% right | Replenishment manager |

Rule of thumb: every R$ 100 M of sales loses ~R$ 4 M to stockouts. Recovering a third is worth ~R$ 1.4 M.

## 5. What changes for each of them

**Executive sponsor: VP of Operations & Supply Chain**
- **Sales back on the P&L:** ≈ R$ 0.8 M/yr in the sample, or ~R$ 1.4 M per R$ 100 M of sales.
- **Idle stock becomes sales:** 39 transfers in a single day used another store's excess, with no new purchase.
- **Risk under control:** the manager decides, and every decision is logged with author and time.
- **Scale without a new project:** the same platform covers the whole chain and new categories.

**Domain owner: Replenishment Manager**
- **A short list:** 8% of items, 3.6× fewer than today's rule, sorted by R$ or by urgency.
- **2.9 days of warning:** time to transfer or expedite, instead of firefighting.
- **The reasoning, ready:** stock, donor store and supplier punctuality on the card itself.
- **One click approves,** and data questions go to Genie in plain Portuguese, no ticket needed.

## 6. An action queue, not a report

1. **Opens the queue at 7 am.** All of the day's actions, sorted by R$ protected or by what empties first.
2. **Reads the card.** Product, store, the cheapest fix, the agent's reasoning and the R$ at stake.
3. **Approves in one click.** The decision is stored with their name, and "R$ protected today" goes up on screen.

There are three actions: **transfer** from a nearby store with excess, **expedite** the order already on its way, or place an **urgent order** when there is no alternative. *(App screenshot: `img/card.png`.)*

## 7. Idle stock in one store fixes the gap in another

- **39 transfers** suggested in a single day, using other stores' excess.
- Only within **450 km**, and never leaving the donor with less than **10 days** of stock.
- They arrive in **1 to 2 days**, ahead of the supplier's order.
- The map shows stockouts per store and the routes. One click opens the store and its actions. *(App screenshot: `img/map.png`.)*

## 8. The model is right more than twice as often as today's rule

- **84%** precision on the daily list, vs **38%** for the rule "cover < lead time".
- **2.9 days** of warning, with 75% of alerts arriving 2 days ahead or more.
- **AUC 0.85**, validated on dates the model never saw.
- The list holds **8%** of in-stock items; the rule would flag 29%.
- The agent looks up the item's position, nearby stores and the supplier's history before recommending. If it tries to decide first, the system rejects the decision.

> "LojaBR Campinas has only 9 units in stock (0.6 days of cover) and the replenishment order only arrives in 2 days. LojaBR Ribeirão Preto, 207 km away, has a surplus of 61 units, so 46 units can be transferred without compromising its own stock."
> — Café Pilão 500g, evidence run of 2026-09-28 (translated from Portuguese)

## 9. What it is worth, depending on execution

| Actions approved and executed on time | 50% | 75% | 100% |
|---|---|---|---|
| Sales protected per week · sample | R$ 8.1 k | R$ 12.1 k | R$ 16.2 k |
| Per year · sample (129 items × 20 stores) | R$ 0.42 M | R$ 0.63 M | R$ 0.84 M |
| Share of the annual loss recovered | 18% | 26% | 35% |
| **Per R$ 100 M of chain sales** | **R$ 0.7 M** | **R$ 1.1 M** | **R$ 1.4 M** |

- **Basis:** one day's queue (run of 2026-09-28) protects R$ 16.2 k over the next 7 days, ≈ 27% of the previous week's loss.
- **Assumptions:** this is **expected** value (risk-weighted), not guaranteed; the sample is high-turnover items; platform cost (serverless, pay per use) is measured in the pilot.

## 10. From raw data to a decision, in one daily job

```
Ingestion → Medallion → Governance → Model → Agent → Serving → Natural language → Decision
Auto Loader  bronze→gold  Unity Catalog  MLflow·UC  FMAPI·tools  Lakebase  Genie       this app
```

- **One job, every day at 06:00.** Ingestion, quality, model, agent and publishing to the app run together, with a single run record.
- **Governed in Unity Catalog.** Lineage for every number, 7 data-quality rules (0 failures in the last run) and least-privilege access for the app.
- **No copies, no spreadsheets.** The same data feeds the app, Genie and the model. Every stage opens in the workspace straight from the app.

## 11. 30-day pilot: controlled risk, measured result

| When | What happens | How we measure |
|---|---|---|
| Week 1 | Connect sales, stock and orders for the 4 pilot stores | data arriving daily, quality ≥ 99% |
| Weeks 2–4 | Action queue in the 4 stores; 4 similar stores as control | stockouts and lost sales, pilot vs control |
| End | Decision to scale | R$ recovered per store, against cost |

- **Success criterion:** stockout rate in pilot stores ≥ 1.5 p.p. below control, and R$ recovered greater than the platform cost.
- **Risks and mitigation:**
  - *The model is wrong:* the list is ranked by R$ and the manager decides.
  - *Adoption:* one click, inside the morning routine.
  - *Incomplete supplier data:* the agent states its confidence and the rule covers the rest.

## 12. The ask

**Sponsor a 30-day pilot in 4 stores, with a control group.** Measure stockouts and recovered sales with LojaBR's own numbers, and decide the scale-up on that basis.

- **Week 0 (sponsor):** pick the 4 pilot stores and the 4 control stores.
- **Week 1 (LojaBR IT + Databricks):** open the sales, stock and purchase-order feeds.
- **Week 4 (steering committee):** decide the scale-up with the measured result in hand.

---

### Appendix: for the technical team
- **Lakeflow Declarative Pipelines:** Auto Loader on 7 raw feeds; medallion with 7 data-quality expectations and 0 failures in the last run.
- **Model:** gradient boosting on *point-in-time* features (the open order with its **expected** arrival, not the actual one); AUC 0.85; registered in Unity Catalog via MLflow.
- **Agent:** tool-calling on the Foundation Model API. It queries 3 tools, and the system rejects any decision made before them.
- **Lakebase:** `serving` schema published atomically and `app` schema with approvals and the Genie log; reads in ~3 ms.
- **Genie:** entity matching, metric definitions and 5 certified SQL queries.
- **App:** React + TypeScript / FastAPI, service principal with least privilege.
- **Evidence as text:** github.com/vitor-bricks/fe-bar-varejo → `evidence/`
