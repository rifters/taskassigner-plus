# Builder Handoff Prompt — Sprint 004 Manager Demo Foundation

You are the Builder for TaskAssigner+ Sprint 004.

## Mission

Build the manager-first working browser demo from the sprint requirements. The completed path must be: login as `demo-manager` → reset/load sample data → maintain job codes, people, and task templates → generate/review/edit/post a weekly assignment set.

## Required Read Order

1. `templates/method/120x-agent-identity.md`
2. `AGENTS.md`
3. `planning/STATE.md`
4. `planning/DECISIONS.md`
5. `planning/DOMAIN.md`
6. `planning/RISKS.md`
7. `planning/QUESTIONS.md`
8. `planning/sprints/004-manager-demo-foundation/requirements.md`
9. `planning/sprints/004-manager-demo-foundation/blueprint.md`
10. `planning/sprints/004-manager-demo-foundation/acceptance.md`

## Execution Rules

- Apply Architect Pack 004 with dry-run, then apply.
- Implement only from the generated Sprint 004 files.
- Stop at the mandatory Builder code gate and present a file-by-file implementation plan before source/test edits.
- Preserve existing JSON contracts and role guards.
- Do not broaden scope to deferred roles or integrations.

## Validation Expectations

- Run focused Sprint 004 tests.
- Run the full test suite.
- Verify the browser demo path with a local seeded database.
- Report SQLAlchemy warnings separately from pass/fail results.

## Closeout Requirements

- Update `planning/ARCHITECT_BRIEFING.md` with actual demo-path evidence.
- Synchronize `planning/STATE.md`, `planning/STATUS.json`, and acceptance results.
- Record durable decisions and remaining risks.
