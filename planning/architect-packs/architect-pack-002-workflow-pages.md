============================================================
FILE: planning/STATUS.json
============================================================
{
  "schemaVersion": 1,
  "phase": "apply-pack",
  "sprint": "002-workflow-pages",
  "updated": "2026-07-08T21:30:00-04:00"
}

============================================================
FILE: planning/STATE.md
============================================================
# Project State

**Project:** TaskAssigner+  
**Client:** Rifters / Eric  
**Last updated:** 2026-07-08

---

## Current Phase

Architect planning for Sprint 002 is complete and ready for Builder apply/execute.

---

## Current Status

Sprint 001 backend/API scope is complete and verified.  
Sprint 002 is approved for implementation focus on daily usability across all roles.

Sprint 002 planning decisions now locked:
- Include all role pages in this sprint (manager + crew + owner).
- Crew history window is last 4 weeks.
- Crew notes are allowed on incomplete tasks and are write-once.
- Manager may mark task completion on behalf of crew.
- On-behalf completion requires a mandatory reason.

---

## Active Sprint

`planning/sprints/002-workflow-pages/`

---

## Verification Snapshot (from completed Sprint 001)

- `python -m pytest tests -q`
- Result: `30 passed`

---

## Next Actions

1. Builder applies Architect Pack 002 (dry-run, then apply).
2. Builder executes only Sprint 002 files under `planning/sprints/002-workflow-pages/`.
3. Builder stops at code gate before source/test edits and waits for explicit build approval.
4. Builder refreshes `planning/ARCHITECT_BRIEFING.md` at sprint close with acceptance evidence.

---

## Blockers

No planning blocker for Sprint 002.

---

## Watch Items

- Keep strict scope guard (no schedule-import engine, no weighting behavior, no multi-location).
- Preserve auditability for completion flows and manager overrides.
- Maintain safe logging and no secret leakage.

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
| 2026-07-08 | **Sprint 002 scope:** implement role pages for manager + crew + owner in one sprint. | User approved Architect recommendation for daily usability first. | Builder should prioritize page workflows over new backend feature classes. |
| 2026-07-08 | **Crew history rule:** show last 4 weeks of crew completion history. | Operationally useful without heavy analytics complexity. | Adds bounded history query + UI card/table requirement. |
| 2026-07-08 | **Crew notes policy:** notes allowed for incomplete tasks; write-once only. | Preserve audit integrity and practical issue reporting. | Notes become immutable records; no edit/delete in v1. |
| 2026-07-08 | **Manager override completion:** manager can mark completion on behalf of crew but reason is mandatory. | Real floor operations include staff who will not use device flow reliably. | Completion model/reporting must distinguish self-completed vs manager-completed with reason. |

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
6. Crew can leave write-once notes, including incomplete-task explanations.
7. Manager can mark completion on behalf of crew with mandatory reason.
8. Manager confirms completions as separate state when needed.
9. Manager/owner review person-centric + task-centric consistency reports.
10. Owner receives automated weekly summary email.

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
- **On-behalf completion** — manager marks completion for a crew user with required reason.

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
- Crew notes are write-once; in v1 they can be attached to incomplete-task explanations.
- Manager on-behalf completion requires mandatory reason and audit trace.
- Crew history view is limited to last 4 weeks in v1.
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
| Manager override misuse (false completions) | Medium | High | Mandatory reason + actor attribution + reporting distinction between self and on-behalf completion. | Active |
| Notes abuse/noise or accidental sensitive content | Medium | Medium | Short note length cap, input sanitization, write-once immutability, manager-visible context. | Active |

============================================================
FILE: planning/QUESTIONS.md
============================================================
# Open Questions

Questions that need answers from Architect/Builder/Client.

---

## Discovery Gate Resolution (2026-07-08)

Mandatory External-facing discovery topics were answered or explicitly deferred with rationale. No blocking discovery gate item remains for Pack 001.

---

## Sprint 002 Resolution Notes (2026-07-08)

All Sprint 002 planning decisions requested in Architect conversation are resolved and approved.

- Include all role pages in Sprint 002: **answered**.
- Crew history window: **last 4 weeks**: **answered**.
- Notes on incomplete tasks allowed: **answered**.
- Notes edit policy: **write-once**: **answered**.
- Manager on-behalf completion allowed: **answered**.
- On-behalf completion reason required: **answered**.

No blocker question remains for Architect Pack 002 generation.

---

## Deferred Tracking

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
- `planning/ARCHITECT_BRIEFING.md`
- `planning/sprints/001-discovery-architecture/requirements.md`
- `planning/sprints/001-discovery-architecture/blueprint.md`
- `planning/sprints/001-discovery-architecture/acceptance.md`
- `planning/sprints/001-discovery-architecture/handoff-prompt.md`
- `planning/sprints/002-workflow-pages/requirements.md`
- `planning/sprints/002-workflow-pages/blueprint.md`
- `planning/sprints/002-workflow-pages/acceptance.md`
- `planning/sprints/002-workflow-pages/handoff-prompt.md`

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

## Reserved Implementation Areas

- `src/`
- `tests/`

============================================================
FILE: planning/sprints/002-workflow-pages/requirements.md
============================================================
# Sprint 002 Requirements — Workflow Pages + Completion Context

## Sprint Goal

Turn Sprint 001 backend/API capability into daily-usable role workflows by delivering core manager, crew, and owner pages, while preserving security and audit integrity.

---

## In Scope (must be implemented)

### 1) Manager daily workflow pages

- Manager landing/dashboard page with clear navigation to weekly operations.
- Week workflow pages for:
  - generate draft,
  - review/edit draft,
  - post assignments,
  - completion review/confirmation.
- Visible distinction between:
  - crew self-completed,
  - manager-completed on behalf.

### 2) Crew pages with history + notes

- Crew task list page (current week) and task detail/interaction page.
- Crew may add note for incomplete tasks (e.g., blocked, unavailable item, staffing conflict).
- Note policy is write-once (no edit/delete in v1).
- Crew page includes history of last 4 weeks of completion records.

### 3) Manager on-behalf completion path

- Manager can mark a task completed on behalf of crew when needed.
- Mandatory reason is required for on-behalf completion.
- On-behalf completion generates audit event.
- Reporting surfaces must preserve who performed completion action.

### 4) Owner read-only pages

- Owner read-only page(s) for weekly reporting visibility.
- Align with existing owner report endpoint behavior.

### 5) Scheduler usability floor

- UI or documented operator path for weekly schedule configuration/read.
- Confirm scheduled runner script path is documented for deployment operation:
  - `scripts/run_scheduled_owner_email.py`.

---

## Explicitly Out of Scope (Sprint 002)

- New assignment engine scoring behavior (weights/difficulty logic).
- Schedule import ETL/parser from Altametrics.
- Multi-location tenancy implementation.
- Full notification center/chat/threaded discussion system.
- Editable/deletable crew notes (write-once only in this sprint).

---

## Non-functional Requirements (minimum)

- Server-side role enforcement remains authoritative for every page action.
- CSRF remains enforced on state-changing actions.
- Notes and completion reason inputs are sanitized and length-bounded.
- On-behalf completion and note submission are auditable.
- Page responses remain compatible with current stack (Flask + vanilla templates).

---

## Assumptions (explicit)

- Existing API routes from Sprint 001 are stable enough to back new pages.
- Existing report endpoints can be reused for owner/manager page rendering in Sprint 002.
- Note length cap can be implemented as a practical fixed limit (recommended: 500 chars) unless Builder finds an existing project standard.

============================================================
FILE: planning/sprints/002-workflow-pages/blueprint.md
============================================================
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

============================================================
FILE: planning/sprints/002-workflow-pages/acceptance.md
============================================================
# Sprint 002 Acceptance Criteria — Builder Checkable

Sprint is complete only when all items pass or are explicitly deferred with rationale.

---

## A. Manager Workflow Pages

- [ ] Manager can access weekly generate/review/edit/post workflow pages.
- [ ] Manager completion review page shows completion actor/source context.
- [ ] Manager can mark completion on behalf of crew from manager workflow.
- [ ] On-behalf completion is blocked if reason is empty.
- [ ] On-behalf completion writes audit evidence with actor + reason + timestamp.

## B. Crew Workflow + Notes

- [ ] Crew can view own current-week tasks on page flow.
- [ ] Crew can submit incomplete-task note.
- [ ] Note is write-once (edit/delete attempts are rejected in v1).
- [ ] Crew history shows last 4 weeks (bounded window).
- [ ] Crew cannot view/modify other users’ tasks/notes/history.

## C. Owner Read-only Pages

- [ ] Owner can access read-only weekly reporting page(s).
- [ ] Owner pages expose reporting data without operational mutation actions.

## D. Data Integrity + Reporting Context

- [ ] Completion data distinguishes self-complete vs manager-on-behalf.
- [ ] Manager reason for on-behalf completion is persisted and retrievable.
- [ ] Existing reporting paths remain functional after Sprint 002 changes.

## E. Security Baseline

- [ ] Role-based authorization enforced server-side for all new/updated page actions.
- [ ] CSRF protections active on state-changing routes.
- [ ] Note/reason inputs are validated and bounded.

## F. Ops Usability

- [ ] Weekly schedule config/read path is usable by manager in app workflow.
- [ ] Scheduled runner script path is documented for deployment operation.

## G. Scope Guard

- [ ] No schedule-import engine implementation.
- [ ] No weight/difficulty algorithm behavior implementation.
- [ ] No multi-location implementation.
- [ ] No editable/deletable notes (write-once policy preserved).

============================================================
FILE: planning/sprints/002-workflow-pages/handoff-prompt.md
============================================================
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

Deliver daily-usable manager, crew, and owner page workflows over existing Sprint 001 backend/API capabilities, including immutable crew notes and manager on-behalf completion with mandatory reason.

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

============================================================
FILE: docs/ARCHITECTURE.md
============================================================
# TaskAssigner+ Architecture

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
- Completion context capture (crew notes + manager on-behalf reason)
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
- **Task-centric** consistency analysis (distribution + completion trends),
- clear completion source context (self vs on-behalf) where applicable.

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
- `POST /api/completions/:assignment_item_id/manager-complete` (manager on-behalf completion; reason required)
- `POST /api/completions/:assignment_item_id/note` (crew incomplete-task note; write-once)

## Reports

- `GET /api/reports/person?week=&job_code=&person=&from=&to=`
- `GET /api/reports/task?week=&job_code=&task=&from=&to=`

## Crew History

- `GET /api/crew/history?weeks=4` (bounded recent completion history)

## Audit

- `GET /api/audit?actor=&action=&entity=&from=&to=&page=`

## Owner

- `GET /api/owner/reports/weekly`
- `GET /api/owner/settings/report-email`
- `POST /api/owner/settings/report-email` (manager updates owner recipient)
- `POST /api/owner/reports/weekly/send-email` (manager-triggered weekly send)
- `POST /api/owner/reports/test-email` (manager-triggered SMTP connectivity/proof send)
- `GET /api/owner/reports/weekly/schedule` (manager/owner reads weekly schedule config)
- `POST /api/owner/reports/weekly/schedule` (manager writes schedule config: `enabled`,`weekday`,`hour_utc`,`minute_utc`)
- `POST /api/owner/reports/weekly/run-scheduled` (manager runs scheduler decision path once; supports `force`/`dry_run`)

## Authorization Expectations

- Every endpoint enforces role + ownership checks server-side.
- Deny-by-default for undefined role access.

============================================================
FILE: docs/VALIDATION.md
============================================================
# Validation Plan

## 1. Test Priorities

1. Auth and authorization boundaries
2. Import parsing/validation and failure behavior
3. Assignment lifecycle state correctness
4. Completion integrity and confirmation flow
5. Reporting correctness for person/task views
6. Audit trail completeness for sensitive actions
7. Workflow page authz and role usability

## 2. Abuse / Negative Tests

- PIN brute-force lockout behavior.
- Access denied for crew attempting privileged endpoints.
- Access denied for cross-user task completion mutation.
- Invalid import lines produce precise error messages and no partial silent corruption.
- Task import/create without job code is rejected.
- Manager on-behalf completion rejected without reason.
- Crew note edit/delete attempts rejected once submitted (write-once enforcement).

## 3. Data Correctness Tests

- Draft vs posted state transitions are correct.
- Manual edit reason persistence when provided.
- Completion timestamps and confirmation metadata persist accurately.
- Task-centric reports correctly compute assignment distribution and completion percentages.
- Completion source context (self vs manager on-behalf) is preserved.
- Crew history query is bounded to last 4 weeks.

## 4. Operational Validation

- Daily backup job runs and restore procedure is documented/tested.
- Logging is structured and excludes secrets/hashes from raw output.
- Auth rate limits are observable and enforce configured behavior.
- Alerting path can be triggered/tested.
- DB schema initialization is idempotent via `python scripts/init_db.py`.
- Scheduler runner script executes with expected due/disabled/error status behavior.

## 5. Acceptance Validation Execution

Before sprint close:
- Execute all checks from `planning/sprints/002-workflow-pages/acceptance.md`.
- Record pass/fail evidence in `planning/ARCHITECT_BRIEFING.md`.
- Any failed item blocks sprint completion unless explicitly deferred with rationale.
