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
