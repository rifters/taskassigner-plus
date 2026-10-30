# Sprint 006 Requirements — Randomized Generation and Paper Trail

## Sprint Goal

Improve weekly assignment rotation without weakening existing eligibility or balanced workload behavior. The manager can regenerate an unsatisfactory draft before posting, while posting can optionally open a print-friendly paper task list grouped by job code and person.

## In Scope

1. Randomize active task order during generation.
2. Randomize eligible-person order independently within each responsible job-code pool.
3. Preserve the current balanced task-count behavior within each job-code pool.
4. Compare generated assignments only with same-person/same-task pairs from the immediately previous posted week.
5. Avoid a prior-week same-person/same-task pairing whenever another eligible person is available.
6. Allow a repeat when no eligible alternative exists; never leave an otherwise assignable task unassigned solely because of repeat avoidance.
7. Enforce eligibility server-side for every generated assignment and assignment edit: active person, responsible job-code membership, and no per-person task exclusion.
8. Permit one active draft per week. Before posting, a confirmed regenerate action replaces the entire unposted draft.
9. Prevent full regeneration after a week is posted.
10. Permit individual posted assignment edits/swaps only within the task's responsible job-code pool, retaining existing validation and audit behavior.
11. Add minimal optional master-list number storage and manager/task-view display needed by the printout. Numbered text-file parsing and complete job-code import UX remain deferred.
12. After successful posting, ask whether the manager wants to print the task list. Declining must not undo or block posting.
13. Provide a browser print-friendly view using the standard browser/system print dialog, including Save as PDF through the browser.
14. Print the posted week grouped by responsible job code, then person. Show each task's master-list number when present, a blank checkbox before each task, and signature space after each person's task list.
15. Preserve digital completion, reporting, JSON/API contracts, CSRF, authorization, and audit behavior.
16. Add focused tests and perform real local smoke verification.

## Eligibility and Rotation Rules

A person is eligible for a task only when active, a member of the task's responsible job-code pool, and not excluded from that task template. Multi-job-code people are randomized independently in each eligible pool. Repeat avoidance is a preference among eligible candidates and examines only the immediately previous posted week.

## Draft Lifecycle

A week has at most one active unposted draft. If a draft exists, the manager may choose Regenerate Draft and must confirm the replacement. Regeneration discards/replaces the current unposted draft. Once posted, generation and regeneration are unavailable; only individual eligible edits/swaps remain available.

## Master-List Number Boundary

The task template receives an optional positive master-list number that can be entered or edited through the existing task-management path and is displayed wherever the print/task views expose task identity. Existing task imports remain compatible. Full parsing of lines such as `1. Clean Fryers`, selected-job-code import, numbering uniqueness policy, and import conflict behavior are deferred to the following sprint.

## Out of Scope

- Numbered plain-text list parsing or selected-job-code list import.
- Schedule importing or schedule-based availability.
- Days-off, shift, capacity, time-estimate, or maximum-assignment rules.
- Long-term weighted fairness, task weighting, or multi-week optimization.
- Cross-job-code posted reassignment.
- Custom PDF generation or a separate document-generation service.
- Shift-lead/owner workflow expansion, multi-location support, frontend framework, or build pipeline.

## Security and Compatibility

Preserve role guards, CSRF protection, server-side eligibility, completion ownership, write-once notes, audit events, existing API response behavior, and secret-safe logging. Do not expose PINs, password hashes, credentials, or secrets.
