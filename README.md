# TaskAssigner+

**Client:** Rifters / Eric  
**Description:** A web-based weekly task assignment system for restaurant teams that fairly distributes tasks across job-code-based crew pools, tracks completion, and reports productivity to management.  
**Project type:** Internal tool  
**Tech stack:** Python 3, Flask, Flask-Login, Flask-SQLAlchemy, Flask-Bcrypt, SQLite, Vanilla JS, HTML/CSS. No frontend framework, no build pipeline. Cloudflare Tunnel for public HTTPS access. Tailscale for private remote access by manager and owner.

---

## Purpose

This project folder was created by the 120x Project Launcher for the 120x Architect / Builder workflow.

It is ready for project-specific discovery and architecture planning.

---

## Quick Start (current Builder state)

### 1) Install deps

```bash
python -m pip install Flask Flask-Login Flask-SQLAlchemy Flask-Bcrypt WTForms Flask-WTF pytest
```

### 2) Initialize schema safely

```bash
python scripts/init_db.py
```

This is idempotent and ensures newly added tables (e.g. app settings) exist.

### 3) Run app

```bash
python src/run.py
```

### 4) Run tests

```bash
python -m pytest tests -q
```

---

## Owner Weekly Email Setup (configurable recipient)

Recipient is managed in-app (not hardcoded):

- `POST /api/owner/settings/report-email` (manager)
- `GET /api/owner/settings/report-email` (manager/owner)

SMTP env config required:

- `SMTP_HOST`
- `SMTP_PORT` (default `587`)
- `SMTP_USER`
- `SMTP_PASSWORD`
- `SMTP_USE_TLS` (`true` / `false`)
- `EMAIL_FROM` (falls back to `SMTP_USER`)

Send endpoints:

- `POST /api/owner/reports/weekly/send-email`
- `POST /api/owner/reports/test-email` (manager test trigger)
- `GET /api/owner/reports/weekly/schedule`
- `POST /api/owner/reports/weekly/schedule` (manager configures weekday/hour/minute + enable)
- `POST /api/owner/reports/weekly/run-scheduled` (manager triggers scheduler logic once; supports force/dry_run)

---

## Next workflow step

1. Review `project-start.md`.
2. Open `architect-chat-starter-prompt.md`.
3. Start a new Architect chat.
4. Start Architect Pack 001 discovery.
5. Generate Architect Pack 001 only after explicit approval.
6. Save the Architect Pack in `planning/architect-packs/`.
7. Dry-run the importer.
8. Apply the Architect Pack after review.
