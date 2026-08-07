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
