# Pitch — LojaBR · Replenishment Center (20–30 min)

> Português: [`PITCH.md`](PITCH.md)

A spoken walkthrough of everything we built: the v2 deck, the live app and the workspace. For each
block: **where to be**, **what to show** and **what to say**. The target is a **26-min**
presentation, with 20- and 30-min cuts at the end. Every "open" or "show" links to the thing it
asks for.

- **In the room:** 🟠 **business**, the VP of Operations & Supply Chain, who funds the pilot. 🔵
  **technical**, the architect or Head of Data, who will live with the solution.
- **Material:**
  - the deck [`LojaBR_Replenishment_Center_EN_v2.pdf`][pdf], also as [text](DECK_EN_v2.md) and in
    [Portuguese][pdf-pt];
  - the [deployed app][app];
  - the workspace, which also opens from the app's **arquitetura** button.
- **The app UI is in Portuguese** (it is built for LojaBR's team). Say the English name the first
  time you open each screen:

  | Portuguese label | Say |
  |---|---|
  | Início | Home |
  | Rede de lojas | Store network |
  | Fila de ação | Action queue |
  | Agente | Agent |
  | Lakebase | Lakebase |
  | Protegido hoje | R$ protected today |
  | Aprovar | Approve |
  | arquitetura | architecture |
  | impacto / criticidade | impact / urgency |
- **The story line:** money → problem → action → trust → cost → platform → ask. Start and end
  on **R$**.
- **Golden rule:** only show what proves a business point. When the technical stakeholder digs
  deep, answer the mechanism and **climb back to R$ in one sentence**.

## Quick links

| What | Link |
|---|---|
| **v2 deck** (PDF, slide N = page N) | [EN][pdf] · [PT][pdf-pt] · [EN text](DECK_EN_v2.md) |
| **App** | [Home][app-home] · [Store network][app-network] · [Action queue][app-queue] · [Agent][app-agent] · [Lakebase][app-lakebase] |
| **Daily job** (today's run is the first in the list) | [`fe_bar_varejo_e2e`][ws-job] · [2026-09-28 reference run][ws-run-ref] |
| **Lakeflow pipeline** (graph + data quality) | [`fe_bar_varejo_pipeline`][ws-pipeline] |
| **Unity Catalog** | [gold schema][ws-gold] · [queue table (Lineage tab)][ws-queue-table] · [model and versions][ws-model] |
| **Genie** (space in the workspace) | [LojaBR · Centro de Abastecimento][ws-genie] |
| **Lakebase** (project) | [`fe-bar-varejo`][ws-lakebase] *(link not yet checked in the workspace)* |
| **Notebooks** | [ingestion][ws-nb-ingest] · [pipeline][ws-nb-pipeline] · [model][ws-nb-model] · [agent][ws-nb-agent] · [Lakebase sync][ws-nb-sync] |
| **Evidence as text** | [index](../evidence/README.md) · [data quality](../evidence/run_02_lakeflow_pipeline.md) · [model](../evidence/run_03_early_warning_model.md) · [agent](../evidence/run_04_replenishment_agent.md) · [Genie](../evidence/run_06_genie_qa.md) · [app](../evidence/run_07_app_checks.md) · [cost](../evidence/run_08_platform_cost.md) |
| **Prep** | [`demo_prep.py`](demo_prep.py) (today's cheat sheet, printed in Portuguese) · [`ROLEPLAY.md`](ROLEPLAY.md) (short demo and objections, PT) |

---

## Before you walk in (T − 30 min)

1. Run [`python3 deck/demo_prep.py`](demo_prep.py) and keep **today's cheat sheet** in view. It
   gives today's numbers, the store to click, the best transfer, the card to approve and the
   closing line.
2. Check the cheat sheet for **"Protegido hoje: R$ 0"** and **"Jornada: todos os estágios OK"**
   (all stages OK).
3. **Warm up the app** 5 min before: open [Home][app-home], [Store network][app-network] and
   [Action queue][app-queue] once. Lakebase scales to zero, so the first read after a quiet period
   is slower.
4. Have the tabs ready, in this order:
   1. the [v2 PDF][pdf] in full screen;
   2. the app on [Home][app-home];
   3. the [job][ws-job], with today's run open;
   4. the [pipeline][ws-pipeline].

   Opening tabs 3 and 4 now gets SSO out of the way before the demo.
5. Browser zoom at 110–125%, notifications off, and only these tabs open.
6. Keep a plan B at hand: slides [6](LojaBR_Replenishment_Center_EN_v2.pdf#page=6),
   [7](LojaBR_Replenishment_Center_EN_v2.pdf#page=7) and
   [10](LojaBR_Replenishment_Center_EN_v2.pdf#page=10) have the app screens; the
   [`evidence/`](../evidence/README.md) folder has everything as text.

> **Deck vs app.** The deck is a snapshot of the 2026-09-28 reference run. The app shows today's
> queue, which changes every day with data through yesterday. Quote the deck's number when you are
> on a slide and the cheat sheet's number when you are in the app. If someone notices: *"the deck
> is a photo of one day; the app is the movie. The items change, the order of magnitude does not."*

---

## Timing map

| ⏱ | Block | Min | Where |
|---|---|---|---|
| 00:00 | 1 · Opening: the outcome and the ask | 2 | slides [1](LojaBR_Replenishment_Center_EN_v2.pdf#page=1)–[2](LojaBR_Replenishment_Center_EN_v2.pdf#page=2) |
| 02:00 | 2 · The problem, in reais | 1.5 | slide [3](LojaBR_Replenishment_Center_EN_v2.pdf#page=3) |
| 03:30 | 3 · The KPIs and the value for each of them | 2.5 | slides [4](LojaBR_Replenishment_Center_EN_v2.pdf#page=4)–[5](LojaBR_Replenishment_Center_EN_v2.pdf#page=5) |
| 06:00 | 4 · **Demo: the manager's morning** | 8 | app: [Home][app-home] → [Network][app-network] → [Queue][app-queue] → **Approve** → Home → [Lakebase][app-lakebase] |
| 14:00 | 5 · Why trust it | 3.5 | slide [8](LojaBR_Replenishment_Center_EN_v2.pdf#page=8) → app: [Agent][app-agent] → Genie |
| 17:30 | 6 · What it is worth and what it costs | 2 | slide [9](LojaBR_Replenishment_Center_EN_v2.pdf#page=9) |
| 19:30 | 7 · How it works and why Databricks | 4 | app: **arquitetura** → [run][ws-job] and [pipeline][ws-pipeline] → slide [11](LojaBR_Replenishment_Center_EN_v2.pdf#page=11) |
| 23:30 | 8 · The pilot and the ask | 2 | slides [12](LojaBR_Replenishment_Center_EN_v2.pdf#page=12)–[13](LojaBR_Replenishment_Center_EN_v2.pdf#page=13) |
| 25:30 | Close and the commitment question | 0.5 | slide [13](LojaBR_Replenishment_Center_EN_v2.pdf#page=13) |
| 26:00 | Questions | — | see "Likely questions" |

Slides 6, 7 and 10 are app screens. Live, the demo replaces them and they stay as backup.

---

## 1 · Opening: the outcome and the ask · 00:00 → 02:00

**[Slide 1](LojaBR_Replenishment_Center_EN_v2.pdf#page=1) (cover).** Speak to the 🟠.
> "LojaBR loses **4.1% of its sales** because products run out on the shelf and shoppers buy from
> the competitor. On the 129 top-selling items, that is **R$ 2.39 million a year**. Today the team
> finds out after the shelf is already empty.
> We built the Replenishment Center on Databricks. It warns **almost 3 days ahead**, brings the
> cheapest fix ready, and the manager approves it **in one click**. The goal is to win back up to
> **R$ 0.8 million a year** on those items. What we are asking for is a **30-day pilot in 4
> stores**, with a control group."

**[Slide 2](LojaBR_Replenishment_Center_EN_v2.pdf#page=2) (executive summary).** Give it 30 s;
don't read the four boxes.
> "If you take one page away, it is this one: problem, solution, value and ask."

**Agenda, in one sentence, to both of them.**
> "I'll show the problem in reais, the system running on today's data, why you can trust the
> alert, what it costs, and the pilot plan. [Technical stakeholder's name], the architecture comes
> at around minute 20, and everything I show opens in the workspace."

---

## 2 · The problem, in reais · 02:00 → 03:30

**[Slide 3](LojaBR_Replenishment_Center_EN_v2.pdf#page=3).** Point at the four numbers first, then
at the cleaning bar.
> "This is 120 days of history from all 20 stores. On-shelf availability is at 93.5%. The key
> point is that **the loss is concentrated**: cleaning and personal care run out twice as often as
> the average, and their suppliers deliver on time only 63% and 68% of the time. It is not a
> problem spread everywhere. You can attack it with a **short list**, and that is what I'll show."

---

## 3 · The KPIs and the value for each of them · 03:30 → 06:00

**[Slide 4](LojaBR_Replenishment_Center_EN_v2.pdf#page=4) (the buyer's KPIs).**
> "We did not invent new metrics. These are the numbers LojaBR already tracks. The range goes from
> half of the actions executed to all of them. Availability goes from 93.5% up to 95.8%. Lost sales
> fall by 18% to 35%. And the manager gets **2.9 days of warning**, which today is zero."

**[Slide 5](LojaBR_Replenishment_Center_EN_v2.pdf#page=5) (what changes for each of them).** Split
your eye contact.
- 🟠 *"For you: sales back on the P&L. And the value comes cheap, because most of it comes from
  **expediting orders already on their way**, with no new purchase and no freight."*
- 🟠/🔵 *"For the team that operates it: a list with 8% of the items instead of 29%, the reasoning
  ready on the card, and questions to Genie in plain language, no ticket needed."*

**Transition to the app:**
> "Instead of showing the screen on a slide, let me open the system with today's queue."

---

## 4 · Demo: the manager's morning · 06:00 → 14:00

This is the heart of the pitch. Every step proves a business point.

### 4a · [Home (Início)][app-home] (1 min)
- **Show:** the 4 KPIs. Use the cheat sheet's numbers: loss per year, at risk over the next 7
  days, **R$ protected today = R$ 0**, and stores in alert.
- **Say:**
  > "These numbers are from today. The job ran at 6 am with data through yesterday, so the queue
  > is ready before stores open. Keep an eye on this **R$ 0** under 'protected today'. We'll change
  > it in a minute."

### 4b · [Store network (Rede de lojas)][app-network] (2 min)
- **Show:**
  1. The map, with stockouts per store.
  2. Click **Sudeste** (Southeast). The dashed lines are **suggested transfers**.
  3. Hover over a store to see the tooltip with its metrics.
  4. Click the **store from the cheat sheet**. Its summary, ranking and the **"Ações para {store}"**
     (actions for this store) panel open.
- **Say:** use the cheat sheet's best transfer.
  > "Idle stock in {donor} fixes the gap in {destination}: {item}, {km} km away, arriving in 1 to
  > 2 days, without waiting for the supplier. The rule is simple: only within 450 km, and the donor
  > never drops below 10 days of stock."

### 4c · [Action queue (Fila de ação)][app-queue]: the demo moment (3 min)
- **Show:**
  1. The queue sorted by **impacto** (impact in R$). Switch to **criticidade** (urgency) and back:
     *"the manager chooses: what is worth most, or what runs out first"*.
  2. Find the **card from the cheat sheet**: product, store, risk, days of cover, the action, the
     **R$ highlighted**, and the agent's reasoning.
  3. Translate **one sentence** of the reasoning aloud, ideally the one about stock and supplier
     punctuality.
  4. **Click Aprovar (Approve).**
- **Say:**
  > "This is a decision, not a report. The agent checked the stock in nearby stores and the
  > supplier's track record before suggesting it. The manager read it, agreed, and approved it in
  > one click."

### 4d · Back to [Home][app-home] (30 s)
- **Show:** "R$ protected today" is no longer R$ 0.
- **Say:**
  > "This is the number the pilot will measure **against the control group**. Every click becomes
  > a counted result."

### 4e · [Lakebase][app-lakebase], for the 🔵 (1 min)
- **Show:** under "Escritas recentes · aprovações" (recent writes · approvals), the decision
  appears with **your name and the time**. Point at the p50 latency, in milliseconds.
- **Say:**
  > "The approval was written to a managed Postgres on Databricks, Lakebase: transactional, with
  > the author. The app reads the queue from here in a few milliseconds. Analytics stays in the
  > lakehouse, governed in the same place. Audit is built in: who approved what, and when."

**Transition back to the deck:**
> "A fair question now is: why trust this alert?"

---

## 5 · Why trust it · 14:00 → 17:30

**[Slide 8](LojaBR_Replenishment_Center_EN_v2.pdf#page=8) (1.5 min).**
> "The model is right on **84%** of the daily list. Today's rule, 'cover below lead time', is
> right 38% of the time. And its list holds 8% of the items, not 29%. We validated it on almost 50
> thousand cases from 4 weeks the model never saw.
> And when it is wrong? A wrong alert does not become a loss: the donor keeps at least 10 days of
> stock, and the item sells at the destination. The worst case is the freight. It is retrained
> every day, in the same job."

Source, if asked: [`run_03_early_warning_model.md`](../evidence/run_03_early_warning_model.md).

**App · [Agent (Agente)][app-agent] (1 min).**
- **Show:** at the top, how many high-value items the agent reviewed ("revisados") and how many
  actions it **changed** after checking the facts ("ações alteradas"). Below, under "Como ele
  decide" (how it decides), the tools it called in this round, a real count from the loop.
- **Say** (to the 🔵):
  > "The agent has to call its tools before deciding. If it tries to decide without looking, the
  > system rejects it. It only quotes numbers the tools returned."
- If the 🔵 wants the code: [agent notebook][ws-nb-agent] ·
  [trace as text](../evidence/run_04_replenishment_agent.md).

**App · Genie (1 min).**
- **Show:** click the app's **amber button** and ask *"Which suppliers are late most often?"*.
  The same space also opens in the [workspace][ws-genie].
- Genie understands the English question and answers in Portuguese, because the space is set up
  for LojaBR's team. Translate the first line: *"Limpa Mais is the worst: about 62% on time."*
- **Say**, while it answers (10–20 s):
  > "The manager asks in their own words, without opening a ticket with the data team. And every
  > question is logged, just like the approval."
- **Hook:** if the approved card mentioned a supplier, show that Genie returns the same on-time
  rate.
  > "The app, the agent and Genie read the same number."

---

## 6 · What it is worth and what it costs · 17:30 → 19:30

**[Slide 9](LojaBR_Replenishment_Center_EN_v2.pdf#page=9).** Speak to the 🟠.
> "In the conservative case, with half of the actions executed, it is **R$ 0.42 million a year**.
> With all of them, **R$ 0.84 million**. For the whole chain, the rule of thumb is **R$ 1.4 million
> per R$ 100 million of sales**.
> The cost is measured, not estimated: **~US$ 440 a month** at list price, to run everything. That
> is under US$ 500 a month of platform against ~R$ 35 thousand a month of sales back, in the most
> conservative case.
> And where the value comes from: in the reference run, 80% came from **expediting orders already
> on their way**."

Cost source, if asked: [`run_08_platform_cost.md`](../evidence/run_08_platform_cost.md).

> ⚠️ The mix bar changes every day. Quote the 80% as "in the reference run" and don't compare it
> with today's queue.

---

## 7 · How it works and why Databricks · 19:30 → 23:30

### 7a · Live architecture (2.5 min)
- **Show:** in the [app][app-home], click the glowing **arquitetura** (architecture) button. The 8
  stages appear: ingestion → medallion → governance → model → agent → serving → natural language →
  decision. Each one shows the **status of today's run**.
- **Say:**
  > "It is a single job, every day at 6 am: from raw data to a decision in about 8 minutes. And
  > every box opens the real resource in the workspace."
- **Open up to 2 links** (already warm in your tabs):
  1. **Today's run**: the [job][ws-job] with the first run in the list, or the link at the top of
     the view. Show the chained tasks: *"one run id, end to end"*.
  2. **[Pipeline][ws-pipeline]** (medallion stage): the bronze → silver → gold graph, and, after
     clicking a silver table, the data quality with the **7 expectations, 0 failures**.
     > "A wrong number never reaches the manager."
- **Go back to the app** before opening a third link.

### 7b · [Slide 11](LojaBR_Replenishment_Center_EN_v2.pdf#page=11), Why Databricks (1.5 min)
> "With separate tools, this would be 7 pieces: ETL, warehouse, ML, an operational database, an
> LLM, BI and app hosting. Here it is one platform. What that changes in the outcome:
> - **The number matches.** The app, Genie and the model read the same data, with lineage.
> - **The time to pilot is 30 days**, because the solution already runs end to end on Databricks.
> - **Security lives in one place.**
> - **The cost is measured.**"

For the 🔵:
> "And the exit stays open: Delta, with Iceberg via UniForm, standard Postgres, MLflow and code in
> Git."

To close the slide:
> "The same data already serves the next use cases: demand forecasting, markdown of excess stock
> and store-level assortment."

---

## 8 · The pilot and the ask · 23:30 → 25:30

**[Slide 12](LojaBR_Replenishment_Center_EN_v2.pdf#page=12).**
> "Week 1: connect sales, stock and orders for the 4 pilot stores. Weeks 2 to 4: the queue runs in
> those 4 stores, with 4 similar stores as control. Same month, same format, same region, so
> seasonality and promotions cancel out. The success criterion: stockouts at least **1.5 points
> below control**, and R$ recovered greater than the cost."

**[Slide 13](LojaBR_Replenishment_Center_EN_v2.pdf#page=13).**
> "Here is the ask: **sponsor a 30-day pilot in 4 stores, with a control group**. In week 0 you
> pick the stores. In week 1, LojaBR IT and Databricks open the feeds. In week 4, the steering
> committee decides the scale-up with the measured result in hand."

### Close (30 s)
Use the cheat sheet's closing line, in English:
> "In practice, this is what keeps us from losing the R$ {value} on {item} in {store} this week.
> Multiply that by a full queue, every day, across 20 stores."

Then the **commitment question**, and stay silent:
> "Which 4 stores would you put in the pilot?"

---

## 20-min version

| Block | 26 min | 20 min | What to cut |
|---|---|---|---|
| 1 · Opening | 2 | 1.5 | the agenda becomes half a sentence |
| 2 · Problem | 1.5 | 1 | only the "concentrated" sentence |
| 3 · KPIs and value | 2.5 | 2 | slide 5 in 30 s, the 🟠 line only |
| 4 · Demo | 8 | 6 | network in 1 min (just the store click); Lakebase in 30 s |
| 5 · Trust | 3.5 | 2.5 | skip the Agent tab; keep Genie |
| 6 · Value and cost | 2 | 1.5 | — |
| 7 · Platform | 4 | 3 | only the overlay and the run link; slide 11 in 1 min |
| 8 · Pilot and ask | 2 | 2 | don't cut |

Never cut **the Approve click and the return to Home**, **slide 9**, or **the ask**.

## 30-min version

Add these to the 26-min script:
- **+1.5 min · Genie:** a follow-up, *"Which actions are recommended for the {cheat-sheet store}
  store?"*, then open the generated SQL for the 🔵.
- **+1.5 min · Unity Catalog:** open the [queue table][ws-queue-table] on the **Lineage** tab, to
  show where every row comes from. Then the [model][ws-model], with one version per day.
- **+1 min · [Appendix A2](LojaBR_Replenishment_Center_EN_v2.pdf#page=15):** the cost table by
  component. The app is 78% of the cost and can be stopped outside business hours.
- **+1 min · Evidence on GitHub:** open
  [`run_08_platform_cost.md`](../evidence/run_08_platform_cost.md).
  > "Every number in this deck has its query right next to it."

---

## If something goes wrong

| Symptom | What to do |
|---|---|
| The app is slow on the first screen | Lakebase is waking up. Talk through slide 5 while it loads; past 20 s, use slides [6](LojaBR_Replenishment_Center_EN_v2.pdf#page=6)–[7](LojaBR_Replenishment_Center_EN_v2.pdf#page=7). |
| "Protegido hoje" is not R$ 0 | *"We already have R$ X approved today. Watch it go up."* The click still shows the effect. |
| The cheat sheet's card is gone from the queue | Sort by impact and use the **first transfer card**. |
| Genie takes more than 30 s | Keep talking. If nothing comes, show Q3 in [`run_06_genie_qa.md`](../evidence/run_06_genie_qa.md). |
| The workspace asks you to log in | Go back to the app and use [slide 10](LojaBR_Replenishment_Center_EN_v2.pdf#page=10) (the architecture image). |
| Someone notices the app's number differs from the deck | *"The deck is the 2026-09-28 snapshot; the app is today's queue."* |

---

## Numbers to know by heart

| | |
|---|---|
| **Loss** | 4.1% of sales · R$ 2.39 M/yr · 129 items × 20 stores · 120 days of history |
| **Value** | R$ 0.42–0.84 M/yr · −18% to −35% lost sales · R$ 1.4 M per R$ 100 M of sales |
| **Alert** | 2.9 days of warning · 75% ≥ 2 days · 84% precision vs 38% for the rule · AUC 0.85 · 49,733 cases |
| **List** | 8% of items, vs 29% for the rule (3.6× shorter) |
| **Transfer** | ≤ 450 km · donor keeps ≥ 10 days · arrives in 1–2 days · protects ~R$ 74 on average |
| **Cost** | ~US$ 440/month (US$ 14.58/day) · daily batch US$ 0.52/day · app = 78% of the cost |
| **Operations** | daily job at 06:00 · ~8 min · 7 data-quality rules, 0 failures · Lakebase reads in ~3 ms |
| **Pilot** | 30 days · 4 stores + 4 control · success = ≥ 1.5 p.p. below control and R$ > cost |

---

## Likely questions (one-sentence answers, then back to R$)

The baseline objections are in [`ROLEPLAY.md`](ROLEPLAY.md) §2 (Portuguese). These are the ones the
two personas raised when they reviewed the deck.

### 🟠 Business
| Question | Answer |
|---|---|
| *What does it cost per month?* | "Measured from the [billing tables](../evidence/run_08_platform_cost.md): ~US$ 440 a month at list price, for everything. The app is 78% of that and can be stopped outside business hours." |
| *Sales are not margin.* | "Right. At a 20–25% gross margin, the ~R$ 35 thousand a month of sales in the conservative case is R$ 7–9 thousand of margin, against ~R$ 2.5 thousand of platform." *(Back-of-the-envelope: check the day's exchange rate.)* |
| *What does a wrong transfer cost?* | "Each transfer protects ~R$ 74. That is why, in the pilot, we only transfer on routes that already run, or by grouping items for the same store pair." |
| *Does 30 days prove anything? What about seasonality?* | "Control lives through the same month, so seasonality and promotions hit both groups. The pilot measures the difference, not the level." |
| *And scaling afterwards?* | "The decision comes in week 4, with R$ recovered per store against the cost. Then we know what each new store is worth." |
| *Who runs it afterwards?* | "It is a scheduled, serverless job, with no cluster to maintain. The manager uses the app, and the data team watches the [daily run][ws-job]." |

### 🔵 Technical
| Question | Answer |
|---|---|
| *Does the click create an order in the ERP?* | "The approval is already a transactional record in Lakebase, with author and time. Wiring it into the ERP is week-1 scope in the pilot, by API or file, whichever LojaBR prefers." |
| *The job is daily. Isn't the warning late?* | "The warning is 2.9 days ahead, so it fits a daily batch. If needed, Auto Loader can run through the day without changing the pipeline." |
| *How do you know the donor really has the stock?* | "The agent looks up the day's position before recommending, and the system rejects any decision made without that lookup. The reasoning quotes the number the tool returned." ([trace](../evidence/run_04_replenishment_agent.md)) |
| *And retraining? Do rejections teach the model?* | "It is retrained every day, with a version in [Unity Catalog][ws-model]. Approvals and rejections are stored with their author and become an evaluation signal in the pilot." |
| *Does it scale to the full assortment?* | "Everything is serverless. In the pilot we measure time and cost with the full assortment of the 4 stores, before any scale-up." |
| *Who sees what?* | "Permissions are role-based in Unity Catalog. The app uses a least-privilege service principal, and every approval records the real user." |
| *What if we want to leave Databricks?* | "The formats are open: Delta, with Iceberg via UniForm, standard Postgres, MLflow and code in Git. Nothing is locked in a closed format." |

[pdf]: LojaBR_Replenishment_Center_EN_v2.pdf
[pdf-pt]: LojaBR_Centro_de_Abastecimento_v2.pdf
[app]: https://fe-bar-varejo-tower-7474654865387615.aws.databricksapps.com/
[app-home]: https://fe-bar-varejo-tower-7474654865387615.aws.databricksapps.com/
[app-network]: https://fe-bar-varejo-tower-7474654865387615.aws.databricksapps.com/rede
[app-queue]: https://fe-bar-varejo-tower-7474654865387615.aws.databricksapps.com/fila
[app-agent]: https://fe-bar-varejo-tower-7474654865387615.aws.databricksapps.com/agente
[app-lakebase]: https://fe-bar-varejo-tower-7474654865387615.aws.databricksapps.com/lakebase
[ws-job]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/jobs/384370635751593
[ws-run-ref]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/jobs/384370635751593/runs/204235693781766
[ws-pipeline]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/pipelines/733e5172-5f51-404b-a790-b40cce95f015
[ws-gold]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/explore/data/serverless_stable_xpbmim_catalog/fe_bar_varejo_gold
[ws-queue-table]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/explore/data/serverless_stable_xpbmim_catalog/fe_bar_varejo_gold/gold_replenishment_queue_final
[ws-model]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/explore/data/models/serverless_stable_xpbmim_catalog/fe_bar_varejo_gold/stockout_early_warning
[ws-genie]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/genie/rooms/01f1b906cf2d15b4b1c72c3b25ddb2f0
[ws-lakebase]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/lakebase/projects/fe-bar-varejo
[ws-nb-ingest]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/editor/notebooks/561894903539841
[ws-nb-pipeline]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/editor/notebooks/561894903539842
[ws-nb-model]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/editor/notebooks/4068321213986550
[ws-nb-agent]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/editor/notebooks/4068321213986545
[ws-nb-sync]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/editor/notebooks/4068321213986551
