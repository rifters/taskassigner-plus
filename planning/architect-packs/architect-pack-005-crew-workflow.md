============================================================
FILE: planning/STATUS.json
============================================================
{
  "schemaVersion": 1,
  "phase": "apply-pack",
  "sprint": "005-crew-workflow",
  "updated": "2026-09-02T00:00:00-04:00"
}

============================================================
FILE: planning/sprints/005-crew-workflow/requirements.md
============================================================
# Sprint 005 Requirements — Crew Workflow

## Sprint Goal

Extend the working manager-first demo into a manager-to-crew vertical slice: a seeded crew member can log in, view posted assignments across multiple job codes, complete work, and leave a write-once note while the manager reviews grouped status.

## In Scope

1. Browser crew authentication using the existing PIN authentication contract and role authorization.
2. Local-development-only, deterministic, idempotent crew demo seed/reset data.
3. Crew task page showing only the authenticated crew member's posted assignments.
4. Multiple assignments per person, including assignments from multiple job-code pools.
5. Crew assignments grouped by responsible job code, all groups expanded by default, with job-code context on every task.
6. Completion and write-once notes using the existing completion/note behavior and ownership rules.
7. Last-four-week completion history where the existing contract provides it.
8. Manager weekly review grouped by responsible job code, all groups expanded by default, retaining fairness counts and review controls.
9. Server-enforced eligibility based on active status, responsible job-code membership, and per-person task exclusions.
10. People-page management of specific task exclusions: add, remove, and clear all.
11. API and browser reassignment rejection for wrong-job-code or excluded people.
12. Tests and real local smoke verification.

## Eligibility Model

A person is eligible for a task when active, in the task's responsible job-code pool, and not excluded from that task template. A person may have multiple job codes and any number of assignments. No schedule, shift, days-off, capacity, or maximum-assignment rule is added in this sprint.

## Out of Scope

- Schedule importing or schedule-based availability.
- Days-off, shift, capacity, time-estimate, or maximum-assignment rules.
- New weighting, fairness, or assignment algorithm behavior.
- Shift-lead or owner browser login.
- Production bootstrap/reset controls.
- Frontend framework or build pipeline.
- Multi-location support or account administration.

## Security and Compatibility

Preserve existing JSON/API contracts, CSRF protection, role guards, completion ownership, write-once note behavior, and audit behavior. Do not render or log PINs, password hashes, secrets, or credentials.

============================================================
FILE: planning/sprints/005-crew-workflow/blueprint.md
============================================================
# Sprint 005 Blueprint — Crew Workflow

## Data Model

Add a normalized per-person/task-template exclusion model with unique `(user_id, task_template_id)` semantics and foreign keys. Key exclusions by stable task-template ID, never by title text. Follow the project's existing deletion/deactivation conventions so active orphan exclusions cannot remain. Keep the existing user/job-code many-to-many relationship as the eligibility source.

## Server-Side Eligibility

Create or reuse one central eligibility helper and use it from weekly generation, API draft reassignment, and browser reassignment. It must require an active eligible crew person, responsible job-code membership, and no exclusion for the task template. If no eligible person remains, preserve the existing safe unassigned behavior and expose a manager-visible warning; never assign outside constraints. UI filtering is supplemental, not authoritative.

## Routes and UI

- Add or extend a role-aware browser crew login flow without breaking manager login or JSON auth.
- Add `/crew` and/or `/crew/tasks` server-rendered pages with existing content negotiation behavior.
- Add constraint editing inside each person's People-page edit area. Support selecting a person, viewing available and excluded tasks, multi-select add/remove, clear-all, confirmation, and validation feedback.
- Group crew and manager weekly assignment rows by responsible job code, expanded by default. Preserve fairness counts, assignment context, and reassignment controls.
- Use existing templates/CSS conventions and CSRF-protected forms.

## Demo Data

Extend the guarded demo seed/reset flow with at least one crew account linked to two job codes, enough active tasks for multiple assignments, and at least one demonstrable task exclusion. Keep seeded values development-only and avoid exposing credentials in rendered pages or logs.

## Tests

Add focused coverage for browser crew login and role guards; own-assignment filtering; multiple job codes and assignments; expanded grouping; completion and write-once notes; exclusion add/remove/clear; task-title rename stability; generator eligibility; API and browser reassignment rejection; visible no-eligible-target warning; idempotent demo reset; and preservation of the existing full suite.

============================================================
FILE: planning/sprints/005-crew-workflow/acceptance.md
============================================================
# Sprint 005 Acceptance — Crew Workflow

- [ ] A local demo crew member can authenticate through the browser PIN flow.
- [ ] Crew can view posted assignments in the browser and sees only their own.
- [ ] A crew member linked to two job codes sees both grouped sections.
- [ ] Crew groups are grouped by responsible job code and expanded by default.
- [ ] Multiple assignments per person are visible and usable, including multiple tasks in one pool.
- [ ] Each displayed task includes job-code context.
- [ ] Crew can complete an assignment and add a write-once note without breaking existing behavior.
- [ ] Existing bounded completion history remains available where defined.
- [ ] Manager weekly review is grouped by job code and expanded by default.
- [ ] Manager review retains fairness counts and reassignment controls.
- [ ] People-page edit UI can add, remove, and clear per-person task exclusions.
- [ ] Exclusions use task-template IDs and remain correct after a task title changes.
- [ ] Generation never assigns an excluded task to a person.
- [ ] Generation never assigns outside responsible job-code membership.
- [ ] API reassignment rejects wrong-job-code and excluded targets server-side.
- [ ] Browser reassignment rejects the same invalid targets server-side.
- [ ] No eligible target produces an explicit manager-visible unassigned/warning state.
- [ ] Demo seed/reset is guarded, deterministic, idempotent, and does not duplicate exclusions.
- [ ] Existing API contracts and the full test suite remain green.
- [ ] No PINs, hashes, secrets, or credentials appear in pages or logs.
- [ ] Deferred schedule and availability scope remains unimplemented.

============================================================
FILE: planning/sprints/005-crew-workflow/handoff-prompt.md
============================================================
# Builder Handoff — Sprint 005 Crew Workflow

Implement Sprint 005 from these generated sprint files only. Before source changes, read `requirements.md`, `blueprint.md`, `acceptance.md`, the existing models/auth/assignment/completion routes, manager People and weekly templates, demo seed/reset, and relevant tests. Do not redefine scope.

Implement the smallest server-rendered manager-to-crew vertical slice satisfying every acceptance item. Centralize and enforce eligibility server-side using responsible job-code membership plus stable task-template exclusions. Preserve JSON contracts, CSRF, role guards, completion ownership, write-once notes, audit behavior, and existing assignment behavior. Do not add schedule or availability rules.

Run focused tests, the full suite, Python compilation, `git diff --check`, demo reset/idempotency verification, and a real local HTTP/browser-path smoke test. Update `planning/STATE.md`, `planning/DECISIONS.md`, `planning/RISKS.md`, and acceptance evidence only after implementation is verified. Do not commit, push, expose credentials, or modify unrelated files.
