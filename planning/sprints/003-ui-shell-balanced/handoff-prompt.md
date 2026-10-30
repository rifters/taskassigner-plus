# Builder Handoff Prompt — Sprint 003 UI Shell + Balanced UX/Ops

You are the Builder for TaskAssigner+ Sprint 003.

## Mission

Implement a **debug-usable visual UI shell** for manager, crew, and owner workflows, then execute a **balanced pass** of UX polish and ops hardening, while preserving Sprint 002 behavior and scope boundaries.

## Required Read Order

1. `templates/method/120x-agent-identity.md`
2. `AGENTS.md`
3. `planning/STATE.md`
4. `planning/DECISIONS.md`
5. `planning/DOMAIN.md`
6. `planning/RISKS.md`
7. `planning/QUESTIONS.md`
8. `planning/sprints/003-ui-shell-balanced/requirements.md`
9. `planning/sprints/003-ui-shell-balanced/blueprint.md`
10. `planning/sprints/003-ui-shell-balanced/acceptance.md`

## Execution Rules

- Apply Architect Pack 003 with dry-run, then apply.
- Implement only from Sprint 003 files under `planning/sprints/003-ui-shell-balanced/`.
- Stop at mandatory code gate and present file-by-file implementation plan before source edits.
- Keep implementation KISS/DRY and style-consistent.
- Do not broaden scope to deferred items.

## Scope Priorities

1. Visual shell first (manager, crew, owner rendered pages).
2. UX baseline clarity (actions, statuses, feedback, mobile crew readability).
3. Ops hardening (smoke/authz/regression checks).

## Explicitly Out of Scope

- Schedule import implementation.
- Weighting/difficulty behavior.
- Multi-location.
- Frontend framework/build tooling.

## Validation Expectations

- Run focused tests for Sprint 003 page routes/guards.
- Run full test suite before close.
- If system requests ad-hoc verification for changed files, run required temp `hermes-verify-*` scripts and report as ad-hoc verification (not suite green).

## Closeout Requirements

- Update `planning/ARCHITECT_BRIEFING.md` with what was actually shipped and verified.
- Update `planning/STATE.md` and `planning/STATUS.json` with final sprint state.
- Record any new durable decisions in `planning/DECISIONS.md`.
