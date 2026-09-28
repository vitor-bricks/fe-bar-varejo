# How this was built with AI

Built with **Claude Code** driving Databricks end to end (CLI + REST + notebooks on serverless),
under a harness-engineering workflow: explicit roles, a written contract, and evaluation that
*runs* the product instead of only reading the code.

## Roles
- **Planner** (AI + the FE): the brief was expanded into a plan with testable "done" criteria
  (`PLAN.md`, then `PLAN_v2.md`) and approved before any build.
- **Generator** (AI): wrote and ran every artifact: data simulation, Lakeflow pipeline, model,
  agent, Lakebase publish, Genie configuration, app backend and frontend, orchestration job.
- **Evaluator** (a separate browser agent): drove the app like a user, clicking approve, opening
  the Genie drawer, reading the console, and compared screenshots with the reference app.

## What went wrong in v1, and what changed
The first version passed its own checks and was still rejected by the FE: *"this app is
shameful; the base app I gave you is extremely praised."* An honest post-mortem (`REVIEW.md`, 18
issues) found:
- the reference app had been treated as "do not touch" and **never studied**;
- the evaluator was asked *"does it render?"* instead of *"is it as good as the reference?"*;
- a wrong network diagnosis (public registries blocked ⇒ assumed no npm/PyPI) pushed the build
  onto a CDN shortcut, although Databricks proxies were available;
- the model "predicted the present" (items already empty), and half the assortment was flagged.

**Harness changes for v2:** study the reference first (read-only local viewer that proxies only
GET requests, full-page captures, design tokens and Tailwind classes extracted from its bundle);
fix credibility at the data/ML root, not in the UI; the evaluator scores **side by side** against
the reference, is told to list raw problems by severity, and is not allowed to rationalize them away.

## Bugs caught by running things (not by reading code)
| Symptom | Root cause | Fix |
|---|---|---|
| Agent `KeyError: 'rationale'` | Claude issued parallel tool calls, deciding before seeing results | loop rejects premature/incomplete decisions and asks again |
| Agent rationales full of `FOR-SAZ`, `pedido_a_caminho_un=0` | tools returned codes/field names | tools return human names; prompt forbids codes |
| Transfers Porto Alegre → Brasília | donor search ignored distance | haversine ≤ 450 km, ETA by distance |
| "Urgent order" while an order was in transit | engine lacked an expedite option | new `EXPEDITE` action |
| Scoring believed nothing was inbound today | open orders absent from received-PO history | score with real open orders |
| Lakebase job SIGABRT once | native `psycopg2-binary` in the job runtime | pure-Python `pg8000` |
| App reads 1.3 s each | new TLS connection per query | pooled, autocommit connections (~1 round trip) |
| Genie "items at risk" = 5,000 | pointed at the wrong table; used `current_date()` | metric definitions + certified SQL + "today = max date" |
| Numbers looked stale (data ended 4 days ago) | fixed end date | generator closes on yesterday; job scheduled daily |

## AI inside the product
- A **tool-calling agent** on the Foundation Model API (`databricks-claude-sonnet-5`) reviews the
  highest-value actions, verifies facts with tools, and writes the rationale managers read.
- **Genie** answers business questions in Portuguese over governed tables; every turn is logged
  in Lakebase.

The conversation ID for this build can be provided on the submission form if requested.
