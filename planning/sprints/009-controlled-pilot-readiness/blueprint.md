# Sprint 009 Blueprint — Controlled Pilot Readiness

## 1. Authorization Hardening

Inspect `src/taskassigner/routes/auth.py`, `src/taskassigner/security.py`, existing role guards, CSRF helpers, audit helpers, and auth tests before editing. For password-reset requests and PIN-reset actions, establish authorization from the authenticated session and server-side target lookup. A form/API `actor_name` may be retained only as display or compatibility input; it must never grant manager authority. Preserve rate limits, lockouts, CSRF, safe response behavior, and audit attribution. Never return reset tokens or credentials in test output.

Test the matrix: anonymous denied, crew/shift lead denied where applicable, manager/owner allowed only for permitted targets, forged actor rejected, invalid target handled safely, CSRF rejected, and successful authorized action audited.

## 2. Pilot Configuration and Operations

Inspect existing config, startup entrypoint, owner scheduler route/script, SMTP guards, health route, and `docs/OPERATIONS.md`. Add only the minimum configuration checks/documentation needed to make pilot mode explicit and fail closed where unsafe. Demo reset/seed must remain development-only. Document the future supervised process, Cloudflare/Tailscale access boundary as applicable, scheduler command/trigger, log location and redaction expectations, and operator ownership. Validate locally; do not attempt host installation, hosting, tunnel setup, external monitoring, production SMTP, or deployment infrastructure while the host PC is unavailable.

## 3. Backup and Restore Drill

Use the existing SQLite backup utility. Document destination, naming/retention, schedule, permissions, failure handling, and restore owner. Run the backup against a disposable or pilot fixture, restore to a separate database, initialize/upgrade schema, and verify representative records and authorized login. Capture only safe evidence: paths may be generalized and secrets must be redacted. Add or extend tests for retention/restore behavior only where the existing utility has a testable gap.

## 4. Monitoring and Email Verification

Verify `/health` locally, application error visibility, and scheduler failure visibility. Exercise email rendering and recipient resolution using a captured test transport or equivalent; do not send unsolicited real mail. Document the external alert destination as a host-PC follow-up. Keep the existing recipient rule: active managers and owners with valid deduplicated addresses; no crew or shift leads.

## 5. Realistic Rehearsal and Runbook

Create a non-secret pilot data checklist and use a fresh non-demo database or disposable pilot fixture. Reconcile counts for people, roles, job codes, task templates, numbers, exclusions, and expected weekly assignments. Manually execute one complete Thursday–Wednesday cycle, including a crew self-completion, a manager on-behalf completion with reason, an unfinished assignment finalized as `not_completed`, statistics, and the summary email plus CSV attachment. Record pass/fail evidence in the runbook and define paper fallback, rollback, pilot owner, and exit criteria.

## Validation

Run focused auth/CSRF/backup/email tests, the full suite, compilation, `git diff --check`, database initialization, backup/restore drill, demo reset safety check, and local HTTP/browser smoke for manager and crew workflows. Update `planning/STATE.md`, `planning/DECISIONS.md`, `planning/RISKS.md`, `docs/API.md`, and `docs/OPERATIONS.md` only with verified results.
