from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify, redirect, request
from flask_login import current_user

from ..audit import log_audit
from ..extensions import db
from ..models import AssignmentItem, AssignmentRun, TaskCompletion, TaskNote
from ..security import role_required

bp = Blueprint("completions", __name__, url_prefix="/api/completions")


def _note_type(value: str | None) -> str:
    v = (value or "general").strip().lower()
    return v if v in {"general", "incomplete"} else "general"


@bp.post("/<int:assignment_item_id>/mark-complete")
@role_required("crew")
def mark_complete(assignment_item_id: int):
    item = AssignmentItem.query.get_or_404(assignment_item_id)
    if item.assignee_user_id != current_user.id:
        return jsonify({"error": "forbidden"}), 403

    completion = TaskCompletion.query.filter_by(assignment_item_id=item.id).first()
    if not completion:
        completion = TaskCompletion(
            assignment_item_id=item.id,
            completed_by=current_user.id,
            completion_source="crew_self",
            completed_at=datetime.utcnow(),
        )
        db.session.add(completion)
    else:
        completion.completed_by = current_user.id
        completion.completed_at = datetime.utcnow()
        completion.completion_status = "completed"
        completion.completion_source = "crew_self"
        completion.manager_reason = None

    db.session.commit()
    log_audit(current_user.id, "complete", "assignment_item", str(item.id), {"source": "crew_self"})
    return jsonify({"ok": True})


@bp.post("/<int:assignment_item_id>/manager-complete")
@role_required("manager")
def manager_complete(assignment_item_id: int):
    item = AssignmentItem.query.get_or_404(assignment_item_id)
    data = request.get_json(silent=True) or request.form.to_dict()
    reason = (data.get("reason") or "").strip()
    if not reason:
        return jsonify({"error": "reason_required"}), 400
    if len(reason) > 500:
        return jsonify({"error": "reason_too_long"}), 400

    completion = TaskCompletion.query.filter_by(assignment_item_id=item.id).first()
    if not completion:
        completion = TaskCompletion(
            assignment_item_id=item.id,
            completed_by=current_user.id,
            completion_source="manager_on_behalf",
            manager_reason=reason,
            completed_at=datetime.utcnow(),
        )
        db.session.add(completion)
    else:
        completion.completed_by = current_user.id
        completion.completed_at = datetime.utcnow()
        completion.completion_status = "completed"
        completion.completion_source = "manager_on_behalf"
        completion.manager_reason = reason

    db.session.commit()
    log_audit(
        current_user.id,
        "manager_complete",
        "assignment_item",
        str(item.id),
        {"assignee_user_id": item.assignee_user_id, "reason": reason},
    )
    if request.form and "text/html" in request.accept_mimetypes:
        run = db.session.get(AssignmentRun, item.run_id)
        return redirect(f"/manager/weeks/{run.week_key}/completions")
    return jsonify({"ok": True})


@bp.post("/<int:assignment_item_id>/note")
@role_required("crew")
def add_note(assignment_item_id: int):
    item = AssignmentItem.query.get_or_404(assignment_item_id)
    if item.assignee_user_id != current_user.id:
        return jsonify({"error": "forbidden"}), 403

    existing = TaskNote.query.filter_by(assignment_item_id=item.id, author_user_id=current_user.id).first()
    if existing:
        return jsonify({"error": "note_already_exists"}), 400

    data = request.get_json(force=True)
    note_text = (data.get("note") or "").strip()
    if not note_text:
        return jsonify({"error": "note_required"}), 400
    if len(note_text) > 500:
        return jsonify({"error": "note_too_long"}), 400

    note = TaskNote(
        assignment_item_id=item.id,
        author_user_id=current_user.id,
        note_type=_note_type(data.get("note_type")),
        note_text=note_text,
    )
    db.session.add(note)
    db.session.commit()
    log_audit(
        current_user.id,
        "task_note",
        "assignment_item",
        str(item.id),
        {"note_type": note.note_type},
    )
    return jsonify({"ok": True, "note_type": note.note_type})


@bp.post("/<int:assignment_item_id>/confirm")
@role_required("manager", "shift_lead")
def confirm_complete(assignment_item_id: int):
    item = AssignmentItem.query.get_or_404(assignment_item_id)
    completion = TaskCompletion.query.filter_by(assignment_item_id=item.id).first()
    if not completion or completion.completion_status != "completed":
        return jsonify({"error": "not_completed_yet"}), 400

    completion.manager_confirmed_by = current_user.id
    completion.manager_confirmed_at = datetime.utcnow()
    db.session.commit()
    log_audit(current_user.id, "confirm_completion", "assignment_item", str(item.id), {})
    return jsonify({"ok": True})
