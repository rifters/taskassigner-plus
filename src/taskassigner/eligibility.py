from __future__ import annotations

from sqlalchemy import exists

from .models import JobCode, TaskExclusion, TaskTemplate, User


def is_eligible(user: User, task: TaskTemplate) -> bool:
    if not user.active or user.role != "crew":
        return False
    if not any(code.id == task.responsible_job_code_id for code in user.job_codes):
        return False
    return not TaskExclusion.query.filter_by(user_id=user.id, task_template_id=task.id).first()


def eligible_users_for_task(task: TaskTemplate) -> list[User]:
    excluded = exists().where(
        (TaskExclusion.user_id == User.id)
        & (TaskExclusion.task_template_id == task.id)
    )
    return (
        User.query.join(User.job_codes)
        .filter(
            JobCode.id == task.responsible_job_code_id,
            User.active.is_(True),
            User.role == "crew",
            ~excluded,
        )
        .order_by(User.id.asc())
        .all()
    )