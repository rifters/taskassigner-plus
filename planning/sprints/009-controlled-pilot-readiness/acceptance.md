# Sprint 009 Acceptance — Controlled Pilot Readiness

- [ ] Anonymous requests cannot perform privileged credential-management actions.
- [ ] Crew and unauthorized roles cannot perform manager/owner credential actions.
- [ ] Caller-supplied `actor_name` cannot grant or spoof authorization.
- [ ] Authorized manager/owner flows succeed only for permitted targets and create safe audit events.
- [ ] CSRF, rate-limit, lockout, invalid-target, and failure paths remain enforced and tested.
- [ ] No passwords, PINs, hashes, reset tokens, secrets, or connection strings appear in pages, logs, tests, or planning artifacts.
- [ ] Pilot configuration explicitly disables demo mode and documents the deferred host-PC access and scheduler steps.
- [ ] Backup destination, schedule, retention, permissions, failure handling, and owner are documented.
- [ ] A restore drill succeeds into a separate database.
- [ ] Restored schema, users, assignments, completions, audit history, and authorized login are verified.
- [ ] Locally testable health and application/scheduler failure behavior are verified; external monitoring and alert setup are documented as host-PC follow-up.
- [ ] Weekly email rendering, recipient resolution, and CSV attachment are verified using a safe captured test path; production SMTP delivery remains host-PC follow-up.
- [ ] Fresh realistic pilot data is reconciled without storing credentials in project artifacts.
- [ ] A local Thursday–Wednesday manager-to-crew-to-report rehearsal passes.
- [ ] The rehearsal verifies crew self-completion, manager on-behalf completion, prior-week `not_completed` finalization, statistics, and email reporting.
- [ ] Pilot runbook includes owner, access procedure, paper fallback, rollback/recovery, incident steps, and go/no-go checklist.
- [ ] Existing assignment, completion, reporting, API, and audit behavior remains green.
- [ ] Schedule import, weighting/capacity, multi-location, native mobile, custom PDF, and unrelated feature work remain deferred.
- [ ] Full tests, compilation, whitespace checks, database initialization, and local smoke validation pass.

- [ ] Host-PC installation, hosting, external monitoring, production SMTP, and real scheduler registration are explicitly recorded as deferred, not silently treated as complete.

## Pilot Decision

The sprint is complete only when the checklist has an explicit **GO**, **NO-GO**, or **GO WITH CONDITIONS** decision. Passing automated tests alone is not a pilot approval.
