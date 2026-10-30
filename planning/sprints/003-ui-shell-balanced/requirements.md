# Sprint 003 Requirements — UI Shell + Balanced UX/Ops

## Sprint Goal

Make TaskAssigner+ visually usable in-browser for manager, crew, and owner workflows, while preserving Sprint 002 behavior and adding pragmatic ops hardening.

## In Scope

1. Add lightweight server-rendered pages (no frontend framework) for:
   - manager workflow entry + week actions,
   - crew current-week tasks + note/complete actions,
   - owner read-only report view.
2. Reuse existing Sprint 002 backend/API contracts as initial data source for rendering.
3. Add targeted UX polish:
   - clear status labels,
   - clear success/error feedback,
   - mobile-safe crew layout basics.
4. Add ops-hardening checks:
   - route smoke coverage for role pages,
   - guard coverage for role boundaries and failure states,
   - preserve redaction/audit behavior.

## Out of Scope

- Any schedule import implementation.
- Any task weighting/difficulty algorithm behavior.
- Any multi-location support.
- Frontend framework introduction or build pipeline setup.
- Broad redesign/theme system work beyond practical readability and flow clarity.

## Functional Expectations

- Manager can navigate visible workflow actions from page UI (generate/draft/post/completion review/schedule link).
- Crew can see own tasks on an actual page, with action affordances for complete and note.
- Crew notes remain write-once (general and incomplete-context usage supported).
- Owner sees read-only weekly reporting page UI.
- Existing auth/role boundaries stay server-enforced.

## Non-Functional Expectations

- Keep implementation simple, local, and maintainable.
- Preserve existing endpoint semantics where already consumed by tests.
- No sensitive payload leakage in logs.
- Keep view layer incremental and testable.
