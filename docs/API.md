# API Surface (Planning Contract, v1)

This is a planning-level API contract to guide Builder implementation.
Actual route names can vary if capability parity is preserved.

## Auth

- `POST /auth/login-password`
- `POST /auth/login-pin`
- `POST /auth/logout`
- `POST /auth/reset-password/request`
- `POST /auth/reset-password/confirm`
- `POST /auth/reset-pin` (manager-only)

## Users / Roles

- `GET /api/users`
- `POST /api/users`
- `PATCH /api/users/:id`
- `DELETE /api/users/:id`

## Job Codes

- `GET /api/job-codes`
- `POST /api/job-codes`
- `PATCH /api/job-codes/:id`
- `DELETE /api/job-codes/:id`

## Task Templates

- `GET /api/task-templates`
- `POST /api/task-templates`
- `PATCH /api/task-templates/:id`
- `DELETE /api/task-templates/:id`

## Imports

- `POST /api/import/people`
- `POST /api/import/job-codes`
- `POST /api/import/task-templates`

Expected payload modes:
- CSV upload
- text input (`value` or optional `value|jobcode`)

## Assignment Lifecycle

- `POST /api/weeks/:week/generate`
- `GET /api/weeks/:week/draft`
- `PATCH /api/weeks/:week/draft/items/:item_id`
- `POST /api/weeks/:week/post`

## Completion

- `POST /api/completions/:assignment_item_id/mark-complete`
- `POST /api/completions/:assignment_item_id/confirm` (manager/lead per policy)
- `POST /api/completions/:assignment_item_id/manager-complete` (manager on-behalf completion; reason required)
- `POST /api/completions/:assignment_item_id/note` (crew incomplete-task note; write-once)

## Reports

- `GET /api/reports/person?week=&job_code=&person=&from=&to=`
- `GET /api/reports/task?week=&job_code=&task=&from=&to=`

## Crew History

- `GET /api/crew/history?weeks=4` (bounded recent completion history)

## Audit

- `GET /api/audit?actor=&action=&entity=&from=&to=&page=`

## Owner

- `GET /api/owner/reports/weekly`
- `GET /api/owner/settings/report-email`
- `POST /api/owner/settings/report-email` (manager updates owner recipient)
- `POST /api/owner/reports/weekly/send-email` (manager-triggered weekly send)
- `POST /api/owner/reports/test-email` (manager-triggered SMTP connectivity/proof send)
- `GET /api/owner/reports/weekly/schedule` (manager/owner reads weekly schedule config)
- `POST /api/owner/reports/weekly/schedule` (manager writes schedule config: `enabled`,`weekday`,`hour_utc`,`minute_utc`)
- `POST /api/owner/reports/weekly/run-scheduled` (manager runs scheduler decision path once; supports `force`/`dry_run`)

## Authorization Expectations

- Every endpoint enforces role + ownership checks server-side.
- Deny-by-default for undefined role access.
