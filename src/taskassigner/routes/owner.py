from __future__ import annotations

import smtplib
from datetime import datetime
from email.message import EmailMessage

from flask import Blueprint, current_app, jsonify, request

from .reports import build_person_rows, build_task_rows
from ..email_report import build_owner_weekly_email_payload, render_owner_weekly_email_text
from ..extensions import db
from ..models import AppSetting
from ..security import role_required

bp = Blueprint("owner", __name__, url_prefix="/api/owner")


def _get_setting(key: str, default: str = "") -> str:
    row = db.session.get(AppSetting, key)
    return row.value if row else default


def _set_setting(key: str, value: str) -> None:
    row = db.session.get(AppSetting, key)
    if row:
        row.value = value
    else:
        row = AppSetting(key=key, value=value)
        db.session.add(row)
    db.session.commit()


def _build_report_payload(week_key: str) -> dict:
    filters = {"week": week_key} if week_key != "current" else {}
    person_rows = build_person_rows(filters)
    task_rows = build_task_rows(filters)
    return build_owner_weekly_email_payload(week_key, person_rows, task_rows)


def _send_email_message(week_key: str, recipient: str, body_text: str) -> None:
    smtp_host = current_app.config.get("SMTP_HOST")
    smtp_port = current_app.config.get("SMTP_PORT", 587)
    smtp_user = current_app.config.get("SMTP_USER")
    smtp_password = current_app.config.get("SMTP_PASSWORD")
    smtp_use_tls = bool(current_app.config.get("SMTP_USE_TLS", True))
    email_from = current_app.config.get("EMAIL_FROM") or smtp_user

    if not smtp_host or not email_from:
        raise RuntimeError("smtp_not_configured")

    msg = EmailMessage()
    msg["Subject"] = f"TaskAssigner+ Weekly Summary ({week_key})"
    msg["From"] = email_from
    msg["To"] = recipient
    msg.set_content(body_text)

    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as smtp:
        if smtp_use_tls:
            smtp.starttls()
        if smtp_user and smtp_password:
            smtp.login(smtp_user, smtp_password)
        smtp.send_message(msg)


def _boolish(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _week_key(now_utc: datetime) -> str:
    return now_utc.strftime("%G-W%V")


def _get_schedule_config() -> dict:
    return {
        "enabled": _boolish(_get_setting("owner_weekly_schedule_enabled", "0")),
        "weekday": int(_get_setting("owner_weekly_schedule_weekday", "1")),
        "hour_utc": int(_get_setting("owner_weekly_schedule_hour_utc", "9")),
        "minute_utc": int(_get_setting("owner_weekly_schedule_minute_utc", "0")),
        "last_sent_week": _get_setting("owner_weekly_schedule_last_sent_week", ""),
    }


def _set_schedule_config(enabled: bool, weekday: int, hour_utc: int, minute_utc: int) -> dict:
    _set_setting("owner_weekly_schedule_enabled", "1" if enabled else "0")
    _set_setting("owner_weekly_schedule_weekday", str(weekday))
    _set_setting("owner_weekly_schedule_hour_utc", str(hour_utc))
    _set_setting("owner_weekly_schedule_minute_utc", str(minute_utc))
    return _get_schedule_config()


def process_scheduled_owner_email(now_utc: datetime | None = None, force: bool = False, dry_run: bool = False) -> tuple[dict, int]:
    now_utc = (now_utc or datetime.utcnow()).replace(second=0, microsecond=0)
    cfg = _get_schedule_config()
    week_key = _week_key(now_utc)

    if not cfg["enabled"] and not force:
        return {"ok": True, "status": "disabled", "week": week_key, "schedule": cfg}, 200

    recipient = _get_setting("owner_report_email", "")
    if not recipient:
        return {"ok": False, "error": "owner_report_email_not_set"}, 400

    smtp_host = current_app.config.get("SMTP_HOST")
    email_from = current_app.config.get("EMAIL_FROM") or current_app.config.get("SMTP_USER")
    if not smtp_host or not email_from:
        return {"ok": False, "error": "smtp_not_configured"}, 400

    if not force:
        if now_utc.weekday() != cfg["weekday"] or now_utc.hour != cfg["hour_utc"] or now_utc.minute != cfg["minute_utc"]:
            return {"ok": True, "status": "not_due", "week": week_key, "schedule": cfg}, 200
        if cfg["last_sent_week"] == week_key:
            return {"ok": True, "status": "already_sent", "week": week_key, "schedule": cfg}, 200

    payload = _build_report_payload(week_key)
    body_text = render_owner_weekly_email_text(payload)

    if dry_run:
        return {"ok": True, "status": "would_send", "week": week_key, "sent_to": recipient, "schedule": cfg}, 200

    _send_email_message(week_key, recipient, body_text)
    _set_setting("owner_weekly_schedule_last_sent_week", week_key)
    return {"ok": True, "status": "sent", "week": week_key, "sent_to": recipient, "schedule": _get_schedule_config()}, 200


@bp.get("/reports/weekly")
@role_required("owner", "manager")
def owner_weekly_reports():
    return jsonify({"person": {"rows": build_person_rows({})}, "task": {"rows": build_task_rows({})}})


@bp.get("/settings/report-email")
@role_required("manager", "owner")
def get_report_email():
    value = _get_setting("owner_report_email", "")
    return jsonify({"owner_report_email": value})


@bp.post("/settings/report-email")
@role_required("manager")
def set_report_email():
    data = request.get_json(force=True)
    email = (data.get("owner_report_email") or "").strip()
    if not email or "@" not in email:
        return jsonify({"error": "valid_email_required"}), 400
    _set_setting("owner_report_email", email)
    return jsonify({"ok": True, "owner_report_email": email})


@bp.post("/reports/weekly/send-email")
@role_required("manager")
def send_owner_weekly_email():
    data = request.get_json(silent=True) or {}
    week_key = (data.get("week") or "current")

    recipient = _get_setting("owner_report_email", "")
    if not recipient:
        return jsonify({"error": "owner_report_email_not_set"}), 400

    payload = _build_report_payload(week_key)
    body_text = render_owner_weekly_email_text(payload)

    try:
        _send_email_message(week_key, recipient, body_text)
    except RuntimeError as exc:
        if str(exc) == "smtp_not_configured":
            return jsonify({"error": "smtp_not_configured"}), 400
        raise

    return jsonify({"ok": True, "sent_to": recipient, "week": week_key})


@bp.post("/reports/test-email")
@role_required("manager")
def send_owner_test_email():
    recipient = _get_setting("owner_report_email", "")
    if not recipient:
        return jsonify({"error": "owner_report_email_not_set"}), 400

    week_key = "test"
    payload = _build_report_payload(week_key)
    body_text = render_owner_weekly_email_text(payload)

    try:
        _send_email_message(week_key, recipient, body_text)
    except RuntimeError as exc:
        if str(exc) == "smtp_not_configured":
            return jsonify({"error": "smtp_not_configured"}), 400
        raise

    return jsonify({"ok": True, "sent_to": recipient, "week": week_key, "test": True})


@bp.get("/reports/weekly/schedule")
@role_required("manager", "owner")
def get_owner_weekly_schedule():
    return jsonify({"ok": True, "schedule": _get_schedule_config()})


@bp.post("/reports/weekly/schedule")
@role_required("manager")
def set_owner_weekly_schedule():
    data = request.get_json(silent=True) or {}
    enabled = _boolish(data.get("enabled", True))
    weekday = int(data.get("weekday", 1))
    hour_utc = int(data.get("hour_utc", 9))
    minute_utc = int(data.get("minute_utc", 0))

    if weekday < 0 or weekday > 6:
        return jsonify({"error": "weekday_out_of_range"}), 400
    if hour_utc < 0 or hour_utc > 23:
        return jsonify({"error": "hour_out_of_range"}), 400
    if minute_utc < 0 or minute_utc > 59:
        return jsonify({"error": "minute_out_of_range"}), 400

    cfg = _set_schedule_config(enabled, weekday, hour_utc, minute_utc)
    return jsonify({"ok": True, "schedule": cfg})


@bp.post("/reports/weekly/run-scheduled")
@role_required("manager")
def run_owner_weekly_schedule_once():
    data = request.get_json(silent=True) or {}
    force = _boolish(data.get("force", False))
    dry_run = _boolish(data.get("dry_run", False))
    payload, status = process_scheduled_owner_email(force=force, dry_run=dry_run)
    return jsonify(payload), status
