import pytest

from taskassigner.app import create_app
from taskassigner.extensions import db
from taskassigner.models import AssignmentItem, AssignmentRun, JobCode, TaskTemplate, TaskCompletion, TaskNote, User


@pytest.fixture
def app():
    class TestConfig:
        SECRET_KEY = "test"
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        LOCKOUT_THRESHOLD = 5
        LOCKOUT_MINUTES = 15
        AUTH_RATE_LIMIT_PER_MINUTE = 5

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

        # posted week used by completion review
        posted_run = AssignmentRun(week_key="2026-W28", status="posted", generated_by=manager.id)
        db.session.add(posted_run)
        db.session.flush()

        i1 = AssignmentItem(run_id=posted_run.id, task_template_id=t1.id, assignee_user_id=crew1.id)
        i2 = AssignmentItem(run_id=posted_run.id, task_template_id=t2.id, assignee_user_id=crew2.id)
        db.session.add_all([i1, i2])
        db.session.flush()

        c1 = TaskCompletion(
            assignment_item_id=i1.id,
            completed_by=crew1.id,
            completion_source="crew_self",
        )
        db.session.add(c1)

        # draft week used by generate/review/post workflow pages
        draft_run = AssignmentRun(week_key="2026-W29", status="draft", generated_by=manager.id)
        db.session.add(draft_run)
        db.session.flush()
        draft_item = AssignmentItem(run_id=draft_run.id, task_template_id=t1.id, assignee_user_id=crew1.id)
        db.session.add(draft_item)

        # old completion (>4 weeks window) should be excluded from crew history
        old_run = AssignmentRun(week_key="2026-W01", status="posted", generated_by=manager.id)
        db.session.add(old_run)
        db.session.flush()
        old_item = AssignmentItem(run_id=old_run.id, task_template_id=t1.id, assignee_user_id=crew1.id)
        db.session.add(old_item)
        db.session.flush()
        old_completion = TaskCompletion(
            assignment_item_id=old_item.id,
            completed_by=crew1.id,
            completion_source="crew_self",
        )
        db.session.add(old_completion)
        db.session.flush()
        # force old timestamp
        from datetime import datetime

        old_completion.completed_at = datetime(2025, 1, 1)

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


def _login_crew(client, name="alice"):
    res = client.post("/auth/login-pin", json={"name": name, "pin": "1234"})
    assert res.status_code == 200


def test_manager_can_access_week_workflow_pages(client):
    _login_manager(client)

    home = client.get("/manager")
    assert home.status_code == 200
    assert home.json["workflow"]["schedule"] == "/api/owner/reports/weekly/schedule"

    generate_page = client.get("/manager/weeks/2026-W29/generate")
    assert generate_page.status_code == 200

    draft_page = client.get("/manager/weeks/2026-W29/draft")
    assert draft_page.status_code == 200
    assert len(draft_page.json["rows"]) >= 1

    post_page = client.get("/manager/weeks/2026-W29/post")
    assert post_page.status_code == 200

    schedule = client.get("/api/owner/reports/weekly/schedule")
    assert schedule.status_code == 200
    assert "schedule" in schedule.json


def test_manager_completions_page_includes_completion_source_context(client):
    _login_manager(client)
    res = client.get("/manager/weeks/2026-W28/completions")
    assert res.status_code == 200
    assert len(res.json["rows"]) >= 1
    assert all("completion_source" in r for r in res.json["rows"])


def test_manager_on_behalf_completion_requires_reason(client):
    _login_manager(client)
    res = client.post("/api/completions/2/manager-complete", json={"reason": ""})
    assert res.status_code == 400
    assert res.json["error"] == "reason_required"


def test_manager_on_behalf_completion_persists_source_and_reason(client, app):
    _login_manager(client)
    res = client.post("/api/completions/2/manager-complete", json={"reason": "Crew not using device"})
    assert res.status_code == 200

    with app.app_context():
        c = TaskCompletion.query.filter_by(assignment_item_id=2).first()
        assert c is not None
        assert c.completion_source == "manager_on_behalf"
        assert c.manager_reason == "Crew not using device"

    page = client.get("/manager/weeks/2026-W28/completions")
    row = [r for r in page.json["rows"] if r["assignment_item_id"] == 2][0]
    assert row["completion_source"] == "manager_on_behalf"
    assert row["manager_reason"] == "Crew not using device"


def test_crew_note_write_once_general_and_incomplete_supported(client, app):
    _login_crew(client, "alice")

    first = client.post("/api/completions/1/note", json={"note_type": "general", "note": "Need new scrubber"})
    assert first.status_code == 200
    assert first.json["note_type"] == "general"

    second = client.post("/api/completions/1/note", json={"note_type": "incomplete", "note": "Could not finish"})
    assert second.status_code == 400
    assert second.json["error"] == "note_already_exists"

    with app.app_context():
        n = TaskNote.query.filter_by(assignment_item_id=1, author_user_id=3).first()
        assert n is not None
        assert n.note_type == "general"


def test_crew_history_is_bounded_to_4_weeks_and_self_only(client):
    _login_crew(client, "alice")
    own = client.get("/crew/tasks")
    assert own.status_code == 200
    assert "history_rows" in own.json
    history_ids = {r["assignment_item_id"] for r in own.json["history_rows"]}
    assert 1 in history_ids  # recent completion
    assert 4 not in history_ids  # old completion excluded

    # bob cannot write note on alice task
    client.post("/auth/logout")
    _login_crew(client, "bob")
    forbidden = client.post("/api/completions/1/note", json={"note_type": "incomplete", "note": "blocked"})
    assert forbidden.status_code == 403


def test_page_level_authz_boundaries(client):
    _login_crew(client, "alice")
    denied_manager_page = client.get("/manager/weeks/2026-W29/draft")
    assert denied_manager_page.status_code == 403

    client.post("/auth/logout")
    _login_owner(client)
    denied_owner_mutation = client.post("/api/owner/reports/weekly/schedule", json={"enabled": True})
    assert denied_owner_mutation.status_code == 403


def test_owner_reports_page_is_read_only(client):
    _login_owner(client)
    page = client.get("/owner/reports")
    assert page.status_code == 200
    assert page.json["read_only"] is True
