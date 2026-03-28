# Demo Script

## Goal
- Land the prototype in under five minutes.
- Keep one guided path obvious while leaving room for judges to explore.
- Use fixture mode as the reliable fallback if the live API or LLM endpoints are unavailable.

## Setup
- Start the frontend with `npm run dev` from `frontend/`.
- If the backend is ready, set `APP_MODE=live` and point `API_BASE_URL` or `VITE_API_BASE_URL` to the FastAPI host.
- If the backend is missing or unstable, stay in fixture mode and present the same story.

## Guided Story
1. Open `/`.
   - Frame the product as a bridge from process-mining evidence to ranked automation ideas and a workflow draft.
   - Call out the measured-user coverage and the visible `Unassigned / Other` bucket to show the app does not hide uncertainty.
   - Explain why `Communication` is the default path: repetitive status chasing, strong context switching, and obvious copy-heavy drafting.
2. Open `/processes/communication`.
   - Use the graph to show the observed path.
   - Point at `Gather latest engineer note` as the bottleneck and `Draft reply in Teams or Outlook` as the strongest copy signal.
   - Use the variant panel to show that the path is stable enough for automation, but still contains an exception loop.
3. Open `/opportunities/opp-comm-sharepoint`.
   - Explain the fixed score formula and show the visible score components.
   - Emphasize that the recommendation is `Workflow automation`, not a black-box full auto reply.
   - Walk through the evidence tiles so the ranking feels grounded in the mined behavior.
4. Open `/workflow/opp-comm-sharepoint`.
   - Show the generated workflow, especially the explicit evidence check and human-review branch.
   - Copy the JSON or YAML export to demonstrate handoff readiness.
   - Close by saying the product keeps the same path available in fixture mode for demo backup.

## Optional Explorer Branches
- Open `/processes/production` to show a more integration-heavy path around Youtrack progress sync.
- Open `/opportunities/review-brief-copilot` to contrast workflow automation with an assistive copilot recommendation.
- Open `/workflow/opp-youtrack-triage` if judges want to see a connector-style export instead of a triage flow.

## Demo Notes
- The UI is intentionally opinionated: one premium story rail, then deeper evidence.
- Keep the narrative on clarity and trust:
  - real process behavior
  - visible bottlenecks and score components
  - responsible automation with guardrails
- If live endpoints fail mid-demo, refresh in fixture mode and continue without changing the story.
