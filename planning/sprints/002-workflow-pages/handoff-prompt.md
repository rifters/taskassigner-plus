# Builder Handoff Prompt — Sprint 002 Workflow Pages

You are the Builder for TaskAssigner+.

Read these files first, in order:
1. `planning/ARCHITECT_BRIEFING.md`
2. `planning/STATE.md`
3. `planning/DECISIONS.md`
4. `planning/DOMAIN.md`
5. `planning/RISKS.md`
6. `planning/sprints/002-workflow-pages/requirements.md`
7. `planning/sprints/002-workflow-pages/blueprint.md`
8. `planning/sprints/002-workflow-pages/acceptance.md`
9. `docs/ARCHITECTURE.md`
10. `docs/API.md`
11. `docs/VALIDATION.md`

## Mission

Deliver daily-usable manager, crew, and owner page workflows over existing Sprint 001 backend/API capabilities, including immutable crew assignment notes (general and incomplete-context) and manager on-behalf completion with mandatory reason.

## Non-negotiable constraints

- Do not add out-of-scope features.
- Preserve strict server-side authorization and CSRF protections.
- Enforce write-once crew notes.
- Enforce mandatory reason for manager on-behalf completion.
- Preserve clear audit trail for sensitive completion actions.
- Keep scope guard: no schedule import, no weighting behavior, no multi-location.

## Deliverables

- Manager workflow pages for week generation/review/edit/post/completion operations.
- Crew pages for task actions + 4-week history.
- Owner read-only report pages verified.
- On-behalf completion path with required reason + auditability.
- Scheduler config/read usability path and ops script visibility in docs/UI.
- Updated tests and acceptance evidence.

## Mandatory code gate

Before editing source/test files, stop and provide:
- exact file-by-file plan,
- explicit scope guard (what will not be changed),
- acceptance mapping.

Wait for explicit human approval before writing code.

## Done criteria

All checkboxes in `planning/sprints/002-workflow-pages/acceptance.md` pass.

## Validation discipline

- Add/adjust tests for:
  - on-behalf completion reason required,
  - write-once notes,
  - 4-week history bound,
  - page-level authz boundaries.
- Run full test suite before close.
- Refresh `planning/ARCHITECT_BRIEFING.md` and `planning/STATE.md` at sprint close.
