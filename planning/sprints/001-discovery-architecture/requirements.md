# Sprint 001 Requirements — Discovery / Architecture to Builder-ready MVP Scope

## Sprint Goal

Define and constrain the first implementation sprint so a Builder can execute without re-defining product scope.

---

## In Scope (must be implemented in first build sprint)

### 1) Role-based access and auth

- Invite-only user lifecycle (manager creates/manages users).
- Crew PIN auth flow.
- Password auth flow for shift lead/manager/owner.
- Session TTL policies by role.
- Lockout behavior after failed auth attempts.
- Reset flows: manager resets crew PIN; email reset for privileged password users.

### 2) Core assignment lifecycle

- Weekly draft generation per job code.
- Draft review with fairness spread/task count visibility.
- Manual draft edits with optional reason capture.
- Explicit post action to publish assignments.
- Crew personal task view and completion action (timestamped).
- Manager completion confirmation workflow.

### 3) Management data setup + maintenance

- People, job codes, task templates CRUD.
- Bulk import for people/job codes/task templates from:
  - CSV, and
  - plain text list.
- Plain-text parser supports:
  - `value`
  - `value|jobcode` where mapping applies.
- Post-import manual maintenance: add/edit/delete single records.
- Task/template requires responsible job code in all create/import paths.

### 4) Reporting + auditability

- Person-centric reporting: assigned/completed/completion %/frequency.
- Task-centric reporting: who gets each task, per-task completion %, consistency trends.
- Filter/drill-down by date range, week, job code, person, task.
- Audit log for sensitive actions (pool changes, draft edits, key auth/admin actions).

### 5) Owner reporting channel

- Read-only owner report views.
- Automated weekly owner summary email.

### 6) Operational baseline

- Structured logs.
- Auth/audit logs.
- Daily SQLite backup routine.
- Uptime + error alerting baseline.

---

## Explicitly Out of Scope (for this first build sprint)

- Altametrics schedule import (PDF parsing/ETL)
- Task weight scoring behavior in assignment algorithm
- Multi-location tenancy behavior
- Native mobile app
- Slack/Teams integrations
- Predictive ML analytics
- Push notifications

---

## Non-functional Requirements (minimum)

- Server-side authorization on all privileged endpoints.
- CSRF protections on state-changing forms.
- Rate limiting on auth endpoints.
- Safe handling/redaction of sensitive logs.
- Reasonable pagination/indexing on report/audit views.
