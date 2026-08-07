# Project Start

## Project Metadata

| Field | Value |
|---|---|
| Project name | TaskAssigner+ |
| Client name | Rifters / Eric |
| Project slug | taskassigner-plus |
| One-sentence description | A web-based weekly task assignment system for restaurant teams that fairly distributes tasks across job-code-based crew pools, tracks completion, and reports productivity to management. |
| Project type | Internal tool |
| Planning folder | taskassigner-plus/ |
| Implementation repo path | Downloaded project folder |
| Canonical GitHub repo | Local: F:\projects\taskassigner-plus\ — push to GitHub (github.com/rifters/taskassigner-plus) when ready. |
| Tech stack | Python 3, Flask, Flask-Login, Flask-SQLAlchemy, Flask-Bcrypt, SQLite, Vanilla JS, HTML/CSS. No frontend framework, no build pipeline. Cloudflare Tunnel for public HTTPS access. Tailscale for private remote access by manager and owner. |
| Scaffold source | Hosted virtual scaffold |

## Created Structure

- `planning/architect-packs/`
- `references/client-docs/`
- `references/source-app/`
- `references/platform/`
- `samples/`

## Personalized Files

- `README.md`
- `AGENTS.md`
- `planning/STATE.md`
- `planning/DOMAIN.md`
- `planning/FILE_INVENTORY.md`

## Generated Files

- `planning/INTAKE.md`
- `project-start.md`
- `architect-chat-starter-prompt.md`

## Architect Intake

`planning/INTAKE.md` captures the guided intake context collected before project creation. Use it as primary discovery context when creating Architect Pack 001.


## Next Steps

1. Open the new project folder.
2. Review `project-start.md`.
3. Review `planning/INTAKE.md`.
4. Open `architect-chat-starter-prompt.md`.
5. Start a new Architect chat.
6. Start Architect Pack 001 discovery.
7. Generate Architect Pack 001 only after explicit approval.
8. Save the Architect Pack in `planning/architect-packs/`.
9. Dry-run the importer.
10. Apply the Architect Pack after review.

## Architect Pack Commands

Save Architect Packs in `planning/architect-packs/`.

Dry-run from the project root:

`node scripts/apply-architect-pack.js planning/architect-packs/architect-pack-###-{sprint-name}.md --dry-run`

Apply from the project root after reviewing the dry-run:

`node scripts/apply-architect-pack.js planning/architect-packs/architect-pack-###-{sprint-name}.md`

After a pack is applied, Builders implement from the generated sprint files under `planning/sprints/`, not directly from the Architect Pack.
