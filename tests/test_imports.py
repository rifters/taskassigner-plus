import pytest

from taskassigner.imports import parse_people_text, parse_task_templates_text


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
