# Sprint 002 Acceptance Criteria — Builder Checkable

Sprint is complete only when all items pass or are explicitly deferred with rationale.

---

## A. Manager Workflow Pages

- [ ] Manager can access weekly generate/review/edit/post workflow pages.
- [ ] Manager completion review page shows completion actor/source context.
- [ ] Manager can mark completion on behalf of crew from manager workflow.
- [ ] On-behalf completion is blocked if reason is empty.
- [ ] On-behalf completion writes audit evidence with actor + reason + timestamp.

## B. Crew Workflow + Notes

- [ ] Crew can view own current-week tasks on page flow.
- [ ] Crew can submit assignment notes (general) and incomplete-task notes.
- [ ] Note is write-once (edit/delete attempts are rejected in v1).
- [ ] Crew history shows last 4 weeks (bounded window).
- [ ] Crew cannot view/modify other users’ tasks/notes/history.

## C. Owner Read-only Pages

- [ ] Owner can access read-only weekly reporting page(s).
- [ ] Owner pages expose reporting data without operational mutation actions.

## D. Data Integrity + Reporting Context

- [ ] Completion data distinguishes self-complete vs manager-on-behalf.
- [ ] Manager reason for on-behalf completion is persisted and retrievable.
- [ ] Existing reporting paths remain functional after Sprint 002 changes.

## E. Security Baseline

- [ ] Role-based authorization enforced server-side for all new/updated page actions.
- [ ] CSRF protections active on state-changing routes.
- [ ] Note/reason inputs are validated and bounded.

## F. Ops Usability

- [ ] Weekly schedule config/read path is usable by manager in app workflow.
- [ ] Scheduled runner script path is documented for deployment operation.

## G. Scope Guard

- [ ] No schedule-import engine implementation.
- [ ] No weight/difficulty algorithm behavior implementation.
- [ ] No multi-location implementation.
- [ ] No editable/deletable notes (write-once policy preserved).
