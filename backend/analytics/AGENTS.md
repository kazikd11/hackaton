# Analytics Layer

## Shared Zone
- This directory is intentionally shared between Agent 1 and Agent 2.
- Split ownership by filename prefix:
  - Agent 1: `prep_`, `derive_`, `extract_`
  - Agent 2: `score_`, `workflow_`, `explain_`

## Responsibilities
- Agent 1 prepares reusable metrics and process structures.
- Agent 2 turns those metrics into opportunity scores, workflow definitions, and explanation payloads.

## Stability Rules
- Prefer pure functions over framework-specific code here.
- Keep public return shapes close to the contract models in `shared/contracts`.
- If a helper becomes shared by both agents, put a short ownership note at the top of the file.

## Core Formula
- The fixed opportunity score is:
- `score = 0.30*manual_effort + 0.25*time_cost + 0.20*handoff + 0.15*repetition + 0.10*variance - 0.10*coverage_penalty`
- Normalize components per process family.

