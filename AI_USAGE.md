# How this was built with AI (force multiplier)

This build was produced with **Claude Code** (Claude Opus) driving Databricks end to end, using
a **harness-engineering** workflow — AI as a teammate with explicit roles, not a one-shot prompt.

## Roles
- **Planner:** the spec was expanded into an approved, testable plan (`PLAN.md`) *before* any
  code — deliverables, sprint acceptance criteria, isolation rules, and trade-offs agreed up front.
- **Generator:** Claude wrote every artifact — the synthetic-data notebook, the Lakeflow
  pipeline, the ML + GenAI notebook, the Lakebase loader, the Genie driver, and the FastAPI +
  React app — and executed them on Databricks serverless.
- **Evaluator:** a dedicated **browser agent (Chrome DevTools)** exercised the app like a user.
  It caught a real rendering bug (React error #62 — a `style` string where React needs an
  object) that static review would have missed; it was fixed and re-validated clean.

## Patterns that made AI effective here
- **Communication by artifact:** `PLAN.md` (the contract), `project_fe_bar_varejo_state.md`
  (running state + resource IDs + gotchas), and the `evidence/*.md` files are how each stage
  hands off to the next — auditable and resumable across sessions.
- **Execution evidence as text:** everything was run on Databricks and the *output* committed
  (row counts, model metrics, query results, real Genie SQL, live API responses) — never
  screenshots — so the result is verifiable.
- **Tight debug loops:** each failed run was diagnosed from the actual error and fixed in one
  focused edit (examples below), not by guessing.

## Real problems AI diagnosed and fixed (documented honestly)
| Symptom | Root cause | Fix |
|---|---|---|
| `CREATE CATALOG` denied | no metastore privilege + Default Storage | isolated schemas in existing catalog |
| `No module named mlflow` on serverless job | minimal job env | `%pip install` in-notebook |
| `log_model` skops error | mlflow blocks HistGradientBoosting via skops | `serialization_format="cloudpickle"` |
| Genie `content` = list | Claude returns content blocks | join block texts |
| FMAPI `temperature not supported` | claude-sonnet-5 constraint | drop the param |
| App blank / React #62 | `style` passed as string to htm/React | CSS-string→object helper |
| pypi + npm blocked | environment egress policy | serverless notebooks + CDN React (build-free) |

## Tooling
- **Claude Code** (Opus) as the build agent; Databricks CLI + REST for pipelines, jobs, Genie,
  Lakebase, apps, permissions.
- **Foundation Model API** (`databricks-claude-sonnet-5`) *inside the product* for reorder
  rationale — AI is both how it was built and part of what it does.
- Sub-agents for isolation: a **web-devloop-tester** (Playwright/Chrome DevTools) for the UI
  evaluation pass.

The conversation ID for this build can be supplied on the submission form if requested.
