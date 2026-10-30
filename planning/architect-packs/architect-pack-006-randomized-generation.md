============================================================
FILE: planning/STATUS.json
============================================================
{
  "schemaVersion": 1,
  "phase": "apply-pack",
  "sprint": "006-randomized-generation",
  "updated": "2026-09-02T00:00:00-04:00"
}

============================================================
FILE: planning/sprints/006-randomized-generation/requirements.md
============================================================
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

============================================================
FILE: planning/sprints/006-randomized-generation/blueprint.md
============================================================
# Sprint 006 Blueprint — Randomized Generation and Paper Trail

## Generation Algorithm

Trace the existing generation path and retain its per-job-code balancing semantics. Build the candidate task collection from active task templates, then randomize task processing order. For each responsible job-code pool, obtain eligible users through the existing centralized eligibility helper and randomize that pool's user order independently. Allocate tasks using the existing balanced-count approach while preferring a candidate who did not receive that task template in the immediately previous posted run. If all eligible candidates are prior-week repeats, use the normal eligible candidate rather than dropping the task. Do not use older posted weeks for blocking or weighting.

Use an injectable or patchable randomness boundary where practical so tests can prove behavior without depending on a lucky random outcome. Do not add a long-term fairness score or hidden weighting.

## Prior-Week Lookup

Identify the immediately previous posted assignment run for the week being generated using the project's existing week-key conventions. Build a task-template/person pairing lookup from that run. If there is no previous posted run, treat every eligible candidate as having no repeat. Keep draft and posted states distinct; a prior draft must not be used as rotation history.

## Draft Regeneration and Lifecycle

Replace the current draft only through an explicit regenerate action protected by a confirmation step in the browser flow and a server-side route/API guard. The replacement must not be allowed after posting. Ensure stale draft items cannot remain attached to the replacement and that regeneration is auditable with the week/run context. Preserve the one-active-draft invariant under normal requests and guard against accidentally selecting a posted run.

The post path remains explicit. After a successful post, the manager-facing workflow asks whether to print. A positive response navigates to the print-friendly posted-week view; a negative response stays on the normal post/result flow. Do not make the print prompt part of the JSON contract unless the existing browser/API content-negotiation pattern requires a compatible additive field.

## Posted Edits

Keep posted edits separate from draft regeneration. Reuse the centralized eligibility helper and restrict replacement candidates to active people who belong to the task's responsible job-code pool and have no task exclusion. Preserve reason capture, audit records, and existing manager authorization. Do not provide cross-pool choices.

## Master-List Number

Add the smallest schema/form/serialization change needed for an optional positive integer on a task template. Preserve null for existing records and old import formats. Display the value alongside the task title in manager and crew/task identity contexts used by the print workflow. Do not implement numbered-line parsing, uniqueness enforcement, or destructive import behavior in this sprint unless already required by an existing path.

## Print View

Add a server-rendered print-friendly route for a posted week using existing authorization and content-negotiation conventions. Load only posted assignments for the requested week. Group rows by responsible job code, then assignee. Within each person's list, retain a stable readable order, preferably master-list number ascending when present and task identity/title as the fallback. Render the number, task title, leading blank checkbox, and a signature line/space after that person's task list. Add print CSS with screen-only navigation/actions hidden and paper-friendly page breaks. Use browser `window.print()` or an equivalent normal browser print action; do not create a custom PDF.

## Tests and Validation

Add focused tests for randomized ordering with controlled randomness, independent multi-job-code pool ordering, balanced counts, prior-week repeat avoidance, no-alternative fallback, no-prior-week behavior, active/job-code/exclusion enforcement, one active draft, confirmed regeneration, regeneration rejection after posting, same-pool posted edits, and audit behavior. Test optional master-list number persistence/display and print grouping/checkbox/signature markup. Preserve existing API and browser regression tests.

Run focused tests, the full suite, compilation, `git diff --check`, demo reset/idempotency checks, and a real local HTTP/browser smoke path covering generate, regenerate confirmation, post, and print navigation. Update planning closeout files only after verification.

============================================================
FILE: planning/sprints/006-randomized-generation/acceptance.md
============================================================
# Sprint 006 Acceptance — Randomized Generation and Paper Trail

- [ ] Active tasks are processed in randomized order during generation.
- [ ] Eligible people are randomized independently within each responsible job-code pool.
- [ ] Multi-job-code people can receive work from each eligible pool without one global ordering bias.
- [ ] Existing balanced task-count behavior is preserved within every job-code pool.
- [ ] Only the immediately previous posted week is used for repeat avoidance.
- [ ] A generated task avoids its previous person when another eligible person exists.
- [ ] No-prior-week generation works normally without false repeat matches.
- [ ] When every eligible person would repeat, the task is still assigned to an eligible person.
- [ ] Generation never assigns inactive, wrong-job-code, or task-excluded people.
- [ ] A week has no more than one active draft.
- [ ] Regenerate Draft requires explicit confirmation and replaces the entire unposted draft.
- [ ] Regeneration cannot replace or recreate a posted week.
- [ ] Posted assignments cannot be fully regenerated.
- [ ] Posted individual edits/swaps remain within the task's responsible job-code pool and enforce all eligibility rules.
- [ ] Draft regeneration, edits, and posting retain required audit behavior.
- [ ] Task templates can store an optional positive master-list number without breaking existing records/import formats.
- [ ] Manager and crew/task identity views display the master-list number when present.
- [ ] Posting asks whether the manager wants to print after successful posting.
- [ ] Declining the print option does not block or undo posting.
- [ ] Print view contains only the selected posted week.
- [ ] Print view groups assignments by responsible job code, then person.
- [ ] Each printed task shows its master-list number when present and has a blank checkbox before the task.
- [ ] Each person's printed task list has signature space after the tasks.
- [ ] Print view uses browser print styling and the normal browser/system print dialog; no custom PDF generator is added.
- [ ] Digital crew completion and planned reporting remain available and are not replaced by paper printing.
- [ ] Existing JSON/API contracts, role authorization, CSRF, completion ownership, notes, and full regression suite remain green.
- [ ] No secrets, credentials, PINs, or password hashes appear in pages or logs.
- [ ] Numbered text-file master-list import and schedule/availability rules remain deferred.

============================================================
FILE: planning/sprints/006-randomized-generation/handoff-prompt.md
============================================================
# Builder Handoff — Sprint 006 Randomized Generation and Paper Trail

Implement Sprint 006 strictly from `requirements.md`, `blueprint.md`, and `acceptance.md` in this sprint folder. Before source changes, inspect the current assignment generation, draft/post/edit routes, manager weekly templates, crew/task templates, models, eligibility helper, imports, audit helpers, database initialization, and relevant tests. Do not redefine scope.

Before editing any source or test file, stop at the code gate and provide a concrete file-by-file implementation plan, explicit scope guards, and the acceptance criteria. Wait for explicit approval of that implementation plan.

Implement the smallest compatible change that adds controlled double randomization, immediate-prior-posted-week repeat avoidance, confirmed pre-post full regeneration, locked post lifecycle, same-job-code posted edits, and the optional grouped paper print view. Preserve balanced task counts and all server-side eligibility rules: active status, responsible job-code membership, and per-person task exclusions. Use a testable randomness boundary rather than flaky tests. Keep JSON/API behavior compatible and do not add schedule, availability, long-term weighting, or cross-pool assignment behavior.

Add only the minimal optional task master-list number support needed for the printout. Do not implement numbered text-file parsing or selected-job-code import in this sprint. The printout must group by job code then person, show numbered tasks with leading checkboxes, and provide signature space after each person's list. Use normal browser printing/Save as PDF rather than custom PDF generation. Printing is optional and cannot replace digital completion/reporting.

Run focused tests, the full suite, compilation, whitespace checks, demo reset/idempotency verification, and a real local HTTP/browser smoke path. Update `planning/STATE.md`, `planning/DECISIONS.md`, `planning/RISKS.md`, and acceptance evidence only after implementation is verified. Do not commit, push, expose credentials, or modify unrelated files.
