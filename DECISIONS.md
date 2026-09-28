# Decisions & trade-offs

The choices that shaped the build, the alternatives we weighed, and why. Includes one
correction to the first version of this build (§10).

## 1. Scope — one sharp problem with the loop closed
**Decision:** anchor on **stockouts in a supermarket chain** and go all the way to the decision:
predict → explain → *approve* → persist → measure "R$ protected today".
**Why:** buyers fund outcomes, not dashboards. A read-only report stops one step short of value.
**Trade-off:** fewer domains than a "platform tour", but a value story an executive can repeat.

## 2. Data — simulated dynamics, not random rows
**Decision:** a day-by-day inventory simulation (Poisson demand with weekday/promo effects, reorder
policy, lead times, **supplier-specific lateness**, store-specific stocking policies), plus purchase
orders with *expected vs actual* arrival and orders still open.
**Why:** stockouts must *emerge* for the model to learn real signal, and the actions need real
levers: an order already in transit (expedite) and excess stock nearby (transfer).
**Trade-off:** a more complex generator; still 100% synthetic, no customer data.

## 3. Predict only what can still be prevented
**Decision:** the model scores items **still on the shelf** and predicts a stockout in the next 7
days. Items already at zero are excluded from training and scoring.
**Why:** the first version ranked items that were already empty — high precision, zero value.
**Evidence:** AUC 0.85; precision on the daily top-K **0.84 vs 0.38 for the planner rule
"cover < lead time"**; median lead of the warning ≈ 2.9 days (measured, not estimated).
**Trade-off:** lower headline precision than "predicting the present", but honest and actionable.

## 4. Point-in-time features
**Decision:** training uses the purchase order that was open *on that day* with its **expected**
arrival (what a planner knew), never the actual arrival.
**Why:** using actual arrivals would leak the future and inflate metrics.

## 5. Rank by money, label by time
**Decision:** priority = R$ protected (risk × units at risk × price); severity = how soon the shelf
empties (critical < 1 day). Transfers only between stores ≤ 450 km.
**Why:** operations has finite capacity; severity alone would make everything "critical", and
Porto Alegre → Brasília for 19 kg of cheese is not a real transfer.

## 6. Rules first, agent on top
**Decision:** a deterministic engine proposes an action for every flagged item; a **tool-calling
agent** (Foundation Model API) reviews the highest-value items, *checks facts with tools* (position,
nearby donors, supplier history) and confirms or changes the action with a rationale.
**Why:** auditable baseline for all items; LLM effort where money is concentrated. The loop rejects
a decision made in the same turn as fact-finding (not grounded) or with missing fields.
**Trade-off:** LLM cost/latency (~13 s/item) limited to the top items; the rest get a rule-based
rationale that is **labelled as rule-based** in the UI.

## 7. Serving — Lakebase with two schemas
**Decision:** `serving` (published by the job, replaced **atomically** in one transaction) and
`app` (approvals and Genie turns, **never dropped**). The job mints its own short-lived credential;
the app uses a cached credential and a small connection pool.
**Why:** operational reads/writes at Postgres latency, decoupled from the analytics warehouse;
decisions survive daily refreshes.
**Alternative considered:** Lakebase synced tables (managed UC → Postgres sync). We chose an explicit
publish step to control atomicity and to derive the journey-status table in the same transaction.
The pure-Python `pg8000` driver replaced `psycopg2-binary` in the job after one native SIGABRT.

## 8. Orchestration — one job, daily
**Decision:** `fe_bar_varejo_e2e`: raw data → Lakeflow pipeline (full refresh) → model → agent →
Lakebase, scheduled daily at 06:00 America/Sao_Paulo. The generator always closes on yesterday.
**Why:** "integrated, not stitched" means one run id from raw to decision.

## 9. Genie — curated, not just pointed at tables
**Decision:** entity matching on store/product/supplier names, metric definitions ("items at risk"
= the action queue), 5 certified example SQLs, and "today" = the latest data date, never
`current_date()`.
**Why:** the first version answered "items at risk" with the wrong table.

## 10. Correction — the first build's "blocked registries" premise was false
The first version of this document justified a build-free CDN React frontend and remote-only Python
by saying npm and PyPI were blocked. That was a misdiagnosis: the public registries are blocked, but
the environment is configured for Databricks proxies (`npm-proxy.cloud.databricks.com`,
`pypi-proxy.cloud.databricks.com`) that work. v2 uses the proper stack: React 18 + Vite + TypeScript
+ Tailwind, built locally.

## 11. App — same product family as the War Room
**Decision:** the app is the *Centro de Abastecimento*, the "Logística & Estoque" center of the
LojaBR operations product, built as a separate app in the same visual language (zinc/amber,
Inter/JetBrains Mono, animated backdrop, Genie drawer). The map is an SVG of Brazil projected with
`d3-geo` (no tile provider or API key).
**Why:** customers judge credibility in seconds; a generic dashboard reads as a template.
