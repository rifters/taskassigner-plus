from __future__ import annotations

from flask import Flask

from .extensions import db


def ensure_schema(app: Flask) -> None:
    """Create any missing tables on the configured database.

    This is intentionally idempotent and safe to run on startup/setup.
    """
    with app.app_context():
        db.create_all()
