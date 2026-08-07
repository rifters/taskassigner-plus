# Decisions

Record durable decisions future sprints must respect.

---

## Decision Log

| Date | Decision | Reason | Impact |
|---|---|---|---|
| 2026-07-08 | **MVP boundary (smallest useful v1):** manager can generate/review/post assignments; crew can view/complete via QR + PIN; owner receives weekly email summary; no public self-signup. | Fastest path to replace paper workflow and remove manager bottleneck. | Sprint scope stays centered on assignment lifecycle, completion, and reporting. |
| 2026-07-08 | **MVP page inventory approved:** manager/admin pages (`/login`, `/manager`, people, job codes, task templates, weekly generate/draft/post/completions, reports, audit); crew pages (`/crew`, `/crew/tasks`, `/crew/tasks/:id`); shift lead pages (`/lead/board`, `/lead/reassign`); owner read-only pages (`/owner/login`, `/owner/reports`, `/owner/reports/weekly`); shared `/403` + `/404`. | Keeps Builder scope executable and explicit. | Route-level responsibilities and role access must be enforced server-side. |
| 2026-07-08 | **Import UX parity:** people, job codes, and task templates support simple CSV or plain-text import, then normal add/edit/delete. | Fast onboarding and simple day-to-day maintenance. | Builder must implement import + CRUD for all three entities. |
| 2026-07-08 | **Plain-text import format (v1):** line-based input supports `value` and optional `value|jobcode` where mapping is needed. | Lightweight format without a mapping wizard. | Parser + validation rules must be explicit in blueprint/tests. |
| 2026-07-08 | **Task ownership rule:** each task/template requires one responsible job code. | Assignment and reporting integrity. | Reject orphan tasks in import and manual forms. |
| 2026-07-08 | **Reporting depth:** include person-centric and task-centric metrics (who gets each task, per-task completion %, consistency trends). | Need to detect repeat non-completion and distribution patterns. | Reports must support drill-down and filtering by week/job code/person/task. |
| 2026-07-08 | **Auth model:** invite-only lifecycle (manager-administered); no public registration. | External-facing risk posture + controlled workforce context. | Requires manager-admin user management and role-aware auth flows. |
| 2026-07-08 | **Role auth UX:** crew PIN-only; shift lead/manager/owner password auth. | Lower crew friction while protecting privileged roles. | Distinct auth paths/policies by role. |
| 2026-07-08 | **Session policy:** manager/lead 8h, crew 12h, owner 24h read-only; no remember-me in v1. | Balance usability with security. | Explicit TTL/reauth behavior required. |
| 2026-07-08 | **Lockout/reset:** 5 failed attempts => 15-minute lock; manager resets crew PINs; manager/owner email reset for passwords. | Mitigate brute force and preserve recovery. | Requires lockout tracking, reset flows, audit events. |
| 2026-07-08 | **PII scope v1:** name, role, PIN/password hash, optional email (non-crew optional), and minimal audit/activity metadata. | Minimum data needed for operations/accountability. | Enforce redaction, least privilege, and safe logging. |
| 2026-07-08 | **Compliance stance:** internal-policy handling only for now; no formal pre-go-live checkpoint chosen. | Client decision during discovery. | Continue sensitive-data baseline; revisit if formal obligations emerge. |
| 2026-07-08 | **Threat priorities:** PIN brute force, privilege escalation, forged completion events. | Highest practical abuse risks for this workflow. | Security controls/tests prioritize these vectors first. |
| 2026-07-08 | **Rate limiting baseline:** strict auth limits (target 5/min per IP + per account), moderate general API limits. | Protect login surfaces and reduce abuse. | Include limit behavior in architecture/validation. |
| 2026-07-08 | **Tenancy stance:** v1 single-tenant deployment with tenant-ready migration path. | Match immediate needs without overbuilding. | Data model should avoid hard dead-ends for future multi-tenant support. |
| 2026-07-08 | **Scale assumption (12 months):** ~25–80 crew users, ~100–500 assignments/week, <20 concurrent users. | Practical baseline for stack choices. | SQLite acceptable for v1 with indexing + backups + observability. |
| 2026-07-08 | **Observability baseline:** structured app logs, auth/audit logs, daily SQLite backups, uptime checks, manager email alerts. | Minimum reliability for external-facing usage. | Validation must include operational checks and failure paths. |
| 2026-07-08 | **Sprint exclusions:** no schedule import, no task weight scoring behavior, no multi-location in first implementation sprint. | Prevent scope creep. | Keep build focused and deliverable. |
| 2026-07-08 | **Sprint 002 scope:** implement role pages for manager + crew + owner in one sprint. | User approved Architect recommendation for daily usability first. | Builder should prioritize page workflows over new backend feature classes. |
| 2026-07-08 | **Crew history rule:** show last 4 weeks of crew completion history. | Operationally useful without heavy analytics complexity. | Adds bounded history query + UI card/table requirement. |
| 2026-07-08 | **Crew notes policy:** notes allowed for incomplete tasks; write-once only. | Preserve audit integrity and practical issue reporting. | Notes become immutable records; no edit/delete in v1. |
| 2026-07-08 | **Manager override completion:** manager can mark completion on behalf of crew but reason is mandatory. | Real floor operations include staff who will not use device flow reliably. | Completion model/reporting must distinguish self-completed vs manager-completed with reason. |
