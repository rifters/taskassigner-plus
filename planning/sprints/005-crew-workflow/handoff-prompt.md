# Builder Handoff — Sprint 005 Crew Workflow

Implement Sprint 005 from these generated sprint files only. Before source changes, read `requirements.md`, `blueprint.md`, `acceptance.md`, the existing models/auth/assignment/completion routes, manager People and weekly templates, demo seed/reset, and relevant tests. Do not redefine scope.

Implement the smallest server-rendered manager-to-crew vertical slice satisfying every acceptance item. Centralize and enforce eligibility server-side using responsible job-code membership plus stable task-template exclusions. Preserve JSON contracts, CSRF, role guards, completion ownership, write-once notes, audit behavior, and existing assignment behavior. Do not add schedule or availability rules.

Run focused tests, the full suite, Python compilation, `git diff --check`, demo reset/idempotency verification, and a real local HTTP/browser-path smoke test. Update `planning/STATE.md`, `planning/DECISIONS.md`, `planning/RISKS.md`, and acceptance evidence only after implementation is verified. Do not commit, push, expose credentials, or modify unrelated files.
