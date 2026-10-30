import sqlite3

from taskassigner.app import create_app
from taskassigner.db_init import ensure_schema


def test_ensure_schema_adds_completion_columns_to_existing_database(tmp_path):
    db_path = tmp_path / "legacy.db"
    connection = sqlite3.connect(db_path)
    connection.execute(
        """
        CREATE TABLE task_completions (
            id INTEGER PRIMARY KEY,
            assignment_item_id INTEGER NOT NULL UNIQUE,
            completed_by INTEGER NOT NULL,
            completed_at DATETIME NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
        """
    )
    connection.commit()
    connection.close()

    class TestConfig:
        SECRET_KEY = "test"
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path.as_posix()}"
        SQLALCHEMY_TRACK_MODIFICATIONS = False

    app = create_app(TestConfig)
    ensure_schema(app)

    connection = sqlite3.connect(db_path)
    columns = {row[1] for row in connection.execute("PRAGMA table_info(task_completions)")}
    connection.close()

    assert {"completion_status", "completion_source", "manager_reason", "manager_confirmed_by", "manager_confirmed_at"} <= columns
