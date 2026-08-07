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

## Builder Notes for Architect

- Sprint 002 closed with acceptance-mapped evidence and status/state/briefing sync complete.
- Implementation stayed within approved sprint boundary; deferred items remain deferred by scope guard.
- Suggested next planning focus: Sprint 003 prioritization (UI polish vs ops hardening) with current workflow baseline preserved.
