from __future__ import annotations

from datetime import datetime, timedelta
from functools import wraps

from flask import abort, current_app, request
from flask_login import current_user, login_required

from .extensions import db
from .models import AuthAttempt


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def _token(identifier: str) -> str:
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
    return f"{identifier}|{ip}"


def record_auth_attempt(identifier: str, success: bool) -> None:
    attempt = AuthAttempt(identifier=identifier, ip_token=_token(identifier), success=success)
    db.session.add(attempt)
    db.session.commit()


def is_locked_out(identifier: str) -> bool:
    window = timedelta(minutes=current_app.config["LOCKOUT_MINUTES"])
    since = datetime.utcnow() - window
    failed_count = (
        AuthAttempt.query.filter_by(identifier=identifier, success=False)
        .filter(AuthAttempt.occurred_at >= since)
        .count()
    )
    return failed_count >= current_app.config["LOCKOUT_THRESHOLD"]


def is_rate_limited(identifier: str) -> bool:
    window = timedelta(minutes=1)
    since = datetime.utcnow() - window
    attempts = (
        AuthAttempt.query.filter_by(identifier=identifier)
        .filter(AuthAttempt.occurred_at >= since)
        .count()
    )
    return attempts >= current_app.config.get("AUTH_RATE_LIMIT_PER_MINUTE", 5)
