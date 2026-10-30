# Sprint 004 Acceptance Criteria — Manager Demo Foundation

Sprint is complete only when all items pass or are explicitly deferred with rationale.

## A. Login and Demo Bootstrap

- [x] Manager login page renders in a browser.
- [x] `demo-manager` can log in with documented demo password `DemoPass123!` in local development.
- [x] Invalid credentials and lockout/rate-limit states are understandable.
- [x] Demo seed/reset is local-development-only and idempotent.
- [x] Reset restores sample job codes, employees, and task templates without duplicates.

## B. Manager Navigation and Pages

- [x] Dashboard renders setup/workflow status and shared navigation.
- [x] People page supports manual create/edit/deactivate.
- [x] Job Codes page supports manual create/edit/deactivate.
- [x] Task Templates page supports manual create/edit/deactivate.
- [x] Separate pages use consistent layout, breadcrumbs, feedback, and active navigation.

## C. Imports

- [x] People CSV/plain-text import is available from the People page.
- [x] Job Code CSV/plain-text import is available from the Job Codes page.
- [x] Task Template CSV/plain-text import is available from the Task Templates page.
- [x] Validation errors and created/existing counts are visible.
- [x] Orphan task templates are rejected.

## D. Weekly Assignment Demo

- [x] Guided weekly flow renders and supports week selection.
- [x] Manager can generate a draft from the page.
- [x] Fairness spread and assignment rows are visible.
- [x] Manager can edit an assignee with optional reason.
- [x] Manager can post the reviewed week with confirmation feedback.
- [x] Advanced dashboard exposes the same workflow in one view.

## E. Security and Compatibility

- [x] All manager pages require manager authorization.
- [x] Unauthenticated and non-manager access is denied.
- [x] State-changing actions preserve CSRF protections.
- [x] Existing JSON/API contracts and Sprint 003 page tests remain green.
- [x] No secrets or password hashes appear in rendered pages or logs.

## F. Scope Guard

- [x] No crew, shift-lead, or owner login implementation.
- [x] No schedule-import engine.
- [x] No weighting behavior.
- [x] No multi-location support.
- [x] No frontend framework or build pipeline.
