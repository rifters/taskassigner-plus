from test_workflow_pages import app, client

from taskassigner.extensions import db
from taskassigner.models import AssignmentItem, AssignmentRun, JobCode, TaskExclusion, TaskTemplate, User


def test_manager_can_manage_person_task_exclusions(client, app):
    client.post("/auth/login-password", json={"name": "eric", "password": "pass123"})
    with app.app_context():
        person = User.query.filter_by(name="alice").first()
        task = TaskTemplate.query.filter_by(title="Clean Grill").first()
        person_id, task_id = person.id, task.id

    added = client.post(f"/manager/people/{person_id}/exclusions", data={"task_template_ids": str(task_id)})
    assert added.status_code == 302
    with app.app_context():
        assert TaskExclusion.query.filter_by(user_id=person_id, task_template_id=task_id).count() == 1

    removed = client.post(f"/manager/people/{person_id}/exclusions/remove", data={"task_template_ids": str(task_id)})
    assert removed.status_code == 302
    with app.app_context():
        assert TaskExclusion.query.filter_by(user_id=person_id, task_template_id=task_id).count() == 0


def test_people_edit_form_preserves_active_status(client):
    client.post("/auth/login-password", json={"name": "eric", "password": "pass123"})
    response = client.get("/manager/people", headers={"Accept": "text/html"})
    assert response.status_code == 200
    assert b'name="active" value="true" checked' in response.data


def test_crew_browser_login_redirects_to_own_tasks(client):
    page = client.get("/auth/login-crew")
    assert page.status_code == 200
    assert b"Crew login" in page.data
    logged_in = client.post("/auth/login-crew", data={"name": "alice", "pin": "1234"})
    assert logged_in.status_code == 302
    assert logged_in.headers["Location"].endswith("/crew/tasks")


def test_reassignment_rejects_wrong_job_code_and_excluded_person(client, app):
    client.post("/auth/login-password", json={"name": "eric", "password": "pass123"})
    with app.app_context():
        manager = User.query.filter_by(name="eric").first()
        alice = User.query.filter_by(name="alice").first()
        bob = User.query.filter_by(name="bob").first()
        servers = JobCode(name="Servers")
        db.session.add(servers)
        db.session.flush()
        task = TaskTemplate(title="Server-only task", responsible_job_code_id=servers.id)
        db.session.add(task)
        db.session.flush()
        run = AssignmentRun(week_key="eligibility", status="draft", generated_by=manager.id)
        db.session.add(run)
        db.session.flush()
        item = AssignmentItem(run_id=run.id, task_template_id=task.id, assignee_user_id=alice.id)
        db.session.add(item)
        db.session.commit()
        item_id, bob_id, alice_id, task_id = item.id, bob.id, alice.id, task.id

    wrong_pool = client.patch(
        f"/api/weeks/eligibility/draft/items/{item_id}",
        json={"assignee_user_id": bob_id},
    )
    assert wrong_pool.status_code == 400
    assert wrong_pool.json["error"] == "ineligible_assignee"

    with app.app_context():
        db.session.add(TaskExclusion(user_id=alice_id, task_template_id=task_id))
        db.session.commit()
    excluded = client.patch(
        f"/api/weeks/eligibility/draft/items/{item_id}",
        json={"assignee_user_id": alice_id},
    )
    assert excluded.status_code == 400
    assert excluded.json["error"] == "ineligible_assignee"


def test_crew_html_groups_assignments_by_job_code_and_shows_context(client, app):
    client.post("/auth/login-pin", json={"name": "alice", "pin": "1234"})
    with app.app_context():
        alice = User.query.filter_by(name="alice").first()
        servers = JobCode(name="Servers")
        db.session.add(servers)
        db.session.flush()
        alice.job_codes.append(servers)
        task = TaskTemplate(title="Server task", responsible_job_code_id=servers.id)
        db.session.add(task)
        db.session.flush()
        run = AssignmentRun(week_key="crew-groups", status="posted", generated_by=1)
        db.session.add(run)
        db.session.flush()
        db.session.add(AssignmentItem(run_id=run.id, task_template_id=task.id, assignee_user_id=alice.id))
        db.session.commit()

    response = client.get("/crew/tasks", headers={"Accept": "text/html"})
    assert response.status_code == 200
    assert b"Cooks" in response.data
    assert b"Servers" in response.data
    assert b"Server task" in response.data
    assert b"Job code" in response.data
    assert b"<details open" in response.data


def test_manager_weekly_html_groups_by_job_code_and_limits_reassignment_choices(client):
    client.post("/auth/login-password", json={"name": "eric", "password": "pass123"})
    response = client.get("/manager/weeks/2026-W29", headers={"Accept": "text/html"})
    assert response.status_code == 200
    assert b"Cooks" in response.data
    assert b"<details open" in response.data
