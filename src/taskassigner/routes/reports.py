from __future__ import annotations

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from ..models import AssignmentItem, AssignmentRun, TaskCompletion, TaskTemplate, User
from ..security import role_required

bp = Blueprint("reports", __name__, url_prefix="/api/reports")


def _apply_common_filters(q, args):
    week = args.get("week")
    if week:
        q = q.filter(AssignmentRun.week_key == week)

    job_code = args.get("job_code")
    if job_code:
        q = q.filter(TaskTemplate.responsible_job_code_id == int(job_code))

    person = args.get("person")
    if person:
        q = q.filter(AssignmentItem.assignee_user_id == int(person))

    task = args.get("task")
    if task:
        q = q.filter(AssignmentItem.task_template_id == int(task))

    return q


def build_person_rows(args):
    base_q = (
        AssignmentItem.query.join(AssignmentRun, AssignmentRun.id == AssignmentItem.run_id)
        .join(TaskTemplate, TaskTemplate.id == AssignmentItem.task_template_id)
    )
    q = _apply_common_filters(base_q, args)

    assigned = (
        q.with_entities(AssignmentItem.assignee_user_id, func.count(AssignmentItem.id))
        .group_by(AssignmentItem.assignee_user_id)
        .all()
    )
    assigned_map = {uid: c for uid, c in assigned}

    completion_q = (
        TaskCompletion.query.join(
            AssignmentItem, AssignmentItem.id == TaskCompletion.assignment_item_id
        )
        .join(AssignmentRun, AssignmentRun.id == AssignmentItem.run_id)
        .join(TaskTemplate, TaskTemplate.id == AssignmentItem.task_template_id)
    )
    completion_q = _apply_common_filters(completion_q, args)

    completed = (
        completion_q.with_entities(AssignmentItem.assignee_user_id, func.count(TaskCompletion.id))
        .group_by(AssignmentItem.assignee_user_id)
        .all()
    )
    completed_map = {uid: c for uid, c in completed}

    user_ids = sorted(set(list(assigned_map.keys()) + list(completed_map.keys())))
    users = {u.id: u for u in User.query.filter(User.id.in_(user_ids)).all()} if user_ids else {}

    rows = []
    for uid in user_ids:
        a = assigned_map.get(uid, 0)
        c = completed_map.get(uid, 0)
        pct = round((c / a) * 100, 2) if a else 0.0
        rows.append(
            {
                "user_id": uid,
                "name": users.get(uid).name if users.get(uid) else f"user-{uid}",
                "assigned": a,
                "completed": c,
                "completion_pct": pct,
            }
        )
    return rows


def build_task_rows(args):
    q = (
        AssignmentItem.query.join(AssignmentRun, AssignmentRun.id == AssignmentItem.run_id)
        .join(TaskTemplate, TaskTemplate.id == AssignmentItem.task_template_id)
    )
    q = _apply_common_filters(q, args)

    task_assignments = (
        q.with_entities(
            AssignmentItem.task_template_id,
            AssignmentItem.assignee_user_id,
            func.count(AssignmentItem.id),
        )
        .group_by(AssignmentItem.task_template_id, AssignmentItem.assignee_user_id)
        .all()
    )

    completion_q = (
        TaskCompletion.query.join(
            AssignmentItem, AssignmentItem.id == TaskCompletion.assignment_item_id
        )
        .join(TaskTemplate, TaskTemplate.id == AssignmentItem.task_template_id)
        .join(AssignmentRun, AssignmentRun.id == AssignmentItem.run_id)
    )
    completion_q = _apply_common_filters(completion_q, args)

    task_completions = (
        completion_q.with_entities(
            AssignmentItem.task_template_id,
            AssignmentItem.assignee_user_id,
            func.count(TaskCompletion.id),
        )
        .group_by(AssignmentItem.task_template_id, AssignmentItem.assignee_user_id)
        .all()
    )

    completed_map = {(tid, uid): cnt for tid, uid, cnt in task_completions}
    users = {u.id: u.name for u in User.query.all()}
    tasks = {t.id: t.title for t in TaskTemplate.query.all()}

    rows = []
    per_task_pcts: dict[int, list[float]] = {}
    for tid, uid, assigned_cnt in task_assignments:
        completed_cnt = completed_map.get((tid, uid), 0)
        pct = round((completed_cnt / assigned_cnt) * 100, 2) if assigned_cnt else 0.0
        per_task_pcts.setdefault(tid, []).append(pct)
        rows.append(
            {
                "task_template_id": tid,
                "task_title": tasks.get(tid, f"task-{tid}"),
                "assignee_user_id": uid,
                "assignee_name": users.get(uid, f"user-{uid}"),
                "assigned": assigned_cnt,
                "completed": completed_cnt,
                "completion_pct": pct,
            }
        )

    # Consistency trend proxy for v1: spread between highest and lowest assignee completion % per task.
    # Lower spread means more consistent completion.
    consistency_by_task = {}
    for tid, pcts in per_task_pcts.items():
        if not pcts:
            consistency_by_task[tid] = {"consistency_spread_pct": 0.0}
        else:
            consistency_by_task[tid] = {
                "consistency_spread_pct": round(max(pcts) - min(pcts), 2),
                "avg_completion_pct": round(sum(pcts) / len(pcts), 2),
            }

    for row in rows:
        row.update(consistency_by_task.get(row["task_template_id"], {"consistency_spread_pct": 0.0}))

    return rows


@bp.get("/person")
@role_required("manager", "shift_lead", "owner")
def person_report():
    return jsonify({"rows": build_person_rows(request.args)})


@bp.get("/task")
@role_required("manager", "shift_lead", "owner")
def task_report():
    return jsonify({"rows": build_task_rows(request.args)})
