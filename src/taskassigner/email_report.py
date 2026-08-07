from __future__ import annotations

from datetime import datetime


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
        f"TaskAssigner+ Weekly Summary - {payload.get('week', 'N/A')}",
        f"Generated: {payload.get('generated_at', '')}",
        "",
        f"People rows: {payload.get('summary', {}).get('people_count', 0)}",
        f"Task rows: {payload.get('summary', {}).get('task_entries', 0)}",
        "",
        "Person completion metrics:",
    ]

    for row in payload.get("person_rows", []):
        lines.append(
            f"- {row.get('name')}: assigned={row.get('assigned', 0)}, completed={row.get('completed', 0)}, completion%={row.get('completion_pct', 0)}"
        )

    lines.append("")
    lines.append("Task consistency metrics:")
    for row in payload.get("task_rows", []):
        lines.append(
            f"- {row.get('task_title')}/{row.get('assignee_name')}: assigned={row.get('assigned', 0)}, completed={row.get('completed', 0)}, completion%={row.get('completion_pct', 0)}, consistency_spread%={row.get('consistency_spread_pct', 0)}"
        )

    return "\n".join(lines)
