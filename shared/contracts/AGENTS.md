# Shared Contracts

## Owner
- Agent 2 owns this directory.

## Goal
- Freeze public data shapes early so the frontend can move without backend churn.

## Required Artifacts
- Contract definitions for:
  - `ProcessOverview`
  - `VariantSummary`
  - `StepInsight`
  - `AutomationOpportunity`
  - `WorkflowDefinition`
  - `CopilotExplanation`
- Example JSON payloads for each major route

## Rules
- Prefer additive changes over breaking changes.
- If a field is optional, say why.
- Keep naming consistent across fixture and live modes.

