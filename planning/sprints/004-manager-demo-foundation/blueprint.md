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
