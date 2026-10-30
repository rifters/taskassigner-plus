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
