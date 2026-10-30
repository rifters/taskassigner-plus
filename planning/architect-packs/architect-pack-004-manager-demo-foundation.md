============================================================
FILE: planning/STATUS.json
============================================================
{
  "schemaVersion": 1,
  "phase": "apply-pack",
  "sprint": "004-manager-demo-foundation",
  "updated": "2026-09-01T06:45:00-04:00"
}

============================================================
FILE: planning/sprints/004-manager-demo-foundation/requirements.md
============================================================
# Sprint 004 Requirements — Manager Demo Foundation

## Sprint Goal

Make TaskAssigner+ runnable as a real manager-first browser demo: a seeded demo manager can log in, load/reset sample data, maintain job codes, people, and task templates, then generate, review, edit, and post a weekly assignment set.

## In Scope

1. Add a browser login page for manager password authentication.
2. Add a manager dashboard with shared navigation and setup/workflow status.
3. Add separate manager pages for:
   - People
   - Job Codes
   - Task Templates
   - Weekly Assignments
4. Add manual CRUD UI for people, job codes, and task templates using existing APIs.
5. Add CSV/plain-text import UI for people, job codes, and task templates using existing import APIs.
6. Add a guided weekly workflow and an advanced weekly dashboard using existing assignment APIs.
7. Add local-development-only demo seeding:
   - `demo-manager`
   - documented password `DemoPass123!`
   - sample job codes, employees, and task templates
   - reset demo data action
8. Preserve current JSON/API behavior and server-side authorization.

## Out of Scope

- Crew, shift-lead, or owner login pages in this sprint.
- Production account bootstrap or production reset controls.
- Schedule import implementation.
- Task weighting/difficulty behavior.
- Multi-location support.
- Frontend framework or build pipeline.
- New assignment algorithm behavior.

## Functional Expectations

- A fresh local demo can authenticate as `demo-manager`.
- Demo reset is visibly labeled local-development-only and restores known sample data.
- Manager can create a job code, person, and task template from browser pages.
- Task templates require a responsible job code.
- Imports show validation errors and created/existing counts.
- Manager can select a week, generate a draft, see fairness spread, edit an assignee with an optional reason, and post the week.
- Existing API clients and Sprint 003 rendered pages remain functional.

## Security Expectations

- Manager routes remain protected by server-side role checks.
- Password is never logged or displayed after submission.
- Demo credentials are clearly development-only and must not be presented as production credentials.
- State-changing forms preserve CSRF protections.

============================================================
FILE: planning/sprints/004-manager-demo-foundation/blueprint.md
============================================================
# Sprint 004 Blueprint — Manager Demo Foundation

## 1) Demo/bootstrap support

- Add an idempotent local demo seed/reset helper in the existing scripts or application support area.
- Use explicit development/demo configuration guard; do not expose reset behavior in production configuration.
- Seed the manager with the exact username `demo-manager` and documented password `DemoPass123!`.
- Seed representative Cooks, Servers, Hosts, and SAs job codes, employees mapped to those codes, and multiple task templates.
- Add tests proving reset is idempotent and does not duplicate records.

## 2) Authentication UI

- Add a GET login page and POST/browser-compatible login flow while retaining existing JSON login endpoints.
- Show demo-only credential guidance without exposing passwords elsewhere.
- Render clear invalid-credential and lockout errors.
- Redirect authenticated managers to the dashboard.

## 3) Shared manager shell

- Extend the existing Sprint 003 base layout with manager navigation:
  - Dashboard
  - People
  - Job Codes
  - Task Templates
  - Weekly Assignments
  - Reports
- Add consistent breadcrumbs, success/error feedback, and active navigation state.
- Keep lightweight server-rendered HTML and existing CSS conventions.

## 4) Setup pages

- Build separate People, Job Codes, and Task Templates pages.
- Use server-rendered list views plus forms; submit through small browser-safe adapters that call existing JSON endpoints or add narrowly scoped HTML POST handlers.
- People fields: name, role, optional email, active state, job-code membership, and appropriate PIN/password handling.
- Job Code fields: name and active state.
- Task Template fields: title, responsible job code, notes, and active state.
- Add import panels with mode selection, text/CSV input, validation feedback, and result counts.
- Never render hashes, PINs, passwords, SMTP values, or reset tokens.

## 5) Weekly assignment experience

- Guided view: week selection, generate draft, fairness summary, review/edit, post confirmation.
- Advanced dashboard: assignment table, assignee display, fairness spread, status, edit controls, and post action.
- Reuse existing assignment routes and preserve audit reasons on manual edits.
- Show clear empty, error, draft, and posted states.

## 6) Validation and closeout

- Add route smoke tests for login, dashboard, all setup pages, import paths, weekly guided/dashboard pages, and reset guard.
- Add authorization tests for unauthenticated and non-manager access.
- Add CRUD/import tests for required fields and responsible job-code enforcement.
- Add idempotent seed/reset tests.
- Run focused tests and the full suite.
- Update briefing, state, status, and decisions at close.

============================================================
FILE: planning/sprints/004-manager-demo-foundation/acceptance.md
============================================================
# Sprint 004 Acceptance Criteria — Manager Demo Foundation

Sprint is complete only when all items pass or are explicitly deferred with rationale.

## A. Login and Demo Bootstrap

- [ ] Manager login page renders in a browser.
- [ ] `demo-manager` can log in with documented demo password `DemoPass123!` in local development.
- [ ] Invalid credentials and lockout/rate-limit states are understandable.
- [ ] Demo seed/reset is local-development-only and idempotent.
- [ ] Reset restores sample job codes, employees, and task templates without duplicates.

## B. Manager Navigation and Pages

- [ ] Dashboard renders setup/workflow status and shared navigation.
- [ ] People page supports manual create/edit/deactivate.
- [ ] Job Codes page supports manual create/edit/deactivate.
- [ ] Task Templates page supports manual create/edit/deactivate.
- [ ] Separate pages use consistent layout, breadcrumbs, feedback, and active navigation.

## C. Imports

- [ ] People CSV/plain-text import is available from the People page.
- [ ] Job Code CSV/plain-text import is available from the Job Codes page.
- [ ] Task Template CSV/plain-text import is available from the Task Templates page.
- [ ] Validation errors and created/existing counts are visible.
- [ ] Orphan task templates are rejected.

## D. Weekly Assignment Demo

- [ ] Guided weekly flow renders and supports week selection.
- [ ] Manager can generate a draft from the page.
- [ ] Fairness spread and assignment rows are visible.
- [ ] Manager can edit an assignee with optional reason.
- [ ] Manager can post the reviewed week with confirmation feedback.
- [ ] Advanced dashboard exposes the same workflow in one view.

## E. Security and Compatibility

- [ ] All manager pages require manager authorization.
- [ ] Unauthenticated and non-manager access is denied.
- [ ] State-changing actions preserve CSRF protections.
- [ ] Existing JSON/API contracts and Sprint 003 page tests remain green.
- [ ] No secrets or password hashes appear in rendered pages or logs.

## F. Scope Guard

- [ ] No crew, shift-lead, or owner login implementation.
- [ ] No schedule-import engine.
- [ ] No weighting behavior.
- [ ] No multi-location support.
- [ ] No frontend framework or build pipeline.

============================================================
FILE: planning/sprints/004-manager-demo-foundation/handoff-prompt.md
============================================================
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
