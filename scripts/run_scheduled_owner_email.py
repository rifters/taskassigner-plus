from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from taskassigner.app import create_app
from taskassigner.routes.owner import process_scheduled_owner_email


def _bool_env(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


if __name__ == "__main__":
    app = create_app()
    force = _bool_env("TASKASSIGNER_SCHEDULE_FORCE", False)
    dry_run = _bool_env("TASKASSIGNER_SCHEDULE_DRY_RUN", False)
    with app.app_context():
        payload, status = process_scheduled_owner_email(force=force, dry_run=dry_run)
    print(json.dumps(payload, separators=(",", ":")))
    raise SystemExit(0 if status < 400 else 1)
