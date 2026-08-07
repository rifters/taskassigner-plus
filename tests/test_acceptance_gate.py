import pytest

from taskassigner.app import create_app
from taskassigner.extensions import db
from taskassigner.models import AssignmentItem, AssignmentRun, JobCode, TaskTemplate, User, TaskCompletion


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

    app = create_app(TestConfig)
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

        manager = User(name="eric", role="manager")
        manager.set_password("pass123")
        lead = User(name="lead", role="shift_lead")
        lead.set_password("pass123")
        owner = User(name="owner", role="owner")
        owner.set_password("pass123")
        crew1 = User(name="alice", role="crew")
        crew1.set_pin("1234")
        crew2 = User(name="bob", role="crew")
        crew2.set_pin("1234")

        jc = JobCode(name="Cooks")
        db.session.add_all([manager, lead, owner, crew1, crew2, jc])
        db.session.flush()

        crew1.job_codes.append(jc)
        crew2.job_codes.append(jc)

        t1 = TaskTemplate(title="Clean Grill", responsible_job_code_id=jc.id)
        t2 = TaskTemplate(title="Stock Freezer", responsible_job_code_id=jc.id)
        db.session.add_all([t1, t2])
        db.session.flush()

        run = AssignmentRun(week_key="2026-W30", status="posted", generated_by=manager.id)
        db.session.add(run)
        db.session.flush()

        i1 = AssignmentItem(run_id=run.id, task_template_id=t1.id, assignee_user_id=crew1.id)
        i2 = AssignmentItem(run_id=run.id, task_template_id=t2.id, assignee_user_id=crew2.id)
        db.session.add_all([i1, i2])
        db.session.flush()

        completion = TaskCompletion(assignment_item_id=i1.id, completed_by=crew1.id)
        db.session.add(completion)
        db.session.commit()

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def login_manager(client):
    res = client.post("/auth/login-password", json={"name": "eric", "password": "pass123"})
    assert res.status_code == 200


def login_crew(client, name="alice"):
    res = client.post("/auth/login-pin", json={"name": name, "pin": "1234"})
    assert res.status_code == 200


def test_lockout_after_threshold(client):
    for _ in range(5):
        client.post("/auth/login-password", json={"name": "eric", "password": "bad"})
    res = client.post("/auth/login-password", json={"name": "eric", "password": "bad"})
    assert res.status_code == 429


def test_manager_task_filters_support_job_code_person_task_week(client):
    login_manager(client)
    res = client.get("/api/reports/task?week=2026-W30&job_code=1&person=4&task=1")
    assert res.status_code == 200


def test_unauthorized_crew_cannot_confirm_other_completion(client):
    login_crew(client, "bob")
    res = client.post("/api/completions/1/confirm")
    assert res.status_code == 403


def test_owner_read_only_report_access(client):
    res = client.post("/auth/login-password", json={"name": "owner", "password": "pass123"})
    assert res.status_code == 200
    report = client.get("/api/owner/reports/weekly")
    assert report.status_code == 200


def test_send_email_requires_configured_owner_email_and_smtp(client):
    login_manager(client)
    res = client.post("/api/owner/reports/weekly/send-email")
    assert res.status_code == 400
    assert res.json["error"] in ("owner_report_email_not_set", "smtp_not_configured")
