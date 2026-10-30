from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass


@dataclass
class ImportResult:
    rows: list[dict]
    errors: list[dict]


def normalize_task_title(title: str) -> str:
    return " ".join((title or "").strip().casefold().split())


_NUMBERED_TEXT_RE = re.compile(r"^(\S+)\s*\.\s*(.*?)\s*$")


def _parse_number(raw: str) -> tuple[int | None, str | None]:
    value = (raw or "").strip()
    if not value:
        return None, "missing_number"
    if not value.isdigit():
        return None, "invalid_number"
    if len(value) > 1 and value.startswith("0"):
        return None, "leading_zero_number"
    number = int(value)
    if number <= 0:
        return None, "nonpositive_number"
    return number, None


def _add_missing_number_error(rows: list[dict], errors: list[dict], job_code: str | None = None) -> None:
    numbers = {row["number"] for row in rows}
    if not numbers:
        return
    expected = set(range(1, max(numbers) + 1))
    missing = sorted(expected - numbers)
    if missing:
        error = {"error": "missing_numbers", "numbers": missing}
        if job_code is not None:
            error["job_code"] = job_code
        errors.append(error)


def parse_numbered_task_text(text: str) -> ImportResult:
    rows = []
    errors = []
    seen: set[int] = set()
    for line_no, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip():
            continue
        match = _NUMBERED_TEXT_RE.match(raw.strip())
        if not match:
            errors.append({"line": line_no, "error": "malformed_numbered_row"})
            continue
        number, number_error = _parse_number(match.group(1))
        title = match.group(2).strip()
        if number_error:
            errors.append({"line": line_no, "error": number_error})
            continue
        if not title:
            errors.append({"line": line_no, "error": "missing_title"})
            continue
        if number in seen:
            errors.append({"line": line_no, "error": "duplicate_number", "number": number})
            continue
        seen.add(number)
        rows.append({"line": line_no, "number": number, "title": title})
    _add_missing_number_error(rows, errors)
    return ImportResult(rows=rows, errors=errors)


def parse_numbered_task_csv(content: str) -> ImportResult:
    rows = []
    errors = []
    reader = csv.DictReader(io.StringIO(content))
    fieldnames = [field.strip() for field in (reader.fieldnames or []) if field]
    if "number" not in fieldnames or "title" not in fieldnames:
        return ImportResult(rows=[], errors=[{"line": 1, "error": "number_and_title_headers_required"}])

    seen_by_job_code: dict[str, set[int]] = {}
    for line_no, raw in enumerate(reader, start=2):
        row = {key.strip(): (value or "").strip() for key, value in raw.items() if key}
        number, number_error = _parse_number(row.get("number", ""))
        if number_error:
            errors.append({"line": line_no, "error": number_error})
            continue
        job_code = row.get("job_code", "")
        seen = seen_by_job_code.setdefault(job_code, set())
        if number in seen:
            errors.append({"line": line_no, "error": "duplicate_number", "number": number})
            continue
        seen.add(number)
        title = row.get("title", "")
        if not title:
            errors.append({"line": line_no, "error": "missing_title"})
            continue
        parsed = {"line": line_no, "number": number, "title": title}
        for key in ("notes", "active", "job_code"):
            if key in row:
                parsed[key] = row[key]
        rows.append(parsed)
    for job_code, numbers in seen_by_job_code.items():
        _add_missing_number_error([{"number": number} for number in numbers], errors, job_code or None)
    return ImportResult(rows=rows, errors=errors)


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
