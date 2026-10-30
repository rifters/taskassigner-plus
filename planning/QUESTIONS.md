# Open Questions

Questions that need answers from Architect/Builder/Client.

---

## Discovery Gate Resolution (2026-07-08)

Mandatory External-facing discovery topics were answered or explicitly deferred with rationale. No blocking discovery gate item remains for Pack 001.

---

## Sprint 002 Resolution Notes (2026-07-08)

All Sprint 002 planning decisions requested in Architect conversation are resolved and approved.

- Include all role pages in Sprint 002: **answered**.
- Crew history window: **last 4 weeks**: **answered**.
- Notes on incomplete tasks allowed: **answered**.
- Notes edit policy: **write-once**: **answered**.
- Manager on-behalf completion allowed: **answered**.
- On-behalf completion reason required: **answered**.

No blocker question remains for Architect Pack 002 generation.

---

## Sprint 003 Resolution Notes (2026-07-08)

Sprint 003 direction is approved:

- Start with debug-usable visual UX shell before polish decisions.
- Execute balanced path: UX polish + ops hardening in same sprint.
- Keep existing scope guard and backend behavior boundaries.

No blocker question remains for Architect Pack 003 generation.

---

## Deferred Tracking

| Question | Owner | Needed By | Status | Answer / Notes |
|---|---|---|---|---|
| Scheduling source/export for future import? | Client + Harri developers | Before extended schedule/analytics sprint | Partially resolved | Initial schedule detection only needs whether a person works on a given day, so Harri PDF can support a first import phase with manual review. CSV/API availability, schema, stable identifiers, and access method should still be requested for future time-availability rules and analytics. |
| Future task-weight model direction? | Client + Architect | Before weighting sprint | Answered (deferred) | Hybrid model (manager weight + estimated minutes) chosen for future. |
| Multi-job-code assignment behavior? | Client | Before crew workflow sprint | Answered | Crew members may receive multiple assignments, including across multiple eligible job-code pools, when task volume exceeds crew capacity. |
| Crew assignment presentation? | Client | Before crew workflow sprint | Answered | Group the crew member's task list by responsible job code; all groups are expanded by default. |
| Manager assignment review presentation? | Client | Before crew workflow sprint | Answered | Group weekly assignments by responsible job code, with all groups expanded by default. |
| Assignment eligibility constraints? | Client + Architect | Before crew workflow sprint | Answered | Current eligibility is manager-maintained job-code membership plus specific per-person task exclusions. Schedule-based availability rules are deferred until schedule importing exists. |
| Formal compliance obligations beyond internal policy? | Client/Legal | Before production hardening if requirements emerge | Answered (current stance) | Internal-policy handling for now; no formal checkpoint selected at this stage. |

## Sprint 006 Discovery

- Sprint 006 scope: **answered** — focus only on double-randomized assignment generation with prior-week same-person/same-task avoidance within existing eligibility constraints.
- Master-list numbered import and manager/crew display: **deferred** — plan as a following sprint, not Sprint 006.
- Repeat-avoidance lookback: **answered** — compare only with the immediately previous posted week; older weeks do not block assignment.
- Workload balance during randomization: **answered** — preserve current balanced task counts within each job-code pool; randomization changes order and recipient selection only.
- Draft lifecycle: **answered** — allow one active draft per week, with full regeneration replacing the unposted draft; after posting, allow only individual eligible edits/swaps with audit history.
- Posted-task edit pool: **answered** — edits and swaps remain within the task's responsible job-code pool, subject to active status and task exclusions.
- Multi-job-code randomization: **answered** — randomize each person's position independently within every eligible job-code pool.
- Draft replacement confirmation: **answered** — require explicit confirmation before replacing an unposted draft.
- Post-print prompt and contents: **answered** — after posting, ask whether to print; if accepted, show a job-code → person → numbered-task print view; declining does not block posting.
- Print mechanism: **answered** — use a browser print-friendly page and the standard browser/system print dialog, including Save as PDF; no custom PDF generation.
- Printed completion marks: **answered** — place a blank checkbox before each task and signature space after the listed tasks.
- Signature placement and paper trail: **answered** — provide signature space after each person's task list; printing is optional and does not replace planned digital completion/reporting.
- Master-list number dependency for Sprint 006 print: **answered** — include minimal number storage/display needed by printing; defer numbered text-file parsing and complete import UX to the following sprint.
- Number/title mismatch behavior for numbered import: **answered** — flag the mismatch for manual manager resolution; do not silently update the existing task.
- Omitted numbers in a later import: **answered** — report the missing source numbers but leave existing tasks active until manually changed.
- Duplicate numbers in one source list: **answered** — flag duplicate rows for manual editing; do not silently choose a winner.
- Numbered text import scope: **answered** — manager selects the job code before importing; each line contains only its number and title.
- Numbered CSV shape and export: **answered** — import uses `number,title,notes` under the selected job code; export must preserve job code, number, title, and notes.
- Export grouping: **answered** — one combined CSV with `job_code`; TXT export is separated by job-code group.
- Import error handling: **answered** — apply valid rows and flag only the invalid rows for manual correction.
- Export task status: **answered** — combined CSV includes active and inactive rows with an `active` flag; grouped TXT includes active rows only.
- Notes on matching imports: **answered** — CSV may update notes on matching number/title; TXT leaves existing notes unchanged.
- Active status on matching CSV imports: **answered** — apply the imported `active` flag when number and title match.
- Combined versus selected-scope CSV: **answered** — accept row-level `job_code` when present, otherwise use the manager-selected job code.
- Legacy unnumbered task matching: **answered** — exact job code/title may be proposed for linking, but assigning the number requires manager confirmation.
- Title matching normalization: **answered** — ignore capitalization and surrounding/repeated whitespace; preserve the stored title unless separately confirmed.
- Punctuation differences: **answered** — flag for manual review rather than treating them as an automatic match.
- Leading-zero numbers: **answered** — flag values such as `01` for manual review instead of normalizing them.
- Numbering gaps: **answered** — require consecutive numbering from `1` and flag missing numbers to the importer.
- Blank lines and malformed TXT rows: **answered** — ignore blank lines and flag other non-numbered nonblank lines.
- New imported rows: **answered** — create valid new rows as active tasks by default, using the selected/row job code and optional notes.
