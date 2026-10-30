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
