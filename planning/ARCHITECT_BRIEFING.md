# ARCHITECT_BRIEFING.md

## Sprint Snapshot

- **Sprint:** `002-workflow-pages`
- **Phase:** `complete`
- **Status:** Builder implementation for sprint 002 is complete with workflow/page scope implemented and verification evidence captured.
- **Scope guard:** enforced (no schedule import implementation, no task-weight scoring behavior, no multi-location implementation).

## What Builder Implemented (Approved Sprint Scope)

### Core app + data
- Flask app factory/config/extensions and runnable entrypoint.
- Core models for users, job codes, task templates, assignment runs/items, completions, audit events, auth attempts.
- Added `AppSetting` for runtime-configurable settings (used for owner report recipient).

### Auth + authorization
- PIN login for crew and password login for privileged roles.
- Lockout tracking and auth rate-limiting behavior.
- Role guards on protected endpoints.
- Role-based session TTL surfaced/applied in auth flow.

### Manager operations + imports
- CRUD endpoints for people, job codes, and task templates.
- CSV and text import support for people/job codes/task templates.
- Text grammar supports `value` and `value|jobcode` patterns where relevant.
- Validation path returns import errors; task templates require responsible job code.

### Assignment + completion
- Weekly assignment lifecycle: generate draft, inspect draft/fairness spread, edit draft item, post week.
- Completion flow now supports:
  - crew self-complete,
  - manager/lead confirm,
  - manager on-behalf completion with mandatory reason,
  - persisted completion source context (`crew_self` vs `manager_on_behalf`).
- Crew assignment notes now support:
  - general assignment notes,
  - incomplete-context notes,
  - write-once enforcement (no edit/delete).

### Reporting + audit + owner outcomes
- Person-centric and task-centric reports with filters.
- Task report includes completion metrics and consistency-spread signal.
- Audit event logging and audit listing endpoint.
- Added workflow page endpoints for Sprint 002:
  - manager week workflow pages (`/manager/weeks/<week>/generate|draft|post|completions`),
  - manager home workflow contract including schedule linkage (`GET /manager` includes `workflow.schedule` => `/api/owner/reports/weekly/schedule`),
  - crew workflow page enhancements (`/crew/tasks` with history and note action metadata),
  - owner read-only report page endpoint (`/owner/reports`).
- Owner weekly email path now supports:
  - manager-configurable recipient (`/api/owner/settings/report-email`)
  - weekly send trigger (`/api/owner/reports/weekly/send-email`)
  - manager test trigger (`/api/owner/reports/test-email`)
  - weekly schedule config/read path (`GET/POST /api/owner/reports/weekly/schedule`)
  - scheduler execution path (`POST /api/owner/reports/weekly/run-scheduled`)
  - runnable scheduler script (`scripts/run_scheduled_owner_email.py`)
  - SMTP config guards when not configured.

### Ops/security baseline
- Structured request logging with payload redaction for sensitive keys.
- Daily backup script (`scripts/backup_sqlite.py`) + tests.
- Idempotent DB init helper/script:
  - `src/taskassigner/db_init.py`
  - `scripts/init_db.py`

## Verification Evidence (What actually ran)

### Canonical tests run
- `python -m pytest tests -q`
- **Result:** `38 passed`

### Required ad-hoc verification runs
- Temp scripts under `C:\Users\Sobee\AppData\Local\Temp` with prefix `hermes-verify-` were executed and cleaned up.
- Most recent run validated:
  - manager auth login
  - manager home workflow contract includes schedule linkage
  - manager on-behalf completion reason-required guard
  - persisted completion source/reason (`manager_on_behalf`)
  - crew write-once note enforcement (general + incomplete-context submission path)
- **Result:** `VERIFY_OK`, `CLEANUP_OK`

## Current Acceptance Position (bounded)

### Clearly satisfied (Sprint 002 scope)
- A. Manager workflow pages: generate/review/post/completion-review surfaces present; on-behalf completion action + reason-required guard verified.
- B. Crew workflow + notes: own tasks view, write-once note behavior, general/incomplete note support, 4-week history bound, and self-only guard verified.
- C. Owner read-only pages: owner reporting page endpoint read-only path verified.
- D. Data integrity + reporting context: completion source + manager reason persisted/retrievable; existing reporting tests remain green.
- E. Security baseline: role authorization enforced on new actions; note/reason validation and bounds present.
- F. Ops usability: manager workflow now exposes schedule linkage; scheduled runner path already documented.
- G. Scope guard: no schedule import engine, no weighting behavior, no multi-location, no note edit/delete.

### Remaining/partial to close explicitly
- None for Sprint 002 implementation scope.

## Sprint 003 Closeout — UI Shell + Balanced UX/Ops

### Where things stand

TaskAssigner+ now has browser-rendered manager, crew, and owner workflows while retaining the existing JSON/API contracts for integrations and tests.

### Delivered

- Shared server-rendered layout and responsive CSS under `src/taskassigner/templates/` and `src/taskassigner/static/`.
- Manager workflow home plus generate, draft, post, and completion review pages.
- Crew task page with completion affordances, four-week history context, and visible write-once note guidance.
- Owner weekly report page with person-centric and task-centric tables, explicitly read-only.
- Content negotiation keeps existing JSON responses for API/test clients and renders HTML for browser requests.
- Added rendered-page smoke and cross-role authorization tests.

### Verification evidence

- Focused: `python -m pytest tests/test_workflow_pages.py -q` → **10 passed**.
- Full: `python -m pytest tests -q` → **40 passed**, 5 existing SQLAlchemy deprecation warnings.
- Acceptance file: all Sprint 003 criteria checked.

### Scope guard

No schedule-import engine, weighting behavior, multi-location support, frontend framework, or build pipeline was added.

### Remaining technical debt

- Existing SQLAlchemy `Query.get()` deprecation warnings remain from prior sprints; they do not fail the suite.

## Sprint 004 Closeout — Manager Demo Foundation

### Delivered

- Browser manager login at `/auth/login` with rate-limit/lockout feedback and existing JSON auth preserved.
- Local-only deterministic demo reset/seed via the dashboard and `scripts/reset_demo.py`.
- Separate manager People, Job Codes, Task Templates, and Reports pages with shared navigation.
- Manual create plus text import forms; edit/deactivate controls for setup records.
- Guided/advanced weekly page with generate, fairness review, assignee edit with reason, and post actions.

### Verification evidence

- Focused: `python -m pytest tests/test_workflow_pages.py -q` → **13 passed**.
- Full: `python -m pytest tests -q` → **43 passed**, 6 existing SQLAlchemy deprecation warnings.
- Demo reset: `python scripts/reset_demo.py` → **DEMO_RESET_OK**.
- HTTP smoke: `/auth/login` and `/health` → **200**.

### Deferred by scope

Crew/shift-lead/owner browser login, production reset controls, schedule importing, weighting behavior, multi-location support, and frontend build tooling remain deferred.

## Sprint 005 Closeout — Crew Workflow

### Where things stand

TaskAssigner+ now completes the manager-to-crew loop: managers can constrain eligibility, post grouped work, and crew members can log in, work their own assignments across multiple job codes, complete tasks, and leave write-once notes.

### Delivered

- Normalized `TaskExclusion` records keyed by user and task-template ID.
- Central eligibility checks applied to generation and API/browser reassignment.
- People-page exclusion editor with multi-select add/remove and clear-all actions.
- Browser crew PIN login at `/auth/login-crew`.
- Crew task page with grouped, expanded-by-default job-code sections and working completion/note forms.
- Manager weekly page with grouped, expanded-by-default review sections, eligible reassignment choices, and no-eligible warnings.
- Demo seed/reset now includes a two-job-code crew member and a demonstrable exclusion.
- Existing JSON contracts preserved.

### Verification evidence

- Focused: `python -m pytest tests/test_crew_workflow.py -q` → **4 passed**.
- Regression: `python -m pytest tests/test_crew_workflow.py tests/test_workflow_pages.py -q` → **17 passed**.
- Full: `python -m pytest tests -q` → **47 passed**, 11 existing SQLAlchemy deprecation warnings.
- Demo reset: `python scripts/reset_demo.py` → **DEMO_RESET_OK**.
- Compile and whitespace checks passed.
- HTTP smoke: `/health` and `/auth/login-crew` → **200**.

### Scope guard

No schedule importing, shift/day availability, capacity, assignment cap, new fairness algorithm, shift-lead/owner workflow, frontend framework, or build pipeline was added.

## Sprint 006 Closeout — Randomized Generation and Paper Trail

### Delivered

- Double-randomized active task and eligible-person ordering with balanced per-job-code assignment counts.
- Immediate previous posted-week repeat avoidance with eligible fallback behavior.
- Confirmed full draft regeneration before posting; generation locked after posting.
- Eligibility-preserving posted individual edits with audit logging.
- Optional positive `master_list_number` on task templates, shown in manager/crew identity views and print output.
- Browser print view grouped by job code, then person, with checkboxes and per-person signature space.

### Verification evidence

- Focused: `python -m pytest tests/test_sprint006.py -q` → **5 passed**.
- Full: `python -m pytest tests -q` → **54 passed**, 13 existing SQLAlchemy deprecation warnings.
- Demo reset: `python scripts/reset_demo.py` → **DEMO_RESET_OK**.
- Compile, whitespace, and HTTP smoke checks passed (`/health`, `/auth/login-crew`, and posted-week print route returned `200`).
- Sprint 006 acceptance file: all criteria checked.

### Deferred by scope

Full numbered text/CSV master-list import, schedule importing, availability/capacity rules, and custom PDF generation remain deferred.

## Sprint 007 Closeout — Numbered Master Lists

### Where things stand

Managers can now maintain stable numbered task master lists by job code without silently renaming, deleting, deactivating, or renumbering existing tasks.

### Delivered

- Numbered TXT imports scoped to a selected job code, including file upload and paste workflows.
- Numbered CSV imports with selected-job-code scope or row-level `job_code` for combined files.
- Consecutive-number validation per job-code list with review messages for gaps, duplicates, leading zeroes, malformed rows, and title mismatches.
- Partial-success application of valid rows while preserving review/error rows for manual correction.
- CSV exact-match notes/status synchronization and TXT exact-match notes/status preservation.
- Legacy unnumbered-task matching with explicit manager confirmation before attaching a number.
- Combined CSV export containing active and inactive tasks with job code, number, title, notes, and active status.
- Active-only, per-job-code TXT export containing numbered titles only.
- Manager authorization, CSRF-protected browser forms, audit events, and backwards-compatible legacy imports.

### Verification evidence

- Focused: `python -m pytest tests/test_imports.py tests/test_sprint007.py -q` → **16 passed**.
- Full: `python -m pytest tests -q` → **68 passed**, 15 existing SQLAlchemy deprecation warnings.
- Demo reset: `python scripts/reset_demo.py` → **DEMO_RESET_OK**.
- Compile and whitespace checks passed.
- HTTP smoke: `/health`, `/auth/login-crew`, and combined CSV export returned **200**.
- Sprint 007 acceptance file: all criteria checked.

### Deferred by scope

Schedule importing, availability/capacity rules, automatic omission deactivation, custom PDF generation, frontend framework/build tooling, and unrelated assignment redesign remain deferred.

## Sprint 008 Closeout — Manager Email Reporting

### Delivered

- Weekly multipart email with HTML summary, plain-text fallback, and assignment-level CSV attachment.
- Recipient resolution for active managers and owners with valid email addresses, excluding crew, shift leads, inactive users, invalid addresses, and duplicates.
- Thursday–Wednesday range in the subject and report body.
- Overall totals, completion-source counts, lowest-rate people/tasks, and never-finished people in the summary.
- Manual, scheduled, and test sends share the same recipient and rendering path; legacy owner recipient setting remains a fallback.

### Verification evidence

- Owner email tests: **10 passed**.
- Full: `python -m pytest tests -q` → **81 passed**, 16 existing SQLAlchemy deprecation warnings.
- Compile and whitespace checks passed.

### Deferred by scope

Custom PDF generation, employee/crew recipients, and report-specific recipient groups remain deferred.

## Sprint 009 Progress — Controlled Pilot Readiness

### Where things stand

Pilot-readiness hardening is underway. The first security blocker is closed and the operational procedures are documented, but the project is not yet approved for a real pilot.

### Delivered and verified

- Credential-management reset routes now require an authenticated manager session; submitted `actor_name` no longer grants authorization.
- Auth/CSRF regression coverage includes anonymous, unauthorized, forged-actor, and authorized paths.
- Production startup rejects enabled demo mode and the default development secret.
- Controlled pilot runbook added with backup, restore, monitoring, scheduler, fallback, and go/no-go procedures.
- Separate-database SQLite backup/restore drill passed with integrity and record checks.
- Local `/health` returned `{"ok": true}` and unauthenticated `/manager` returned the expected redirect.
- Full verification: **84 passed**, compilation passed, and `git diff --check` passed.

### Remaining before closeout

- Configure and verify the real pilot host, backup retention, monitoring, alerts, SMTP, and scheduler ownership when the host PC is available.
- Import and reconcile realistic pilot data without storing credentials in project artifacts.
- Execute the complete Thursday–Wednesday manual rehearsal and record the result.
- Obtain an explicit GO, GO WITH CONDITIONS, or NO-GO decision.
