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
