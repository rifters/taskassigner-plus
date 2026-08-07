============================================================
FILE: planning/STATE.md
============================================================
# Project State

**Project:** TaskAssigner+  
**Client:** Rifters / Eric  
**Last updated:** 2026-07-08

---

## Current Phase

Discovery / Architecture complete for Pack 001.

---

## Current Status

- Mandatory Discovery Gate passed (External-facing tier).
- Core business workflow, roles, risks, auth model, and reporting requirements are documented.
- MVP boundaries and explicit out-of-scope items are locked.
- Builder-ready Sprint 001 artifacts are defined under `planning/sprints/001-discovery-architecture/`.
- No application code is included in this pack.

---

## Active Sprint

`planning/sprints/001-discovery-architecture/`

---

## What This Pack Produces

- Durable planning records (`STATE`, `DECISIONS`, `DOMAIN`, `RISKS`, `QUESTIONS`, `FILE_INVENTORY`)
- Builder-ready implementation guidance (`requirements`, `blueprint`, `acceptance`, `handoff-prompt`)
- Durable technical docs (`docs/ARCHITECTURE.md`, `docs/API.md`, `docs/VALIDATION.md`)

---

## Next Actions (after apply)

1. Run pack dry-run from project root:
   - `node scripts/apply-architect-pack.js planning/architect-packs/architect-pack-001-discovery.md --dry-run`
2. Apply pack:
   - `node scripts/apply-architect-pack.js planning/architect-packs/architect-pack-001-discovery.md`
3. Start Builder from `planning/sprints/001-discovery-architecture/handoff-prompt.md`.
4. Build only what is in-scope for this sprint.

---

## Blockers

No blocker for Sprint 001 implementation.

---

## Watch Items

- Keep v1 scope tight (no schedule import, no task-weight engine behavior, no multi-location).
- Maintain role boundaries and auditability requirements on all sensitive flows.
- Preserve future extensibility for task weights/time estimates and tenantization.

============================================================
FILE: planning/DECISIONS.md
============================================================
# Decisions

Record durable decisions future sprints must respect.

---

## Decision Log

| Date | Decision | Reason | Impact |
|---|---|---|---|
| 2026-07-08 | **MVP boundary (smallest useful v1):** manager can generate/review/post assignments; crew can view/complete via QR + PIN; owner receives weekly email summary; no public self-signup. | Fastest path to replace paper workflow and remove manager bottleneck. | Sprint scope stays centered on assignment lifecycle, completion, and reporting. |
| 2026-07-08 | **MVP page inventory approved:** manager/admin pages (`/login`, `/manager`, people, job codes, task templates, weekly generate/draft/post/completions, reports, audit); crew pages (`/crew`, `/crew/tasks`, `/crew/tasks/:id`); shift lead pages (`/lead/board`, `/lead/reassign`); owner read-only pages (`/owner/login`, `/owner/reports`, `/owner/reports/weekly`); shared `/403` + `/404`. | Keeps Builder scope executable and explicit. | Route-level responsibilities and role access must be enforced server-side. |
| 2026-07-08 | **Import UX parity:** people, job codes, and task templates support simple CSV or plain-text import, then normal add/edit/delete. | Fast onboarding and simple day-to-day maintenance. | Builder must implement import + CRUD for all three entities. |
| 2026-07-08 | **Plain-text import format (v1):** line-based input supports `value` and optional `value|jobcode` where mapping is needed. | Lightweight format without a mapping wizard. | Parser + validation rules must be explicit in blueprint/tests. |
| 2026-07-08 | **Task ownership rule:** each task/template requires one responsible job code. | Assignment and reporting integrity. | Reject orphan tasks in import and manual forms. |
| 2026-07-08 | **Reporting depth:** include person-centric and task-centric metrics (who gets each task, per-task completion %, consistency trends). | Need to detect repeat non-completion and distribution patterns. | Reports must support drill-down and filtering by week/job code/person/task. |
| 2026-07-08 | **Auth model:** invite-only lifecycle (manager-administered); no public registration. | External-facing risk posture + controlled workforce context. | Requires manager-admin user management and role-aware auth flows. |
| 2026-07-08 | **Role auth UX:** crew PIN-only; shift lead/manager/owner password auth. | Lower crew friction while protecting privileged roles. | Distinct auth paths/policies by role. |
| 2026-07-08 | **Session policy:** manager/lead 8h, crew 12h, owner 24h read-only; no remember-me in v1. | Balance usability with security. | Explicit TTL/reauth behavior required. |
| 2026-07-08 | **Lockout/reset:** 5 failed attempts => 15-minute lock; manager resets crew PINs; manager/owner email reset for passwords. | Mitigate brute force and preserve recovery. | Requires lockout tracking, reset flows, audit events. |
| 2026-07-08 | **PII scope v1:** name, role, PIN/password hash, optional email (non-crew optional), and minimal audit/activity metadata. | Minimum data needed for operations/accountability. | Enforce redaction, least privilege, and safe logging. |
| 2026-07-08 | **Compliance stance:** internal-policy handling only for now; no formal pre-go-live checkpoint chosen. | Client decision during discovery. | Continue sensitive-data baseline; revisit if formal obligations emerge. |
| 2026-07-08 | **Threat priorities:** PIN brute force, privilege escalation, forged completion events. | Highest practical abuse risks for this workflow. | Security controls/tests prioritize these vectors first. |
| 2026-07-08 | **Rate limiting baseline:** strict auth limits (target 5/min per IP + per account), moderate general API limits. | Protect login surfaces and reduce abuse. | Include limit behavior in architecture/validation. |
| 2026-07-08 | **Tenancy stance:** v1 single-tenant deployment with tenant-ready migration path. | Match immediate needs without overbuilding. | Data model should avoid hard dead-ends for future multi-tenant support. |
| 2026-07-08 | **Scale assumption (12 months):** ~25–80 crew users, ~100–500 assignments/week, <20 concurrent users. | Practical baseline for stack choices. | SQLite acceptable for v1 with indexing + backups + observability. |
| 2026-07-08 | **Observability baseline:** structured app logs, auth/audit logs, daily SQLite backups, uptime checks, manager email alerts. | Minimum reliability for external-facing usage. | Validation must include operational checks and failure paths. |
| 2026-07-08 | **Sprint exclusions:** no schedule import, no task weight scoring behavior, no multi-location in first implementation sprint. | Prevent scope creep. | Keep build focused and deliverable. |

============================================================
FILE: planning/DOMAIN.md
============================================================
# Domain Context

This file captures operating context for TaskAssigner+.

---

## Client

Rifters / Eric

---

## Business Goal

A web-based weekly task assignment system for restaurant teams that fairly distributes tasks across job-code-based crew pools, tracks completion, and reports productivity to management.

---

## Audience / Rigor Tier

External-facing (untrusted users). Security, authorization, abuse prevention, and auditability are first-class requirements.

---

## Primary Users / Roles

- **Crew** — view own weekly assignments; mark complete from phone/browser via QR flow.
- **Shift Lead** — crew capabilities plus board visibility and reassignment actions.
- **Manager (Eric)** — full operational control: users, job codes, templates, constraints, generation, review/edit/post, confirmations, reports.
- **Owner** — read-only reporting dashboard + weekly summary email.

---

## Current Workflow

1. Manager adjusts crew pool manually.
2. Algorithm creates draft.
3. Manager reviews fairness and manually tweaks.
4. Manager posts assignments.
5. Crew completes work; manager tracks manually.
6. Manager prints/signs paper report and hand-delivers to owner.

---

## Target Workflow

1. Manager adjusts crew pools in app.
2. System generates weekly draft by job code using fairness/rotation constraints.
3. Manager reviews fairness/task distribution and applies edits (optionally with reason).
4. Manager posts assignments.
5. Crew accesses tasks via QR/URL and marks complete (timestamped).
6. Manager confirms completions.
7. Manager/owner review person-centric + task-centric consistency reports.
8. Owner receives automated weekly summary email.

---

## Key Terms

- **Job code** — operational crew group (Cooks, Servers, Hosts, SAs, etc.).
- **Crew pool** — eligible users for a generation run.
- **Draft assignment** — generated, editable pre-post state.
- **Posted assignment** — published weekly assignment visible to crew.
- **Fairness spread** — distribution indicator for task balance across eligible crew.
- **Completion confirmation** — manager verification state after crew completion.
- **Task-centric report** — analytics by task: assignment distribution + completion consistency.
- **Audit event** — immutable record for sensitive actions (who/what/when).

---

## Business Rules

- Invite-only user lifecycle for v1 (no public signup).
- Crew uses PIN auth; privileged roles use password auth.
- Lockout: 5 failed attempts => 15-minute lock.
- Manager can reset crew PINs; manager/owner password resets via email flow.
- People, job codes, and task templates support bulk import from CSV or plain text.
- Plain-text import supports `value` and optional `value|jobcode` where mapping applies.
- After import, manager can add/edit/delete single records.
- Every task/template must reference one responsible job code.
- Manual pool adjustments and draft edits must be auditable.
- Draft and posted states are distinct; posting is explicit.
- Completion timestamp is required; manager confirmation is separate.
- v1 is single-tenant with future tenantization path.

---

## Out of Scope (v1 / first implementation sprint)

- Schedule import from Altametrics PDF tables
- Task weighting/difficulty behavior (schema extensibility only)
- Multi-location support
- Native mobile app
- Slack/Teams integrations
- Predictive ML analytics
- Push notifications

---

## Systems / Integrations

- Denny's in-store WiFi (crew LAN access)
- Cloudflare Tunnel (public HTTPS)
- Tailscale (private manager/owner access)
- QR code entry for crew
- SMTP-based weekly owner report email

---

## Deferred / Unknown

- Altametrics currently only provides PDF print tables; no direct CSV export.
- Task weighting direction chosen for future: hybrid (weight + estimated minutes), deferred.
- No formal external compliance framework selected yet; internal-policy handling in effect.

============================================================
FILE: planning/RISKS.md
============================================================
# Risks

Known project risks and mitigation notes.

---

| Risk | Likelihood | Impact | Mitigation | Status |
|---|---:|---:|---|---|
| PIN brute-force against crew auth | Medium | High | Lockouts, strict auth rate limits, failed-attempt auditing, alert thresholds. | Active |
| Privilege escalation / horizontal data access | Medium | High | Server-side role checks on every endpoint, per-role tests, deny-by-default authorization. | Active |
| Forged completion events | Medium | High | Ownership checks, immutable audit records, manager confirmation state, tamper-resistant logs. | Active |
| Public tunnel attack surface | Medium | High | HTTPS only, secure cookie/session settings, CSRF defense, input validation, dependency hygiene. | Active |
| Sensitive data leakage in logs | Low | High | Structured logs with redaction policy, no secrets/PIN/password logs, restricted log access. | Active |
| Scope creep in first build sprint | High | Medium | Enforced in/out-of-scope list, acceptance gates, explicit exclusions. | Active |
| Cold-start fairness quality in week one | Medium | Medium | Mark first-cycle caveat in UI/reporting, allow manager override with audit trail. | Accepted |
| Operational fragility (backup/alerts absent) | Medium | High | Daily backups, restore verification steps, uptime/error alerts to manager. | Active |

============================================================
FILE: planning/QUESTIONS.md
============================================================
# Open Questions

Questions that need answers from Architect/Builder/Client.

---

## Discovery Gate Resolution (2026-07-08)

Mandatory External-facing discovery topics were answered or explicitly deferred with rationale. No blocking discovery gate item remains for Pack 001.

---

## Answered / Deferred Tracking

| Question | Owner | Needed By | Status | Answer / Notes |
|---|---|---|---|---|
| Scheduling source/export for future import? | Client | Before schedule-import sprint | Answered (deferred) | Source is Altametrics; currently only PDF table print output. Import strategy deferred. |
| Future task-weight model direction? | Client + Architect | Before weighting sprint | Answered (deferred) | Hybrid model (manager weight + estimated minutes) chosen for future. |
| Formal compliance obligations beyond internal policy? | Client/Legal | Before production hardening if requirements emerge | Answered (current stance) | Internal-policy handling for now; no formal checkpoint selected at this stage. |

============================================================
FILE: planning/FILE_INVENTORY.md
============================================================
# File Inventory

Source of truth file map for planning + references.

---

## Planning Files

- `planning/STATE.md`
- `planning/DECISIONS.md`
- `planning/DOMAIN.md`
- `planning/RISKS.md`
- `planning/QUESTIONS.md`
- `planning/FILE_INVENTORY.md`
- `planning/sprints/001-discovery-architecture/requirements.md`
- `planning/sprints/001-discovery-architecture/blueprint.md`
- `planning/sprints/001-discovery-architecture/acceptance.md`
- `planning/sprints/001-discovery-architecture/handoff-prompt.md`

## Durable Technical Docs

- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/VALIDATION.md`
- `docs/RIGOR_PROFILE.md`

## Inputs / References

- `planning/INTAKE.md`
- `architect-chat-starter-prompt.md`
- `intake.md`
- `references/README.md`
- Existing source app reference: `F:\projects\taskmate\` (read-only reference)

## Scripts / Method Tools

- `scripts/apply-architect-pack.js`
- `scripts/update-method.js`
- `planning/architect-packs/README.md`

## Reserved Implementation Areas (not authored by this pack)

- `src/`
- `tests/`

============================================================
FILE: planning/sprints/001-discovery-architecture/requirements.md
============================================================
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

============================================================
FILE: planning/sprints/001-discovery-architecture/blueprint.md
============================================================
# Sprint 001 Blueprint — Practical Implementation Plan

## Architecture Shape

- **Backend:** Flask app with Blueprints per domain area.
- **Persistence:** SQLite via Flask-SQLAlchemy.
- **Auth:** Flask-Login + role-aware auth middleware/decorators.
- **Password/PIN hashing:** Flask-Bcrypt.
- **Frontend:** Server-rendered HTML + Vanilla JS for small interactivity.
- **Deployment access:** Cloudflare Tunnel (public HTTPS), Tailscale (private).

---

## Proposed Module Boundaries

- `auth` — login/logout, session/lockout/reset flows.
- `users` — people management, roles, crew PIN admin.
- `job_codes` — job code CRUD and memberships.
- `task_templates` — task CRUD with required responsible job code.
- `imports` — CSV/text parsing + validation + preview/commit.
- `assignments` — generation, draft review/edit, posting.
- `completions` — crew completion capture + manager confirmation.
- `reports` — person-centric and task-centric analytics.
- `audit` — queryable audit timeline.
- `owner` — read-only report surfaces + weekly email job trigger.

---

## Data Model (v1 minimum)

- `users` (id, name, role, email nullable, password_hash nullable, pin_hash nullable, active, timestamps)
- `job_codes` (id, name, active, timestamps)
- `user_job_codes` (user_id, job_code_id)
- `task_templates` (id, title, notes, responsible_job_code_id, weight_nullable, est_minutes_nullable, active)
- `assignment_runs` (id, week_key, status[draft|posted], generated_by, generated_at, posted_by, posted_at)
- `assignment_items` (id, run_id, task_template_id, assignee_user_id, source[generated|manual], edited_by nullable, edited_reason nullable)
- `task_completions` (id, assignment_item_id, completed_by, completed_at, manager_confirmed_by nullable, manager_confirmed_at nullable)
- `audit_events` (id, actor_user_id, action_type, entity_type, entity_id, payload_json, created_at)
- `auth_attempts` (id, identifier, ip_hash_or_token, success, occurred_at)

Notes:
- Keep schema tenant-ready (e.g., optional future `tenant_id` migration path).
- Keep weight/estimated minutes fields nullable for future weighting sprint.

---

## Page/Route Responsibilities (MVP)

### Manager/Admin

- `/login`
- `/manager`
- `/manager/people`
- `/manager/job-codes`
- `/manager/tasks`
- `/manager/imports` (or per-entity import tabs)
- `/manager/weeks/<week>/generate`
- `/manager/weeks/<week>/draft`
- `/manager/weeks/<week>/post`
- `/manager/weeks/<week>/completions`
- `/manager/reports`
- `/manager/audit`

### Crew

- `/crew` (PIN entry / landing)
- `/crew/tasks`
- `/crew/tasks/<assignment_item_id>`

### Shift Lead

- `/lead/board`
- `/lead/reassign`

### Owner

- `/owner/login`
- `/owner/reports`
- `/owner/reports/weekly`

### Shared

- `/403`
- `/404`

---

## Import UX Contract (v1)

- Input methods:
  - CSV upload
  - Plain text paste/upload
- Plain text grammar:
  - `value`
  - `value|jobcode` (when job-code mapping is relevant)
- Validate before commit and show line-level errors.
- No advanced mapping wizard.
- On successful import, records become editable/deletable via normal CRUD pages.
- All import commits write audit events.

---

## Security / Abuse Controls

- Role checks enforced server-side (never UI-only).
- CSRF on all state changes.
- Auth endpoint throttling + lockout handling.
- Session cookie hardening (secure, httponly, samesite appropriate for deployment).
- Input validation and output escaping.
- Minimal sensitive logging; hash or redact where practical.

---

## Reporting Contract (v1)

- Person-centric metrics:
  - assigned count
  - completed count
  - completion %
  - task frequency breakdown
- Task-centric metrics:
  - assignee distribution per task
  - completion % per task
  - consistency trend over selectable window
- Filters:
  - week/date range
  - job code
  - person
  - task

---

## Build Order Recommendation

1. Auth + role guardrails + lockout baseline.
2. People/job code/task template CRUD.
3. Import pipeline + parser + validation + audit.
4. Assignment draft/post lifecycle.
5. Crew completion + manager confirmation.
6. Reports + audit views.
7. Owner views + weekly email.
8. Operational hardening + validation pass.

============================================================
FILE: planning/sprints/001-discovery-architecture/acceptance.md
============================================================
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

============================================================
FILE: planning/sprints/001-discovery-architecture/handoff-prompt.md
============================================================
# Builder Handoff Prompt — Sprint 001 Implementation

You are the Builder for TaskAssigner+.

Read these files first, in order:
1. `planning/STATE.md`
2. `planning/DECISIONS.md`
3. `planning/DOMAIN.md`
4. `planning/RISKS.md`
5. `planning/sprints/001-discovery-architecture/requirements.md`
6. `planning/sprints/001-discovery-architecture/blueprint.md`
7. `planning/sprints/001-discovery-architecture/acceptance.md`
8. `docs/ARCHITECTURE.md`
9. `docs/API.md`
10. `docs/VALIDATION.md`

## Mission

Implement the first production-usable MVP slice exactly within defined scope.

## Non-negotiable constraints

- Do not add out-of-scope features.
- Enforce role authorization server-side for every protected action.
- Keep imports lightweight (CSV/text parser; no mapping wizard).
- Ensure all sensitive operational actions are auditable.
- Preserve extensibility for deferred features (weights/time estimate; tenant path).

## Deliverables

- Working Flask app paths/pages for MVP roles.
- CRUD + import workflows for people/job codes/task templates.
- Assignment draft/review/post lifecycle.
- Crew completion + manager confirmation.
- Person/task reports with required filters.
- Owner read-only reporting + weekly summary email capability.
- Security/operational baseline per requirements.

## Done criteria

All checkboxes in `planning/sprints/001-discovery-architecture/acceptance.md` pass.

## Validation discipline

- Add tests for authz boundaries and abuse-prone endpoints first.
- Validate error paths and invalid import lines.
- Demonstrate report metric correctness with sample fixture data.
- Document anything deferred with explicit rationale.

============================================================
FILE: docs/ARCHITECTURE.md
============================================================
# TaskAssigner+ Architecture (Pack 001)

## 1. System Overview

TaskAssigner+ is a role-based web app for weekly restaurant task assignment, completion capture, and management/owner reporting.

Core principles:
- low-friction crew usage,
- strict server-side role boundaries,
- auditable operational edits,
- practical MVP scope with future extensibility.

## 2. Runtime Stack

- Python 3
- Flask
- Flask-Login
- Flask-SQLAlchemy
- Flask-Bcrypt
- SQLite
- Vanilla JS + HTML/CSS

## 3. Access Topology

- Public HTTPS via Cloudflare Tunnel for workforce access.
- Private remote access via Tailscale for manager/owner.
- Session and auth policies differ by role.

## 4. Domain Components

- Identity/Auth
- Workforce setup (people/job codes/task templates)
- Imports (CSV/plain text)
- Assignment engine workflow (draft/review/post)
- Completion capture/confirmation
- Reporting (person-centric and task-centric)
- Audit trail
- Owner weekly summary delivery

## 5. Security Model (v1)

- Invite-only accounts.
- Crew PIN auth; privileged password auth.
- Lockout/rate limit defenses on auth surfaces.
- CSRF + input validation + output escaping.
- Hardened session cookie settings.
- Least-privilege role checks in server endpoints.

## 6. Data Persistence

SQLite is acceptable for projected v1 scale.

Required supporting practices:
- indexing for hot query paths,
- pagination for report/audit views,
- daily backup routine,
- restore verification procedure.

## 7. Reporting Architecture

Reports must support both:
- **Person-centric** performance summaries,
- **Task-centric** consistency analysis (distribution + completion trends).

This is required for identifying repeated completion gaps by task.

## 8. Extensibility Hooks

- Nullable `weight` and `estimated_minutes` fields reserved.
- Data model should remain migration-friendly for future `tenant_id` introduction.
- Schedule import intentionally deferred until viable source format exists.

## 9. Risks Driving Design

- unauthorized access and role leakage,
- forged completion updates,
- missing audit trails for manual edits,
- operational blind spots without backup/alerts.

Architecture and validation plans prioritize these risks.

============================================================
FILE: docs/API.md
============================================================
# API Surface (Planning Contract, v1)

This is a planning-level API contract to guide Builder implementation.
Actual route names can vary if capability parity is preserved.

## Auth

- `POST /auth/login-password`
- `POST /auth/login-pin`
- `POST /auth/logout`
- `POST /auth/reset-password/request`
- `POST /auth/reset-password/confirm`
- `POST /auth/reset-pin` (manager-only)

## Users / Roles

- `GET /api/users`
- `POST /api/users`
- `PATCH /api/users/:id`
- `DELETE /api/users/:id`

## Job Codes

- `GET /api/job-codes`
- `POST /api/job-codes`
- `PATCH /api/job-codes/:id`
- `DELETE /api/job-codes/:id`

## Task Templates

- `GET /api/task-templates`
- `POST /api/task-templates`
- `PATCH /api/task-templates/:id`
- `DELETE /api/task-templates/:id`

## Imports

- `POST /api/import/people`
- `POST /api/import/job-codes`
- `POST /api/import/task-templates`

Expected payload modes:
- CSV upload
- text input (`value` or optional `value|jobcode`)

## Assignment Lifecycle

- `POST /api/weeks/:week/generate`
- `GET /api/weeks/:week/draft`
- `PATCH /api/weeks/:week/draft/items/:item_id`
- `POST /api/weeks/:week/post`

## Completion

- `POST /api/completions/:assignment_item_id/mark-complete`
- `POST /api/completions/:assignment_item_id/confirm` (manager/lead per policy)

## Reports

- `GET /api/reports/person?week=&job_code=&person=&from=&to=`
- `GET /api/reports/task?week=&job_code=&task=&from=&to=`

## Audit

- `GET /api/audit?actor=&action=&entity=&from=&to=&page=`

## Owner

- `GET /api/owner/reports/weekly`
- `POST /api/owner/reports/weekly/send-email` (manager-triggered or scheduled job path)

## Authorization Expectations

- Every endpoint enforces role + ownership checks server-side.
- Deny-by-default for undefined role access.

============================================================
FILE: docs/VALIDATION.md
============================================================
# Validation Plan (Pack 001)

## 1. Test Priorities

1. Auth and authorization boundaries
2. Import parsing/validation and failure behavior
3. Assignment lifecycle state correctness
4. Completion integrity and confirmation flow
5. Reporting correctness for person/task views
6. Audit trail completeness for sensitive actions

## 2. Abuse / Negative Tests

- PIN brute-force lockout behavior.
- Access denied for crew attempting privileged endpoints.
- Access denied for cross-user task completion mutation.
- Invalid import lines produce precise error messages and no partial silent corruption.
- Task import/create without job code is rejected.

## 3. Data Correctness Tests

- Draft vs posted state transitions are correct.
- Manual edit reason persistence when provided.
- Completion timestamps and confirmation metadata persist accurately.
- Task-centric reports correctly compute assignment distribution and completion percentages.

## 4. Operational Validation

- Daily backup job runs and restore procedure is documented/tested.
- Logging is structured and excludes secrets/hashes from raw output.
- Auth rate limits are observable and enforce configured behavior.
- Alerting path can be triggered/tested.

## 5. Acceptance Validation Execution

Before sprint close:
- Execute all checks from `planning/sprints/001-discovery-architecture/acceptance.md`.
- Record pass/fail evidence in sprint review notes.
- Any failed item blocks sprint completion.
