# Automation Opportunity Score Formula

## Overview

Each automation opportunity is scored using a fixed weighted formula that combines six signal components. The score ranges from 0 to 1, where higher scores indicate stronger automation candidates.

## Formula

```
score = 0.30 × manual_effort
      + 0.25 × time_cost
      + 0.20 × handoff
      + 0.15 × repetition
      + 0.10 × variance
      - 0.10 × coverage_penalty
```

## Component Definitions

| Component | Weight | Source Signals | Interpretation |
|---|---|---|---|
| **manual_effort** | +0.30 | Active duration ratio, click density, text entry count | How much human manual work is involved. High click/text rates indicate manual labor. |
| **time_cost** | +0.25 | Total process time, active hours consumed | Total organizational time investment. Log-scaled for large values. |
| **handoff** | +0.20 | App transitions per case, user switches | Cross-system and cross-person handoffs. High rates indicate fragmented workflows. |
| **repetition** | +0.15 | Copy-paste density, variant concentration | How repetitive and predictable the process is. High copy-paste = structured repetition. |
| **variance** | +0.10 | Number of distinct variants | Process complexity and unpredictability. Many variants = complex decision-making. |
| **coverage_penalty** | -0.10 | Measured users / expected users | Penalty for low observation coverage. Less data = less confidence in the score. |

## Normalization

Each component is normalized to [0, 1] using **min-max scaling** within the process family:

```
normalized_value = (value - min) / (max - min)
```

If all values within a family are equal (only one item, or all items identical), the normalized value defaults to **0.5**.

This ensures that scores are comparable within a family but reflect relative positioning, not absolute thresholds.

## Recommendation Classification

After scoring, each opportunity is classified into a recommendation type. The rules are evaluated in priority order:

| Recommendation | Conditions | Rationale |
|---|---|---|
| **RPA/Integration** | `score ≥ 0.70` AND `repetition ≥ 0.60` AND `manual_effort ≥ 0.50` | Structured, repetitive tasks with high manual effort → automate with bots or direct integrations |
| **Workflow automation** | `score ≥ 0.50` AND `handoff ≥ 0.50` | Cross-system flows with significant handoffs → orchestrate end-to-end |
| **Assistive copilot** | `score ≥ 0.40` AND `variance ≥ 0.50` | Complex knowledge work with high variability → augment humans with AI assistance |
| **Monitor only** | All others | Low score or no dominant signal → observe and reassess |

## Examples

### High score: Sharepoint Copy-Paste (0.82)
- `manual_effort=0.85, time_cost=0.70, handoff=0.90, repetition=0.92, variance=0.35, penalty=0.12`
- Classification: **RPA/Integration** (score ≥ 0.70, repetition ≥ 0.60, manual_effort ≥ 0.50)

### Medium score: Email Composition (0.68)
- `manual_effort=0.78, time_cost=0.62, handoff=0.65, repetition=0.58, variance=0.50, penalty=0.15`
- Classification: **Assistive copilot** (score ≥ 0.40, variance ≥ 0.50)

### Low score: Support Tickets (0.32)
- `manual_effort=0.40, time_cost=0.25, handoff=0.35, repetition=0.50, variance=0.20, penalty=0.30`
- Classification: **Monitor only** (no conditions met)
