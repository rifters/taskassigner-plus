from __future__ import annotations

import csv
import io
from dataclasses import dataclass


@dataclass
class ImportResult:
    rows: list[dict]
    errors: list[dict]


def _parse_text(text: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for idx, raw in enumerate(text.splitlines(), start=1):
        value = raw.strip()
        if value:
            out.append((idx, value))
    return out


def parse_people_text(text: str) -> ImportResult:
    rows = []
    errors = []
    for line_no, value in _parse_text(text):
        parts = [p.strip() for p in value.split("|", 1)]
        if len(parts[0]) == 0:
            errors.append({"line": line_no, "error": "Missing person name"})
            continue
        row = {"name": parts[0]}
        if len(parts) == 2 and parts[1]:
            row["job_code"] = parts[1]
        rows.append(row)
    return ImportResult(rows=rows, errors=errors)


def parse_job_codes_text(text: str) -> ImportResult:
    rows = []
    errors = []
    for line_no, value in _parse_text(text):
        name = value.strip()
        if not name:
            errors.append({"line": line_no, "error": "Missing job code name"})
            continue
        rows.append({"name": name})
    return ImportResult(rows=rows, errors=errors)


def parse_task_templates_text(text: str) -> ImportResult:
    rows = []
    errors = []
    for line_no, value in _parse_text(text):
        parts = [p.strip() for p in value.split("|", 1)]
        if len(parts[0]) == 0:
            errors.append({"line": line_no, "error": "Missing task title"})
            continue
        row = {"title": parts[0]}
        if len(parts) == 2 and parts[1]:
            row["job_code"] = parts[1]
        rows.append(row)
    return ImportResult(rows=rows, errors=errors)


def parse_csv(content: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(content))
    return [dict(r) for r in reader]
