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
