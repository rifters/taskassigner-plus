# Sprint 002 Blueprint — Page Workflow Implementation Plan

## Delivery Shape

- Keep backend architecture intact.
- Add server-rendered pages/templates and role-aware handlers over existing service/API behavior.
- Only add data model fields/tables if needed for notes + on-behalf reason persistence/auditability.

---

## Workstreams

### A) Manager pages

- Add/update manager routes + templates for:
  - weekly generation trigger,
  - draft review grid,
  - edit/save action,
  - post action,
  - completion review table.
- Completion table columns should include:
  - task,
  - assignee,
  - completed status,
  - completed-by actor,
  - completion source (`crew_self` / `manager_on_behalf`),
  - reason (when on-behalf).

### B) Crew pages

- Task list page for current week assignments.
- Task action for:
  - self-complete,
  - assignment-note submission (general),
  - incomplete-note submission.
- Enforce write-once note semantics:
  - first submission persists,
  - subsequent edit attempts rejected.
- Add 4-week history view section:
  - task/date/status/completed-by.

### C) On-behalf completion flow

- Add manager action endpoint/handler for marking completion on behalf.
- Require non-empty reason.
- Persist reason with completion event or linked audit payload.
- Ensure manager action does not overwrite original crew actor identity semantics incorrectly.

### D) Owner pages

- Ensure owner report pages are functional and read-only.
- Display weekly summary data already exposed by owner reporting logic.

### E) Scheduler operator workflow

- Ensure schedule config/read routes are reachable through manager UI or clearly linked operator page.
- Confirm docs and in-app hints reference scheduled runner script for deployment operations.

---

## Data/Model Notes

- If existing completion schema lacks explicit source/reason fields, add bounded migration-compatible fields.
- For notes:
  - prefer immutable records associated to assignment item + actor + timestamp,
  - or immutable field with first-write lock; choose simplest robust path.

---

## Security and Integrity

- Role checks:
  - crew can only affect own tasks,
  - manager can perform on-behalf completion,
  - owner remains read-only.
- CSRF on all state-changing form routes.
- Input validation:
  - non-empty manager reason for on-behalf completion,
  - note length cap,
  - server-side enforcement regardless of UI behavior.

---

## Test Plan (Builder execution order)

1. Add/adjust tests for on-behalf completion with reason required.
2. Add tests for write-once note behavior.
3. Add tests for 4-week history filtering window.
4. Add page-level authz tests (crew/manager/owner boundaries).
5. Run full suite and capture updated evidence.

---

## Suggested Build Order

1. Model/route support for on-behalf completion reason and note write-once.
2. Manager completion workflow page.
3. Crew pages (current tasks + history + note submission).
4. Owner read-only pages verification.
5. Scheduler config/run operator wiring in UI/docs.
6. Acceptance validation + briefing refresh.
