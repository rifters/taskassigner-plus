from __future__ import annotations

from datetime import datetime

from flask_login import UserMixin

from .extensions import bcrypt, db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=True)
    role = db.Column(db.String(32), nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    pin_hash = db.Column(db.String(255), nullable=True)
    active = db.Column(db.Boolean, default=True, nullable=False)

    job_codes = db.relationship("JobCode", secondary="user_job_codes", back_populates="users")

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return bcrypt.check_password_hash(self.password_hash, password)

    def set_pin(self, pin: str) -> None:
        self.pin_hash = bcrypt.generate_password_hash(pin).decode("utf-8")

    def check_pin(self, pin: str) -> bool:
        if not self.pin_hash:
            return False
        return bcrypt.check_password_hash(self.pin_hash, pin)


class JobCode(TimestampMixin, db.Model):
    __tablename__ = "job_codes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)

    users = db.relationship("User", secondary="user_job_codes", back_populates="job_codes")


class UserJobCode(db.Model):
    __tablename__ = "user_job_codes"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    job_code_id = db.Column(db.Integer, db.ForeignKey("job_codes.id"), primary_key=True)


class TaskTemplate(TimestampMixin, db.Model):
    __tablename__ = "task_templates"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    responsible_job_code_id = db.Column(db.Integer, db.ForeignKey("job_codes.id"), nullable=False)
    weight = db.Column(db.Integer, nullable=True)
    est_minutes = db.Column(db.Integer, nullable=True)
    active = db.Column(db.Boolean, default=True, nullable=False)

    responsible_job_code = db.relationship("JobCode")


class AssignmentRun(TimestampMixin, db.Model):
    __tablename__ = "assignment_runs"

    id = db.Column(db.Integer, primary_key=True)
    week_key = db.Column(db.String(20), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="draft")
    generated_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    posted_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    posted_at = db.Column(db.DateTime, nullable=True)


class AssignmentItem(TimestampMixin, db.Model):
    __tablename__ = "assignment_items"

    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey("assignment_runs.id"), nullable=False, index=True)
    task_template_id = db.Column(db.Integer, db.ForeignKey("task_templates.id"), nullable=False)
    assignee_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    source = db.Column(db.String(20), nullable=False, default="generated")
    edited_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    edited_reason = db.Column(db.String(300), nullable=True)


class TaskCompletion(TimestampMixin, db.Model):
    __tablename__ = "task_completions"

    id = db.Column(db.Integer, primary_key=True)
    assignment_item_id = db.Column(
        db.Integer, db.ForeignKey("assignment_items.id"), nullable=False, unique=True
    )
    completed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    completed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completion_source = db.Column(db.String(32), nullable=False, default="crew_self")
    manager_reason = db.Column(db.String(500), nullable=True)
    manager_confirmed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    manager_confirmed_at = db.Column(db.DateTime, nullable=True)


class TaskNote(TimestampMixin, db.Model):
    __tablename__ = "task_notes"

    id = db.Column(db.Integer, primary_key=True)
    assignment_item_id = db.Column(db.Integer, db.ForeignKey("assignment_items.id"), nullable=False, index=True)
    author_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    note_type = db.Column(db.String(32), nullable=False, default="general")
    note_text = db.Column(db.String(500), nullable=False)


class AuditEvent(db.Model):
    __tablename__ = "audit_events"

    id = db.Column(db.Integer, primary_key=True)
    actor_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action_type = db.Column(db.String(100), nullable=False, index=True)
    entity_type = db.Column(db.String(100), nullable=False)
    entity_id = db.Column(db.String(100), nullable=True)
    payload_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)


class AuthAttempt(db.Model):
    __tablename__ = "auth_attempts"

    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(255), nullable=False, index=True)
    ip_token = db.Column(db.String(255), nullable=True, index=True)
    success = db.Column(db.Boolean, nullable=False, default=False)
    occurred_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)


class AppSetting(db.Model):
    __tablename__ = "app_settings"

    key = db.Column(db.String(128), primary_key=True)
    value = db.Column(db.String(512), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    target_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    token = db.Column(db.String(255), nullable=False, unique=True, index=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    used_at = db.Column(db.DateTime, nullable=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
