# Sprint 002 Requirements — Workflow Pages + Completion Context

## Sprint Goal

Turn Sprint 001 backend/API capability into daily-usable role workflows by delivering core manager, crew, and owner pages, while preserving security and audit integrity.

---

## In Scope (must be implemented)

### 1) Manager daily workflow pages

- Manager landing/dashboard page with clear navigation to weekly operations.
- Week workflow pages for:
  - generate draft,
  - review/edit draft,
  - post assignments,
  - completion review/confirmation.
- Visible distinction between:
  - crew self-completed,
  - manager-completed on behalf.

### 2) Crew pages with history + notes

- Crew task list page (current week) and task detail/interaction page.
- Crew may add a write-once note on an assignment (general context) or as an incomplete-task explanation.
- Note policy is write-once (no edit/delete in v1).
- Crew page includes history of last 4 weeks of completion records.

### 3) Manager on-behalf completion path

- Manager can mark a task completed on behalf of crew when needed.
- Mandatory reason is required for on-behalf completion.
- On-behalf completion generates audit event.
- Reporting surfaces must preserve who performed completion action.

### 4) Owner read-only pages

- Owner read-only page(s) for weekly reporting visibility.
- Align with existing owner report endpoint behavior.

### 5) Scheduler usability floor

- UI or documented operator path for weekly schedule configuration/read.
- Confirm scheduled runner script path is documented for deployment operation:
  - `scripts/run_scheduled_owner_email.py`.

---

## Explicitly Out of Scope (Sprint 002)

- New assignment engine scoring behavior (weights/difficulty logic).
- Schedule import ETL/parser from Altametrics.
- Multi-location tenancy implementation.
- Full notification center/chat/threaded discussion system.
- Editable/deletable crew notes (write-once only in this sprint).

---

## Non-functional Requirements (minimum)

- Server-side role enforcement remains authoritative for every page action.
- CSRF remains enforced on state-changing actions.
- Notes and completion reason inputs are sanitized and length-bounded.
- On-behalf completion and note submission are auditable.
- Page responses remain compatible with current stack (Flask + vanilla templates).

---

## Assumptions (explicit)

- Existing API routes from Sprint 001 are stable enough to back new pages.
- Existing report endpoints can be reused for owner/manager page rendering in Sprint 002.
- Note length cap can be implemented as a practical fixed limit (recommended: 500 chars) unless Builder finds an existing project standard.
