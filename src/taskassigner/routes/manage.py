from __future__ import annotations

import csv
import io
from datetime import date, timedelta

from flask import Blueprint, Response, jsonify, redirect, render_template, request
from flask_login import current_user

from ..audit import log_audit
from ..extensions import db
from ..imports import (
    parse_csv,
    parse_job_codes_text,
    parse_numbered_task_csv,
    parse_numbered_task_text,
    parse_people_text,
    parse_task_templates_text,
)
from ..models import JobCode, TaskExclusion, TaskTemplate, User
from ..numbered_imports import apply_numbered_task_rows
from ..security import role_required
from .reports import build_summary

bp = Blueprint("manage", __name__, url_prefix="/manager")


def _ensure_manager() -> bool:
    return current_user.is_authenticated and current_user.role == "manager"


def _positive_number(value):
    if value in (None, ""):
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _import_content(data: dict, *keys: str) -> str:
    uploaded = request.files.get("file")
    if uploaded and uploaded.filename:
        return uploaded.read().decode("utf-8-sig")
    for key in keys:
        if data.get(key):
            return data[key]
    return ""


@bp.get("")
@role_required("manager")
def manager_home():
    if "text/html" in request.accept_mimetypes:
        return render_template(
            "manager/home.html",
            workflow={
                "generate": "/manager/weeks/generate",
                "draft": "/manager/weeks/current/draft",
                "post": "/manager/weeks/current/post",
                "completion_review": "/manager/weeks/current/completions",
                "reports": "/manager/reports",
                "schedule": "/api/owner/reports/weekly/schedule",
            },
        )
    return jsonify(
        {
            "ok": True,
            "message": "manager_home",
            "workflow": {
                "generate": "/manager/weeks/<week>/generate",
                "draft": "/manager/weeks/<week>/draft",
                "post": "/manager/weeks/<week>/post",
                "completion_review": "/manager/weeks/<week>/completions",
                "reports": "/manager/reports",
                "schedule": "/api/owner/reports/weekly/schedule",
            },
        }
    )


@bp.get("/reports")
@role_required("manager")
def manager_reports():
    start = request.args.get("start") or (date.today() - timedelta(days=90)).isoformat()
    end = request.args.get("end") or date.today().isoformat()
    report_args = request.args.copy()
    report_args.setdefault("start", start)
    report_args.setdefault("end", end)
    data = build_summary(report_args)
    return render_template(
        "manager/reports.html",
        report=data,
        start=start,
        end=end,
    )


@bp.get("/people")
@role_required("manager")
def list_people():
    rows = User.query.order_by(User.name.asc()).all()
    if "text/html" in request.accept_mimetypes:
        tasks = TaskTemplate.query.filter_by(active=True).order_by(TaskTemplate.title.asc()).all()
        exclusions = {}
        for exclusion in TaskExclusion.query.all():
            exclusions.setdefault(exclusion.user_id, set()).add(exclusion.task_template_id)
        return render_template("manager/people.html", people=rows, tasks=tasks, exclusions=exclusions)
    return jsonify([
        {"id": u.id, "name": u.name, "role": u.role, "active": u.active}
        for u in rows
    ])


@bp.post("/people")
@role_required("manager")
def create_person():
    data = request.get_json(silent=True) or request.form.to_dict()
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
    if "text/html" in request.accept_mimetypes:
        return redirect("/manager/people")
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


@bp.post("/people/<int:user_id>/edit")
@role_required("manager")
def edit_person_page(user_id: int):
    user = User.query.get_or_404(user_id)
    user.name = (request.form.get("name") or user.name).strip()
    user.active = request.form.get("active") == "true"
    db.session.commit()
    return redirect("/manager/people")


def _selected_task_ids() -> set[int]:
    return {int(value) for value in request.form.getlist("task_template_ids") if value.isdigit()}


@bp.post("/people/<int:user_id>/exclusions")
@role_required("manager")
def add_person_exclusions(user_id: int):
    user = User.query.get_or_404(user_id)
    task_ids = _selected_task_ids()
    existing = {row.task_template_id for row in TaskExclusion.query.filter_by(user_id=user.id).all()}
    for task_id in task_ids - existing:
        if TaskTemplate.query.get(task_id):
            db.session.add(TaskExclusion(user_id=user.id, task_template_id=task_id))
    db.session.commit()
    log_audit(current_user.id, "add_task_exclusions", "user", str(user.id), {"task_ids": sorted(task_ids)})
    return redirect("/manager/people")


@bp.post("/people/<int:user_id>/exclusions/remove")
@role_required("manager")
def remove_person_exclusions(user_id: int):
    user = User.query.get_or_404(user_id)
    task_ids = _selected_task_ids()
    if task_ids:
        TaskExclusion.query.filter(
            TaskExclusion.user_id == user.id,
            TaskExclusion.task_template_id.in_(task_ids),
        ).delete(synchronize_session=False)
        db.session.commit()
    log_audit(current_user.id, "remove_task_exclusions", "user", str(user.id), {"task_ids": sorted(task_ids)})
    return redirect("/manager/people")


@bp.post("/people/<int:user_id>/exclusions/clear")
@role_required("manager")
def clear_person_exclusions(user_id: int):
    user = User.query.get_or_404(user_id)
    TaskExclusion.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    db.session.commit()
    log_audit(current_user.id, "clear_task_exclusions", "user", str(user.id), {})
    return redirect("/manager/people")


@bp.get("/job-codes")
@role_required("manager")
def list_job_codes():
    rows = JobCode.query.order_by(JobCode.name.asc()).all()
    if "text/html" in request.accept_mimetypes:
        return render_template("manager/job_codes.html", job_codes=rows)
    return jsonify([{"id": r.id, "name": r.name, "active": r.active} for r in rows])


@bp.post("/job-codes")
@role_required("manager")
def create_job_code():
    data = request.get_json(silent=True) or request.form.to_dict()
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name_required"}), 400
    row = JobCode(name=name)
    db.session.add(row)
    db.session.commit()
    log_audit(current_user.id, "create", "job_code", str(row.id), {"name": name})
    if "text/html" in request.accept_mimetypes:
        return redirect("/manager/job-codes")
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


@bp.post("/job-codes/<int:job_code_id>/edit")
@role_required("manager")
def edit_job_code_page(job_code_id: int):
    row = JobCode.query.get_or_404(job_code_id)
    row.name = (request.form.get("name") or row.name).strip()
    row.active = request.form.get("active") == "true"
    db.session.commit()
    return redirect("/manager/job-codes")


@bp.get("/tasks")
@role_required("manager")
def list_tasks():
    rows = TaskTemplate.query.order_by(TaskTemplate.title.asc()).all()
    if "text/html" in request.accept_mimetypes:
        return render_template("manager/tasks.html", tasks=rows, job_codes=JobCode.query.order_by(JobCode.name.asc()).all())
    return jsonify([
        {
            "id": t.id,
            "title": t.title,
            "master_list_number": t.master_list_number,
            "job_code_id": t.responsible_job_code_id,
            "active": t.active,
        }
        for t in rows
    ])


@bp.post("/tasks")
@role_required("manager")
def create_task():
    data = request.get_json(silent=True) or request.form.to_dict()
    title = (data.get("title") or "").strip()
    job_code_id = data.get("responsible_job_code_id")
    if not title or not job_code_id:
        return jsonify({"error": "title_and_responsible_job_code_required"}), 400

    jc = JobCode.query.get(job_code_id)
    if not jc:
        return jsonify({"error": "invalid_job_code"}), 400

    row = TaskTemplate(
        title=title,
        master_list_number=_positive_number(data.get("master_list_number")),
        notes=data.get("notes"),
        responsible_job_code_id=jc.id,
        weight=data.get("weight"),
        est_minutes=data.get("est_minutes"),
    )
    db.session.add(row)
    db.session.commit()
    log_audit(current_user.id, "create", "task_template", str(row.id), {"title": title})
    if "text/html" in request.accept_mimetypes:
        return redirect("/manager/tasks")
    return jsonify({"id": row.id, "title": row.title, "master_list_number": row.master_list_number}), 201


@bp.patch("/tasks/<int:task_id>")
@role_required("manager")
def update_task(task_id: int):
    row = TaskTemplate.query.get_or_404(task_id)
    data = request.get_json(force=True)
    if "title" in data:
        row.title = (data["title"] or "").strip()
    if "master_list_number" in data:
        row.master_list_number = _positive_number(data.get("master_list_number"))
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
    return jsonify({"ok": True, "master_list_number": row.master_list_number})


@bp.delete("/tasks/<int:task_id>")
@role_required("manager")
def delete_task(task_id: int):
    row = TaskTemplate.query.get_or_404(task_id)
    db.session.delete(row)
    db.session.commit()
    log_audit(current_user.id, "delete", "task_template", str(task_id), {})
    return jsonify({"ok": True})


@bp.post("/tasks/<int:task_id>/edit")
@role_required("manager")
def edit_task_page(task_id: int):
    row = TaskTemplate.query.get_or_404(task_id)
    row.title = (request.form.get("title") or row.title).strip()
    row.master_list_number = _positive_number(request.form.get("master_list_number"))
    row.active = request.form.get("active") == "true"
    db.session.commit()
    return redirect("/manager/tasks")


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
    data = request.get_json(silent=True) or request.form.to_dict()
    mode = data.get("mode")
    if mode == "text":
        parsed = parse_people_text(data.get("text") or "")
        rows, errors = parsed.rows, parsed.errors
    elif mode == "csv":
        rows = parse_csv(data.get("csv") or data.get("text") or "")
        errors = []
    else:
        return jsonify({"error": "mode_required"}), 400

    result = _import_people(rows)
    log_audit(current_user.id, "import", "people", None, {"rows": len(result), "errors": len(errors)})
    if "text/html" in request.accept_mimetypes:
        return render_template("manager/people.html", people=User.query.order_by(User.name.asc()).all(), import_result={"created": sum(r["status"] == "created" for r in result), "errors": errors})
    return jsonify({"result": result, "errors": errors})


@bp.post("/imports/job-codes")
@role_required("manager")
def import_job_codes():
    data = request.get_json(silent=True) or request.form.to_dict()
    mode = data.get("mode")
    if mode == "text":
        parsed = parse_job_codes_text(data.get("text") or "")
        rows, errors = parsed.rows, parsed.errors
    elif mode == "csv":
        rows = parse_csv(data.get("csv") or data.get("text") or "")
        errors = []
    else:
        return jsonify({"error": "mode_required"}), 400

    result = _import_job_codes(rows)
    log_audit(current_user.id, "import", "job_codes", None, {"rows": len(result), "errors": len(errors)})
    if "text/html" in request.accept_mimetypes:
        return render_template("manager/job_codes.html", job_codes=JobCode.query.order_by(JobCode.name.asc()).all(), import_result={"created": sum(r["status"] == "created" for r in result), "errors": errors})
    return jsonify({"result": result, "errors": errors})


@bp.post("/imports/task-templates")
@role_required("manager")
def import_task_templates():
    data = request.get_json(silent=True) or request.form.to_dict()
    mode = data.get("mode")
    if mode == "numbered_txt":
        selected_job_code = (data.get("selected_job_code") or "").strip()
        if not selected_job_code:
            return jsonify({"error": "selected_job_code_required"}), 400
        parsed = parse_numbered_task_text(_import_content(data, "text"))
        result = apply_numbered_task_rows(
            parsed.rows,
            parsed.errors,
            selected_job_code=selected_job_code,
            source_format="txt",
        )
        log_audit(current_user.id, "import_numbered", "task_templates", None, {"format": "txt", "created": result["created"], "updated": result["updated"], "errors": len(result["errors"]), "reviews": len(result["reviews"])})
        if "text/html" in request.accept_mimetypes:
            return render_template("manager/tasks.html", tasks=TaskTemplate.query.order_by(TaskTemplate.title.asc()).all(), job_codes=JobCode.query.order_by(JobCode.name.asc()).all(), import_result=result)
        return jsonify(result)
    if mode == "numbered_csv":
        selected_job_code = (data.get("selected_job_code") or "").strip() or None
        parsed = parse_numbered_task_csv(_import_content(data, "csv", "text"))
        result = apply_numbered_task_rows(
            parsed.rows,
            parsed.errors,
            selected_job_code=selected_job_code,
            source_format="csv",
        )
        log_audit(current_user.id, "import_numbered", "task_templates", None, {"format": "csv", "created": result["created"], "updated": result["updated"], "errors": len(result["errors"]), "reviews": len(result["reviews"])})
        if "text/html" in request.accept_mimetypes:
            return render_template("manager/tasks.html", tasks=TaskTemplate.query.order_by(TaskTemplate.title.asc()).all(), job_codes=JobCode.query.order_by(JobCode.name.asc()).all(), import_result=result)
        return jsonify(result)
    if mode == "text":
        parsed = parse_task_templates_text(data.get("text") or "")
        rows, errors = parsed.rows, parsed.errors
    elif mode == "csv":
        rows = parse_csv(data.get("csv") or data.get("text") or "")
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
    if "text/html" in request.accept_mimetypes:
        return render_template("manager/tasks.html", tasks=TaskTemplate.query.order_by(TaskTemplate.title.asc()).all(), job_codes=JobCode.query.order_by(JobCode.name.asc()).all(), import_result={"created": sum(r["status"] == "created" for r in result), "errors": all_errors})
    return jsonify({"result": result, "errors": all_errors})


@bp.get("/exports/task-templates.csv")
@role_required("manager")
def export_task_templates_csv():
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["job_code", "number", "title", "notes", "active"])
    tasks = TaskTemplate.query.join(JobCode).order_by(JobCode.name.asc(), TaskTemplate.master_list_number.asc(), TaskTemplate.title.asc()).all()
    for task in tasks:
        writer.writerow([
            task.responsible_job_code.name,
            "" if task.master_list_number is None else task.master_list_number,
            task.title,
            task.notes or "",
            "true" if task.active else "false",
        ])
    log_audit(current_user.id, "export", "task_templates", None, {"format": "csv", "rows": len(tasks)})
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=task-templates.csv"},
    )


@bp.get("/exports/task-templates.txt")
@role_required("manager")
def export_task_templates_txt():
    job_code_name = (request.args.get("job_code") or "").strip()
    if not job_code_name:
        return jsonify({"error": "job_code_required"}), 400
    job_code = JobCode.query.filter_by(name=job_code_name).first_or_404()
    tasks = TaskTemplate.query.filter_by(
        responsible_job_code_id=job_code.id,
        active=True,
    ).filter(TaskTemplate.master_list_number.isnot(None)).order_by(TaskTemplate.master_list_number.asc(), TaskTemplate.title.asc()).all()
    content = "".join(f"{task.master_list_number}. {task.title}\n" for task in tasks)
    log_audit(current_user.id, "export", "task_templates", str(job_code.id), {"format": "txt", "rows": len(tasks)})
    return Response(
        content,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment; filename={job_code.name}-tasks.txt"},
    )


@bp.post("/imports/task-templates/confirm-legacy")
@role_required("manager")
def confirm_legacy_task_number():
    data = request.get_json(silent=True) or request.form.to_dict()
    task = TaskTemplate.query.get_or_404(data.get("task_id"))
    number = _positive_number(data.get("number"))
    if number is None:
        return jsonify({"error": "positive_number_required"}), 400
    if task.master_list_number is not None:
        return jsonify({"error": "task_already_numbered"}), 409
    collision = TaskTemplate.query.filter_by(
        responsible_job_code_id=task.responsible_job_code_id,
        master_list_number=number,
    ).first()
    if collision:
        return jsonify({"error": "number_already_in_use"}), 409
    task.master_list_number = number
    db.session.commit()
    log_audit(current_user.id, "confirm_legacy_number", "task_template", str(task.id), {"number": number})
    return jsonify({"ok": True, "task_id": task.id, "master_list_number": number})


@bp.post("/demo/reset")
@role_required("manager")
def reset_demo():
    from ..demo_seed import reset_demo_data

    try:
        summary = reset_demo_data()
    except RuntimeError:
        return jsonify({"error": "demo_reset_disabled"}), 403
    if "text/html" in request.accept_mimetypes:
        return render_template("manager/home.html", workflow={"generate": "/manager/weeks/current/generate", "draft": "/manager/weeks/current/draft", "post": "/manager/weeks/current/post", "completion_review": "/manager/weeks/current/completions", "schedule": "/api/owner/reports/weekly/schedule"}, demo_summary=summary)
    return jsonify({"ok": True, "summary": summary})
