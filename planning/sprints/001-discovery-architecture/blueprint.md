# Sprint 001 Blueprint — Practical Implementation Plan

## Architecture Shape

- **Backend:** Flask app with Blueprints per domain area.
- **Persistence:** SQLite via Flask-SQLAlchemy.
- **Auth:** Flask-Login + role-aware auth middleware/decorators.
- **Password/PIN hashing:** Flask-Bcrypt.
- **Frontend:** Server-rendered HTML + Vanilla JS for small interactivity.
- **Deployment access:** Cloudflare Tunnel (public HTTPS), Tailscale (private).

---

## Proposed Module Boundaries

- `auth` — login/logout, session/lockout/reset flows.
- `users` — people management, roles, crew PIN admin.
- `job_codes` — job code CRUD and memberships.
- `task_templates` — task CRUD with required responsible job code.
- `imports` — CSV/text parsing + validation + preview/commit.
- `assignments` — generation, draft review/edit, posting.
- `completions` — crew completion capture + manager confirmation.
- `reports` — person-centric and task-centric analytics.
- `audit` — queryable audit timeline.
- `owner` — read-only report surfaces + weekly email job trigger.

---

## Data Model (v1 minimum)

- `users` (id, name, role, email nullable, password_hash nullable, pin_hash nullable, active, timestamps)
- `job_codes` (id, name, active, timestamps)
- `user_job_codes` (user_id, job_code_id)
- `task_templates` (id, title, notes, responsible_job_code_id, weight_nullable, est_minutes_nullable, active)
- `assignment_runs` (id, week_key, status[draft|posted], generated_by, generated_at, posted_by, posted_at)
- `assignment_items` (id, run_id, task_template_id, assignee_user_id, source[generated|manual], edited_by nullable, edited_reason nullable)
- `task_completions` (id, assignment_item_id, completed_by, completed_at, manager_confirmed_by nullable, manager_confirmed_at nullable)
- `audit_events` (id, actor_user_id, action_type, entity_type, entity_id, payload_json, created_at)
- `auth_attempts` (id, identifier, ip_hash_or_token, success, occurred_at)

Notes:
- Keep schema tenant-ready (e.g., optional future `tenant_id` migration path).
- Keep weight/estimated minutes fields nullable for future weighting sprint.

---

## Page/Route Responsibilities (MVP)

### Manager/Admin

- `/login`
- `/manager`
- `/manager/people`
- `/manager/job-codes`
- `/manager/tasks`
- `/manager/imports` (or per-entity import tabs)
- `/manager/weeks/<week>/generate`
- `/manager/weeks/<week>/draft`
- `/manager/weeks/<week>/post`
- `/manager/weeks/<week>/completions`
- `/manager/reports`
- `/manager/audit`

### Crew

- `/crew` (PIN entry / landing)
- `/crew/tasks`
- `/crew/tasks/<assignment_item_id>`

### Shift Lead

- `/lead/board`
- `/lead/reassign`

### Owner

- `/owner/login`
- `/owner/reports`
- `/owner/reports/weekly`

### Shared

- `/403`
- `/404`

---

## Import UX Contract (v1)

- Input methods:
  - CSV upload
  - Plain text paste/upload
- Plain text grammar:
  - `value`
  - `value|jobcode` (when job-code mapping is relevant)
- Validate before commit and show line-level errors.
- No advanced mapping wizard.
- On successful import, records become editable/deletable via normal CRUD pages.
- All import commits write audit events.

---

## Security / Abuse Controls

- Role checks enforced server-side (never UI-only).
- CSRF on all state changes.
- Auth endpoint throttling + lockout handling.
- Session cookie hardening (secure, httponly, samesite appropriate for deployment).
- Input validation and output escaping.
- Minimal sensitive logging; hash or redact where practical.

---

## Reporting Contract (v1)

- Person-centric metrics:
  - assigned count
  - completed count
  - completion %
  - task frequency breakdown
- Task-centric metrics:
  - assignee distribution per task
  - completion % per task
  - consistency trend over selectable window
- Filters:
  - week/date range
  - job code
  - person
  - task

---

## Build Order Recommendation

1. Auth + role guardrails + lockout baseline.
2. People/job code/task template CRUD.
3. Import pipeline + parser + validation + audit.
4. Assignment draft/post lifecycle.
5. Crew completion + manager confirmation.
6. Reports + audit views.
7. Owner views + weekly email.
8. Operational hardening + validation pass.
