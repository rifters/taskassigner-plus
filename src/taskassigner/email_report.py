from __future__ import annotations

import csv
import io
import re
from datetime import datetime


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def resolve_weekly_report_recipients(users, legacy_recipient: str = "") -> list[str]:
    addresses = set()
    for user in users:
        email = (user.email or "").strip().lower()
        if user.active and user.role in {"manager", "owner"} and _EMAIL_RE.fullmatch(email):
            addresses.add(email)
    if not addresses:
        fallback = (legacy_recipient or "").strip().lower()
        if _EMAIL_RE.fullmatch(fallback):
            addresses.add(fallback)
    return sorted(addresses)


def render_weekly_report_csv(payload: dict) -> str:
    fields = [
        "week", "task_number", "task_title", "job_code", "assignee_name",
        "completion_status", "completion_source", "completed_by_name",
        "manager_reason", "completed_at",
    ]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(payload.get("assignment_rows", []))
    return output.getvalue()


def render_owner_weekly_email_html(payload: dict) -> str:
    summary = payload.get("summary", {})
    people = payload.get("lowest_people", [])
    tasks = payload.get("lowest_tasks", [])
    rows = lambda values, label: "".join(
        f"<tr><td>{row.get(label, '')}</td><td>{row.get('assigned', 0)}</td>"
        f"<td>{row.get('completed', 0)}</td><td>{row.get('not_completed', 0)}</td>"
        f"<td>{row.get('completion_pct', 0)}%</td></tr>" for row in values
    )
    return f"""<html><body>
<h1>TaskAssigner+ Weekly Completion Report</h1>
<p><strong>{payload.get('week_label', payload.get('week', 'N/A'))}</strong></p>
<h2>Overall performance</h2>
<p>Assigned: <strong>{summary.get('assigned', 0)}</strong> · Completed: <strong>{summary.get('completed', 0)}</strong> · Not completed: <strong>{summary.get('not_completed', 0)}</strong> · Completion rate: <strong>{summary.get('completion_pct', 0)}%</strong></p>
<p>Crew self-completed: {summary.get('crew_self', 0)} · Manager on behalf: {summary.get('manager_on_behalf', 0)}</p>
<h2>Lowest completion-rate people</h2>
<table border="1" cellpadding="5"><tr><th>Person</th><th>Assigned</th><th>Completed</th><th>Not completed</th><th>Rate</th></tr>{rows(people, 'name')}</table>
<h2>Lowest completion-rate tasks</h2>
<table border="1" cellpadding="5"><tr><th>Task</th><th>Assigned</th><th>Completed</th><th>Not completed</th><th>Rate</th></tr>{rows(tasks, 'task_title')}</table>
<p>The complete assignment-level report is attached as a CSV file.</p>
</body></html>"""


def build_owner_weekly_email_payload(week_key: str, person_rows: list[dict], task_rows: list[dict]) -> dict:
    return {
        "week": week_key,
        "generated_at": datetime.utcnow().isoformat(),
        "person_rows": person_rows,
        "task_rows": task_rows,
        "summary": {
            "people_count": len(person_rows),
            "task_entries": len(task_rows),
        },
    }


def render_owner_weekly_email_text(payload: dict) -> str:
    lines = [
        f"TaskAssigner+ Weekly Completion Report - {payload.get('week_label', payload.get('week', 'N/A'))}",
        f"Generated: {payload.get('generated_at', '')}",
        "",
        f"Assigned: {payload.get('summary', {}).get('assigned', 0)}",
        f"Completed: {payload.get('summary', {}).get('completed', 0)}",
        f"Not completed: {payload.get('summary', {}).get('not_completed', 0)}",
        f"Completion rate: {payload.get('summary', {}).get('completion_pct', 0)}%",
        f"Crew self-completed: {payload.get('summary', {}).get('crew_self', 0)}",
        f"Manager on behalf: {payload.get('summary', {}).get('manager_on_behalf', 0)}",
        "",
        "Lowest completion-rate people:",
    ]

    for row in payload.get("lowest_people", payload.get("person_rows", [])):
        lines.append(
            f"- {row.get('name')}: assigned={row.get('assigned', 0)}, completed={row.get('completed', 0)}, completion%={row.get('completion_pct', 0)}"
        )

    lines.append("")
    lines.append("Top people with zero completed assignments:")
    for row in payload.get("never_finished_people", []):
        lines.append(f"- {row.get('name')}: assigned={row.get('assigned', 0)}, not_completed={row.get('not_completed', 0)}")

    lines.append("")
    lines.append("Lowest completion-rate tasks:")
    for row in payload.get("lowest_tasks", []):
        lines.append(
            f"- {row.get('task_title')}: assigned={row.get('assigned', 0)}, completed={row.get('completed', 0)}, not_completed={row.get('not_completed', 0)}, completion%={row.get('completion_pct', 0)}"
        )

    return "\n".join(lines)
