# Agent 2: API, Scoring, And Copilot

## Your Scope
- You own this directory.
- You may create scoring and workflow files in `backend/analytics` using the prefixes `score_`, `workflow_`, or `explain_`.
- You own `shared/contracts`.

## Objective
- Build the FastAPI layer, scoring engine, workflow generation, and optional OpenAI integration.

## Required Endpoints
- `GET /overview`
- `GET /processes`
- `GET /processes/{id}/variants`
- `GET /processes/{id}/graph`
- `GET /processes/{id}/steps`
- `GET /opportunities`
- `POST /workflow/generate`
- `POST /copilot/explain`

## Required Response Types
- `ProcessOverview`
- `VariantSummary`
- `StepInsight`
- `AutomationOpportunity`
- `WorkflowDefinition`
- `CopilotExplanation`

## Rules
- Consume fixtures and derived metrics rather than re-deriving raw data in route handlers.
- Keep OpenAI usage structured and optional.
- Never hardcode the model name.
- If LLM access fails or is not configured, return deterministic fallback summaries from the same evidence pack.
- Keep recommendation classes limited to:
  - `RPA/Integration`
  - `Workflow automation`
  - `Assistive copilot`
  - `Monitor only`

## Contract Discipline
- If you change a response shape, update the shared contract docs and example payloads in the same change.
- Avoid ad hoc fields that only one route uses unless they are documented.

