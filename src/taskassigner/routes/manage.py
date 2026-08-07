from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_login import current_user

from ..audit import log_audit
from ..extensions import db
from ..imports import parse_csv, parse_job_codes_text, parse_people_text, parse_task_templates_text
from ..models import JobCode, TaskTemplate, User
from ..security import role_required

bp = Blueprint("manage", __name__, url_prefix="/manager")


def _ensure_manager() -> bool:
    return current_user.is_authenticated and current_user.role == "manager"


@bp.get("")
@role_required("manager")
def manager_home():
    return jsonify(
        {
            "ok": True,
            "message": "manager_home",
            "workflow": {
                "generate": "/manager/weeks/<week>/generate",
                "draft": "/manager/weeks/<week>/draft",
                "post": "/manager/weeks/<week>/post",
                "completion_review": "/manager/weeks/<week>/completions",
                "schedule": "/api/owner/reports/weekly/schedule",
            },
        }
    )


@bp.get("/people")
@role_required("manager")
def list_people():
    rows = User.query.order_by(User.name.asc()).all()
    return jsonify([
        {"id": u.id, "name": u.name, "role": u.role, "active": u.active}
        for u in rows
    ])


@bp.post("/people")
@role_required("manager")
def create_person():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    role = (data.get("role") or "").strip()
    if not name or role not in {"crew", "shift_lead", "manager", "owner"}:
        return jsonify({"error": "invalid_fields"}), 400

    user = User(name=name, role=role, email=data.get("email"))
    if role == "crew":
        pin = str(data.get("pin") or "").strip()
        if not pin:
            return jsonify({"error": "pin_required"}), 400
        user.set_pin(pin)
    else:
        pw = str(data.get("password") or "").strip()
        if not pw:
            return jsonify({"error": "password_required"}), 400
        user.set_password(pw)

    db.session.add(user)
    db.session.commit()
    log_audit(current_user.id, "create", "user", str(user.id), {"name": name, "role": role})
    return jsonify({"id": user.id, "name": user.name, "role": user.role}), 201


@bp.patch("/people/<int:user_id>")
@role_required("manager")
def update_person(user_id: int):
    user = User.query.get_or_404(user_id)
    data = request.get_json(force=True)
    if "name" in data:
        user.name = (data["name"] or "").strip()
    if "role" in data and data["role"] in {"crew", "shift_lead", "manager", "owner"}:
        user.role = data["role"]
    if "active" in data:
        user.active = bool(data["active"])
    db.session.commit()
    log_audit(current_user.id, "update", "user", str(user.id), data)
    return jsonify({"ok": True})


@bp.delete("/people/<int:user_id>")
@role_required("manager")
def delete_person(user_id: int):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    log_audit(current_user.id, "delete", "user", str(user_id), {})
    return jsonify({"ok": True})


@bp.get("/job-codes")
@role_required("manager")
def list_job_codes():
    rows = JobCode.query.order_by(JobCode.name.asc()).all()
    return jsonify([{"id": r.id, "name": r.name, "active": r.active} for r in rows])


@bp.post("/job-codes")
@role_required("manager")
def create_job_code():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name_required"}), 400
    row = JobCode(name=name)
    db.session.add(row)
    db.session.commit()
    log_audit(current_user.id, "create", "job_code", str(row.id), {"name": name})
    return jsonify({"id": row.id, "name": row.name}), 201


@bp.patch("/job-codes/<int:job_code_id>")
@role_required("manager")
def update_job_code(job_code_id: int):
    row = JobCode.query.get_or_404(job_code_id)
    data = request.get_json(force=True)
    if "name" in data:
        row.name = (data["name"] or "").strip()
    if "active" in data:
        row.active = bool(data["active"])
    db.session.commit()
    log_audit(current_user.id, "update", "job_code", str(row.id), data)
    return jsonify({"ok": True})


@bp.delete("/job-codes/<int:job_code_id>")
@role_required("manager")
def delete_job_code(job_code_id: int):
    row = JobCode.query.get_or_404(job_code_id)
    db.session.delete(row)
    db.session.commit()
    log_audit(current_user.id, "delete", "job_code", str(job_code_id), {})
    return jsonify({"ok": True})


@bp.get("/tasks")
@role_required("manager")
def list_tasks():
    rows = TaskTemplate.query.order_by(TaskTemplate.title.asc()).all()
    return jsonify([
        {
            "id": t.id,
            "title": t.title,
            "job_code_id": t.responsible_job_code_id,
            "active": t.active,
        }
        for t in rows
    ])


@bp.post("/tasks")
@role_required("manager")
def create_task():
    data = request.get_json(force=True)
    title = (data.get("title") or "").strip()
    job_code_id = data.get("responsible_job_code_id")
    if not title or not job_code_id:
        return jsonify({"error": "title_and_responsible_job_code_required"}), 400

    jc = JobCode.query.get(job_code_id)
    if not jc:
        return jsonify({"error": "invalid_job_code"}), 400

    row = TaskTemplate(
        title=title,
        notes=data.get("notes"),
        responsible_job_code_id=jc.id,
        weight=data.get("weight"),
        est_minutes=data.get("est_minutes"),
    )
    db.session.add(row)
    db.session.commit()
    log_audit(current_user.id, "create", "task_template", str(row.id), {"title": title})
    return jsonify({"id": row.id, "title": row.title}), 201


@bp.patch("/tasks/<int:task_id>")
@role_required("manager")
def update_task(task_id: int):
    row = TaskTemplate.query.get_or_404(task_id)
    data = request.get_json(force=True)
    if "title" in data:
        row.title = (data["title"] or "").strip()
    if "notes" in data:
        row.notes = data["notes"]
    if "active" in data:
        row.active = bool(data["active"])
    if "responsible_job_code_id" in data:
        jc = JobCode.query.get(data["responsible_job_code_id"])
        if not jc:
            return jsonify({"error": "invalid_job_code"}), 400
        row.responsible_job_code_id = jc.id
    db.session.commit()
    log_audit(current_user.id, "update", "task_template", str(row.id), data)
    return jsonify({"ok": True})


@bp.delete("/tasks/<int:task_id>")
@role_required("manager")
def delete_task(task_id: int):
    row = TaskTemplate.query.get_or_404(task_id)
    db.session.delete(row)
    db.session.commit()
    log_audit(current_user.id, "delete", "task_template", str(task_id), {})
    return jsonify({"ok": True})


def _import_people(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows:
        name = (row.get("name") or "").strip()
        if not name:
            continue
        role = (row.get("role") or "crew").strip() or "crew"
        existing = User.query.filter_by(name=name).first()
        if existing:
            out.append({"name": name, "status": "exists"})
            continue
        user = User(name=name, role=role)
        if role == "crew":
            user.set_pin(str(row.get("pin") or "0000"))
        else:
            user.set_password(str(row.get("password") or "changeme"))
        db.session.add(user)
        db.session.flush()

        job_code_name = (row.get("job_code") or "").strip()
        if job_code_name:
            jc = JobCode.query.filter_by(name=job_code_name).first()
            if jc:
                user.job_codes.append(jc)
        out.append({"name": name, "status": "created", "id": user.id})
    db.session.commit()
    return out


def _import_job_codes(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows:
        name = (row.get("name") or "").strip()
        if not name:
            continue
        existing = JobCode.query.filter_by(name=name).first()
        if existing:
            out.append({"name": name, "status": "exists"})
            continue
        jc = JobCode(name=name)
        db.session.add(jc)
        db.session.flush()
        out.append({"name": name, "status": "created", "id": jc.id})
    db.session.commit()
    return out


def _import_tasks(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    out = []
    errors = []
    for idx, row in enumerate(rows, start=1):
        title = (row.get("title") or "").strip()
        if not title:
            errors.append({"line": idx, "error": "title_required"})
            continue
        job_code_name = (row.get("job_code") or "").strip()
        job_code_id = row.get("responsible_job_code_id")
        jc = None
        if job_code_id:
            jc = JobCode.query.get(job_code_id)
        elif job_code_name:
            jc = JobCode.query.filter_by(name=job_code_name).first()
        if not jc:
            errors.append({"line": idx, "error": "responsible_job_code_required"})
            continue

        existing = TaskTemplate.query.filter_by(title=title, responsible_job_code_id=jc.id).first()
        if existing:
            out.append({"title": title, "status": "exists"})
            continue
        t = TaskTemplate(title=title, notes=row.get("notes"), responsible_job_code_id=jc.id)
        db.session.add(t)
        db.session.flush()
        out.append({"title": title, "status": "created", "id": t.id})
    db.session.commit()
    return out, errors


@bp.post("/imports/people")
@role_required("manager")
def import_people():
    data = request.get_json(force=True)
    mode = data.get("mode")
    if mode == "text":
        parsed = parse_people_text(data.get("text") or "")
        rows, errors = parsed.rows, parsed.errors
    elif mode == "csv":
        rows = parse_csv(data.get("csv") or "")
        errors = []
    else:
        return jsonify({"error": "mode_required"}), 400

    result = _import_people(rows)
    log_audit(current_user.id, "import", "people", None, {"rows": len(result), "errors": len(errors)})
    return jsonify({"result": result, "errors": errors})


@bp.post("/imports/job-codes")
@role_required("manager")
def import_job_codes():
    data = request.get_json(force=True)
    mode = data.get("mode")
    if mode == "text":
        parsed = parse_job_codes_text(data.get("text") or "")
        rows, errors = parsed.rows, parsed.errors
    elif mode == "csv":
        rows = parse_csv(data.get("csv") or "")
        errors = []
    else:
        return jsonify({"error": "mode_required"}), 400

    result = _import_job_codes(rows)
    log_audit(current_user.id, "import", "job_codes", None, {"rows": len(result), "errors": len(errors)})
    return jsonify({"result": result, "errors": errors})


@bp.post("/imports/task-templates")
@role_required("manager")
def import_task_templates():
    data = request.get_json(force=True)
    mode = data.get("mode")
    if mode == "text":
        parsed = parse_task_templates_text(data.get("text") or "")
        rows, errors = parsed.rows, parsed.errors
    elif mode == "csv":
        rows = parse_csv(data.get("csv") or "")
        errors = []
    else:
        return jsonify({"error": "mode_required"}), 400

    result, import_errors = _import_tasks(rows)
    all_errors = [*errors, *import_errors]
    log_audit(
        current_user.id,
        "import",
        "task_templates",
        None,
        {"rows": len(result), "errors": len(all_errors)},
    )
    return jsonify({"result": result, "errors": all_errors})
