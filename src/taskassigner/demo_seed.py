from __future__ import annotations

from .extensions import db
from .models import AssignmentItem, AssignmentRun, AuditEvent, AuthAttempt, JobCode, PasswordResetToken, TaskCompletion, TaskExclusion, TaskNote, TaskTemplate, User, UserJobCode

DEMO_MANAGER_NAME = "demo-manager"
DEMO_MANAGER_PASSWORD = "DemoPass123!"
DEMO_JOB_CODES = ("Cooks", "Servers", "Hosts", "SAs")


def reset_demo_data() -> dict[str, int]:
    """Replace local application data with a deterministic demo dataset."""
    from flask import current_app

    if not current_app.config.get("DEMO_MODE", False) or current_app.config.get("ENVIRONMENT") == "production":
        raise RuntimeError("demo_reset_disabled")

    for model in (TaskExclusion, TaskNote, TaskCompletion, AssignmentItem, AssignmentRun, TaskTemplate, AuditEvent, AuthAttempt, PasswordResetToken, UserJobCode, User, JobCode):
        db.session.query(model).delete()
    db.session.commit()
    db.session.expunge_all()

    codes = {name: JobCode(name=name) for name in DEMO_JOB_CODES}
    db.session.add_all(codes.values())
    db.session.flush()

    manager = User(name=DEMO_MANAGER_NAME, role="manager")
    manager.set_password(DEMO_MANAGER_PASSWORD)
    db.session.add(manager)

    people = [
        ("Alice", "crew", "Cooks"),
        ("Bob", "crew", "Cooks"),
        ("Carol", "crew", "Servers"),
        ("Dan", "crew", "Servers"),
        ("Eva", "crew", "Hosts"),
        ("Frank", "crew", "SAs"),
    ]
    users = []
    for name, role, code_name in people:
        user = User(name=name, role=role)
        user.set_pin("1234")
        user.job_codes.append(codes[code_name])
        users.append(user)
    db.session.add_all(users)
    db.session.flush()

    task_specs = [
        ("Clean grill", "Cooks"),
        ("Stock freezer", "Cooks"),
        ("Wipe server stations", "Servers"),
        ("Restock drink station", "Servers"),
        ("Clean entrance glass", "Hosts"),
        ("Check wait list supplies", "Hosts"),
        ("Sweep dining room", "SAs"),
        ("Restock takeout area", "SAs"),
    ]
    db.session.add_all(
        TaskTemplate(title=title, responsible_job_code_id=codes[code_name].id, notes="Demo task")
        for title, code_name in task_specs
    )
    db.session.flush()
    alice = next(user for user in users if user.name == "Alice")
    alice.job_codes.append(codes["Servers"])
    clean_grill = TaskTemplate.query.filter_by(title="Clean grill").first()
    db.session.add(TaskExclusion(user_id=alice.id, task_template_id=clean_grill.id))
    db.session.commit()
    return {"manager": 1, "job_codes": len(codes), "people": len(users), "task_templates": len(task_specs), "task_exclusions": 1}
