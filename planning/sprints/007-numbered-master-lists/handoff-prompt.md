# Builder Handoff — Sprint 007 Numbered Master Lists

Implement only from `requirements.md`, `blueprint.md`, and `acceptance.md` in this sprint folder. Before source changes, inspect the current models, task import parsers/routes, manager Task Templates page, authorization/CSRF patterns, audit helper, DB initialization, existing API contracts, and Sprint 006 tests.

Before editing source or test files, stop at the Builder code gate and provide a file-by-file implementation plan, scope guards, and acceptance mapping. Wait for explicit approval of that implementation plan.

Build the numbered task-list import/export workflow with partial-success validation. Keep numbered identity scoped to job code. Use case/whitespace-normalized title matching only; punctuation changes, leading-zero values, duplicate numbers, gaps, malformed rows, and number/title mismatches require manual review. Do not silently rename, deactivate omitted tasks, choose duplicate winners, or renumber existing tasks. Legacy unnumbered exact matches require manager confirmation before attaching a number.

Support selected-job-code TXT and CSV imports plus combined CSV imports with row-level `job_code`. Apply valid rows while reporting review/error rows. CSV exact matches may update notes and active status; TXT must preserve existing notes/status. New valid rows default active. Export one complete combined CSV including inactive tasks and active status, plus active-only TXT output separated by job-code group with number/title only.

Preserve existing mixed import formats, assignment/constraint/completion/reporting/print behavior, role authorization, CSRF, auditability, and secret-safe logging. Do not add schedule importing, availability rules, custom PDF generation, frontend frameworks, or unrelated refactors.

Run focused and full tests, compilation, whitespace checks, demo reset/idempotency verification, and real local HTTP smoke checks for both import and export paths. Update planning state, decisions, risks, and acceptance evidence only after verification. Do not commit, push, expose credentials, or modify unrelated files.
