# TaskAssigner+ Architecture

## 1. System Overview

TaskAssigner+ is a role-based web app for weekly restaurant task assignment, completion capture, and management/owner reporting.

Core principles:
- low-friction crew usage,
- strict server-side role boundaries,
- auditable operational edits,
- practical MVP scope with future extensibility.

## 2. Runtime Stack

- Python 3
- Flask
- Flask-Login
- Flask-SQLAlchemy
- Flask-Bcrypt
- SQLite
- Vanilla JS + HTML/CSS

## 3. Access Topology

- Public HTTPS via Cloudflare Tunnel for workforce access.
- Private remote access via Tailscale for manager/owner.
- Session and auth policies differ by role.

## 4. Domain Components

- Identity/Auth
- Workforce setup (people/job codes/task templates)
- Imports (CSV/plain text)
- Assignment engine workflow (draft/review/post)
- Completion capture/confirmation
- Completion context capture (crew notes + manager on-behalf reason)
- Reporting (person-centric and task-centric)
- Audit trail
- Owner weekly summary delivery

## 5. Security Model (v1)

- Invite-only accounts.
- Crew PIN auth; privileged password auth.
- Lockout/rate limit defenses on auth surfaces.
- CSRF + input validation + output escaping.
- Hardened session cookie settings.
- Least-privilege role checks in server endpoints.

## 6. Data Persistence

SQLite is acceptable for projected v1 scale.

Required supporting practices:
- indexing for hot query paths,
- pagination for report/audit views,
- daily backup routine,
- restore verification procedure.

## 7. Reporting Architecture

Reports must support both:
- **Person-centric** performance summaries,
- **Task-centric** consistency analysis (distribution + completion trends),
- clear completion source context (self vs on-behalf) where applicable.

## 8. Extensibility Hooks

- Nullable `weight` and `estimated_minutes` fields reserved.
- Data model should remain migration-friendly for future `tenant_id` introduction.
- Schedule import intentionally deferred until viable source format exists.

## 9. Risks Driving Design

- unauthorized access and role leakage,
- forged completion updates,
- missing audit trails for manual edits,
- operational blind spots without backup/alerts.

Architecture and validation plans prioritize these risks.
