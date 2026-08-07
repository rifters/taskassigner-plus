from __future__ import annotations

import json
from typing import Any

from .extensions import db
from .models import AuditEvent


def log_audit(actor_user_id: int, action_type: str, entity_type: str, entity_id: str | None = None, payload: dict[str, Any] | None = None) -> None:
    event = AuditEvent(
        actor_user_id=actor_user_id,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        payload_json=json.dumps(payload or {}),
    )
    db.session.add(event)
    db.session.commit()
