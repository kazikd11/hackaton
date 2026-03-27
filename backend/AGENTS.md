# Backend Workspace

## Goal
- Build a FastAPI backend with an ETL/cache layer, analytics layer, and API layer for the Process-to-Automation Copilot prototype.

## Boundary
- `backend/etl` is owned by Agent 1.
- `backend/api` is owned by Agent 2.
- `backend/analytics` is shared, but file naming must avoid collisions:
  - Agent 1 owns files prefixed `prep_`, `derive_`, `extract_`
  - Agent 2 owns files prefixed `score_`, `workflow_`, `explain_`

## Technical Defaults
- Python 3.11
- FastAPI for HTTP API
- Cached analytics under `.cache/analytics`
- Event-log-first processing with safe handling for large CSV cells

## Required Behaviors
- Ingest raw CSVs without exploding on large text fields.
- Preserve named process families and map empty names to `Unassigned/Other`.
- Support both fixture-backed and live-backed API behavior.
- Keep LLM use optional and behind clean boundaries.

## Coordination Notes
- If analytics code needs a shared helper, create a small utility module and note ownership in the file header.
- Avoid editing the same analytics file from two agents at once.

