# AGENTS.md

## Project

**Name:** TaskAssigner+  
**Client:** Rifters / Eric  
**Description:** A web-based weekly task assignment system for restaurant teams that fairly distributes tasks across job-code-based crew pools, tracks completion, and reports productivity to management.  
**Tech stack:** Python 3, Flask, Flask-Login, Flask-SQLAlchemy, Flask-Bcrypt, SQLite, Vanilla JS, HTML/CSS. No frontend framework, no build pipeline. Cloudflare Tunnel for public HTTPS access. Tailscale for private remote access by manager and owner.  
**Planning folder:** `taskassigner-plus/`  
**Implementation repo:** Downloaded project folder  
**Created:** 2026-07-03

---

## Operating Model

This project uses the 120x Architect / Builder methodology.

The handoff is a folder, not a conversation.

The Architect defines requirements, blueprint, acceptance criteria, risks, decisions, and Builder handoff prompts.

The Builder executes from written artifacts and must not redefine scope or invent product behavior.

---

## Two Roles

This folder is built for both 120x roles. The handoff between them is this folder, not a conversation.

- **Architect** — plans the work: writes requirements, blueprint, acceptance, and the Builder handoff prompt, then saves an Architect Pack in `planning/architect-packs/`. Start an Architect session by reading `templates/method/120x-agent-identity.md`, then the filled starter prompt at the project root, `architect-chat-starter-prompt.md`. In Claude Code, run `/architect`.
- **Builder** — executes the plan: applies the pack, then implements only from the generated sprint files under `planning/sprints/`. In Claude Code, run `/build`.

Read `templates/method/120x-agent-identity.md` first to assume a role. Codex and other agents: state which role you are taking, then follow that role's files below.

---

## First Files to Read

Read these in order at the start of every session, in either role:

1. `AGENTS.md`
2. `README.md`
3. `project-start.md`
4. `planning/STATE.md`
5. `planning/DECISIONS.md`
6. `planning/DOMAIN.md`
7. `planning/RISKS.md`
8. `planning/QUESTIONS.md`
9. Active sprint files under `planning/sprints/`
10. Relevant docs under `docs/`

---

## Project Structure

```text
.
├── docs/                  # Durable technical documentation
├── planning/              # Project planning, Architect Packs, domain context, decisions, risks, sprints
│   ├── architect-packs/   # Architect Pack files before importer dry-run/apply
│   └── sprints/           # Builder execution files after packs are applied
├── references/            # Raw reference material and source examples
├── samples/               # Sample project metadata or generated examples
├── scripts/               # Utility scripts, including Architect Pack importer
├── src/                   # Source code when implementation begins
├── templates/             # Reusable templates used by the project
└── tests/                 # Tests and validation fixtures
```

---

## Current Boundary

This folder was generated from:

`Hosted virtual scaffold`

The current phase is Discovery / Architecture.

Until an active sprint explicitly authorizes implementation, do not write production application code.

---

## Builder Rules

- Do not write production application code unless the active sprint explicitly authorizes it.
- Do not redefine scope or invent product behavior.
- Do not expand scope into a dashboard or project management system unless the Architect documents that scope.
- Do not add auth, database, cloud sync, CRM, invoicing, or GitHub API automation unless explicitly authorized by an active sprint.
- Do not overwrite existing user project folders without an explicit confirmation strategy.
- Do not delete user files.
- Do not store secrets, API keys, passwords, tokens, or private credentials.
- Prefer boring, local, file-based automation.
- Keep generated files plain Markdown where practical.
- Update `planning/STATE.md` at the end of each meaningful session.
- Record durable decisions in `planning/DECISIONS.md`.
- Update `docs/ARCHITECTURE.md` when architecture changes.
- Update `docs/VALIDATION.md` when validation behavior changes.

---

## Sprint Workflow

Each sprint lives in:

```text
planning/sprints/###-{sprint-name}/
```

Each sprint should include:

- `requirements.md` — what and why
- `blueprint.md` — how to build it
- `acceptance.md` — what done means
- `handoff-prompt.md` — exact Builder prompt

The Builder should read all four before implementation.

Architect Packs live in `planning/architect-packs/`. Builder execution lives in `planning/sprints/`.

After an Architect Pack is applied, do not implement directly from the pack file. Implement from the generated sprint files under `planning/sprints/`.

---

## Completion Standard

A sprint is complete only when:

- The requested behavior is implemented or documented as intentionally deferred.
- Acceptance criteria are satisfied.
- Validation has been run or a clear reason is documented.
- State and documentation are updated.
- New decisions are recorded in `planning/DECISIONS.md`.
- New risks or open questions are recorded.
