import pytest

from taskassigner.app import create_app
from taskassigner.extensions import db
from taskassigner import email_report
from taskassigner.models import User
from taskassigner.routes import owner as owner_routes


@pytest.fixture
def app():
    class TestConfig:
        SECRET_KEY = "test"
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        LOCKOUT_THRESHOLD = 5
        LOCKOUT_MINUTES = 15
        AUTH_RATE_LIMIT_PER_MINUTE = 5
        SESSION_TTL_HOURS = {"crew": 12, "shift_lead": 8, "manager": 8, "owner": 24}
        SMTP_HOST = ""
        SMTP_PORT = 587
        SMTP_USER = ""
        SMTP_PASSWORD = ""
        SMTP_USE_TLS = True
        EMAIL_FROM = ""

    app = create_app(TestConfig)
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        manager = User(name="eric", role="manager")
        manager.set_password("pass123")
        owner = User(name="owner", role="owner")
        owner.set_password("pass123")
        db.session.add_all([manager, owner])
        db.session.commit()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def _login_manager(client):
    res = client.post("/auth/login-password", json={"name": "eric", "password": "pass123"})
    assert res.status_code == 200


def _login_owner(client):
    res = client.post("/auth/login-password", json={"name": "owner", "password": "pass123"})
    assert res.status_code == 200


def test_manager_can_set_and_get_owner_report_email(client):
    _login_manager(client)
    set_res = client.post("/api/owner/settings/report-email", json={"owner_report_email": "owner@example.com"})
    assert set_res.status_code == 200

    get_res = client.get("/api/owner/settings/report-email")
    assert get_res.status_code == 200
    assert get_res.json["owner_report_email"] == "owner@example.com"


def test_owner_can_get_but_not_set_report_email(client):
    _login_owner(client)
    get_res = client.get("/api/owner/settings/report-email")
    assert get_res.status_code == 200

    set_res = client.post("/api/owner/settings/report-email", json={"owner_report_email": "x@y.com"})
    assert set_res.status_code == 403


def test_send_email_requires_config_and_configured_owner_email(client):
    _login_manager(client)

    # Missing owner report recipient first
    res = client.post("/api/owner/reports/weekly/send-email", json={"week": "2026-W32"})
    assert res.status_code == 400
    assert res.json["error"] == "owner_report_email_not_set"

    # Set recipient, still fail because SMTP is not configured in test config
    client.post("/api/owner/settings/report-email", json={"owner_report_email": "owner@example.com"})
    res2 = client.post("/api/owner/reports/weekly/send-email", json={"week": "2026-W32"})
    assert res2.status_code == 400
    assert res2.json["error"] == "smtp_not_configured"


def test_test_email_endpoint_requires_same_config_guards(client):
    _login_manager(client)

    # Missing recipient setting
    res = client.post("/api/owner/reports/test-email")
    assert res.status_code == 400
    assert res.json["error"] == "owner_report_email_not_set"

    # Recipient set, but SMTP still missing in test config
    client.post("/api/owner/settings/report-email", json={"owner_report_email": "owner@example.com"})
    res2 = client.post("/api/owner/reports/test-email")
    assert res2.status_code == 400
    assert res2.json["error"] == "smtp_not_configured"


def test_weekly_schedule_set_and_get(client):
    _login_manager(client)

    set_res = client.post(
        "/api/owner/reports/weekly/schedule",
        json={"enabled": True, "weekday": 2, "hour_utc": 6, "minute_utc": 30},
    )
    assert set_res.status_code == 200
    assert set_res.json["schedule"]["enabled"] is True
    assert set_res.json["schedule"]["weekday"] == 2
    assert set_res.json["schedule"]["hour_utc"] == 6
    assert set_res.json["schedule"]["minute_utc"] == 30

    get_res = client.get("/api/owner/reports/weekly/schedule")
    assert get_res.status_code == 200
    assert get_res.json["schedule"]["weekday"] == 2


def test_weekly_schedule_rejects_out_of_range_values(client):
    _login_manager(client)

    bad_weekday = client.post("/api/owner/reports/weekly/schedule", json={"weekday": 7})
    assert bad_weekday.status_code == 400
    assert bad_weekday.json["error"] == "weekday_out_of_range"

    bad_hour = client.post("/api/owner/reports/weekly/schedule", json={"weekday": 1, "hour_utc": 24})
    assert bad_hour.status_code == 400
    assert bad_hour.json["error"] == "hour_out_of_range"

    bad_min = client.post("/api/owner/reports/weekly/schedule", json={"weekday": 1, "hour_utc": 8, "minute_utc": 60})
    assert bad_min.status_code == 400
    assert bad_min.json["error"] == "minute_out_of_range"


def test_weekly_schedule_run_requires_owner_email_and_smtp(client):
    _login_manager(client)

    # schedule defaults to enabled=False -> force run to verify guard behavior
    res = client.post("/api/owner/reports/weekly/run-scheduled", json={"force": True, "dry_run": True})
    assert res.status_code == 400
    assert res.json["error"] == "owner_report_email_not_set"

    client.post("/api/owner/settings/report-email", json={"owner_report_email": "owner@example.com"})
    res2 = client.post("/api/owner/reports/weekly/run-scheduled", json={"force": True, "dry_run": True})
    assert res2.status_code == 400
    assert res2.json["error"] == "smtp_not_configured"


def test_weekly_recipients_include_active_managers_and_owners_only(app):
    with app.app_context():
        db.session.add_all([
            User(name="manager2", role="manager", email="manager@example.com", active=True),
            User(name="owner2", role="owner", email="owner@example.com", active=True),
            User(name="crew", role="crew", email="crew@example.com", active=True),
            User(name="lead", role="shift_lead", email="lead@example.com", active=True),
            User(name="inactive", role="manager", email="inactive@example.com", active=False),
            User(name="bad-email", role="manager", email="not-an-email", active=True),
        ])
        db.session.commit()
        recipients = email_report.resolve_weekly_report_recipients(User.query.all(), "owner@example.com")
    assert recipients == ["manager@example.com", "owner@example.com"]


def test_weekly_csv_contains_assignment_level_completion_fields():
    csv_text = email_report.render_weekly_report_csv({
        "week": "2026-W36",
        "assignment_rows": [{
            "week": "2026-W36", "task_number": 4, "task_title": "Clean Grill",
            "job_code": "Cooks", "assignee_name": "Alice", "completion_status": "completed",
            "completion_source": "crew_self", "completed_by_name": "Alice",
            "manager_reason": "", "completed_at": "2026-09-09T20:00:00",
        }],
    })
    assert "task_number,task_title" in csv_text
    assert "Clean Grill" in csv_text
    assert "crew_self" in csv_text


def test_weekly_email_is_multipart_with_csv_attachment(app, monkeypatch):
    captured = {}

    class FakeSMTP:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def starttls(self):
            pass

        def send_message(self, message):
            captured["message"] = message

    monkeypatch.setattr(owner_routes.smtplib, "SMTP", FakeSMTP)
    with app.app_context():
        app.config.update(SMTP_HOST="smtp.example.com", EMAIL_FROM="reports@example.com")
        owner_routes._send_email_message("2026-W36", ["manager@example.com", "owner@example.com"], {
            "week": "2026-W36", "week_label": "Thursday, September 3, 2026 through Wednesday, September 9, 2026",
            "summary": {"assigned": 1, "completed": 1, "not_completed": 0, "completion_pct": 100,
                        "crew_self": 1, "manager_on_behalf": 0},
            "lowest_people": [], "never_finished_people": [], "lowest_tasks": [],
            "assignment_rows": [{"task_number": 1, "task_title": "Clean Grill"}],
        })
    message = captured["message"]
    assert message["To"] == "manager@example.com, owner@example.com"
    assert "September 3" in message["Subject"]
    assert message.is_multipart()
    assert any(part.get_filename() == "taskassigner-weekly-report-2026-W36.csv" for part in message.iter_attachments())
