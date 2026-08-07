from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_login import current_user

from ..models import AuditEvent
from ..security import role_required

bp = Blueprint("audit", __name__, url_prefix="/api/audit")


@bp.get("")
@role_required("manager", "owner")
def audit_list():
    q = AuditEvent.query.order_by(AuditEvent.created_at.desc())

    actor = request.args.get("actor")
    action = request.args.get("action")
    entity = request.args.get("entity")
    if actor:
        q = q.filter(AuditEvent.actor_user_id == int(actor))
    if action:
        q = q.filter(AuditEvent.action_type == action)
    if entity:
        q = q.filter(AuditEvent.entity_type == entity)

    page = int(request.args.get("page", 1))
    page_size = 50
    rows = q.limit(page_size).offset((page - 1) * page_size).all()
    return jsonify(
        {
            "rows": [
                {
                    "id": r.id,
                    "actor_user_id": r.actor_user_id,
                    "action_type": r.action_type,
                    "entity_type": r.entity_type,
                    "entity_id": r.entity_id,
                    "payload_json": r.payload_json,
                    "created_at": r.created_at.isoformat(),
                }
                for r in rows
            ]
        }
    )
