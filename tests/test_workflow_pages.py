from datetime import date, timedelta

import pytest

from taskassigner.app import create_app
from taskassigner.extensions import db
from taskassigner.models import AssignmentItem, AssignmentRun, JobCode, TaskTemplate, TaskCompletion, TaskNote, User
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
        DEMO_MODE = True

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


def test_post_assignments_link_handles_already_posted_week(client):
    _login_manager(client)
    response = client.get("/manager/weeks/2026-W28/post", headers={"Accept": "text/html"})
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/manager/weeks/2026-W28")


def test_manager_can_confirm_all_completed_items_from_review_page(client, app):
    _login_manager(client)
    page = client.get("/manager/weeks/2026-W28/completions", headers={"Accept": "text/html"})
    assert page.status_code == 200
    assert b"Confirm all completed" in page.data
    assert b"/manager/weeks/2026-W28/completions/confirm-all" in page.data

    confirmed = client.post(
        "/manager/weeks/2026-W28/completions/confirm-all",
        headers={"Accept": "text/html"},
    )
    assert confirmed.status_code == 302
    assert confirmed.headers["Location"].endswith("/manager/weeks/2026-W28/completions")

    with app.app_context():
        completion = TaskCompletion.query.filter_by(assignment_item_id=1).first()
        assert completion.manager_confirmed_by == 1
        assert completion.manager_confirmed_at is not None


def test_current_completions_finalize_prior_week_as_not_completed(client, app):
    _login_manager(client)
    today = date.today()
    current_start = today - timedelta(days=(today.weekday() - 3) % 7)
    iso_year, iso_week, _ = current_start.isocalendar()
    current_key = f"{iso_year:04d}-W{iso_week:02d}"
    with app.app_context():
        manager = User.query.filter_by(name="eric").one()
        db.session.add(AssignmentRun(week_key=current_key, status="posted", generated_by=manager.id))
        db.session.commit()
    page = client.get("/manager/weeks/current/completions", headers={"Accept": "text/html"})
    assert page.status_code == 200
    prior_page = client.get("/manager/weeks/2026-W28/completions", headers={"Accept": "text/html"})
    assert b"Not completed" in prior_page.data

    with app.app_context():
        not_completed = TaskCompletion.query.filter_by(assignment_item_id=2).one()
        assert not_completed.completion_status == "not_completed"
        assert not_completed.completed_by == 1


def test_reports_include_not_completed_counts(client):
    _login_manager(client)
    with client.application.app_context():
        manager = User.query.filter_by(name="eric").one()
        item = AssignmentItem.query.filter_by(id=2).one()
        db.session.add(
            TaskCompletion(
                assignment_item_id=item.id,
                completed_by=manager.id,
                completion_status="not_completed",
                completion_source="manager_week_close",
            )
        )
        db.session.commit()
    response = client.get("/api/reports/person?week=2026-W28")
    assert response.status_code == 200
    alice = next(row for row in response.json["rows"] if row["name"] == "alice")
    bob = next(row for row in response.json["rows"] if row["name"] == "bob")
    assert alice["completed"] == 1
    assert alice["not_completed"] == 0
    assert bob["completed"] == 0
    assert bob["not_completed"] == 1


def test_manager_completions_html_provides_on_behalf_form(client, app):
    _login_manager(client)
    page = client.get("/manager/weeks/2026-W28/completions", headers={"Accept": "text/html"})
    assert page.status_code == 200
    assert b"Complete on behalf" in page.data
    assert b"/api/completions/2/manager-complete" in page.data

    completed = client.post(
        "/api/completions/2/manager-complete",
        data={"reason": "Crew could not access the app."},
        headers={"Accept": "text/html"},
    )
    assert completed.status_code == 302
    assert completed.headers["Location"].endswith("/manager/weeks/2026-W28/completions")

    with app.app_context():
        completion = TaskCompletion.query.filter_by(assignment_item_id=2).first()
        assert completion is not None
        assert completion.completion_source == "manager_on_behalf"
        assert completion.manager_reason == "Crew could not access the app."


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


def test_manager_reports_dashboard_supports_date_range_and_rankings(client):
    _login_manager(client)
    with client.application.app_context():
        manager = User.query.filter_by(name="eric").one()
        db.session.add(TaskCompletion(
            assignment_item_id=2,
            completed_by=manager.id,
            completion_status="not_completed",
            completion_source="manager_week_close",
        ))
        db.session.commit()
    api = client.get("/api/reports/summary?start=2026-06-01&end=2026-09-30")
    assert api.status_code == 200
    assert api.json["summary"]["assigned"] == 2
    assert api.json["summary"]["completed"] == 1
    assert api.json["summary"]["not_completed"] == 1
    assert api.json["lowest_people"][0]["name"] == "bob"
    assert api.json["lowest_tasks"][0]["task_title"] == "Stock Freezer"

    page = client.get("/manager/reports?start=2026-06-01&end=2026-09-30", headers={"Accept": "text/html"})
    assert page.status_code == 200
    assert b"Top 10 people with lowest completion rate" in page.data
    assert b"Top 10 tasks with lowest completion rate" in page.data
    assert b"Stock Freezer" in page.data


def test_weekly_email_payload_contains_posted_assignment_rows(client):
    _login_manager(client)
    with client.application.app_context():
        payload = owner_routes._build_report_payload("2026-W28")
    assert len(payload["assignment_rows"]) == 2
    assert payload["assignment_rows"][0]["week"] == "2026-W28"
    assert {row["completion_status"] for row in payload["assignment_rows"]} == {"completed", "open"}


def test_rendered_role_pages_keep_json_contract_and_render_html(client):
    _login_manager(client)
    html = client.get("/manager", headers={"Accept": "text/html"})
    assert html.status_code == 200
    assert b"Weekly assignment workflow" in html.data
    assert b"Generate" in html.data


def test_manager_generate_flow_asks_for_assignment_week(client):
    _login_manager(client)
    home = client.get("/manager", headers={"Accept": "text/html"})
    assert b"/manager/weeks/generate" in home.data

    selection = client.get("/manager/weeks/generate", headers={"Accept": "text/html"})
    assert selection.status_code == 200
    assert b"Assignment week" in selection.data
    assert b"Thursday through Wednesday" in selection.data

    chosen = client.get(
        "/manager/weeks/generate?week_start=2026-09-03",
        headers={"Accept": "text/html"},
    )
    assert chosen.status_code == 302
    assert chosen.headers["Location"].endswith("/manager/weeks/2026-W36/generate")

    week_page = client.get("/manager/weeks/2026-W36", headers={"Accept": "text/html"})
    assert b"Thu Sep 3, 2026" in week_page.data
    assert b"Wed Sep 9, 2026" in week_page.data


def test_manager_generate_flow_rejects_invalid_assignment_week(client):
    _login_manager(client)
    response = client.get(
        "/manager/weeks/generate?week_start=2026-09-02",
        headers={"Accept": "text/html"},
    )
    assert response.status_code == 400

    draft = client.get("/manager/weeks/2026-W29/draft", headers={"Accept": "text/html"})
    assert draft.status_code == 200
    assert b"Review draft assignments" in draft.data

    weekly = client.get("/manager/weeks/2026-W29", headers={"Accept": "text/html"})
    assert b"Generated weeks" in weekly.data
    assert b"2026-W28" in weekly.data
    assert b"Posted" in weekly.data
    assert b"/manager/weeks/2026-W28" in weekly.data

    client.post("/auth/logout")
    _login_crew(client, "alice")
    crew = client.get("/crew/tasks", headers={"Accept": "text/html"})
    assert crew.status_code == 200
    assert b"write-once" in crew.data
    assert b"Mark complete" in crew.data

    client.post("/auth/logout")
    _login_owner(client)
    owner = client.get("/owner/reports", headers={"Accept": "text/html"})
    assert owner.status_code == 200
    assert b"Read-only" in owner.data


def test_rendered_pages_preserve_role_guards(client):
    _login_crew(client, "alice")
    denied = client.get("/manager", headers={"Accept": "text/html"})
    assert denied.status_code == 403

    client.post("/auth/logout")
    _login_owner(client)
    denied = client.get("/crew/tasks", headers={"Accept": "text/html"})
    assert denied.status_code == 403


def test_manager_browser_login_and_demo_reset(client, app):
    login_page = client.get("/auth/login")
    assert login_page.status_code == 200
    assert b"Local development demo only" in login_page.data

    logged_in = client.post(
        "/auth/login",
        data={"name": "eric", "password": "pass123"},
        headers={"Accept": "text/html"},
    )
    assert logged_in.status_code == 302
    assert logged_in.headers["Location"].endswith("/manager")

    reset = client.post("/manager/demo/reset", headers={"Accept": "text/html"})
    assert reset.status_code == 200
    assert b"Demo data reset" in reset.data

    with app.app_context():
        from taskassigner.demo_seed import DEMO_MANAGER_NAME

        assert User.query.filter_by(name=DEMO_MANAGER_NAME, role="manager").count() == 1
        assert JobCode.query.count() == 4
        assert TaskTemplate.query.count() == 8


def test_manager_setup_pages_render_and_create_from_forms(client):
    _login_manager(client)
    for path, marker in [("/manager/people", b"Add person"), ("/manager/job-codes", b"Add job code"), ("/manager/tasks", b"Add task template")]:
        response = client.get(path, headers={"Accept": "text/html"})
        assert response.status_code == 200
        assert marker in response.data
    assert client.post("/manager/job-codes", data={"name": "Dessert"}, headers={"Accept": "text/html"}).status_code == 302
    assert client.post("/manager/tasks", data={"title": "Clean dessert station", "responsible_job_code_id": "1"}, headers={"Accept": "text/html"}).status_code == 302


def test_manager_week_browser_flow(client):
    _login_manager(client)
    client.post("/manager/demo/reset", headers={"Accept": "text/html"})
    generated = client.post("/manager/weeks/2026-W29/generate", headers={"Accept": "text/html"})
    assert generated.status_code == 302
    page = client.get("/manager/weeks/2026-W29", headers={"Accept": "text/html"})
    assert page.status_code == 200
    assert b"Review fairness" in page.data
    assert b"Clean grill" in page.data
    posted = client.post("/manager/weeks/2026-W29/post", headers={"Accept": "text/html"})
    assert posted.status_code == 302
    assert b"Posted" in client.get("/manager/weeks/2026-W29", headers={"Accept": "text/html"}).data
