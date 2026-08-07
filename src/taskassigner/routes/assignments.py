from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user

from ..audit import log_audit
from ..extensions import db
from ..models import AssignmentItem, AssignmentRun, JobCode, TaskTemplate, User
from ..security import role_required

bp = Blueprint("assignments", __name__, url_prefix="/api/weeks")


def _eligible_users_for_job_code(job_code_id: int) -> list[User]:
    return (
        User.query.join(User.job_codes)
        .filter(JobCode.id == job_code_id, User.active.is_(True))
        .order_by(User.id.asc())
        .all()
    )


@bp.post("/<week_key>/generate")
@role_required("manager")
def generate_week(week_key: str):
    run = AssignmentRun.query.filter_by(week_key=week_key, status="draft").first()
    if run:
        return jsonify({"error": "draft_exists", "run_id": run.id}), 409

    run = AssignmentRun(week_key=week_key, status="draft", generated_by=current_user.id)
    db.session.add(run)
    db.session.flush()

    templates = TaskTemplate.query.filter_by(active=True).order_by(TaskTemplate.id.asc()).all()
    per_job_assignment_index: dict[int, int] = {}

    for tpl in templates:
        users = _eligible_users_for_job_code(tpl.responsible_job_code_id)
        if not users:
            continue
        idx = per_job_assignment_index.get(tpl.responsible_job_code_id, 0)
        assignee = users[idx % len(users)]
        per_job_assignment_index[tpl.responsible_job_code_id] = idx + 1

        item = AssignmentItem(
            run_id=run.id,
            task_template_id=tpl.id,
            assignee_user_id=assignee.id,
            source="generated",
        )
        db.session.add(item)

    db.session.commit()
    log_audit(current_user.id, "generate", "assignment_run", str(run.id), {"week": week_key})
    return jsonify({"ok": True, "run_id": run.id})


@bp.get("/<week_key>/draft")
@role_required("manager", "shift_lead")
def view_draft(week_key: str):
    run = AssignmentRun.query.filter_by(week_key=week_key, status="draft").first()
    if not run:
        return jsonify({"error": "draft_not_found"}), 404

    items = (
        AssignmentItem.query.filter_by(run_id=run.id)
        .order_by(AssignmentItem.id.asc())
        .all()
    )

    counts: dict[int, int] = {}
    serialized = []
    for item in items:
        counts[item.assignee_user_id] = counts.get(item.assignee_user_id, 0) + 1
        serialized.append(
            {
                "id": item.id,
                "task_template_id": item.task_template_id,
                "assignee_user_id": item.assignee_user_id,
                "source": item.source,
                "edited_reason": item.edited_reason,
            }
        )

    spread_values = list(counts.values())
    fairness_spread = (max(spread_values) - min(spread_values)) if spread_values else 0
    return jsonify({"run_id": run.id, "items": serialized, "fairness_spread": fairness_spread})


@bp.patch("/<week_key>/draft/items/<int:item_id>")
@role_required("manager", "shift_lead")
def edit_draft_item(week_key: str, item_id: int):
    run = AssignmentRun.query.filter_by(week_key=week_key, status="draft").first()
    if not run:
        return jsonify({"error": "draft_not_found"}), 404

    item = AssignmentItem.query.filter_by(id=item_id, run_id=run.id).first_or_404()
    data = request.get_json(force=True)
    assignee_user_id = data.get("assignee_user_id")
    reason = (data.get("reason") or "").strip() or None

    if not assignee_user_id:
        return jsonify({"error": "assignee_required"}), 400

    user = User.query.filter_by(id=assignee_user_id, active=True).first()
    if not user:
        return jsonify({"error": "invalid_assignee"}), 400

    item.assignee_user_id = user.id
    item.source = "manual"
    item.edited_by = current_user.id
    item.edited_reason = reason
    db.session.commit()
    log_audit(
        current_user.id,
        "draft_edit",
        "assignment_item",
        str(item.id),
        {"assignee_user_id": assignee_user_id, "reason": reason},
    )
    return jsonify({"ok": True})


@bp.post("/<week_key>/post")
@role_required("manager")
def post_week(week_key: str):
    run = AssignmentRun.query.filter_by(week_key=week_key, status="draft").first()
    if not run:
        return jsonify({"error": "draft_not_found"}), 404

    run.status = "posted"
    run.posted_by = current_user.id
    run.posted_at = datetime.utcnow()
    db.session.commit()
    log_audit(current_user.id, "post", "assignment_run", str(run.id), {"week": week_key})
    return jsonify({"ok": True, "run_id": run.id})
