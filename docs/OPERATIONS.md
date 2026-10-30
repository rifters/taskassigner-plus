# Operational Notes (Builder Sprint 001)

## Daily SQLite Backup

Preferred script (testable):

```bash
python scripts/backup_sqlite.py
```

Environment overrides:

- `TASKASSIGNER_DB_PATH` (default: `taskassigner.db`)
- `TASKASSIGNER_BACKUP_DIR` (default: `backups`)

## Owner Weekly Schedule Runner

For actual recurring schedule execution, run this script from your scheduler (Windows Task Scheduler / cron / automation service):

```bash
python scripts/run_scheduled_owner_email.py
```

Optional environment flags:

- `TASKASSIGNER_SCHEDULE_FORCE=1` to force run outside due window.
- `TASKASSIGNER_SCHEDULE_DRY_RUN=1` to validate due/send decision without sending.

The script exits non-zero on configuration/runtime failure (e.g., missing recipient/SMTP), which makes it alert-friendly.

## Uptime and Error Alert Baseline

- Health endpoint: `GET /health`
- Hook external monitor (Uptime Kuma, Better Stack, etc.) to check every minute.
- Alert path for failures: manager email/channel.

Testability baseline:

- A monitor can assert `200` + JSON `{ "ok": true }` from `/health`.
- Failed checks should route to manager alert target.

## Logging Baseline

- Structured request logs are emitted per request with method/path/status/duration.
- Sensitive payload keys are redacted (`password`, `pin`, `new_pin`, `smtp_password`).
- Do not log raw credentials or secrets.

## Controlled Pilot Runbook

Before pilot use, set `ENVIRONMENT=production`, set `DEMO_MODE=false`, provide a non-default `SECRET_KEY`, and use the supervised private/public access path approved for the site. Never place these values in this repository or in logs. The application refuses production startup when demo mode is enabled or the default development secret is used.

### Backup and restore

- Run `python scripts/backup_sqlite.py` daily from the host scheduler.
- Set `TASKASSIGNER_DB_PATH` to the pilot database and `TASKASSIGNER_BACKUP_DIR` to a restricted backup directory.
- Keep backups on a separate protected location with an operator-defined retention policy; the current utility safely replaces the latest copy and must be paired with host-level versioned snapshots or rotation for historical retention.
- The pilot owner is responsible for checking the scheduler result and preserving the latest known-good backup.
- Restore only to a separate database first. Run schema initialization, verify `/health`, authorized login, roster, assignments, completions, and audit history, then schedule any production replacement during a controlled outage.

### Scheduler and monitoring

- Run `python scripts/run_scheduled_owner_email.py` from Windows Task Scheduler or an equivalent supervised scheduler.
- A non-zero scheduler exit is an operational failure and must alert the pilot owner.
- Monitor `GET /health` every minute and alert the pilot owner when it is not HTTP 200 with `{ "ok": true }`.
- Retain application logs with restricted access; request payload redaction must remain enabled.
- Use a captured test transport for email checks. Do not send test reports to real recipients without explicit approval.

### Pilot workflow and fallback

1. Reconcile the roster, roles, job-code memberships, numbered task lists, and exclusions in a fresh non-demo database.
2. Generate a Thursday–Wednesday draft, review fairness, and post it.
3. Confirm one crew self-completion and one manager on-behalf completion with a reason.
4. Open the next current-week completion review so unfinished prior-week work is finalized as `not_completed`.
5. Verify statistics, the weekly summary, and the CSV attachment using a captured email path.
6. If the app or email path is unavailable, use the printed task list and paper completion/signature process; record the event and reconcile it in the app when restored.

### Host-PC follow-up

The host PC is not currently available. Do not treat local verification as proof that hosting is ready. When the host becomes available, repeat the production-mode startup check, install the supervised service, configure the approved access path, register the backup and email scheduler, configure external health monitoring and alerts, and perform a host-based restore drill before pilot approval.

### Go/no-go

Pilot use is **GO** only after the Sprint 009 acceptance checklist has passed, the restore drill is recorded, the real-data rehearsal is complete, and the pilot owner has approved the fallback and incident contacts. Otherwise mark **NO-GO** or **GO WITH CONDITIONS** and keep the paper process active.
