from __future__ import annotations

from datetime import date, timedelta
import re

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from ..models import AssignmentItem, AssignmentRun, TaskCompletion, TaskTemplate, User
from ..security import role_required

bp = Blueprint("reports", __name__, url_prefix="/api/reports")


def _report_run_ids(args):
    start_text = args.get("start") or args.get("from")
    end_text = args.get("end") or args.get("to")
    if not start_text and not end_text:
        return None
    try:
        start = date.fromisoformat(start_text) if start_text else date.today() - timedelta(days=90)
        end = date.fromisoformat(end_text) if end_text else date.today()
    except (TypeError, ValueError):
        return []
    if start > end:
        return []
    run_ids = []
    for run in AssignmentRun.query.all():
        match = re.fullmatch(r"(\d{4})-W(\d{2})", run.week_key or "")
        if match:
            week_start = date.fromisocalendar(int(match.group(1)), int(match.group(2)), 4)
            if start <= week_start <= end:
                run_ids.append(run.id)
    return run_ids


def _apply_common_filters(q, args):
    run_ids = _report_run_ids(args)
    if run_ids is not None:
        q = q.filter(AssignmentRun.id.in_(run_ids))
    if args.get("posted_only"):
        q = q.filter(AssignmentRun.status == "posted")

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
        completion_q.filter(TaskCompletion.completion_status == "completed")
        .with_entities(AssignmentItem.assignee_user_id, func.count(TaskCompletion.id))
        .group_by(AssignmentItem.assignee_user_id)
        .all()
    )
    completed_map = {uid: c for uid, c in completed}
    not_completed = (
        completion_q.filter(TaskCompletion.completion_status == "not_completed")
        .with_entities(AssignmentItem.assignee_user_id, func.count(TaskCompletion.id))
        .group_by(AssignmentItem.assignee_user_id)
        .all()
    )
    not_completed_map = {uid: c for uid, c in not_completed}

    user_ids = sorted(set(list(assigned_map.keys()) + list(completed_map.keys()) + list(not_completed_map.keys())))
    users = {u.id: u for u in User.query.filter(User.id.in_(user_ids)).all()} if user_ids else {}

    rows = []
    for uid in user_ids:
        a = assigned_map.get(uid, 0)
        c = completed_map.get(uid, 0)
        nc = not_completed_map.get(uid, 0)
        pct = round((c / a) * 100, 2) if a else 0.0
        rows.append(
            {
                "user_id": uid,
                "name": users.get(uid).name if users.get(uid) else f"user-{uid}",
                "assigned": a,
                "completed": c,
                "not_completed": nc,
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
        completion_q.filter(TaskCompletion.completion_status == "completed").with_entities(
            AssignmentItem.task_template_id,
            AssignmentItem.assignee_user_id,
            func.count(TaskCompletion.id),
        )
        .group_by(AssignmentItem.task_template_id, AssignmentItem.assignee_user_id)
        .all()
    )

    completed_map = {(tid, uid): cnt for tid, uid, cnt in task_completions}
    not_completed_rows = (
        completion_q.filter(TaskCompletion.completion_status == "not_completed")
        .with_entities(
            AssignmentItem.task_template_id,
            AssignmentItem.assignee_user_id,
            func.count(TaskCompletion.id),
        )
        .group_by(AssignmentItem.task_template_id, AssignmentItem.assignee_user_id)
        .all()
    )
    not_completed_map = {(tid, uid): cnt for tid, uid, cnt in not_completed_rows}
    users = {u.id: u.name for u in User.query.all()}
    tasks = {t.id: t.title for t in TaskTemplate.query.all()}

    rows = []
    per_task_pcts: dict[int, list[float]] = {}
    for tid, uid, assigned_cnt in task_assignments:
        completed_cnt = completed_map.get((tid, uid), 0)
        not_completed_cnt = not_completed_map.get((tid, uid), 0)
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
                "not_completed": not_completed_cnt,
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


def build_summary(args):
    summary_args = args.copy()
    summary_args["posted_only"] = "1"
    person_rows = build_person_rows(summary_args)
    task_rows = build_task_rows(summary_args)
    task_map = {}
    for row in task_rows:
        summary = task_map.setdefault(
            row["task_template_id"],
            {"task_template_id": row["task_template_id"], "task_title": row["task_title"],
             "assigned": 0, "completed": 0, "not_completed": 0, "details": []},
        )
        for key in ("assigned", "completed", "not_completed"):
            summary[key] += row[key]
        summary["details"].append(row)
    task_summary = list(task_map.values())
    for row in task_summary:
        row["completion_pct"] = round((row["completed"] / row["assigned"]) * 100, 2) if row["assigned"] else 0.0

    totals = {
        "assigned": sum(row["assigned"] for row in person_rows),
        "completed": sum(row["completed"] for row in person_rows),
        "not_completed": sum(row["not_completed"] for row in person_rows),
    }
    totals["completion_pct"] = round((totals["completed"] / totals["assigned"]) * 100, 2) if totals["assigned"] else 0.0
    lowest_people = sorted(person_rows, key=lambda row: (row["completion_pct"], -row["not_completed"], row["name"]))[:10]
    never_finished = [row for row in person_rows if row["assigned"] and row["completed"] == 0]
    never_finished = sorted(never_finished, key=lambda row: (-row["assigned"], row["name"]))[:5]
    lowest_tasks = sorted(task_summary, key=lambda row: (row["completion_pct"], -row["not_completed"], row["task_title"]))[:10]
    return {
        "summary": totals,
        "lowest_people": lowest_people,
        "never_finished_people": never_finished,
        "lowest_tasks": lowest_tasks,
        "task_rows": task_rows,
    }


@bp.get("/person")
@role_required("manager", "shift_lead", "owner")
def person_report():
    return jsonify({"rows": build_person_rows(request.args)})


@bp.get("/task")
@role_required("manager", "shift_lead", "owner")
def task_report():
    return jsonify({"rows": build_task_rows(request.args)})


@bp.get("/summary")
@role_required("manager", "shift_lead", "owner")
def summary_report():
    return jsonify(build_summary(request.args))
