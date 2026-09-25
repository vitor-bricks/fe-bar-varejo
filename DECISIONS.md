# Decisions & Trade-offs

Why this build looks the way it does — the choices that mattered and the alternatives we
weighed. (Short by design; the goal is to signal *why*, not to narrate every step.)

## 1. Scope: one sharp hero problem, not four equal ones
- **Decision:** anchor everything on **on-shelf availability / stockout** as the hero, with
  demand forecast, markdown and next-best-offer as *connected modules* on the same data journey.
- **Why:** the FE Bar (and buyers) reward a specific, quantified problem. Building "four things
  equally" is the classic *"improve operations"* trap — broad, no crisp value story, and it
  sinks the roleplay because you can't lead with one outcome.
- **Trade-off:** less breadth demoed live now, but a far stronger value narrative (~R$5M/yr
  recoverable) and a clean roadmap for the modules.

## 2. Data: synthetic simulation, not canned rows
- **Decision:** generate the dataset with a **path-dependent inventory simulation** (Poisson
  demand, reorder policy, lead time + supplier delay) rather than random independent rows.
- **Why:** stockouts must *emerge* from the dynamics so the ML model learns genuine signal
  (categories with longer lead times really do rupture more — see the category breakdown). Also
  keeps it 100% synthetic: no customer data, ever.
- **Trade-off:** more generator complexity vs. trivial random data that would give the model
  nothing real to learn.

## 3. Compute: serverless notebooks, not local/Connect
- **Decision:** run all Python on **Databricks serverless** via one-off jobs; frontend is
  **build-free React from a CDN**.
- **Why:** the build environment blocks the pypi and npm registries. Running on serverless
  (Databricks' own mirror) is reliable *and* produces exactly the execution evidence the
  evaluator wants (committed run output). CDN React avoids an npm build entirely.
- **Trade-off:** no local inner-loop and no Vite production bundle; acceptable given the app is
  small and was validated interactively in a browser.

## 4. Governance: new schemas in an existing catalog
- **Decision:** create isolated `fe_bar_varejo_{bronze,silver,gold}` schemas inside the existing
  managed catalog (no new catalog).
- **Why:** the principal lacks `CREATE CATALOG` on the metastore. A new namespace still gives
  full isolation without touching anything pre-existing (esp. the `lojabr-warroom` demo).
- **Trade-off:** shares a catalog, but with clean prefixing and least-privilege grants.

## 5. Transform: Lakeflow Declarative Pipeline (medallion), not a plain notebook
- **Decision:** a declarative pipeline (Auto Loader → bronze → silver → gold) with
  `@dlt.expect` quality rules.
- **Why:** gets governance for free — automatic lineage, data-quality expectations, and managed
  incremental ingestion — which is the whole point of the Lakeflow + Unity Catalog story.
- **Trade-off:** slightly more ceremony than a one-shot notebook, but far stronger governance.

## 6. ML: rank by money, not by probability
- **Decision:** `HistGradientBoostingClassifier` predicting stockout-in-7-days, but the worklist
  is ordered by **expected lost revenue** (risk × 7-day demand × price), not raw probability.
- **Why:** ops teams have finite capacity; prioritizing by R$ at risk targets the highest-value
  actions. Precision@top-100 = 1.0 means the top of the list is trustworthy.
- **Trade-off:** a simple, explainable gradient-boosting model over a heavier deep model —
  faster, reproducible, and enough (AUC 0.86). Time-based split avoids leakage.

## 7. GenAI: turn a score into an action
- **Decision:** use the Foundation Model API (Claude Sonnet) to write a reorder rationale per
  at-risk SKU, grounded in that SKU's own numbers.
- **Why:** a probability doesn't move a store manager; *"estoque zerado, vende 87/dia, dispare X
  unidades"* does. Closes the loop predict → explain → act.
- **Trade-off:** an LLM call per item (batched to the top-N) vs. a static template.

## 8. Serving: Lakebase operational + warehouse analytical
- **Decision:** sync the serving tables to **Lakebase (Postgres)** and have the app read from it,
  with a **per-request fallback to the SQL warehouse** if Lakebase is briefly unavailable.
- **Why:** operational reads (a store's worklist) want low-latency Postgres, decoupled from the
  analytics warehouse that powers Genie and dashboards. The fallback means a transient blip
  never blanks the app.
- **Trade-off:** two data paths to maintain, but resilience + the right tool for each read.

## 9. App: FastAPI + React, least-privilege service principal
- **Decision:** the app's service principal gets only what it needs — a Lakebase Postgres role
  with `SELECT`, warehouse `CAN_USE`, gold `SELECT`, and Genie `CAN_RUN`.
- **Why:** security by default; the app can't do more than read the serving data and run the
  Genie space.
- **Trade-off:** more grants to wire up front vs. broad access.
