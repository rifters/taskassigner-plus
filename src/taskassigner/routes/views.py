from __future__ import annotations

from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_login import current_user

from ..models import AssignmentItem, AssignmentRun, TaskCompletion, TaskNote, TaskTemplate, User
from ..security import role_required

bp = Blueprint("views", __name__)


def _current_week_start() -> datetime:
    now = datetime.utcnow()
    return now - timedelta(days=now.weekday())


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
    return jsonify({"ok": True, "week": week_key, "action": "/api/weeks/%s/generate" % week_key})


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
    return jsonify({"week": week_key, "rows": rows, "edit_action": f"/api/weeks/{week_key}/draft/items/<id>"})


@bp.get("/manager/weeks/<week_key>/post")
@role_required("manager")
def manager_week_post(week_key: str):
    run = AssignmentRun.query.filter_by(week_key=week_key, status="draft").first()
    if not run:
        return jsonify({"error": "draft_not_found"}), 404
    return jsonify({"ok": True, "week": week_key, "post_action": f"/api/weeks/{week_key}/post"})


@bp.get("/manager/weeks/<week_key>/completions")
@role_required("manager", "shift_lead")
def manager_week_completions(week_key: str):
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
                "completed": c is not None,
                "completed_by": user_map.get(c.completed_by) if c else None,
                "completion_source": c.completion_source if c else None,
                "manager_reason": c.manager_reason if c else None,
            }
        )

    return jsonify(
        {
            "week": week_key,
            "rows": rows,
            "manager_complete_action": "/api/completions/<assignment_item_id>/manager-complete",
            "confirm_action": "/api/completions/<assignment_item_id>/confirm",
        }
    )


@bp.get("/crew/tasks")
@role_required("crew")
def crew_tasks():
    runs = AssignmentRun.query.filter_by(status="posted").all()
    run_ids = [r.id for r in runs]
    if not run_ids:
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

    return jsonify(
        {
            "rows": [
                {
                    "assignment_item_id": i.id,
                    "task_template_id": i.task_template_id,
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


@bp.get("/owner/reports")
@role_required("owner")
def owner_reports_page():
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
