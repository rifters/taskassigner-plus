from __future__ import annotations

from flask import Flask
from sqlalchemy import inspect, text

from .extensions import db


def ensure_schema(app: Flask) -> None:
    """Create any missing tables on the configured database.

    This is intentionally idempotent and safe to run on startup/setup.
    """
    with app.app_context():
        db.create_all()
        columns = {column["name"] for column in inspect(db.engine).get_columns("task_templates")}
        if "master_list_number" not in columns:
            with db.engine.begin() as connection:
                connection.execute(text("ALTER TABLE task_templates ADD COLUMN master_list_number INTEGER"))

        completion_columns = {
            column["name"] for column in inspect(db.engine).get_columns("task_completions")
        }
        completion_migrations = {
            "completion_status": "ALTER TABLE task_completions ADD COLUMN completion_status VARCHAR(20) NOT NULL DEFAULT 'completed'",
            "completion_source": "ALTER TABLE task_completions ADD COLUMN completion_source VARCHAR(32) NOT NULL DEFAULT 'crew_self'",
            "manager_reason": "ALTER TABLE task_completions ADD COLUMN manager_reason VARCHAR(500)",
            "manager_confirmed_by": "ALTER TABLE task_completions ADD COLUMN manager_confirmed_by INTEGER",
            "manager_confirmed_at": "ALTER TABLE task_completions ADD COLUMN manager_confirmed_at DATETIME",
        }
        missing_completion_migrations = [
            statement for name, statement in completion_migrations.items() if name not in completion_columns
        ]
        if missing_completion_migrations:
            with db.engine.begin() as connection:
                for statement in missing_completion_migrations:
                    connection.execute(text(statement))
