# Agent 3: Frontend And Demo Experience

## Your Scope
- You own this directory.
- You own `docs/demo-script.md`.

## Objective
- Build a custom, judge-friendly web app that works first with fixtures and then with the live API.

## Routes
- `/`
- `/processes/:id`
- `/opportunities/:id`
- `/workflow/:id`

## UI Priorities
- Keep one guided story obvious.
- Preserve explorer behavior for filters and drill-down.
- Avoid generic dashboard-card sprawl.
- Favor strong typography, restrained color, and clear information hierarchy.
- Keep the product understandable in under five minutes.

## Required Sections
- Overview KPIs and top process cards
- Process graph plus variant table
- Bottleneck, context-switch, and copy-paste evidence
- Ranked automation opportunities with score breakdown
- Workflow export viewer with JSON or YAML copy and diagram preview

## Build Strategy
- Start against `shared/fixtures`.
- Move to live API only after shared contracts are frozen.
- Maintain a reliable fixture-mode fallback for demo backup.

