# Builder Handoff — Sprint 006 Randomized Generation and Paper Trail

Implement Sprint 006 strictly from `requirements.md`, `blueprint.md`, and `acceptance.md` in this sprint folder. Before source changes, inspect the current assignment generation, draft/post/edit routes, manager weekly templates, crew/task templates, models, eligibility helper, imports, audit helpers, database initialization, and relevant tests. Do not redefine scope.

Before editing any source or test file, stop at the code gate and provide a concrete file-by-file implementation plan, explicit scope guards, and the acceptance criteria. Wait for explicit approval of that implementation plan.

Implement the smallest compatible change that adds controlled double randomization, immediate-prior-posted-week repeat avoidance, confirmed pre-post full regeneration, locked post lifecycle, same-job-code posted edits, and the optional grouped paper print view. Preserve balanced task counts and all server-side eligibility rules: active status, responsible job-code membership, and per-person task exclusions. Use a testable randomness boundary rather than flaky tests. Keep JSON/API behavior compatible and do not add schedule, availability, long-term weighting, or cross-pool assignment behavior.

Add only the minimal optional task master-list number support needed for the printout. Do not implement numbered text-file parsing or selected-job-code import in this sprint. The printout must group by job code then person, show numbered tasks with leading checkboxes, and provide signature space after each person's list. Use normal browser printing/Save as PDF rather than custom PDF generation. Printing is optional and cannot replace digital completion/reporting.

Run focused tests, the full suite, compilation, whitespace checks, demo reset/idempotency verification, and a real local HTTP/browser smoke path. Update `planning/STATE.md`, `planning/DECISIONS.md`, `planning/RISKS.md`, and acceptance evidence only after implementation is verified. Do not commit, push, expose credentials, or modify unrelated files.
