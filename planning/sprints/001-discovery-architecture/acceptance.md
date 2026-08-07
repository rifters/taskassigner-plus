# Sprint 001 Acceptance Criteria — Builder Checkable

Sprint is complete only when all items pass.

---

## A. Access/Auth

- [ ] Invite-only flow exists (no public signup route).
- [ ] Crew can authenticate via PIN and view only own tasks.
- [ ] Shift lead/manager/owner password auth works.
- [ ] Failed auth lockout triggers after configured threshold.
- [ ] Session expiry matches role policy.
- [ ] Reset flows work per role policy.

## B. Data Management + Import

- [ ] Manager can CRUD people/job codes/task templates.
- [ ] CSV imports work for people/job codes/task templates.
- [ ] Plain-text imports accept `value` and optional `value|jobcode` where relevant.
- [ ] Import validation reports line-level failures.
- [ ] Imported records are editable/deletable/addable afterward.
- [ ] Task templates cannot exist without responsible job code.

## C. Assignment Lifecycle

- [ ] Weekly draft generation works by job code.
- [ ] Draft review shows fairness/task distribution.
- [ ] Manual edits save and are auditable.
- [ ] Post action publishes assignments to crew-facing views.

## D. Completion Flow

- [ ] Crew completion action stores timestamp.
- [ ] Manager confirmation state is separate and persisted.
- [ ] Unauthorized users cannot alter others' completion states.

## E. Reporting + Audit

- [ ] Person-centric report metrics are available.
- [ ] Task-centric report metrics are available (distribution, completion %, consistency trend).
- [ ] Report filters/drill-down (week/job code/person/task) work.
- [ ] Audit log captures sensitive actions with actor + timestamp + action context.

## F. Owner Outcomes

- [ ] Owner read-only report views work.
- [ ] Weekly owner summary email can be generated/sent by configured schedule/trigger.

## G. Operational + Security Baseline

- [ ] Structured logs implemented without leaking sensitive secrets.
- [ ] Rate limiting present on auth endpoints.
- [ ] CSRF protection on state changes.
- [ ] Daily SQLite backup routine documented and testable.
- [ ] Basic uptime/error alert path documented and testable.

## H. Scope Guard

- [ ] No schedule-import implementation beyond placeholder notes.
- [ ] No task-weight scoring behavior implemented.
- [ ] No multi-location implementation.
