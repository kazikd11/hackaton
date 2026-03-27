# Shared Assets

## Purpose
- This area holds the pieces every agent depends on.

## Ownership
- Agent 2 owns `shared/contracts`.
- Agent 1 owns `shared/fixtures`.

## Rules
- Keep shared files small, explicit, and versionable.
- If contracts change, fixtures must be updated in the same cycle or marked stale.
- Example payloads should be realistic and derived from the actual challenge data.

