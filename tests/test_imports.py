import pytest

from taskassigner.imports import (
    normalize_task_title,
    parse_numbered_task_csv,
    parse_numbered_task_text,
    parse_people_text,
    parse_task_templates_text,
)


def test_parse_people_text_accepts_value_and_value_pipe_jobcode():
    parsed = parse_people_text("Alice\nBob|Cooks\n")
    assert parsed.errors == []
    assert parsed.rows == [{"name": "Alice"}, {"name": "Bob", "job_code": "Cooks"}]


def test_parse_task_templates_text_parses_title_and_optional_jobcode():
    parsed = parse_task_templates_text("Clean grill|Cooks\nWipe tables\n")
    assert parsed.errors == []
    assert parsed.rows == [
        {"title": "Clean grill", "job_code": "Cooks"},
        {"title": "Wipe tables"},
    ]


def test_parse_numbered_task_text_ignores_blanks_and_requires_consecutive_numbers():
    parsed = parse_numbered_task_text("1.  Clean   Grill\n\n3. Stock Freezer\nnot numbered\n")

    assert parsed.rows == [{"line": 1, "number": 1, "title": "Clean   Grill"}, {"line": 3, "number": 3, "title": "Stock Freezer"}]
    assert {error["error"] for error in parsed.errors} == {"malformed_numbered_row", "missing_numbers"}
    assert parsed.errors[-1]["numbers"] == [2]


def test_parse_numbered_csv_rejects_leading_zero_numbers():
    parsed = parse_numbered_task_csv(
        "number,title,notes\n01,Opening,one\n1,Opening valid,two\n2,Closing,three\n"
    )

    assert parsed.rows == [
        {"line": 3, "number": 1, "title": "Opening valid", "notes": "two"},
        {"line": 4, "number": 2, "title": "Closing", "notes": "three"},
    ]
    assert [error["error"] for error in parsed.errors] == ["leading_zero_number"]


def test_parse_numbered_csv_rejects_duplicate_numbers():
    parsed = parse_numbered_task_csv("number,title\n1,Opening\n1,Duplicate\n2,Closing\n")

    assert parsed.rows == [
        {"line": 2, "number": 1, "title": "Opening"},
        {"line": 4, "number": 2, "title": "Closing"},
    ]
    assert parsed.errors == [{"line": 3, "error": "duplicate_number", "number": 1}]


def test_parse_numbered_csv_checks_consecutive_numbers_per_job_code():
    parsed = parse_numbered_task_csv(
        "job_code,number,title\nCooks,1,Open\nCooks,3,Close\nSAs,1,Seat\n"
    )

    assert parsed.rows[-1]["job_code"] == "SAs"
    assert parsed.errors == [{"error": "missing_numbers", "numbers": [2], "job_code": "Cooks"}]


def test_normalize_task_title_only_collapses_case_and_whitespace():
    assert normalize_task_title("  Clean   Grill ") == "clean grill"
    assert normalize_task_title("Clean-Grill") != normalize_task_title("Clean Grill")
