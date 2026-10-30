# Sprint 009 Pilot Runbook and Verification Record

## Purpose

Operational checklist for a controlled TaskAssigner+ pilot. This document contains no credentials or secret values.

## Ownership

- Pilot owner: ____________________
- Backup/restore owner: ____________________
- Scheduler/monitoring owner: ____________________
- Pilot dates: ____________________

## Preflight

- [ ] Host-PC deployment items are deferred until that machine is available; local verification is not a live-pilot approval
- [ ] `ENVIRONMENT=production`
- [ ] `DEMO_MODE=false`
- [ ] Non-default secret configured outside the repository
- [ ] Supervised access path verified
- [ ] SMTP/scheduler configuration verified with safe test transport
- [ ] Fresh non-demo database selected
- [ ] Roster and role counts reconciled
- [ ] Job-code memberships reconciled
- [ ] Numbered master lists reconciled
- [ ] Task exclusions reconciled
- [ ] Credential/PIN distribution procedure approved; no credentials stored here

## Recovery

- [ ] Backup destination is restricted and documented
- [ ] Backup schedule and retention owner assigned
- [ ] Latest backup result checked
- [ ] Restore completed into a separate database
- [ ] Restored schema initialized/upgraded
- [ ] Restored users, assignments, completions, and audit records verified
- [ ] Authorized login verified against the restored database

## End-to-end rehearsal

- [ ] Manager selects a Thursday start and generates a draft
- [ ] Manager reviews and posts the Thursday–Wednesday week
- [ ] Crew views assignments from the crew path
- [ ] Crew self-completes an assignment
- [ ] Manager completes an assignment on behalf with a reason
- [ ] An unfinished prior-week assignment is finalized as `not_completed`
- [ ] Statistics report shows the expected date range and rankings
- [ ] Weekly summary and assignment-level CSV are captured and checked
- [ ] Printed/paper fallback is available

## Incident and fallback

If the app, access path, database, scheduler, or email fails:

1. Keep the paper task list and signature process active.
2. Notify the pilot owner; do not repeatedly retry destructive actions.
3. Preserve the latest backup and relevant redacted logs.
4. Restore only into a separate database until the restore is verified.
5. Reconcile paper completions into the application using manager on-behalf completion with an accurate reason.

## Verification evidence

- Focused automated tests: ____________________
- Full automated tests: ____________________
- Compilation and whitespace checks: ____________________
- Backup/restore drill result: ____________________
- Health check result: ____________________
- Scheduler/email test result: ____________________
- Manual rehearsal result: ____________________

## Decision

- [ ] GO
- [ ] GO WITH CONDITIONS
- [ ] NO-GO

Decision owner: ____________________  Date: ____________________  Notes: ____________________
