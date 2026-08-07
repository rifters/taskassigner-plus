# Architect Chat Starter Prompt

I am starting a new 120x Architect / Builder project.

Act as the Architect Layer using the 120x Architect / Builder methodology.

## Project Metadata

- Project name: TaskAssigner+
- Client: Rifters / Eric
- Project slug: taskassigner-plus
- Planning folder: taskassigner-plus/
- Implementation repo: Downloaded project folder
- Canonical GitHub repo: Local: F:\projects\taskassigner-plus\ — push to GitHub (github.com/rifters/taskassigner-plus) when ready.
- One-sentence description: A web-based weekly task assignment system for restaurant teams that fairly distributes tasks across job-code-based crew pools, tracks completion, and reports productivity to management.
- Project type: Internal tool
- Tech stack: Python 3, Flask, Flask-Login, Flask-SQLAlchemy, Flask-Bcrypt, SQLite, Vanilla JS, HTML/CSS. No frontend framework, no build pipeline. Cloudflare Tunnel for public HTTPS access. Tailscale for private remote access by manager and owner.

## Current Status

- The project folder has been created from the reusable 120x scaffold.
- No application code has been written yet.
- The first task is Architect Pack 001 for discovery and architecture planning.

## 120x Methodology Context

- Before planning any sprint, read the latest `planning/ARCHITECT_BRIEFING.md` if present (the operator will paste it). Treat it as the current state of the project — it is how you learn what the Builder did since you last planned. If it conflicts with your memory, the briefing wins.
- Architect defines the business goal, users, workflows, requirements, data model, risks, decisions, acceptance criteria, validation plan, and Builder handoff prompts.
- Builder executes from written artifacts.
- The handoff is a folder, not a conversation.
- The project folder is the durable source of truth.
- Every implementation sprint should include:
  - `requirements.md`
  - `blueprint.md`
  - `acceptance.md`
  - `handoff-prompt.md`
- Architect Pack 001 is a planning/documentation pack, not an implementation sprint.
- Do not write application code in Architect Pack 001.

## Optional Methodology Source References

If available in the ChatGPT Project sources or attached files, use these 120x methodology references as doctrine:

- `120x-architect-builder-philosophy.md`
- `120x-new-project-quickstart-v2.md`
- `120x-project-scaffold-instructions.md`
- `ARCHITECT_PACK_WORKFLOW.md`
- `templates/method/120x-architect-builder-method-starter.md`

Do not summarize those methodology files unless needed. Use them to keep the Architect Pack aligned with the 120x workflow.

## Source Material Folder Conventions

- `references/client-docs/` is for client documents, proposals, emails, meeting notes, and intake material.
- `references/source-app/` is for existing app, code, assets, exports, or source-system material.
- `references/platform/` is for platform notes, repo notes, hosting notes, and integration context.
- `samples/` is for sample data, exports, workbooks, fixtures, and generated examples.
- `docs/` is for durable technical documentation.
- `planning/` is for project state, decisions, domain context, risks, questions, file inventory, and sprint artifacts.

## Project Intake Context

Use the intake context below as the primary project context for Architect Pack 001.

If the intake is incomplete, do not invent details. Preserve unknowns in `planning/QUESTIONS.md` and label assumptions clearly.

### Who Will Use This App

External-facing

### Business Problem

A Denny's manager manually assigns weekly tasks to crew members across multiple job codes (Cooks, Servers, Hosts, SAs), tracks completion on paper, and hand-delivers signed reports to the owner. The current C# desktop app (Taskmate) works but is single-operator and Windows-only — crew cannot view or complete tasks themselves, and the owner has no remote visibility.

### Primary Users / Roles

- **Crew** — View their own weekly task assignments, mark tasks complete from any phone or browser
- **Shift Lead** — Crew-level access plus ability to view full job code board and reassign tasks
- **Manager (Eric)** — Full access: manage job codes, task templates, crew pools, constraints, run and review assignment drafts, post assignments, confirm completions, view all reports
- **Owner** — Reports-only dashboard plus automated weekly email summary; no operational access needed

### Current Workflow

1. Eric selects a job code group and adjusts the crew pool manually (removes absent staff)
2. Algorithm generates a draft assignment across eligible crew, respecting constraints and rotation history
3. Eric reviews the draft, checks fairness spread, manually tweaks if needed
4. Eric posts the assignments for the week
5. Crew completes tasks; Eric tracks completion
6. Eric prints a signed task completion page and hand-delivers it to the owner weekly

### Pain Points

- Desktop-only — Eric is the sole operator; crew cannot self-serve
- Owner has no visibility unless Eric physically delivers the report
- Manual pool adjustment has no audit trail (gaps in history are unexplained)
- Manual draft edits are untracked, dirtying productivity evaluation data
- No ad-hoc task support — unplanned tasks fall outside the system
- Completion data is thin — no timestamp, no manager verification flag
- Cold start problem — week one has no rotation history to inform fairness

### Target Workflow

1. Eric adjusts crew pools if needed (future: schedule import does this automatically)
2. System generates weekly draft per job code — balances task count, respects constraints, checks rotation history
3. Eric reviews draft in browser — sees fairness spread, task counts per person, flags imbalances
4. Eric tweaks if needed (all changes logged with optional reason)
5. Eric posts — crew immediately sees their tasks on any phone via QR code or URL
6. Crew marks tasks complete (timestamped)
7. Eric confirms completions
8. Owner receives automated weekly email report — formatted to replace the paper sign-off

### Source Materials

- Existing C# WPF Taskmate codebase: F:\projects\taskmate\ — reference for data model, constraint engine, rotation/fairness logic, and smart assignment algorithm. Not being ported directly but logic is reusable.

### Systems / Tools Involved

- Denny's in-store WiFi (LAN access for crew)
- Cloudflare Tunnel (free public HTTPS URL — no port forwarding required)
- Tailscale (private VPN mesh — Eric and owner remote access)
- QR code posted in kitchen (crew entry point)
- Email (weekly owner report via SMTP/MailKit equivalent in Python)

### Data Inputs And Outputs

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

### Out Of Scope For First Version

- Schedule import (future — format TBD, likely CSV from scheduling software)
- Task weight / difficulty scoring (future — data model supports it, not implemented in v1)
- Multi-location support (future — architecture allows it, not built in v1)
- Native mobile app (PWA via browser is sufficient)
- Slack / Teams integration
- Predictive ML analytics (rotation history builds the foundation; ML layer added later)
- Push notifications (browser-based completion flow is sufficient for v1)

### Success Criteria

- Crew can view and complete their weekly tasks from any phone without Eric's involvement
- Owner receives an automated weekly email report replacing the hand-delivered paper sign-off
- Eric's manual assignment preparation time drops by 50% or more
- All assignment changes and pool adjustments are logged and auditable
- Per-person productivity data is clean and reliable enough to support employee evaluations

### Open Questions

- Schedule import: what software does Denny's use for scheduling, and what export format is available (CSV, PDF, other)?
- Task weight system: how will difficulty be scored when implemented — manager-defined numeric scale, time estimates, or something else?

## Rigor Profile

This profile is derived from the "Who will use this app?" intake answer. Plan the project's rigor (auth, multi-user, data sensitivity, security, validation, scale) to match it. The full profile is in the generated `docs/RIGOR_PROFILE.md`.

**Tier: External-facing.** Customers or the public; untrusted users; higher stakes. Trust and safety — assume adversarial users.

Plan rigor to match this tier across access/auth, multi-user, data sensitivity, security, validation, and scale. See `docs/RIGOR_PROFILE.md` for the full profile.

- **Access / Auth:** Full authentication + authorization. Account lifecycle (signup, password reset, lockout). Treat every request boundary as untrusted.
- **Multi-user / Tenancy:** Multi-tenant isolation where multiple customers/orgs share the system — no cross-tenant data leakage.
- **Data Sensitivity:** Treat all user data as sensitive. PII handling, encryption in transit, least privilege, and a clear view of compliance obligations.
- **Security:** Explicit threat model; rate limiting and abuse prevention; injection/XSS/CSRF/SSRF defenses; dependency hygiene; secrets management; logging that never leaks PII.
- **Validation & Tests:** Validate and sanitize all external input; test authz boundaries, error paths, and abuse cases; load/perf-check the hot paths.
- **Scale:** Design for growth — pagination, indexing, caching, background jobs, observability, and alerting.
- **Plan For:** Trust and safety. Assume adversarial users.

## Mandatory Discovery Gate

Before creating Architect Pack 001, check whether the intake is complete enough to produce useful Builder-ready planning documents.

If any of the following are TBD, vague, missing, or unclear, do not create the Architect Pack yet:

- business problem
- primary users / roles
- current workflow
- pain points
- target workflow
- systems / tools involved
- data inputs and outputs
- out-of-scope boundaries
- success criteria
- MVP / smallest useful next sprint

### Tier-specific required questions — External-facing

This is an **External-facing** project (untrusted, public users). Before generating Architect Pack 001, REQUIRE answers to:

- authentication & authorization model (account lifecycle, session handling)
- what user data is collected and its sensitivity / PII / compliance obligations
- threat model and the top abuse vectors
- rate limiting / quotas
- multi-tenant isolation (if multiple customers/orgs share the system)
- expected scale and growth
- observability / alerting

Do not generate the pack until these are answered or explicitly deferred with rationale recorded in `planning/QUESTIONS.md`.

Instead, run a discovery brainstorm first.

The discovery brainstorm should:

- ask practical, targeted questions
- avoid overwhelming me
- group questions by business goal, workflow, users, data, success criteria, and MVP scope
- propose 2-3 possible project directions if the idea is vague
- help me choose the smallest useful first version
- preserve unknowns instead of inventing them
- challenge weak assumptions
- keep the project from becoming too broad

Do not generate the downloadable Architect Pack until I explicitly say one of the following:

- "Generate the pack"
- "Create the pack"
- "Make the Architect Pack"
- "Proceed with the pack"

If the intake is incomplete, your output should be a discovery conversation, not a file.

## Task

Begin the Architect Pack 001 process.

First, apply the Mandatory Discovery Gate.

If the intake is incomplete, run the discovery brainstorm and do not create the pack yet.

If the intake is complete enough and I have explicitly approved pack generation, create the downloadable Architect Pack file.

Save Architect Packs in `planning/architect-packs/`. The importer still runs from the project root with a relative pack path.

The pack should populate:

- `planning/STATE.md`
- `planning/DECISIONS.md`
- `planning/DOMAIN.md`
- `planning/RISKS.md`
- `planning/QUESTIONS.md`
- `planning/FILE_INVENTORY.md`
- `planning/sprints/001-discovery-architecture/requirements.md`
- `planning/sprints/001-discovery-architecture/blueprint.md`
- `planning/sprints/001-discovery-architecture/acceptance.md`
- `planning/sprints/001-discovery-architecture/handoff-prompt.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`, if useful
- `docs/VALIDATION.md`

## Builder-Ready Sprint Expectations

Any sprint created by Architect Pack 001 should be small enough for a Builder to execute from the folder without redefining scope.

The sprint artifacts should include:

- clear in-scope and out-of-scope boundaries
- requirements tied to the business goal
- a practical implementation blueprint
- acceptance criteria that can be checked
- validation expectations
- risks and open questions
- an exact Builder handoff prompt

## Architect Pack Output Requirement

Only after I explicitly say "Generate the pack," create a downloadable Markdown file named:

`architect-pack-001-discovery.md`

Do not paste the full Architect Pack into chat unless file creation is unavailable.

The file must be ready to use with:

`node scripts/apply-architect-pack.js planning/architect-packs/architect-pack-001-discovery.md --dry-run`

After dry-run review, it should be ready to apply with:

`node scripts/apply-architect-pack.js planning/architect-packs/architect-pack-001-discovery.md`

## Delimiter Rules

The Architect Pack must use this exact file section format:

```text
============================================================
FILE: relative/path/from/project-root.md
============================================================

File content goes here.
```

Important:

- Every separator line must be exactly 60 equals signs.
- Do not shorten the separator.
- Do not use markdown headings instead of `FILE:` sections.
- Do not wrap the entire Architect Pack in triple backticks.
- Do not include extra commentary inside the downloadable pack unless it belongs in a target file.

## Rules

- Do not write application code.
- Do not write application code in Architect Pack 001.
- Do not invent unknown facts.
- Use assumptions only when necessary and label them clearly.
- Keep first drafts practical and lightweight.
- Keep the MVP and next sprint practical.
- Create Builder-ready requirements, blueprint, acceptance criteria, and handoff prompt.
- Output should be ready for `scripts/apply-architect-pack.js`.
- After the pack is applied, Builders should implement from the generated files under `planning/sprints/`, not directly from the Architect Pack.
