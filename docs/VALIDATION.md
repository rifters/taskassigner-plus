# Validation Plan

## 1. Test Priorities

1. Auth and authorization boundaries
2. Import parsing/validation and failure behavior
3. Assignment lifecycle state correctness
4. Completion integrity and confirmation flow
5. Reporting correctness for person/task views
6. Audit trail completeness for sensitive actions
7. Workflow page authz and role usability

## 2. Abuse / Negative Tests

- PIN brute-force lockout behavior.
- Access denied for crew attempting privileged endpoints.
- Access denied for cross-user task completion mutation.
- Invalid import lines produce precise error messages and no partial silent corruption.
- Task import/create without job code is rejected.
- Manager on-behalf completion rejected without reason.
- Crew note edit/delete attempts rejected once submitted (write-once enforcement).

## 3. Data Correctness Tests

- Draft vs posted state transitions are correct.
- Manual edit reason persistence when provided.
- Completion timestamps and confirmation metadata persist accurately.
- Task-centric reports correctly compute assignment distribution and completion percentages.
- Completion source context (self vs manager on-behalf) is preserved.
- Crew history query is bounded to last 4 weeks.

## 4. Operational Validation

- Daily backup job runs and restore procedure is documented/tested.
- Logging is structured and excludes secrets/hashes from raw output.
- Auth rate limits are observable and enforce configured behavior.
- Alerting path can be triggered/tested.
- DB schema initialization is idempotent via `python scripts/init_db.py`.
- Scheduler runner script executes with expected due/disabled/error status behavior.

## 5. Acceptance Validation Execution

Before sprint close:
- Execute all checks from `planning/sprints/002-workflow-pages/acceptance.md`.
- Record pass/fail evidence in `planning/ARCHITECT_BRIEFING.md`.
- Any failed item blocks sprint completion unless explicitly deferred with rationale.
