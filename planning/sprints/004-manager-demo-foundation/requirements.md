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
