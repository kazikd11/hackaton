# Process-to-Automation Copilot

## Mission
- Build a local-laptop-first prototype that turns process-mining evidence into ranked automation opportunities and a demo-ready workflow definition.
- Use the provided challenge assets in place. Do not move, rename, or modify files under `Process-to-Automation Copilot Challenge/`.

## Source Of Truth
- Repo root: `C:\Users\kazik\Desktop\hackaton`
- Dataset root: `C:\Users\kazik\Desktop\hackaton\Process-to-Automation Copilot Challenge\Dataset`
- Brief PDF: `C:\Users\kazik\Desktop\hackaton\Process-to-Automation Copilot Challenge\Wyzwanie Process to Automation Copilot.pdf`
- Event logs are the primary truth for process behavior.
- BPMN and PDD are enrichment and validation inputs, not execution truth.

## Working Model
- This repo is prepared for three parallel agents.
- Agents do not share live memory. Keep interfaces explicit.
- Work fixture-first. Frontend should not block on live ETL.
- Report updates in this format:
  - `Done`
  - `Next`
  - `Blocked`
  - `Contract changes`

## Ownership
- Agent 1: `backend/etl`, metric-prep files in `backend/analytics`, `shared/fixtures`, `docs/data-decisions.md`
- Agent 2: `backend/api`, scoring/workflow files in `backend/analytics`, `shared/contracts`, `docs/score-formula.md`
- Agent 3: `frontend`, `docs/demo-script.md`

## Shared Rules
- Do not overwrite or revert another agent's work.
- If a shared interface changes, update the contract docs and note the change explicitly.
- Keep environment variables configurable:
  - `DATASET_DIR`
  - `CACHE_DIR`
  - `APP_MODE`
  - `OPENAI_API_KEY`
  - `OPENAI_MODEL`
- Support both `fixture` and `live` modes.

## Product Requirements
- Show named process families plus `Unassigned/Other`.
- Surface variants, bottlenecks, context switching, copy-paste signals, and manual effort.
- Rank automation opportunities with visible score components.
- Generate a simplified workflow definition.
- Keep one clear guided demo path while preserving exploration.

## Contracts To Preserve
- `ProcessOverview`
- `VariantSummary`
- `StepInsight`
- `AutomationOpportunity`
- `WorkflowDefinition`
- `CopilotExplanation`

## Required Endpoints
- `GET /overview`
- `GET /processes`
- `GET /processes/{id}/variants`
- `GET /processes/{id}/graph`
- `GET /processes/{id}/steps`
- `GET /opportunities`
- `POST /workflow/generate`
- `POST /copilot/explain`

