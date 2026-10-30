# Sprint 003 Blueprint — Builder Implementation Plan

## 1) View Layer Foundation

- Introduce Flask templates + static assets structure:
  - `src/taskassigner/templates/`
  - `src/taskassigner/static/`
- Keep minimal styling and component vocabulary (cards, tables, actions, badges, alerts).
- Add shared base layout for role pages.

## 2) Route/View Wiring

- Add/adjust role page routes to render templates for:
  - manager home/workflow,
  - manager week pages (generate/draft/post/completions),
  - crew tasks page,
  - owner reports page.
- Keep existing JSON action contracts available where tests/integrations rely on them.
- Prefer explicit page routes and predictable URL structure.

## 3) UX Pass (bounded)

- Manager: show clear action next-steps and status blocks.
- Crew: mobile-first readability, prominent actions, clear completion/note state.
- Owner: clean read-only report summary with no mutation controls.
- Add concise error/success messaging patterns.

## 4) Ops Hardening Pass

- Add route smoke tests for all new/updated visual page endpoints by role.
- Add authz tests for cross-role access denials.
- Add at least one regression test guarding write-once note behavior through page flow path.
- Preserve/adapt existing tests to ensure backend behavior remains unchanged.

## 5) Documentation + Closeout

- Update `planning/ARCHITECT_BRIEFING.md` with visual UX scope actually delivered.
- Update `planning/STATE.md` and `planning/STATUS.json` at close.
- Record any new durable design decisions in `planning/DECISIONS.md`.

## Implementation Notes

- Keep KISS: no JS framework, no heavy client state.
- Server-render first; add only lightweight JS where needed for usability.
- Do not move deferred features into sprint scope.
