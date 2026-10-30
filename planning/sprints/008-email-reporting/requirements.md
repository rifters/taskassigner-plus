# Sprint 008 — Manager Weekly Email Reporting

## Goal
Send the weekly completion report to all active managers and owners with valid email addresses, using a concise summary email and a complete assignment-level CSV attachment.

## In scope
- Active `manager` and `owner` users are recipients when they have a valid email.
- Duplicate addresses are sent once.
- HTML email with plain-text fallback.
- Thursday–Wednesday date range in subject and body.
- Overall totals, completion sources, lowest-rate people/tasks, and never-finished people.
- Full posted-assignment CSV attachment.
- Scheduled and test sends use the same recipient resolution.

## Out of scope
- Crew or shift-lead recipients.
- Custom PDF generation.
- Employee-specific private reports.
- SMTP credential changes.
