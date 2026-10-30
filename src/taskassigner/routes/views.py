from __future__ import annotations

from datetime import date, datetime, timedelta
import re

from flask import Blueprint, jsonify, redirect, render_template, request
from flask_login import current_user

from ..audit import log_audit
from ..extensions import db
from ..models import AssignmentItem, AssignmentRun, TaskCompletion, TaskNote, TaskTemplate, User
from ..security import role_required

bp = Blueprint("views", __name__)


def _wants_html() -> bool:
    return "text/html" in request.accept_mimetypes


def _current_week_start() -> datetime:
    now = datetime.utcnow()
    return now - timedelta(days=now.weekday())


def _current_company_week_key() -> str:
    today = date.today()
    start = today - timedelta(days=(today.weekday() - 3) % 7)
    iso_year, iso_week, _ = start.isocalendar()
    return f"{iso_year:04d}-W{iso_week:02d}"


def _resolve_current_week(week_key: str) -> str:
    return _current_company_week_key() if week_key == "current" else week_key


def _finalize_previous_week(current_week_key: str) -> None:
    previous = max(
        (run for run in AssignmentRun.query.filter_by(status="posted").all() if run.week_key < current_week_key),
        key=lambda run: run.week_key,
        default=None,
    )
    if not previous:
        return
    items = AssignmentItem.query.filter_by(run_id=previous.id).all()
    existing_ids = {
        row.assignment_item_id
        for row in TaskCompletion.query.filter(
            TaskCompletion.assignment_item_id.in_([item.id for item in items] or [-1])
        ).all()
    }
    for item in items:
        if item.id not in existing_ids:
            db.session.add(
                TaskCompletion(
                    assignment_item_id=item.id,
                    completed_by=current_user.id,
                    completion_status="not_completed",
                    completion_source="manager_week_close",
                    completed_at=datetime.utcnow(),
                )
            )
    db.session.commit()


@bp.get("/manager")
@role_required("manager")
def manager_home():
    return jsonify(
        {
            "ok": True,
            "workflow": {
                "generate": "/api/weeks/<week>/generate",
                "draft": "/api/weeks/<week>/draft",
                "post": "/api/weeks/<week>/post",
                "completion_review": "/manager/weeks/<week>/completions",
                "schedule": "/api/owner/reports/weekly/schedule",
            },
        }
    )


@bp.get("/manager/weeks/<week_key>/generate")
@role_required("manager")
def manager_week_generate(week_key: str):
    if _wants_html():
        return render_template("manager/week.html", week=week_key, title="Generate weekly assignments", action=f"/api/weeks/{week_key}/generate", rows=[])
    return jsonify({"ok": True, "week": week_key, "action": "/api/weeks/%s/generate" % week_key})


@bp.get("/manager/weeks/generate")
@role_required("manager")
def manager_week_generate_select():
    week_start = (request.args.get("week_start") or "").strip()
    legacy_week_key = (request.args.get("week_key") or "").strip().upper()
    if not week_start and not legacy_week_key:
        if _wants_html():
            return render_template("manager/week-select.html")
        return jsonify({"ok": True, "action": "/manager/weeks/generate?week_start=YYYY-MM-DD"})
    if week_start:
        try:
            start = date.fromisoformat(week_start)
        except ValueError:
            start = None
        if not start or start.weekday() != 3:
            return jsonify({"error": "invalid_week_start", "expected": "a Thursday in YYYY-MM-DD format"}), 400
        iso_year, iso_week, _ = start.isocalendar()
        week_key = f"{iso_year:04d}-W{iso_week:02d}"
    else:
        week_key = legacy_week_key
    if not re.fullmatch(r"\d{4}-W(?:0[1-9]|[1-4]\d|5[0-3])", week_key):
        return jsonify({"error": "invalid_week_key", "expected": "YYYY-W##"}), 400
    return redirect(f"/manager/weeks/{week_key}/generate")


@bp.get("/manager/weeks/<week_key>/draft")
@role_required("manager", "shift_lead")
def manager_week_draft(week_key: str):
    run = AssignmentRun.query.filter_by(week_key=week_key, status="draft").first()
    if not run:
        return jsonify({"error": "draft_not_found"}), 404

    items = AssignmentItem.query.filter_by(run_id=run.id).order_by(AssignmentItem.id.asc()).all()
    rows = [
        {
            "assignment_item_id": i.id,
            "task_template_id": i.task_template_id,
            "assignee_user_id": i.assignee_user_id,
            "source": i.source,
            "edited_reason": i.edited_reason,
        }
        for i in items
    ]
    if _wants_html():
        return render_template("manager/week.html", week=week_key, title="Review draft assignments", action=f"/api/weeks/{week_key}/draft/items/<id>", rows=rows)
    return jsonify({"week": week_key, "rows": rows, "edit_action": f"/api/weeks/{week_key}/draft/items/<id>"})


@bp.get("/manager/weeks/<week_key>/post")
@role_required("manager")
def manager_week_post(week_key: str):
    run = AssignmentRun.query.filter_by(week_key=week_key, status="draft").first()
    if not run:
        posted = AssignmentRun.query.filter_by(week_key=week_key, status="posted").first()
        if posted:
            if _wants_html():
                return redirect(f"/manager/weeks/{week_key}")
            return jsonify({"ok": True, "week": week_key, "status": "posted"})
        return jsonify({"error": "draft_not_found"}), 404
    if _wants_html():
        return render_template("manager/week.html", week=week_key, title="Post weekly assignments", action=f"/api/weeks/{week_key}/post", rows=[])
    return jsonify({"ok": True, "week": week_key, "post_action": f"/api/weeks/{week_key}/post"})


@bp.get("/manager/weeks/<week_key>/completions")
@role_required("manager", "shift_lead")
def manager_week_completions(week_key: str):
    if week_key == "current":
        week_key = _resolve_current_week(week_key)
        _finalize_previous_week(week_key)
    run = AssignmentRun.query.filter_by(week_key=week_key, status="posted").first()
    if not run:
        return jsonify({"error": "posted_week_not_found"}), 404

    items = AssignmentItem.query.filter_by(run_id=run.id).order_by(AssignmentItem.id.asc()).all()
    task_map = {t.id: t.title for t in TaskTemplate.query.all()}
    user_map = {u.id: u.name for u in User.query.all()}
    completions = {
        c.assignment_item_id: c
        for c in TaskCompletion.query.filter(TaskCompletion.assignment_item_id.in_([i.id for i in items])).all()
    }

    rows = []
    for i in items:
        c = completions.get(i.id)
        rows.append(
            {
                "assignment_item_id": i.id,
                "task": task_map.get(i.task_template_id, f"task-{i.task_template_id}"),
                "assignee": user_map.get(i.assignee_user_id, f"user-{i.assignee_user_id}"),
                "completed": bool(c and c.completion_status == "completed"),
                "completion_status": c.completion_status if c else None,
                "completed_by": user_map.get(c.completed_by) if c else None,
                "completion_source": c.completion_source if c else None,
                "manager_reason": c.manager_reason if c else None,
                "confirmed": bool(c and c.manager_confirmed_at),
            }
        )

    if _wants_html():
        return render_template(
            "manager/completions.html",
            week=week_key,
            rows=rows,
            has_unconfirmed_completions=any(row["completed"] and not row["confirmed"] for row in rows),
        )
    return jsonify(
        {
            "week": week_key,
            "rows": rows,
            "manager_complete_action": "/api/completions/<assignment_item_id>/manager-complete",
            "confirm_action": "/api/completions/<assignment_item_id>/confirm",
        }
    )


@bp.post("/manager/weeks/<week_key>/completions/confirm-all")
@role_required("manager")
def manager_confirm_all_completions(week_key: str):
    week_key = _resolve_current_week(week_key)
    run = AssignmentRun.query.filter_by(week_key=week_key, status="posted").first_or_404()
    item_ids = [item.id for item in AssignmentItem.query.filter_by(run_id=run.id).all()]
    completions = (
        TaskCompletion.query.filter(
            TaskCompletion.assignment_item_id.in_(item_ids or [-1]),
            TaskCompletion.completion_status == "completed",
            TaskCompletion.manager_confirmed_at.is_(None),
        )
        .all()
    )
    now = datetime.utcnow()
    for completion in completions:
        completion.manager_confirmed_by = current_user.id
        completion.manager_confirmed_at = now
    db.session.commit()
    log_audit(
        current_user.id,
        "confirm_all_completions",
        "assignment_run",
        str(run.id),
        {"week": week_key, "confirmed_count": len(completions)},
    )
    if _wants_html():
        return redirect(f"/manager/weeks/{week_key}/completions")
    return jsonify({"ok": True, "week": week_key, "confirmed_count": len(completions)})


@bp.get("/crew/tasks")
@role_required("crew")
def crew_tasks():
    runs = AssignmentRun.query.filter_by(status="posted").all()
    run_ids = [r.id for r in runs]
    if not run_ids:
        if _wants_html():
            return render_template("crew/tasks.html", groups={}, history_rows=[])
        return jsonify({"rows": [], "history_rows": []})

    items = (
        AssignmentItem.query.filter(
            AssignmentItem.run_id.in_(run_ids),
            AssignmentItem.assignee_user_id == current_user.id,
        )
        .order_by(AssignmentItem.id.asc())
        .all()
    )

    note_map = {
        n.assignment_item_id: n
        for n in TaskNote.query.filter(
            TaskNote.author_user_id == current_user.id,
            TaskNote.assignment_item_id.in_([i.id for i in items] or [-1]),
        ).all()
    }

    completion_map = {
        c.assignment_item_id: c
        for c in TaskCompletion.query.filter(TaskCompletion.assignment_item_id.in_([i.id for i in items] or [-1])).all()
    }

    history_since = _current_week_start() - timedelta(weeks=4)
    history_rows = []
    for i in items:
        c = completion_map.get(i.id)
        if c and c.completed_at >= history_since:
            history_rows.append(
                {
                    "assignment_item_id": i.id,
                    "completed_at": c.completed_at.isoformat(),
                    "completion_source": c.completion_source,
                    "completed_by": c.completed_by,
                }
            )

    if _wants_html():
        tasks = {task.id: task for task in TaskTemplate.query.all()}
        groups = {}
        for item in items:
            task = tasks.get(item.task_template_id)
            if not task:
                continue
            code = task.responsible_job_code.name if task.responsible_job_code else "Unassigned"
            groups.setdefault(code, []).append({
                "title": task.title,
                "master_list_number": task.master_list_number,
                "job_code": code,
                "assignment_item_id": item.id,
                "has_note": item.id in note_map,
                "completed": bool(completion_map.get(item.id) and completion_map[item.id].completion_status == "completed"),
            })
        return render_template("crew/tasks.html", groups=dict(sorted(groups.items())), history_rows=history_rows)
    task_numbers = {task.id: task.master_list_number for task in TaskTemplate.query.all()}
    return jsonify(
        {
            "rows": [
                {
                    "assignment_item_id": i.id,
                    "task_template_id": i.task_template_id,
                    "master_list_number": task_numbers.get(i.task_template_id),
                    "run_id": i.run_id,
                    "has_note": i.id in note_map,
                }
                for i in items
            ],
            "history_rows": history_rows,
            "note_action": "/api/completions/<assignment_item_id>/note",
            "complete_action": "/api/completions/<assignment_item_id>/mark-complete",
        }
    )


@bp.post("/crew/tasks/<int:assignment_item_id>/complete")
@role_required("crew")
def crew_complete_page(assignment_item_id: int):
    item = AssignmentItem.query.get_or_404(assignment_item_id)
    if item.assignee_user_id != current_user.id:
        return jsonify({"error": "forbidden"}), 403
    completion = TaskCompletion.query.filter_by(assignment_item_id=item.id).first()
    if not completion:
        completion = TaskCompletion(assignment_item_id=item.id, completed_by=current_user.id, completion_source="crew_self")
        db.session.add(completion)
    else:
        completion.completed_by = current_user.id
        completion.completed_at = datetime.utcnow()
        completion.completion_source = "crew_self"
    db.session.commit()
    log_audit(current_user.id, "complete", "assignment_item", str(item.id), {"source": "crew_self"})
    return redirect("/crew/tasks")


@bp.post("/crew/tasks/<int:assignment_item_id>/note")
@role_required("crew")
def crew_note_page(assignment_item_id: int):
    item = AssignmentItem.query.get_or_404(assignment_item_id)
    if item.assignee_user_id != current_user.id:
        return jsonify({"error": "forbidden"}), 403
    if TaskNote.query.filter_by(assignment_item_id=item.id, author_user_id=current_user.id).first():
        return redirect("/crew/tasks")
    note_text = (request.form.get("note") or "").strip()
    if note_text and len(note_text) <= 500:
        db.session.add(TaskNote(assignment_item_id=item.id, author_user_id=current_user.id, note_type="general", note_text=note_text))
        db.session.commit()
        log_audit(current_user.id, "task_note", "assignment_item", str(item.id), {"note_type": "general"})
    return redirect("/crew/tasks")


@bp.get("/owner/reports")
@role_required("owner")
def owner_reports_page():
    if _wants_html():
        from .reports import build_person_rows, build_task_rows

        return render_template("owner/reports.html", person_rows=build_person_rows({}), task_rows=build_task_rows({}))
    return jsonify({"ok": True, "weekly_report": "/api/owner/reports/weekly", "read_only": True})


@bp.get("/lead/board")
@role_required("shift_lead", "manager")
def lead_board():
    runs = AssignmentRun.query.filter_by(status="posted").order_by(AssignmentRun.id.desc()).all()
    if not runs:
        return jsonify({"rows": []})
    latest = runs[0]
    items = AssignmentItem.query.filter_by(run_id=latest.id).all()
    return jsonify(
        {
            "week": latest.week_key,
            "rows": [
                {
                    "assignment_item_id": i.id,
                    "task_template_id": i.task_template_id,
                    "assignee_user_id": i.assignee_user_id,
                }
                for i in items
            ],
        }
    )


@bp.post("/lead/reassign")
@role_required("shift_lead", "manager")
def lead_reassign_placeholder():
    return jsonify({"ok": True, "note": "Use /api/weeks/<week>/draft/items/<id> for reassignment"})
