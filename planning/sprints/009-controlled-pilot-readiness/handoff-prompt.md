# Builder Handoff — Sprint 009 Controlled Pilot Readiness

Implement only from `requirements.md`, `blueprint.md`, and `acceptance.md` in this sprint folder. Before source changes, inspect the current auth routes/security helpers, CSRF and audit patterns, config/startup, scheduler/email paths, backup utility, operations docs, and relevant tests.

Before editing any source or test file, stop at the Builder code gate and provide a concrete file-by-file implementation plan, scope guards, and acceptance mapping. Wait for explicit approval of that implementation plan.

First close the P0 credential-management authorization flaw. Authorization must come from the authenticated session and server-side role/target checks; a submitted actor name must never grant authority. Preserve CSRF, rate limiting, lockouts, safe errors, auditability, and secret-safe output. Add focused abuse/regression coverage.

Then perform only the minimum pilot hardening and verification described in the sprint files: explicit production/demo configuration checks, supervised access and scheduler documentation, backup/restore drill, monitoring and failure visibility, safe email verification, realistic non-secret pilot-data rehearsal, and the pilot runbook/go/no-go checklist. Do not add schedule importing, weighting, capacity, multi-location, native mobile, custom PDF, deployment automation, or unrelated refactors.

Do not send unsolicited email, expose credentials, commit, push, or modify unrelated files. Run focused tests, full tests, compileall, `git diff --check`, schema initialization, backup/restore verification, demo safety checks, and real local HTTP/browser smoke checks. Update planning and operations documentation only after evidence exists.
