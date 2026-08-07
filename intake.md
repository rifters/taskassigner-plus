## Project Name
TaskAssigner+

## Client / Company
Rifters / Eric

## Project Slug
taskassigner-plus

## Project Type
Internal tool

## Tech Stack
Python 3, Flask, Flask-Login, Flask-SQLAlchemy, Flask-Bcrypt, SQLite, Vanilla JS, HTML/CSS. No frontend framework, no build pipeline. Cloudflare Tunnel for public HTTPS access. Tailscale for private remote access by manager and owner.

## Canonical GitHub Repo
Local: F:\projects\taskassigner-plus\ — push to GitHub (github.com/rifters/taskassigner-plus) when ready.

## One-Sentence Description
A web-based weekly task assignment system for restaurant teams that fairly distributes tasks across job-code-based crew pools, tracks completion, and reports productivity to management.

## Business Problem
A Denny's manager manually assigns weekly tasks to crew members across multiple job codes (Cooks, Servers, Hosts, SAs), tracks completion on paper, and hand-delivers signed reports to the owner. The current C# desktop app (Taskmate) works but is single-operator and Windows-only — crew cannot view or complete tasks themselves, and the owner has no remote visibility.

## Users / Roles
- **Crew** — View their own weekly task assignments, mark tasks complete from any phone or browser
- **Shift Lead** — Crew-level access plus ability to view full job code board and reassign tasks
- **Manager (Eric)** — Full access: manage job codes, task templates, crew pools, constraints, run and review assignment drafts, post assignments, confirm completions, view all reports
- **Owner** — Reports-only dashboard plus automated weekly email summary; no operational access needed

## Current Workflow
1. Eric selects a job code group and adjusts the crew pool manually (removes absent staff)
2. Algorithm generates a draft assignment across eligible crew, respecting constraints and rotation history
3. Eric reviews the draft, checks fairness spread, manually tweaks if needed
4. Eric posts the assignments for the week
5. Crew completes tasks; Eric tracks completion
6. Eric prints a signed task completion page and hand-delivers it to the owner weekly

## Pain Points
- Desktop-only — Eric is the sole operator; crew cannot self-serve
- Owner has no visibility unless Eric physically delivers the report
- Manual pool adjustment has no audit trail (gaps in history are unexplained)
- Manual draft edits are untracked, dirtying productivity evaluation data
- No ad-hoc task support — unplanned tasks fall outside the system
- Completion data is thin — no timestamp, no manager verification flag
- Cold start problem — week one has no rotation history to inform fairness

## Target Workflow
1. Eric adjusts crew pools if needed (future: schedule import does this automatically)
2. System generates weekly draft per job code — balances task count, respects constraints, checks rotation history
3. Eric reviews draft in browser — sees fairness spread, task counts per person, flags imbalances
4. Eric tweaks if needed (all changes logged with optional reason)
5. Eric posts — crew immediately sees their tasks on any phone via QR code or URL
6. Crew marks tasks complete (timestamped)
7. Eric confirms completions
8. Owner receives automated weekly email report — formatted to replace the paper sign-off

## Source Materials
- Existing C# WPF Taskmate codebase: F:\projects\taskmate\ — reference for data model, constraint engine, rotation/fairness logic, and smart assignment algorithm. Not being ported directly but logic is reusable.

## Systems / Tools
- Denny's in-store WiFi (LAN access for crew)
- Cloudflare Tunnel (free public HTTPS URL — no port forwarding required)
- Tailscale (private VPN mesh — Eric and owner remote access)
- QR code posted in kitchen (crew entry point)
- Email (weekly owner report via SMTP/MailKit equivalent in Python)

## Data Inputs and Outputs
**Inputs:**
- Job codes (name, task template list, crew member list, constraints per person)
- People (name, PIN, role, job code memberships, hours per job code this week)
- Task templates (title, notes, job code — weight field reserved for future use)
- Manual pool adjustments before each generation run
- Crew task completions (timestamped)
- Manager confirmation of completions
- Manual draft edits (logged with reason)

**Outputs:**
- Weekly assignment draft (per job code) — task count per person, fairness rating
- Posted assignment list (crew-facing, per person)
- Assignment history (who got what, when, how often, completion rate)
- Per-person productivity view (tasks assigned, completion %, task frequency breakdown)
- Weekly owner email report (assignments posted, completions confirmed, per-person summary)
- Audit log (pool adjustments, manual draft edits, constraint changes)

## Out of Scope
- Schedule import (future — format TBD, likely CSV from scheduling software)
- Task weight / difficulty scoring (future — data model supports it, not implemented in v1)
- Multi-location support (future — architecture allows it, not built in v1)
- Native mobile app (PWA via browser is sufficient)
- Slack / Teams integration
- Predictive ML analytics (rotation history builds the foundation; ML layer added later)
- Push notifications (browser-based completion flow is sufficient for v1)

## Success Criteria
- Crew can view and complete their weekly tasks from any phone without Eric's involvement
- Owner receives an automated weekly email report replacing the hand-delivered paper sign-off
- Eric's manual assignment preparation time drops by 50% or more
- All assignment changes and pool adjustments are logged and auditable
- Per-person productivity data is clean and reliable enough to support employee evaluations

## Open Questions
- Schedule import: what software does Denny's use for scheduling, and what export format is available (CSV, PDF, other)?
- Task weight system: how will difficulty be scored when implemented — manager-defined numeric scale, time estimates, or something else?
