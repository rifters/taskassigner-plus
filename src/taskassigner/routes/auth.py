from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user

from ..extensions import db
from ..models import PasswordResetToken, User
from ..security import is_locked_out, is_rate_limited, record_auth_attempt, role_required

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.get("/login")
def login_page():
    return render_template("auth/login.html", error=None)


@bp.post("/login")
def browser_login():
    identifier = (request.form.get("name") or "").strip()
    password = request.form.get("password") or ""
    if not identifier or not password:
        return render_template("auth/login.html", error="Enter both username and password."), 400
    if is_rate_limited(identifier) or is_locked_out(identifier):
        return render_template("auth/login.html", error="Login temporarily locked. Try again later."), 429

    user = User.query.filter_by(name=identifier, active=True).first()
    if not user or not user.check_password(password) or user.role != "manager":
        record_auth_attempt(identifier, False)
        return render_template("auth/login.html", error="Invalid manager credentials."), 401

    login_user(user, remember=False)
    _apply_session_ttl(user.role)
    record_auth_attempt(identifier, True)
    return redirect(url_for("manage.manager_home"))


@bp.get("/login-crew")
def crew_login_page():
    return render_template("auth/crew_login.html", error=None)


@bp.post("/login-crew")
def browser_crew_login():
    identifier = (request.form.get("name") or "").strip()
    pin = str(request.form.get("pin") or "").strip()
    if not identifier or not pin:
        return render_template("auth/crew_login.html", error="Enter both name and PIN."), 400
    user = User.query.filter_by(name=identifier, active=True, role="crew").first()
    if not user or not user.check_pin(pin):
        record_auth_attempt(identifier, False)
        return render_template("auth/crew_login.html", error="Invalid crew credentials."), 401
    login_user(user, remember=False)
    _apply_session_ttl(user.role)
    record_auth_attempt(identifier, True)
    return redirect("/crew/tasks")


def _apply_session_ttl(role: str) -> None:
    ttl_map = current_app.config.get(
        "SESSION_TTL_HOURS",
        {"crew": 12, "shift_lead": 8, "manager": 8, "owner": 24},
    )
    ttl_hours = ttl_map.get(role, 8)
    session.permanent = True
    session["role"] = role
    session["session_ttl_hours"] = ttl_hours
    current_app.permanent_session_lifetime = timedelta(hours=ttl_hours)


def _issue_password_reset_token(target_user: User, actor_user: User) -> PasswordResetToken:
    token = secrets.token_urlsafe(24)
    expires_minutes = int(current_app.config.get("PASSWORD_RESET_TOKEN_MINUTES", 30))
    row = PasswordResetToken(
        target_user_id=target_user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(minutes=expires_minutes),
        created_by_user_id=actor_user.id,
    )
    db.session.add(row)
    db.session.commit()
    return row


@bp.post("/login-password")
def password_login():
    data = request.get_json(force=True)
    identifier = (data.get("name") or "").strip()
    password = data.get("password") or ""
    if not identifier or not password:
        return jsonify({"error": "missing_credentials"}), 400

    if is_rate_limited(identifier):
        return jsonify({"error": "rate_limited"}), 429

    if is_locked_out(identifier):
        return jsonify({"error": "locked_out"}), 429

    user = User.query.filter_by(name=identifier, active=True).first()
    if not user or not user.check_password(password):
        record_auth_attempt(identifier, False)
        return jsonify({"error": "invalid_credentials"}), 401

    if user.role not in {"shift_lead", "manager", "owner"}:
        record_auth_attempt(identifier, False)
        return jsonify({"error": "wrong_auth_method"}), 403

    login_user(user, remember=False)
    _apply_session_ttl(user.role)
    record_auth_attempt(identifier, True)
    return jsonify({"ok": True, "role": user.role, "session_ttl_hours": session["session_ttl_hours"]})


@bp.post("/login-pin")
def pin_login():
    data = request.get_json(force=True)
    identifier = (data.get("name") or "").strip()
    pin = str(data.get("pin") or "").strip()
    if not identifier or not pin:
        return jsonify({"error": "missing_credentials"}), 400

    if is_rate_limited(identifier):
        return jsonify({"error": "rate_limited"}), 429

    if is_locked_out(identifier):
        return jsonify({"error": "locked_out"}), 429

    user = User.query.filter_by(name=identifier, active=True).first()
    if not user or not user.check_pin(pin):
        record_auth_attempt(identifier, False)
        return jsonify({"error": "invalid_credentials"}), 401

    if user.role != "crew":
        record_auth_attempt(identifier, False)
        return jsonify({"error": "wrong_auth_method"}), 403

    login_user(user, remember=False)
    _apply_session_ttl(user.role)
    record_auth_attempt(identifier, True)
    return jsonify({"ok": True, "role": user.role, "session_ttl_hours": session["session_ttl_hours"]})


@bp.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    session.clear()
    return jsonify({"ok": True})


@bp.post("/reset-pin")
@role_required("manager")
def reset_pin():
    data = request.get_json(force=True)
    target_name = data.get("target_name")
    new_pin = str(data.get("new_pin") or "").strip()
    if not target_name or not new_pin:
        return jsonify({"error": "missing_fields"}), 400

    target = User.query.filter_by(name=target_name, active=True).first()
    if not target or target.role != "crew":
        return jsonify({"error": "target_invalid"}), 400

    target.set_pin(new_pin)
    db.session.commit()
    return jsonify({"ok": True})


@bp.post("/reset-password/request")
@role_required("manager")
def reset_password_request():
    data = request.get_json(force=True)
    target_name = (data.get("target_name") or "").strip()
    if not target_name:
        return jsonify({"error": "missing_fields"}), 400

    target = User.query.filter_by(name=target_name, active=True).first()
    if not target or target.role not in {"shift_lead", "manager", "owner"}:
        return jsonify({"error": "target_invalid"}), 400

    row = _issue_password_reset_token(target, current_user)
    return jsonify(
        {
            "ok": True,
            "target": target.name,
            "reset_token": row.token,
            "expires_at": row.expires_at.isoformat(),
        }
    )


@bp.post("/reset-password/confirm")
def reset_password_confirm():
    data = request.get_json(force=True)
    token = (data.get("token") or "").strip()
    new_password = (data.get("new_password") or "").strip()
    if not token or not new_password:
        return jsonify({"error": "missing_fields"}), 400

    row = PasswordResetToken.query.filter_by(token=token).first()
    if not row:
        return jsonify({"error": "invalid_token"}), 400
    if row.used_at is not None:
        return jsonify({"error": "token_already_used"}), 400
    if row.expires_at < datetime.utcnow():
        return jsonify({"error": "token_expired"}), 400

    target = db.session.get(User, row.target_user_id)
    if not target or not target.active:
        return jsonify({"error": "target_invalid"}), 400

    target.set_password(new_password)
    row.used_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"ok": True, "target": target.name})
