============================================================
FILE: planning/STATUS.json
============================================================
{
  "schemaVersion": 1,
  "phase": "apply-pack",
  "sprint": "007-numbered-master-lists",
  "updated": "2026-09-02T00:00:00-04:00"
}

============================================================
FILE: planning/sprints/007-numbered-master-lists/requirements.md
============================================================
# Sprint 007 Requirements — Numbered Master Lists

## Sprint Goal

Add a manager workflow for importing and exporting stable, numbered task master lists by job code without silently changing existing task definitions. Preserve the current unnumbered/mixed import formats and the assignment, exclusion, completion, reporting, and print workflows.

## In Scope

1. Import numbered TXT lists scoped to a manager-selected job code. Example: `1. Clean Fryers`.
2. Import numbered CSV files with `number,title,notes` under the selected job code.
3. Accept combined CSV files with a `job_code` column; when present, the row value supplies scope. A CSV without that column requires the selected job code.
4. Export one combined CSV containing job code, number, title, notes, and active status for all task templates, including inactive rows.
5. Export TXT lists grouped/separated by job code, containing active tasks only and only number plus title.
6. Require positive consecutive numbering beginning at 1 for each imported job-code list.
7. Ignore blank TXT lines; flag every other non-numbered nonblank TXT line.
8. Flag leading-zero numbers, duplicate numbers, numbering gaps, malformed rows, and title mismatches for manual correction.
9. Apply valid rows even when other rows in the same import are rejected; report every rejected row with a useful reason.
10. Treat matching numbers as stable identifiers within a job-code group.
11. If number and normalized title match an existing task, update CSV notes and active status as supplied. TXT imports preserve existing notes and status.
12. If an existing numbered task has a title mismatch, do not rename it or apply that row automatically; flag it for manual resolution.
13. If a source number is omitted, report it but leave the existing task active.
14. If a legacy task has no number and normalized job code/title match, offer attaching the incoming number and require manager confirmation.
15. Create valid new rows as active task templates by default, with selected/row job code and optional CSV notes.
16. Normalize title matching for case and surrounding/repeated whitespace only. Punctuation differences remain mismatches.
17. Preserve authorization, CSRF, audit logging, backwards-compatible existing import formats, and secret-safe logging.
18. Add focused tests and real local verification.

## Import Rules

- TXT input is a numbered list for one selected job code. Blank lines are ignored.
- CSV input supports `number,title,notes` with selected job-code scope, or a combined form with an additional `job_code` column and optional `active` column.
- A number must be written without leading zeroes and must be a positive integer.
- Each imported list must contain exactly `1..N`; missing numbers are errors for that list.
- Duplicate numbers are errors for the affected rows and never choose a winner silently.
- Existing number/title mismatches and punctuation differences are review items, not automatic updates.
- Valid independent rows may be applied while review items remain flagged.

## Out of Scope

- Schedule importing, availability, shifts, capacity, or maximum-assignment rules.
- Automatic task deletion or deactivation based on omitted TXT rows.
- Automatic title renaming on mismatch.
- Silent duplicate resolution.
- Custom PDF generation or frontend framework/build tooling.
- Multi-location, long-term weighted fairness, or unrelated assignment redesign.

============================================================
FILE: planning/sprints/007-numbered-master-lists/blueprint.md
============================================================
# Sprint 007 Blueprint — Numbered Master Lists

## Data and Matching

Use the existing `TaskTemplate` model and its optional master-list number. Treat `(responsible_job_code_id, master_list_number)` as the stable numbered identity for numbered lists. Inspect current constraints and foreign-key behavior before changing uniqueness. Do not silently renumber existing records. Preserve null numbers for legacy tasks until a confirmed match assigns one.

Implement a shared title normalizer that trims surrounding whitespace, collapses repeated whitespace, and case-folds. Do not remove punctuation. Matching must include responsible job code. For a legacy task with null number and normalized title match, return a confirmation-required review item rather than applying the number automatically.

## Parsers

Extend the import layer with explicit numbered TXT and numbered CSV parsers. TXT accepts a leading positive integer, a period/list marker, whitespace, and title; blank lines are ignored. Reject leading-zero representations, nonpositive numbers, missing titles, and other non-numbered nonblank lines. CSV validates headers and row values, supports optional notes and active fields, and resolves job code from the row when `job_code` is present or from the selected form value otherwise.

Validation must inspect the complete per-job-code number set and report missing numbers, duplicate numbers, malformed rows, title mismatches, and legacy-number confirmation candidates. Keep existing `title|job_code` text import and existing CSV import behavior additive and backwards-compatible.

## Apply Workflow

Build an import service that separates rows into safe-to-apply records and review/error records. Apply valid new records and exact numbered matches in one transaction, while leaving review records unchanged. For CSV exact matches, update notes and active status. For TXT exact matches, preserve notes and current active status. New rows default active. Never deactivate omitted rows. Add audit events containing actor, source format, job-code scope, counts, and review/error counts without logging credentials or file contents unnecessarily.

The browser importer should show selected job-code scope, accepted format examples, applied-row count, and row-level review messages. Legacy unnumbered number assignments require a manager confirmation step. Keep JSON/API responses additive and role-protected.

## Exports

Add manager-authorized CSV and TXT export routes. CSV is one download for all task templates, ordered by job code then number/title, with columns `job_code,number,title,notes,active`; include inactive rows and preserve blank numbers where legacy data remains unnumbered. TXT export provides a separate downloadable text output per job-code group (or a clearly separated multi-file response supported by the existing app conventions), contains active rows only, and renders `number. title` without notes. Escape CSV values using the standard library CSV writer.

## UI and Compatibility

Extend the existing manager Task Templates page with numbered import controls, selected job-code selection, export controls, and review results. Do not remove the existing mixed import form. Keep manager authorization and CSRF protection on all browser actions. Existing task list JSON should expose number and active fields; existing consumers must continue to work.

## Tests and Validation

Add parser tests for valid TXT, blank lines, malformed rows, leading zeroes, gaps, duplicates, punctuation mismatch, and normalization. Add service/API tests for partial success, exact numbered matches, CSV notes/status updates, TXT preservation, new active rows, legacy confirmation, omitted-number reporting, combined/selected CSV scope, exports, role authorization, CSRF, audit records, and backwards compatibility. Run focused tests, full suite, compileall, `git diff --check`, demo reset, and a local HTTP smoke path for import/export.

============================================================
FILE: planning/sprints/007-numbered-master-lists/acceptance.md
============================================================
# Sprint 007 Acceptance — Numbered Master Lists

- [ ] Manager can select a job code and import numbered TXT rows.
- [ ] Manager can import selected-scope CSV with `number,title,notes`.
- [ ] Combined CSV with row-level `job_code` imports successfully without requiring one selected job code.
- [ ] Existing unnumbered/mixed task import formats remain compatible.
- [ ] Blank TXT lines are ignored.
- [ ] Non-numbered nonblank TXT rows are flagged.
- [ ] Leading-zero and nonpositive numbers are flagged.
- [ ] Duplicate numbers are flagged without silently choosing a winner.
- [ ] Numbering gaps are flagged and valid independent rows still apply.
- [ ] Numbered lists require consecutive numbering beginning at 1.
- [ ] Case and whitespace differences match; punctuation differences are flagged.
- [ ] Number/title mismatches do not silently rename or update existing tasks.
- [ ] Omitted source numbers are reported and existing tasks remain active.
- [ ] Legacy unnumbered exact job-code/title matches require manager confirmation before numbering.
- [ ] Exact numbered matches update CSV notes and active status.
- [ ] TXT exact matches preserve existing notes and active status.
- [ ] Valid new rows create active task templates by default.
- [ ] Combined CSV export includes all tasks, job code, number, title, notes, and active status.
- [ ] TXT export is separated by job-code group, includes active tasks only, and contains number plus title only.
- [ ] Import/export actions are manager-authorized, CSRF-protected, and audited.
- [ ] Review output identifies row numbers and actionable reasons.
- [ ] Assignment generation, exclusions, completion, reports, and print workflows remain green.
- [ ] No secrets, credentials, PINs, or password hashes appear in pages or logs.
- [ ] Schedule/availability behavior and automatic omission deactivation remain deferred.

============================================================
FILE: planning/sprints/007-numbered-master-lists/handoff-prompt.md
============================================================
# Builder Handoff — Sprint 007 Numbered Master Lists

Implement only from `requirements.md`, `blueprint.md`, and `acceptance.md` in this sprint folder. Before source changes, inspect the current models, task import parsers/routes, manager Task Templates page, authorization/CSRF patterns, audit helper, DB initialization, existing API contracts, and Sprint 006 tests.

Before editing source or test files, stop at the Builder code gate and provide a file-by-file implementation plan, scope guards, and acceptance mapping. Wait for explicit approval of that implementation plan.

Build the numbered task-list import/export workflow with partial-success validation. Keep numbered identity scoped to job code. Use case/whitespace-normalized title matching only; punctuation changes, leading-zero values, duplicate numbers, gaps, malformed rows, and number/title mismatches require manual review. Do not silently rename, deactivate omitted tasks, choose duplicate winners, or renumber existing tasks. Legacy unnumbered exact matches require manager confirmation before attaching a number.

Support selected-job-code TXT and CSV imports plus combined CSV imports with row-level `job_code`. Apply valid rows while reporting review/error rows. CSV exact matches may update notes and active status; TXT must preserve existing notes/status. New valid rows default active. Export one complete combined CSV including inactive tasks and active status, plus active-only TXT output separated by job-code group with number/title only.

Preserve existing mixed import formats, assignment/constraint/completion/reporting/print behavior, role authorization, CSRF, auditability, and secret-safe logging. Do not add schedule importing, availability rules, custom PDF generation, frontend frameworks, or unrelated refactors.

Run focused and full tests, compilation, whitespace checks, demo reset/idempotency verification, and real local HTTP smoke checks for both import and export paths. Update planning state, decisions, risks, and acceptance evidence only after verification. Do not commit, push, expose credentials, or modify unrelated files.
