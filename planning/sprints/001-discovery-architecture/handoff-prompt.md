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
