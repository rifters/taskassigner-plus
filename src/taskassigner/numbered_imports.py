from __future__ import annotations

from typing import Iterable

from .extensions import db
from .imports import normalize_task_title
from .models import JobCode, TaskTemplate


def _active_value(value: object) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().casefold()
    if normalized in {"true", "1", "yes", "active"}:
        return True
    if normalized in {"false", "0", "no", "inactive"}:
        return False
    return None


def _review(row: dict, error: str, **details: object) -> dict:
    result = {"line": row.get("line"), "error": error}
    result.update(details)
    return result


def apply_numbered_task_rows(
    rows: Iterable[dict],
    errors: Iterable[dict],
    *,
    selected_job_code: str | None = None,
    source_format: str = "csv",
) -> dict:
    rows = list(rows)
    result = {
        "created": 0,
        "updated": 0,
        "errors": list(errors),
        "reviews": [],
    }
    incoming_by_job_code: dict[int, set[int]] = {}

    for row in rows:
        job_code_name = (row.get("job_code") or selected_job_code or "").strip()
        if not job_code_name:
            result["errors"].append(_review(row, "responsible_job_code_required"))
            continue
        job_code = JobCode.query.filter_by(name=job_code_name).first()
        if not job_code:
            result["errors"].append(_review(row, "unknown_job_code", job_code=job_code_name))
            continue

        number = row.get("number")
        incoming_by_job_code.setdefault(job_code.id, set()).add(number)
        matches = TaskTemplate.query.filter_by(
            responsible_job_code_id=job_code.id,
            master_list_number=number,
        ).all()
        if len(matches) > 1:
            result["reviews"].append(_review(row, "duplicate_existing_number", number=number))
            continue
        existing = matches[0] if matches else None
        if existing:
            if normalize_task_title(existing.title) != normalize_task_title(row.get("title", "")):
                result["reviews"].append(
                    _review(row, "number_title_mismatch", number=number, existing_title=existing.title)
                )
                continue
            if source_format == "csv":
                if "notes" in row:
                    existing.notes = row.get("notes") or None
                if "active" in row:
                    active = _active_value(row.get("active"))
                    if active is None and row.get("active") not in (None, ""):
                        result["errors"].append(_review(row, "invalid_active_value"))
                        continue
                    if active is not None:
                        existing.active = active
            result["updated"] += 1
            continue

        legacy = TaskTemplate.query.filter_by(
            responsible_job_code_id=job_code.id,
            master_list_number=None,
        ).all()
        legacy_matches = [
            task for task in legacy if normalize_task_title(task.title) == normalize_task_title(row.get("title", ""))
        ]
        if legacy_matches:
            result["reviews"].append(
                _review(row, "legacy_number_confirmation_required", task_id=legacy_matches[0].id)
            )
            continue

        active = _active_value(row.get("active")) if source_format == "csv" else None
        if source_format == "csv" and row.get("active") not in (None, "") and active is None:
            result["errors"].append(_review(row, "invalid_active_value"))
            continue
        task = TaskTemplate(
            title=row["title"].strip(),
            master_list_number=number,
            notes=(row.get("notes") or None) if source_format == "csv" else None,
            responsible_job_code_id=job_code.id,
            active=True if active is None else active,
        )
        db.session.add(task)
        result["created"] += 1

    for job_code_id, numbers in incoming_by_job_code.items():
        existing_numbered = TaskTemplate.query.filter(
            TaskTemplate.responsible_job_code_id == job_code_id,
            TaskTemplate.master_list_number.isnot(None),
        ).all()
        for task in existing_numbered:
            if task.master_list_number not in numbers:
                result["reviews"].append(
                    {
                        "error": "missing_source_number",
                        "number": task.master_list_number,
                        "task_id": task.id,
                    }
                )

    db.session.commit()
    return result
