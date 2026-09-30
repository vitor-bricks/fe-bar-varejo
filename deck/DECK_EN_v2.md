# LojaBR · Replenishment Center — business deck v2 (text version)

> PDF: `LojaBR_Replenishment_Center_EN_v2.pdf` · Português: `DECK_v2.md` / `LojaBR_Centro_de_Abastecimento_v2.pdf`
> Audience: **VP of Operations & Supply Chain** (executive sponsor) and **Replenishment Manager** (domain owner).
> **Where the numbers come from:** a prototype already running on Databricks, on a calibrated simulation of the chain (20 stores × 129 high-turnover items × 120 days, synthetic data). Figures from the 2026-09-28 evidence run; cost measured from the billing tables (`evidence/run_08_platform_cost.md`). The pilot swaps the simulation for real data. The app UI is in Portuguese.
> v2 = v1 + the fixes from a review with two simulated personas (the VP who funds it and the Head of Data who runs it).

---

## 1. Win back up to R$ 0.8 M a year in sales that vanish from the shelf today

The Replenishment Center warns **2.9 days ahead** that an item will run out. The cheapest fix for each case comes ready, and the replenishment manager approves it **in one click**.

- **Today:** 4.1% of sales lost to stockouts, R$ 2.39 M/yr in the simulation.
- **Chain-wide:** ~R$ 1.4 M recoverable per R$ 100 M of sales (⅓ of the loss).
- **The ask:** a 30-day pilot in 4 stores, with 4 control stores.

## 2. Executive summary

| | |
|---|---|
| **The problem** | In the chain simulation, 4.1% of sales is lost to stockouts: R$ 2.39 M a year, in line with retail's ~4%. The team finds out after the shelf is empty. |
| **The solution** | A model flags which in-stock items will run out in the next 7 days. An AI agent checks the facts and proposes the cheapest fix: transfer, expedite or urgent order. The manager approves in one click. All on a single platform, Databricks. |
| **The value** | Up to ⅓ of the loss recovered: R$ 0.4 to 0.8 M a year in the simulation, depending on execution; R$ 0.7 to 1.4 M per R$ 100 M of sales. Measured platform cost: ~US$ 440 a month, at list price. |
| **The ask** | A 30-day pilot in 4 stores, with 4 control stores, on real data. |

## 3. The problem, in reais (calibrated simulation)

- 4.1% of sales lost; R$ 2.39 M/yr (20 stores × 129 items); 93.5% on-shelf availability over the last 7 days; the worst supplier is on time 63% of the time.
- The simulation replays, day by day, demand, orders, each supplier's delays and each store's stocking policy. Stockouts emerge from those dynamics; they are not drawn at random.
- The loss is concentrated. By category (average 5.3%): cleaning 11.3%, personal care 9.2%, frozen 8.1%, grocery 5.2%, beverages 4.5%, dairy 4.2%, produce 1.2% and bakery 0.6%. Cleaning and personal care suppliers are on time 63% and 68% of the time.

## 4. The buyer's KPIs (range for 50% to 100% of actions executed)

| KPI | Today | With the Center | Who tracks it |
|---|---|---|---|
| On-shelf availability | 93.5% | 94.7% to 95.8% | VP of Operations |
| Stockout rate (store × item × day) | 6.5% | 5.3% to 4.2% | VP and manager |
| Sales lost to stockouts | 4.1% · R$ 2.39 M/yr | −18% to −35% · R$ 0.42 to 0.84 M/yr back | VP and finance |
| Warning before the shelf empties | none | ~2.9 days · 75% ≥ 2 days | Replenishment manager |
| Items to review per day | 29% · 38% right | 8% · 84% right | Replenishment manager |

Assumption: stockouts fall in the same proportion as recovered sales.

## 5. What changes for each of them

**Executive sponsor: VP of Operations & Supply Chain**
- **Sales back on the P&L:** R$ 0.42 to 0.84 M/yr in the simulation, ~R$ 1.4 M per R$ 100 M of sales.
- **The value comes cheap:** 80% of it comes from expediting orders already on their way, with no new purchase and no freight.
- **Risk under control:** the manager decides, and every decision is logged with author and time.
- **Measured cost:** ~US$ 440 a month to run everything, at list price.

**Domain owner: Replenishment Manager**
- **A short list:** 8% of items, 3.6× fewer than today's rule, sorted by R$ or by urgency.
- **2.9 days of warning:** time to transfer or expedite, instead of firefighting.
- **The reasoning, ready:** stock, donor store and supplier punctuality on the card.
- **One click approves,** and data questions go to Genie in plain Portuguese, no ticket needed.

## 6. An action queue, not a report

1. Opens the queue at 7 am: all of the day's actions, sorted by R$ protected or by what empties first.
2. Reads the card: product, store, the cheapest fix, the agent's reasoning and the R$ at stake.
3. Approves in one click, and "R$ protected today" goes up on screen.

**After the click.** *In the prototype:* the decision is stored in Lakebase with author and time. *In the pilot:* the order goes on to LojaBR's ERP, through an API or an integration file, and that integration is week 1's scope. *(Screenshot: `img/card.png`.)*

## 7. Idle stock in one store fixes the gap in another

- 39 transfers suggested in a single day. Only within 450 km, never leaving the donor with less than 10 days of stock, and arriving in 1 to 2 days.
- **When a transfer pays off:** each one protects **R$ 74** on average. It only pays off if the marginal freight costs less than that. So in the pilot we only transfer on routes that already run (such as the DC delivery) or by grouping the items of the same store pair.
- Transfers are 18% of the value. Most of it, 80%, comes from expediting orders already on their way. *(Screenshot: `img/map.png`.)*

## 8. The model is right more than twice as often as today's rule

- **84%** precision on the daily list, vs 38% for the rule "cover < lead time".
- **2.9 days** of warning: 3,691 correct alerts in the test, 75% of them 2 days or more ahead.
- **AUC 0.85**, validated on 49,733 cases from 4 weeks the model never saw.
- The list holds **8%** of items; the rule would flag 29%.
- **And when it is wrong?** A wrong alert does not become a loss. The donor keeps at least 10 days of stock, and the transferred item sells at the destination. The worst case is the freight.
- **How it stays good:** the model is retrained every day in the same job, with a new version in Unity Catalog. The agent looks up the facts before recommending, and the system rejects decisions made without that lookup.

## 9. What it is worth, by execution, and what it costs

| Actions approved and executed on time | 50% | 75% | 100% |
|---|---|---|---|
| Sales protected per week · simulation | R$ 8.1 k | R$ 12.1 k | R$ 16.2 k |
| Per year · 20 stores × 129 items | R$ 0.42 M | R$ 0.63 M | R$ 0.84 M |
| Share of the annual loss recovered | 18% | 26% | 35% |
| **Per R$ 100 M of chain sales** | **R$ 0.7 M** | **R$ 1.1 M** | **R$ 1.4 M** |
| Measured platform cost (list price) | ~US$ 440 a month in every scenario | | |

**Where one day's queue gets its value:**

| Action | Count | Value | Share |
|---|---|---|---|
| Expedite | 142 | R$ 12.9 k | 80% |
| Transfer | 39 | R$ 2.9 k | 18% |
| Urgent order | 7 | R$ 0.4 k | 2% |

**Assumptions:**
- This is expected value (risk-weighted), not guaranteed.
- It is based on the queue of the 2026-09-28 run.
- The simulation covers high-turnover items.
- Transfer freight is left out, hence the route rule.

## 10. From raw data to a decision, in one daily job

- One job, every day at 06:00: with data through yesterday, the queue is ready before stores open. It all runs in 8.4 min.
- Governed in Unity Catalog: lineage, 7 data-quality rules (0 failures) and least-privilege access for the app.
- No copies, no spreadsheets: the same data feeds the app, Genie and the model, and every stage opens in the workspace straight from the app.
- Every number is traceable: `evidence/`, including the cost queries.

## 11. Why Databricks: what the platform changes in the outcome

| | With separate tools | With Databricks |
|---|---|---|
| **Integration** | 7 pieces to integrate and run | One platform: Lakeflow, Unity Catalog, MLflow, Foundation Model API, Lakebase, Genie and Apps |
| **The number** | Copies between systems | One governed dataset, with lineage |
| **Time to pilot** | Months of integration and security reviews | The prototype already runs; the pilot takes 30 days |
| **Security** | Spread across every tool | One place: who sees what, and who approved each action |
| **Cost** | Fixed licences | Measured: ~US$ 440/month; the daily batch journey costs US$ 0.52/day |
| **Exit** | Closed formats | Open formats: Delta (and Iceberg via UniForm), standard Postgres, MLflow and code in Git |

Next use cases on the same data: demand forecasting, markdown of excess stock and store-level assortment.

## 12. 30-day pilot

| When | What happens | How we measure |
|---|---|---|
| Week 1 | Connect sales, stock and orders for the 4 pilot stores; wire the approval into the ERP | data arriving daily, quality ≥ 99% |
| Weeks 2–4 | Action queue in the 4 stores; 4 similar stores as control | stockouts and lost sales, pilot vs control |
| End | Decision to scale | R$ recovered per store, against cost |

- **Success criterion:** cumulative stockout rate over weeks 2–4 at least 1.5 p.p. below control, and R$ recovered greater than the cost.
- **Choosing the stores:** 4 stores with above-average stockouts, across 2 regions and 2 formats. Control is matched on format, region and stockout rate and lives the same month, so seasonality and promotions cancel out.
- **Risks and mitigation:**
  - *The model is wrong:* the manager decides.
  - *Adoption:* one click, in the morning routine.
  - *Freight:* existing routes only.
  - *Incomplete supplier data:* the rule covers it.

## 13. The ask

**Sponsor a 30-day pilot in 4 stores, with a control group.** Measure with LojaBR's real numbers and decide the scale-up on that basis. The platform costs ~US$ 440 a month at list price.

- **Week 0 (sponsor):** pick the stores.
- **Week 1 (LojaBR IT + Databricks):** open the feeds and wire the approval into the ERP.
- **Week 4 (steering committee):** decide the scale-up.

---

### A1. Technical appendix
- **Lakeflow:** Auto Loader on 7 feeds; medallion with 7 expectations and 0 failures.
- **Model:** gradient boosting on *point-in-time* features; trained on 153 k cases and tested on 49.7 k from later dates; AUC 0.85; retrained on every run.
- **Agent:** tool-calling on the Foundation Model API, with 3 tools and rejection of decisions made without a prior lookup.
- **Lakebase:** `serving` published atomically and `app` with approvals, rejections and the Genie log; reads in ~3 ms.
- **Genie:** entity matching, metrics and 5 certified SQL queries.
- **App:** React + TypeScript / FastAPI, service principal with least privilege and sign-in via the workspace SSO.

### A2. Measured cost and operations (2026-09-29, scheduled run only, list price)

| Component | Usage | US$/day |
|---|---|---|
| Serverless job (4 tasks) | 0.35 DBU | 0.16 |
| Lakeflow pipeline | 0.39 DBU | 0.17 |
| Agent (LLM, 24 calls) | 2.72 DBU | 0.19 |
| Lakebase (scales to zero) | 5.11 DBU | 2.66 |
| App (always on) | 12 DBU | 11.40 |
| **Total** | ~US$ 440 / 30 days | **14.58** |

**Operations:**
- **Latency:** daily batch at 06:00 with data through yesterday. Auto Loader can run through the day if needed.
- **Retraining:** daily. Approvals and rejections are stored with their author.
- **Scale:** serverless; time and cost are measured in the pilot with the full assortment of the 4 stores.
- **Security:** role-based permissions in Unity Catalog.
- **App:** it is 78% of the cost and can be stopped outside business hours.
