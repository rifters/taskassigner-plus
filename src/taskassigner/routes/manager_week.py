from __future__ import annotations

from datetime import date, datetime, timedelta
import re

from flask import Blueprint, jsonify, redirect, render_template, request
from flask_login import current_user

from ..audit import log_audit
from ..extensions import db
from ..eligibility import eligible_users_for_task, is_eligible
from ..models import AssignmentItem, AssignmentRun, TaskTemplate, User
from ..security import role_required
from .assignments import _generate_items

bp = Blueprint("manager_week", __name__, url_prefix="/manager/weeks")


def _load_week(week_key: str):
    return AssignmentRun.query.filter_by(week_key=week_key, status="draft").first()


def _find_week(week_key: str):
    return AssignmentRun.query.filter_by(week_key=week_key).order_by(AssignmentRun.id.desc()).first()


def _week_label(week_key: str) -> str:
    if week_key == "current":
        return "Current week"
    match = re.fullmatch(r"(\d{4})-W(\d{2})", week_key)
    if not match:
        return week_key
    start = date.fromisocalendar(int(match.group(1)), int(match.group(2)), 4)
    end = start + timedelta(days=6)
    return f"{start:%a %b} {start.day}, {start.year} – {end:%a %b} {end.day}, {end.year}"


def _wants_html() -> bool:
    return "text/html" in request.accept_mimetypes


@bp.get("/<week_key>")
@role_required("manager")
def week_page(week_key: str):
    run = _find_week(week_key)
    generated_weeks = [
        {"key": row.week_key, "label": _week_label(row.week_key), "status": row.status}
        for row in AssignmentRun.query.order_by(AssignmentRun.generated_at.desc(), AssignmentRun.id.desc()).all()
    ]
    items = [] if not run else AssignmentItem.query.filter_by(run_id=run.id).order_by(AssignmentItem.id).all()
    templates = {row.id: row for row in TaskTemplate.query.all()}
    users = {row.id: row for row in User.query.all()}
    rows = []
    for item in items:
        task = templates.get(item.task_template_id)
        if not task:
            continue
        rows.append({"item": item, "task": task, "assignee": users.get(item.assignee_user_id), "eligible_people": eligible_users_for_task(task)})
    groups = {}
    for row in rows:
        groups.setdefault(row["task"].responsible_job_code.name, []).append(row)
    unassigned_tasks = [task for task in TaskTemplate.query.filter_by(active=True).all() if not eligible_users_for_task(task)]
    return render_template(
        "manager/weekly.html",
        week_key=week_key,
        week_label=_week_label(week_key),
        run=run,
        items=rows,
        people=User.query.filter_by(active=True, role="crew").order_by(User.name).all(),
        groups=dict(sorted(groups.items())),
        unassigned_tasks=unassigned_tasks,
        generated=bool(run),
        generated_weeks=generated_weeks,
    )


@bp.get("/<week_key>/draft")
@role_required("manager")
def draft_page(week_key: str):
    run = _load_week(week_key)
    if not run and not _wants_html():
        return jsonify({"error": "draft_not_found"}), 404
    if _wants_html():
        return week_page(week_key)
    items = AssignmentItem.query.filter_by(run_id=run.id).order_by(AssignmentItem.id.asc()).all()
    return jsonify({"week": week_key, "rows": [{"assignment_item_id": item.id, "task_template_id": item.task_template_id, "assignee_user_id": item.assignee_user_id, "source": item.source, "edited_reason": item.edited_reason} for item in items], "edit_action": f"/api/weeks/{week_key}/draft/items/<id>"})


@bp.route("/<week_key>/generate", methods=["GET", "POST"])
@role_required("manager")
def generate_week_page(week_key: str):
    if request.method == "GET":
        if _wants_html():
            return week_page(week_key)
        return jsonify({"ok": True, "week": week_key, "action": f"/api/weeks/{week_key}/generate"})
    if _load_week(week_key):
        return redirect(f"/manager/weeks/{week_key}")
    posted = AssignmentRun.query.filter_by(week_key=week_key, status="posted").first()
    if posted:
        return redirect(f"/manager/weeks/{week_key}")
    run = AssignmentRun(week_key=week_key, status="draft", generated_by=current_user.id)
    db.session.add(run)
    db.session.flush()
    _generate_items(run, week_key)
    db.session.commit()
    log_audit(current_user.id, "generate", "assignment_run", str(run.id), {"week": week_key})
    return redirect(f"/manager/weeks/{week_key}")


@bp.post("/<week_key>/regenerate")
@role_required("manager")
def regenerate_week_page(week_key: str):
    run = _load_week(week_key)
    if not run or request.form.get("confirm") != "true":
        return redirect(f"/manager/weeks/{week_key}")
    AssignmentItem.query.filter_by(run_id=run.id).delete(synchronize_session=False)
    _generate_items(run, week_key)
    db.session.commit()
    log_audit(current_user.id, "regenerate", "assignment_run", str(run.id), {"week": week_key})
    return redirect(f"/manager/weeks/{week_key}")


@bp.post("/<week_key>/edit/<int:item_id>")
@role_required("manager")
def edit_week_item(week_key: str, item_id: int):
    run = _find_week(week_key)
    item = AssignmentItem.query.filter_by(id=item_id, run_id=run.id if run else -1).first_or_404()
    assignee = User.query.filter_by(id=request.form.get("assignee_user_id"), active=True, role="crew").first_or_404()
    task = TaskTemplate.query.get_or_404(item.task_template_id)
    if not is_eligible(assignee, task):
        return "Selected person is not eligible for this task.", 400
    item.assignee_user_id = assignee.id
    item.source = "manual"
    item.edited_by = current_user.id
    item.edited_reason = (request.form.get("reason") or "").strip() or None
    db.session.commit()
    log_audit(current_user.id, "assignment_edit", "assignment_item", str(item.id), {"assignee_user_id": assignee.id, "reason": item.edited_reason, "week": week_key})
    return redirect(f"/manager/weeks/{week_key}")


@bp.post("/<week_key>/post")
@role_required("manager")
def post_week_page(week_key: str):
    run = _load_week(week_key)
    if run:
        run.status = "posted"
        run.posted_by = current_user.id
        run.posted_at = datetime.utcnow()
        db.session.commit()
        log_audit(current_user.id, "post", "assignment_run", str(run.id), {"week": week_key})
    if request.form.get("print") == "true":
        return redirect(f"/manager/weeks/{week_key}/print")
    return redirect(f"/manager/weeks/{week_key}")


@bp.get("/<week_key>/print")
@role_required("manager")
def print_week_page(week_key: str):
    run = AssignmentRun.query.filter_by(week_key=week_key, status="posted").first_or_404()
    items = AssignmentItem.query.filter_by(run_id=run.id).all()
    tasks = {task.id: task for task in TaskTemplate.query.all()}
    users = {user.id: user for user in User.query.all()}
    groups = {}
    for item in items:
        task = tasks.get(item.task_template_id)
        person = users.get(item.assignee_user_id)
        if not task or not person:
            continue
        job_code = task.responsible_job_code.name if task.responsible_job_code else "Unassigned"
        groups.setdefault(job_code, {}).setdefault(person.name, {"person": person, "tasks": []})["tasks"].append(task)
    for people in groups.values():
        for payload in people.values():
            payload["tasks"].sort(key=lambda task: (task.master_list_number is None, task.master_list_number or 0, task.title.lower()))
    return render_template("manager/weekly_print.html", week_key=week_key, run=run, groups=dict(sorted((code, dict(sorted(people.items()))) for code, people in groups.items())))
