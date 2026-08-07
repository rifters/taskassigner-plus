from __future__ import annotations

import logging
import time
from logging import StreamHandler

from flask import Flask, g, jsonify, request

from .config import Config
from .extensions import bcrypt, csrf, db, login_manager
from .models import User
from .db_init import ensure_schema


def _configure_logging(app: Flask) -> None:
    app.logger.handlers.clear()
    handler = StreamHandler()
    handler.setLevel(getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO))
    app.logger.addHandler(handler)
    app.logger.setLevel(getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO))


SENSITIVE_KEYS = {"password", "pin", "smtp_password", "new_pin"}


def _sanitize_payload(payload: dict | None) -> dict:
    if not payload:
        return {}
    out = {}
    for k, v in payload.items():
        if k.lower() in SENSITIVE_KEYS:
            out[k] = "[REDACTED]"
        else:
            out[k] = v
    return out


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    _configure_logging(app)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.password_login"

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    from .routes.auth import bp as auth_bp
    from .routes.manage import bp as manage_bp
    from .routes.assignments import bp as assignments_bp
    from .routes.completions import bp as completions_bp
    from .routes.reports import bp as reports_bp
    from .routes.audit import bp as audit_bp
    from .routes.owner import bp as owner_bp
    from .routes.views import bp as views_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(manage_bp)
    app.register_blueprint(assignments_bp)
    app.register_blueprint(completions_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(owner_bp)
    app.register_blueprint(views_bp)

    @app.before_request
    def _start_timer():
        g.request_started_at = time.time()

    @app.after_request
    def _log_request(response):
        duration_ms = int((time.time() - getattr(g, "request_started_at", time.time())) * 1000)
        payload = None
        if request.method in {"POST", "PATCH", "PUT", "DELETE"}:
            try:
                payload = request.get_json(silent=True)
            except Exception:
                payload = None
        app.logger.info(
            {
                "event": "http_request",
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
                "payload": _sanitize_payload(payload),
            }
        )
        return response

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.errorhandler(403)
    def forbidden(_):
        return jsonify({"error": "forbidden"}), 403

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "not_found"}), 404

    ensure_schema(app)

    return app
