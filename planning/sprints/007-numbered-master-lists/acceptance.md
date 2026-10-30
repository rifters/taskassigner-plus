# Sprint 007 Acceptance — Numbered Master Lists

- [x] Manager can select a job code and import numbered TXT rows.
- [x] Manager can import selected-scope CSV with `number,title,notes`.
- [x] Combined CSV with row-level `job_code` imports successfully without requiring one selected job code.
- [x] Existing unnumbered/mixed task import formats remain compatible.
- [x] Blank TXT lines are ignored.
- [x] Non-numbered nonblank TXT rows are flagged.
- [x] Leading-zero and nonpositive numbers are flagged.
- [x] Duplicate numbers are flagged without silently choosing a winner.
- [x] Numbering gaps are flagged and valid independent rows still apply.
- [x] Numbered lists require consecutive numbering beginning at 1.
- [x] Case and whitespace differences match; punctuation differences are flagged.
- [x] Number/title mismatches do not silently rename or update existing tasks.
- [x] Omitted source numbers are reported and existing tasks remain active.
- [x] Legacy unnumbered exact job-code/title matches require manager confirmation before numbering.
- [x] Exact numbered matches update CSV notes and active status.
- [x] TXT exact matches preserve existing notes and active status.
- [x] Valid new rows create active task templates by default.
- [x] Combined CSV export includes all tasks, job code, number, title, notes, and active status.
- [x] TXT export is separated by job-code group, includes active tasks only, and contains number plus title only.
- [x] Import/export actions are manager-authorized, CSRF-protected, and audited.
- [x] Review output identifies row numbers and actionable reasons.
- [x] Assignment generation, exclusions, completion, reports, and print workflows remain green.
- [x] No secrets, credentials, PINs, or password hashes appear in pages or logs.
- [x] Schedule/availability behavior and automatic omission deactivation remain deferred.

## Verification Evidence

- Focused: `python -m pytest tests/test_imports.py tests/test_sprint007.py -q` → **16 passed**.
- Full: `python -m pytest tests -q` → **68 passed** with 15 existing SQLAlchemy deprecation warnings.
- Compilation and whitespace: `python -m compileall -q src scripts/reset_demo.py` and `git diff --check` passed.
- Demo reset: `python scripts/reset_demo.py` → `DEMO_RESET_OK`.
- HTTP smoke: `/health`, `/auth/login-crew`, and `/manager/exports/task-templates.csv` → **200**.
