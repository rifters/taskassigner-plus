============================================================
FILE: planning/STATUS.json
============================================================
{
  "schemaVersion": 1,
  "phase": "apply-pack",
  "sprint": "003-ui-shell-balanced",
  "updated": "2026-07-08T22:10:00-04:00"
}

============================================================
FILE: planning/STATE.md
============================================================
# Project State

**Project:** TaskAssigner+  
**Client:** Rifters / Eric  
**Last updated:** 2026-07-08

---

## Current Phase

Architect planning for Sprint 003 is complete and ready for Builder apply/execute.

---

## Current Status

Sprint 001 backend/API scope remains complete and verified.  
Sprint 002 workflow-pages sprint is complete and verified with acceptance-mapped evidence.  
Sprint 003 is approved for implementation focus on a visible UI shell plus balanced UX polish and ops hardening.

Sprint 003 planning decisions now locked:
- Start with a usable server-rendered visual shell for manager, crew, and owner workflows.
- Keep backend contracts from Sprint 002 as the data source for initial UI pages.
- Add practical UX polish (clarity, feedback, status readability) without broad redesign scope.
- Add ops hardening in parallel (smoke checks, route coverage, guardrails) without changing product boundaries.

---

## Active Sprint

`planning/sprints/003-ui-shell-balanced/`

---

## Verification Snapshot (from completed Sprint 002)

- Focused: `python -m pytest tests/test_workflow_pages.py -q` → `8 passed`
- Full: `python -m pytest tests -q` → `38 passed`
- Ad-hoc verification: temp `hermes-verify-*` scripts under `C:\Users\Sobee\AppData\Local\Temp` validated workflow guard behavior (`VERIFY_OK`, `CLEANUP_OK`).

---

## Next Actions

1. Builder applies Architect Pack 003 (dry-run, then apply).
2. Builder implements only Sprint 003 files under `planning/sprints/003-ui-shell-balanced/`.
3. Builder stops at code gate before source/test edits and waits for explicit build approval.
4. Builder refreshes `planning/ARCHITECT_BRIEFING.md` at sprint close with visual UX evidence + verification evidence.

---

## Blockers

No planning blocker for Sprint 003.

---

## Watch Items

- Keep strict scope guard (no schedule-import engine, no weighting behavior, no multi-location).
- Avoid frontend framework/build-pipeline expansion in this sprint.
- Preserve auditability, authz, and secret-safe logging while adding UI.

============================================================
FILE: planning/DECISIONS.md
============================================================
# Decisions

Record durable decisions future sprints must respect.

---

## Decision Log

| Date | Decision | Reason | Impact |
|---|---|---|---|
| 2026-07-08 | **MVP boundary (smallest useful v1):** manager can generate/review/post assignments; crew can view/complete via QR + PIN; owner receives weekly email summary; no public self-signup. | Fastest path to replace paper workflow and remove manager bottleneck. | Sprint scope stays centered on assignment lifecycle, completion, and reporting. |
| 2026-07-08 | **MVP page inventory approved:** manager/admin pages (`/login`, `/manager`, people, job codes, task templates, weekly generate/draft/post/completions, reports, audit); crew pages (`/crew`, `/crew/tasks`, `/crew/tasks/:id`); shift lead pages (`/lead/board`, `/lead/reassign`); owner read-only pages (`/owner/login`, `/owner/reports`, `/owner/reports/weekly`); shared `/403` + `/404`. | Keeps Builder scope executable and explicit. | Route-level responsibilities and role access must be enforced server-side. |
| 2026-07-08 | **Import UX parity:** people, job codes, and task templates support simple CSV or plain-text import, then normal add/edit/delete. | Fast onboarding and simple day-to-day maintenance. | Builder must implement import + CRUD for all three entities. |
| 2026-07-08 | **Plain-text import format (v1):** line-based input supports `value` and optional `value\|jobcode` where mapping is needed. | Lightweight format without a mapping wizard. | Parser + validation rules must be explicit in blueprint/tests. |
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
| 2026-07-08 | **Sprint 003 strategy:** balanced path = build a thin server-rendered UI shell first, then apply targeted UX polish plus ops hardening in same sprint. | Current system is JSON-first; visual UX cannot be evaluated/polished without an actual screen layer. | Builder must implement templates/static styling + keep backend contracts stable + add smoke/guard coverage. |

============================================================
FILE: planning/DOMAIN.md
============================================================
# Domain Context

This file captures operating context for TaskAssigner+.

---

## Client

Rifters / Eric

---

## Business Goal

A web-based weekly task assignment system for restaurant teams that fairly distributes tasks across job-code-based crew pools, tracks completion, and reports productivity to management.

---

## Audience / Rigor Tier

External-facing (untrusted users). Security, authorization, abuse prevention, and auditability are first-class requirements.

---

## Primary Users / Roles

- **Crew** — view own weekly assignments; mark complete from phone/browser via QR flow.
- **Shift Lead** — crew capabilities plus board visibility and reassignment actions.
- **Manager (Eric)** — full operational control: users, job codes, templates, constraints, generation, review/edit/post, confirmations, reports.
- **Owner** — read-only reporting dashboard + weekly summary email.

---

## Current Workflow

1. Manager adjusts crew pool manually.
2. Algorithm creates draft.
3. Manager reviews fairness and manually tweaks.
4. Manager posts assignments.
5. Crew completes work; manager tracks manually.
6. Manager prints/signs paper report and hand-delivers to owner.

---

## Target Workflow

1. Manager adjusts crew pools in app.
2. System generates weekly draft by job code using fairness/rotation constraints.
3. Manager reviews fairness/task distribution and applies edits (optionally with reason).
4. Manager posts assignments.
5. Crew accesses tasks via QR/URL and marks complete (timestamped).
6. Crew can leave write-once notes, including incomplete-task explanations.
7. Manager can mark completion on behalf of crew with mandatory reason.
8. Manager confirms completions as separate state when needed.
9. Manager/owner review person-centric + task-centric consistency reports.
10. Owner receives automated weekly summary email.
11. Manager/crew/owner workflows are visually usable in browser via lightweight server-rendered pages.

---

## Key Terms

- **Job code** — operational crew group (Cooks, Servers, Hosts, SAs, etc.).
- **Crew pool** — eligible users for a generation run.
- **Draft assignment** — generated, editable pre-post state.
- **Posted assignment** — published weekly assignment visible to crew.
- **Fairness spread** — distribution indicator for task balance across eligible crew.
- **Completion confirmation** — manager verification state after crew completion.
- **Task-centric report** — analytics by task: assignment distribution + completion consistency.
- **Audit event** — immutable record for sensitive actions (who/what/when).
- **On-behalf completion** — manager marks completion for a crew user with required reason.

---

## Business Rules

- Invite-only user lifecycle for v1 (no public signup).
- Crew uses PIN auth; privileged roles use password auth.
- Lockout: 5 failed attempts => 15-minute lock.
- Manager can reset crew PINs; manager/owner password resets via email flow.
- People, job codes, and task templates support bulk import from CSV or plain text.
- Plain-text import supports `value` and optional `value|jobcode` where mapping applies.
- After import, manager can add/edit/delete single records.
- Every task/template must reference one responsible job code.
- Manual pool adjustments and draft edits must be auditable.
- Draft and posted states are distinct; posting is explicit.
- Completion timestamp is required; manager confirmation is separate.
- Crew notes are write-once; in v1 they can be attached to incomplete-task explanations.
- Manager on-behalf completion requires mandatory reason and audit trace.
- Crew history view is limited to last 4 weeks in v1.
- v1 is single-tenant with future tenantization path.
- Sprint 003 introduces a lightweight visual UI shell without introducing a frontend framework/build pipeline.

---

## Out of Scope (v1 / first implementation sprint)

- Schedule import from Altametrics PDF tables
- Task weighting/difficulty behavior (schema extensibility only)
- Multi-location support
- Native mobile app
- Slack/Teams integrations
- Predictive ML analytics
- Push notifications

---

## Systems / Integrations

- Denny's in-store WiFi (crew LAN access)
- Cloudflare Tunnel (public HTTPS)
- Tailscale (private manager/owner access)
- QR code entry for crew
- SMTP-based weekly owner report email

---

## Deferred / Unknown

- Altametrics currently only provides PDF print tables; no direct CSV export.
- Task weighting direction chosen for future: hybrid (weight + estimated minutes), deferred.
- No formal external compliance framework selected yet; internal-policy handling in effect.

============================================================
FILE: planning/RISKS.md
============================================================
# Risks

Known project risks and mitigation notes.

---

| Risk | Likelihood | Impact | Mitigation | Status |
|---|---:|---:|---|---|
| PIN brute-force against crew auth | Medium | High | Lockouts, strict auth rate limits, failed-attempt auditing, alert thresholds. | Active |
| Privilege escalation / horizontal data access | Medium | High | Server-side role checks on every endpoint, per-role tests, deny-by-default authorization. | Active |
| Forged completion events | Medium | High | Ownership checks, immutable audit records, manager confirmation state, tamper-resistant logs. | Active |
| Public tunnel attack surface | Medium | High | HTTPS only, secure cookie/session settings, CSRF defense, input validation, dependency hygiene. | Active |
| Sensitive data leakage in logs | Low | High | Structured logs with redaction policy, no secrets/PIN/password logs, restricted log access. | Active |
| Scope creep in first build sprint | High | Medium | Enforced in/out-of-scope list, acceptance gates, explicit exclusions. | Active |
| Cold-start fairness quality in week one | Medium | Medium | Mark first-cycle caveat in UI/reporting, allow manager override with audit trail. | Accepted |
| Operational fragility (backup/alerts absent) | Medium | High | Daily backups, restore verification steps, uptime/error alerts to manager. | Active |
| Manager override misuse (false completions) | Medium | High | Mandatory reason + actor attribution + reporting distinction between self and on-behalf completion. | Active |
| Notes abuse/noise or accidental sensitive content | Medium | Medium | Short note length cap, input sanitization, write-once immutability, manager-visible context. | Active |
| UI shell regressions break existing role flows | Medium | High | Keep backend contracts stable; add route-level smoke tests across manager/crew/owner before/after UI wiring. | Active |
| Mobile readability too poor for crew usage | Medium | High | Mobile-first crew page constraints (single-column, large tap targets, concise status states) + manual viewport checks. | Active |

============================================================
FILE: planning/QUESTIONS.md
============================================================
# Open Questions

Questions that need answers from Architect/Builder/Client.

---

## Discovery Gate Resolution (2026-07-08)

Mandatory External-facing discovery topics were answered or explicitly deferred with rationale. No blocking discovery gate item remains for Pack 001.

---

## Sprint 002 Resolution Notes (2026-07-08)

All Sprint 002 planning decisions requested in Architect conversation are resolved and approved.

- Include all role pages in Sprint 002: **answered**.
- Crew history window: **last 4 weeks**: **answered**.
- Notes on incomplete tasks allowed: **answered**.
- Notes edit policy: **write-once**: **answered**.
- Manager on-behalf completion allowed: **answered**.
- On-behalf completion reason required: **answered**.

No blocker question remains for Architect Pack 002 generation.

---

## Sprint 003 Resolution Notes (2026-07-08)

Sprint 003 direction is approved:

- Start with debug-usable visual UX shell before polish decisions.
- Execute balanced path: UX polish + ops hardening in same sprint.
- Keep existing scope guard and backend behavior boundaries.

No blocker question remains for Architect Pack 003 generation.

---

## Deferred Tracking

| Question | Owner | Needed By | Status | Answer / Notes |
|---|---|---|---|---|
| Scheduling source/export for future import? | Client | Before schedule-import sprint | Answered (deferred) | Source is Altametrics; currently only PDF table print output. Import strategy deferred. |
| Future task-weight model direction? | Client + Architect | Before weighting sprint | Answered (deferred) | Hybrid model (manager weight + estimated minutes) chosen for future. |
| Formal compliance obligations beyond internal policy? | Client/Legal | Before production hardening if requirements emerge | Answered (current stance) | Internal-policy handling for now; no formal checkpoint selected at this stage. |

============================================================
FILE: planning/sprints/003-ui-shell-balanced/requirements.md
============================================================
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

============================================================
FILE: planning/sprints/003-ui-shell-balanced/blueprint.md
============================================================
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

============================================================
FILE: planning/sprints/003-ui-shell-balanced/acceptance.md
============================================================
# Sprint 003 Acceptance Criteria — Builder Checkable

Sprint is complete only when all items pass or are explicitly deferred with rationale.

---

## A. Visual Shell Exists

- [ ] Manager workflow is available as rendered page(s), not JSON-only.
- [ ] Crew workflow is available as rendered page(s), not JSON-only.
- [ ] Owner reporting workflow is available as rendered page(s), not JSON-only.
- [ ] Shared layout provides readable navigation/context for role pages.

## B. UX Baseline Quality

- [ ] Manager page shows clear next actions (generate/draft/post/completions/schedule).
- [ ] Crew page is mobile-usable (single-column readability + touch-friendly actions).
- [ ] Crew page clearly communicates note write-once policy.
- [ ] Owner page clearly indicates read-only status.
- [ ] Success/failure states are visible and understandable in-page.

## C. Behavior Integrity

- [ ] Existing Sprint 002 workflow behavior remains functional.
- [ ] Manager on-behalf completion still requires reason.
- [ ] Completion source/reason remains persisted and retrievable.
- [ ] Crew notes still support general + incomplete-context and remain write-once.
- [ ] Crew 4-week history bound remains intact.

## D. Security + Authz

- [ ] Role-based authorization enforced on all new/updated page routes.
- [ ] Cross-role access attempts to protected pages are denied.
- [ ] State-changing actions preserve CSRF protections.

## E. Ops Hardening

- [ ] Route smoke coverage exists for manager/crew/owner visual endpoints.
- [ ] Regression coverage exists for at least one critical page-flow guard.
- [ ] Logging remains redacted for sensitive auth payload fields.

## F. Scope Guard

- [ ] No schedule-import engine implementation.
- [ ] No weighting behavior implementation.
- [ ] No multi-location implementation.
- [ ] No frontend framework/build pipeline introduction.

============================================================
FILE: planning/sprints/003-ui-shell-balanced/handoff-prompt.md
============================================================
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
