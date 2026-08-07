import pytest

from taskassigner.app import create_app
from taskassigner.extensions import db
from taskassigner.models import AssignmentItem, AssignmentRun, JobCode, TaskTemplate, TaskCompletion, User


@pytest.fixture
def app():
    class TestConfig:
        SECRET_KEY = "test"
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        LOCKOUT_THRESHOLD = 5
        LOCKOUT_MINUTES = 15

    app = create_app(TestConfig)
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

        manager = User(name="eric", role="manager")
        manager.set_password("pass123")
        owner = User(name="owner", role="owner")
        owner.set_password("pass123")
        crew1 = User(name="alice", role="crew")
        crew1.set_pin("1234")
        crew2 = User(name="bob", role="crew")
        crew2.set_pin("1234")

        cooks = JobCode(name="Cooks")
        db.session.add_all([manager, owner, crew1, crew2, cooks])
        db.session.flush()

        crew1.job_codes.append(cooks)
        crew2.job_codes.append(cooks)

        t1 = TaskTemplate(title="Clean Grill", responsible_job_code_id=cooks.id)
        t2 = TaskTemplate(title="Stock Freezer", responsible_job_code_id=cooks.id)
        db.session.add_all([t1, t2])
        db.session.flush()

        run = AssignmentRun(week_key="2026-W28", status="posted", generated_by=manager.id)
        db.session.add(run)
        db.session.flush()

        i1 = AssignmentItem(run_id=run.id, task_template_id=t1.id, assignee_user_id=crew1.id)
        i2 = AssignmentItem(run_id=run.id, task_template_id=t2.id, assignee_user_id=crew2.id)
        db.session.add_all([i1, i2])
        db.session.flush()

        c1 = TaskCompletion(assignment_item_id=i1.id, completed_by=crew1.id)
        db.session.add(c1)
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


def test_person_report_returns_completion_metrics(client):
    _login_manager(client)
    res = client.get("/api/reports/person?week=2026-W28")
    assert res.status_code == 200
    assert len(res.json["rows"]) >= 1
    assert all("completion_pct" in r for r in res.json["rows"])


def test_task_report_returns_task_distribution_completion_pct_and_consistency(client):
    _login_manager(client)
    res = client.get("/api/reports/task?week=2026-W28")
    assert res.status_code == 200
    assert len(res.json["rows"]) >= 1
    assert all(
        "task_title" in r
        and "completion_pct" in r
        and "consistency_spread_pct" in r
        for r in res.json["rows"]
    )


def test_owner_can_view_owner_weekly_reports(client):
    _login_owner(client)
    res = client.get("/api/owner/reports/weekly")
    assert res.status_code == 200
    assert "person" in res.json and "task" in res.json
