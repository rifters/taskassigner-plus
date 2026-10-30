from __future__ import annotations

from datetime import datetime
import random
import re

from flask import Blueprint, jsonify, request
from flask_login import current_user

from ..audit import log_audit
from ..extensions import db
from ..eligibility import eligible_users_for_task, is_eligible
from ..models import AssignmentItem, AssignmentRun, JobCode, TaskTemplate, User
from ..security import role_required

bp = Blueprint("assignments", __name__, url_prefix="/api/weeks")


def _eligible_users_for_job_code(job_code_id: int) -> list[User]:
    task = TaskTemplate.query.filter_by(responsible_job_code_id=job_code_id, active=True).first()
    return eligible_users_for_task(task) if task else []


def _previous_posted_pairs(week_key: str) -> set[tuple[int, int]]:
    posted = AssignmentRun.query.filter_by(status="posted").all()
    if not posted:
        return set()
    if re.fullmatch(r"\d{4}-W\d{2}", week_key):
        candidates = [run for run in posted if run.week_key < week_key]
        previous = max(candidates, key=lambda run: run.week_key, default=None)
    else:
        previous = max(posted, key=lambda run: run.id)
    if not previous:
        return set()
    return {
        (item.task_template_id, item.assignee_user_id)
        for item in AssignmentItem.query.filter_by(run_id=previous.id).all()
    }


def _generate_items(run: AssignmentRun, week_key: str) -> None:
    templates = TaskTemplate.query.filter_by(active=True).order_by(TaskTemplate.id.asc()).all()
    random.shuffle(templates)
    previous_pairs = _previous_posted_pairs(week_key)
    per_job_assignment_index: dict[int, int] = {}
    pool_orders: dict[int, list[User]] = {}

    for template in templates:
        pool_id = template.responsible_job_code_id
        if pool_id not in pool_orders:
            pool_orders[pool_id] = (
                User.query.join(User.job_codes)
                .filter(
                    JobCode.id == pool_id,
                    User.active.is_(True),
                    User.role == "crew",
                )
                .order_by(User.id.asc())
                .all()
            )
            random.shuffle(pool_orders[pool_id])
        people = [person for person in pool_orders[pool_id] if is_eligible(person, template)]
        if not people:
            continue
        index = per_job_assignment_index.get(pool_id, 0)
        ordered = people[index % len(people):] + people[: index % len(people)]
        non_repeat = [person for person in ordered if (template.id, person.id) not in previous_pairs]
        assignee = (non_repeat or ordered)[0]
        per_job_assignment_index[pool_id] = index + 1
        db.session.add(
            AssignmentItem(
                run_id=run.id,
                task_template_id=template.id,
                assignee_user_id=assignee.id,
                source="generated",
            )
        )


@bp.post("/<week_key>/generate")
@role_required("manager")
def generate_week(week_key: str):
    run = AssignmentRun.query.filter_by(week_key=week_key).order_by(AssignmentRun.id.desc()).first()
    if run:
        return jsonify({"error": "week_already_generated", "status": run.status, "run_id": run.id}), 409

    run = AssignmentRun(week_key=week_key, status="draft", generated_by=current_user.id)
    db.session.add(run)
    db.session.flush()

    _generate_items(run, week_key)

    db.session.commit()
    log_audit(current_user.id, "generate", "assignment_run", str(run.id), {"week": week_key})
    return jsonify({"ok": True, "run_id": run.id})


@bp.post("/<week_key>/regenerate")
@role_required("manager")
def regenerate_week(week_key: str):
    run = AssignmentRun.query.filter_by(week_key=week_key, status="draft").first()
    if not run:
        return jsonify({"error": "draft_not_found"}), 404
    data = request.get_json(silent=True) or {}
    if data.get("confirm") is not True:
        return jsonify({"error": "confirmation_required"}), 400
    AssignmentItem.query.filter_by(run_id=run.id).delete(synchronize_session=False)
    _generate_items(run, week_key)
    db.session.commit()
    log_audit(current_user.id, "regenerate", "assignment_run", str(run.id), {"week": week_key})
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
                "master_list_number": TaskTemplate.query.get(item.task_template_id).master_list_number,
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
    run = AssignmentRun.query.filter(
        AssignmentRun.week_key == week_key,
        AssignmentRun.status.in_(["draft", "posted"]),
    ).order_by(AssignmentRun.id.desc()).first()
    if not run:
        return jsonify({"error": "draft_not_found"}), 404

    item = AssignmentItem.query.filter_by(id=item_id, run_id=run.id).first_or_404()
    data = request.get_json(force=True)
    assignee_user_id = data.get("assignee_user_id")
    reason = (data.get("reason") or "").strip() or None

    if not assignee_user_id:
        return jsonify({"error": "assignee_required"}), 400

    user = User.query.filter_by(id=assignee_user_id, active=True).first()
    task = TaskTemplate.query.get(item.task_template_id)
    if not user:
        return jsonify({"error": "invalid_assignee"}), 400
    if not task or not is_eligible(user, task):
        return jsonify({"error": "ineligible_assignee"}), 400

    item.assignee_user_id = user.id
    item.source = "manual"
    item.edited_by = current_user.id
    item.edited_reason = reason
    db.session.commit()
    log_audit(
        current_user.id,
        "posted_edit" if run.status == "posted" else "draft_edit",
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
