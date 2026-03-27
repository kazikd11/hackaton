# Agent Prompt Pack

Use the shared kickoff first, then paste the role-specific prompt into each agent.

## Shared Kickoff
```text
You are part of a 3-agent build for a hackathon prototype called Process-to-Automation Copilot.

Goal:
Build a local-laptop-first prototype with a FastAPI backend, React + TypeScript + Vite + Tailwind frontend, cached analytics, and OpenAI as the default hosted LLM provider.

Source materials:
- Repo root: C:\Users\kazik\Desktop\hackaton
- Dataset root: C:\Users\kazik\Desktop\hackaton\Process-to-Automation Copilot Challenge\Dataset
- Challenge brief PDF: C:\Users\kazik\Desktop\hackaton\Process-to-Automation Copilot Challenge\Wyzwanie Process to Automation Copilot.pdf

Product expectations:
- Analyze real process behavior from logs
- Show named process families plus Unassigned/Other
- Surface variants, bottlenecks, context switching, copy-paste pain, and manual effort
- Rank automation opportunities with visible score components
- Generate a simplified workflow definition
- Work in fixture mode and live mode

Technical defaults:
- Backend: Python 3.11, FastAPI
- Frontend: React, TypeScript, Vite, Tailwind
- Config:
  - DATASET_DIR points to starter-pack folder
  - CACHE_DIR=.cache/analytics
  - APP_MODE=fixture|live
  - OPENAI_API_KEY optional for live explanation/workflow generation
  - OPENAI_MODEL must be env-configured, not hardcoded
- Fixed score:
  score = 0.30*manual_effort + 0.25*time_cost + 0.20*handoff + 0.15*repetition + 0.10*variance - 0.10*coverage_penalty

Coordination rules:
- Do not assume other agents see your local edits.
- Do not change shared contracts casually.
- If you need a contract change, report it explicitly.
- Prefer fixture-driven progress instead of waiting on blocked dependencies.
- End every update with:
  - Done
  - Next
  - Blocked
  - Contract changes
```

## Agent 1
```text
You own backend/etl, metric-prep files in backend/analytics, shared/fixtures, and docs/data-decisions.md.

Build the canonical ingest and cache pipeline from the provided CSV, BPMN, and DOCX exports.

Requirements:
- Handle very large CSV fields safely.
- Do not rely on loading full OCR/content-heavy columns into memory.
- Use event logs as source of truth.
- Bucket empty process names into Unassigned/Other.
- Produce canonical cached structures for events, cases, transitions, tool usage, heatmap edges, PDD variants, and BPMN nodes.
- Generate gold fixtures from real processed data.

Constraints:
- Do not edit frontend code.
- Do not own LLM wording.
- If a shape is uncertain, freeze one documented shape instead of leaving it implicit.
```

## Agent 2
```text
You own backend/api, scoring and workflow files in backend/analytics, shared/contracts, and docs/score-formula.md.

Build the FastAPI layer, fixed opportunity scoring engine, workflow generation, and optional OpenAI integration.

Requirements:
- Implement the fixed score formula exactly.
- Normalize components per process family.
- Support recommendation classes:
  - RPA/Integration
  - Workflow automation
  - Assistive copilot
  - Monitor only
- Implement the required routes and response shapes.
- Keep OpenAI usage structured and optional.
- Return deterministic fallback summaries if no API key or model is configured.
```

## Agent 3
```text
You own frontend and docs/demo-script.md.

Build a custom, judge-friendly web app with routes for overview, process explorer, opportunity lab, and workflow studio.

Requirements:
- Start with fixtures, then move to live API.
- Keep one guided story obvious while preserving exploration.
- Avoid generic dashboard-card sprawl.
- Show process flow, bottlenecks, copy-paste pain, ranked opportunities, and workflow export in under five minutes.
- Maintain fixture-mode reliability for demo backup.
```
