# Sprint 003 Acceptance Criteria — Builder Checkable

Sprint is complete only when all items pass or are explicitly deferred with rationale.

---

## A. Visual Shell Exists

- [x] Manager workflow is available as rendered page(s), not JSON-only.
- [x] Crew workflow is available as rendered page(s), not JSON-only.
- [x] Owner reporting workflow is available as rendered page(s), not JSON-only.
- [x] Shared layout provides readable navigation/context for role pages.

## B. UX Baseline Quality

- [x] Manager page shows clear next actions (generate/draft/post/completions/schedule).
- [x] Crew page is mobile-usable (single-column readability + touch-friendly actions).
- [x] Crew page clearly communicates note write-once policy.
- [x] Owner page clearly indicates read-only status.
- [x] Success/failure states are visible and understandable in-page.

## C. Behavior Integrity

- [x] Existing Sprint 002 workflow behavior remains functional.
- [x] Manager on-behalf completion still requires reason.
- [x] Completion source/reason remains persisted and retrievable.
- [x] Crew notes still support general + incomplete-context and remain write-once.
- [x] Crew 4-week history bound remains intact.

## D. Security + Authz

- [x] Role-based authorization enforced on all new/updated page routes.
- [x] Cross-role access attempts to protected pages are denied.
- [x] State-changing actions preserve CSRF protections.

## E. Ops Hardening

- [x] Route smoke coverage exists for manager/crew/owner visual endpoints.
- [x] Regression coverage exists for at least one critical page-flow guard.
- [x] Logging remains redacted for sensitive auth payload fields.

## F. Scope Guard

- [x] No schedule-import engine implementation.
- [x] No weighting behavior implementation.
- [x] No multi-location implementation.
- [x] No frontend framework/build pipeline introduction.
