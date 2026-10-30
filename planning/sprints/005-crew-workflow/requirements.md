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
