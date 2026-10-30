# Project State

**Project:** TaskAssigner+  
**Client:** Rifters / Eric  
**Last updated:** 2026-09-02

---

## Current Phase

Sprint 009 pilot-readiness hardening is in progress. The credential-management authorization fix, production safety guards, operational runbook, and local backup/restore drill are implemented or verified. The host PC is currently unavailable, so host installation, hosting, external monitoring, production SMTP, and real scheduler registration are deferred. Local pilot-data rehearsal and the final go/no-go decision remain open.

---

## Current Status

Sprints 001–008 remain complete and verified. Sprint 009 now requires authenticated manager authorization for credential-management routes, rejects unsafe production demo/default-secret configuration, and documents backup/restore, monitoring, scheduler, fallback, and go/no-go procedures. The local backup/restore drill passed against a separate database. The local demo health endpoint returns `{"ok": true}` and unauthenticated manager access redirects as expected. Full verification is green at 84 tests, compilation, and whitespace validation. Real pilot data, the local manual Thursday–Wednesday rehearsal, and the final decision remain outstanding; host-PC operations are deferred until that machine is available.

---

## Active Sprint

`planning/sprints/009-controlled-pilot-readiness/`

---

## Verification Snapshot

- Focused: `python -m pytest tests/test_imports.py tests/test_sprint007.py -q` → `16 passed`
- Focused Sprint 009: auth/CSRF/acceptance/backup/email suites → `30 passed`
- Full: `python -m pytest tests -q` → `84 passed` (16 existing SQLAlchemy deprecation warnings)
- Demo reset script: `python scripts/reset_demo.py` → `DEMO_RESET_OK` with one seeded exclusion.
- Compile and whitespace checks: `python -m compileall -q src scripts/reset_demo.py` and `git diff --check` passed.
- HTTP smoke: `/health`, `/auth/login-crew`, and combined CSV export → `200`.
- Acceptance criteria: all Sprint 007 items checked.

---

## Next Actions

1. Load and reconcile realistic pilot data, then execute and record the complete local manager-to-crew-to-report workflow manually.
2. Complete the Sprint 009 local verification and go/no-go readiness decision; keep the paper fallback active until host checks are complete.
3. When the host PC is available, configure production mode, supervised hosting, backups/retention, monitoring/alerts, SMTP, and scheduler ownership, then repeat the restore and end-to-end checks.
4. Carry forward SQLAlchemy `Query.get()` deprecation cleanup as technical debt.
5. Keep schedule importing deferred until explicitly planned; initial scope may be day-level work detection from Harri PDF, while time availability and analytics remain later phases.

---

## Blockers

No blocker for the posted-week/completion-review workflow. Pilot-readiness blockers remain documented in `planning/REALWORLD_TEST_READINESS.md`.

---

## Watch Items

- Keep strict scope guard (no schedule-import engine, no weighting behavior, no multi-location).
- Avoid frontend framework/build-pipeline expansion unless explicitly planned.
- Preserve auditability, authz, and secret-safe logging.
- Use `planning/REALWORLD_TEST_READINESS.md` as the gate checklist before a controlled pilot.
