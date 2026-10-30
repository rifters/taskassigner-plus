from taskassigner.extensions import db
from taskassigner.models import AssignmentItem, AssignmentRun, TaskExclusion, TaskTemplate, User

from test_workflow_pages import _login_manager, app, client


def test_generation_avoids_only_immediately_previous_posted_pair(client, app):
    _login_manager(client)
    response = client.post("/api/weeks/2026-W30/generate")
    assert response.status_code == 200

    with app.app_context():
        run = AssignmentRun.query.filter_by(week_key="2026-W30").one()
        previous = AssignmentRun.query.filter_by(week_key="2026-W28").one()
        old_pairs = {
            (item.task_template_id, item.assignee_user_id)
            for item in AssignmentItem.query.filter_by(run_id=previous.id).all()
        }
        new_pairs = {
            (item.task_template_id, item.assignee_user_id)
            for item in AssignmentItem.query.filter_by(run_id=run.id).all()
        }
        assert new_pairs
        assert not old_pairs & new_pairs


def test_generation_rechecks_exclusions_for_each_task_in_pool(client, app, monkeypatch):
    _login_manager(client)
    monkeypatch.setattr(
        "taskassigner.routes.assignments.random.shuffle",
        lambda values: values.sort(key=lambda value: getattr(value, "title", getattr(value, "name", "")), reverse=True),
    )
    with app.app_context():
        alice = User.query.filter_by(name="alice").one()
        clean_grill = TaskTemplate.query.filter_by(title="Clean Grill").one()
        db.session.add(TaskExclusion(user_id=alice.id, task_template_id=clean_grill.id))
        previous = AssignmentRun.query.filter_by(week_key="2026-W28").one()
        AssignmentItem.query.filter_by(run_id=previous.id, task_template_id=clean_grill.id).delete(
            synchronize_session=False
        )
        db.session.commit()

    assert client.post("/api/weeks/2026-W30/generate").status_code == 200
    with app.app_context():
        run = AssignmentRun.query.filter_by(week_key="2026-W30").one()
        item = AssignmentItem.query.filter_by(run_id=run.id, task_template_id=1).one()
        alice = User.query.filter_by(name="alice").one()
        assert item.assignee_user_id != alice.id


def test_regeneration_requires_confirmation_and_replaces_items(client, app):
    _login_manager(client)
    first = client.post("/api/weeks/2026-W30/generate")
    assert first.status_code == 200
    run_id = first.get_json()["run_id"]

    assert client.post("/api/weeks/2026-W30/regenerate", json={}).status_code == 400
    before = client.get("/api/weeks/2026-W30/draft").get_json()["items"]
    response = client.post("/api/weeks/2026-W30/regenerate", json={"confirm": True})
    assert response.status_code == 200
    assert response.get_json()["run_id"] == run_id
    with app.app_context():
        assert AssignmentRun.query.filter_by(week_key="2026-W30").count() == 1
        after = [
            item.id
            for item in AssignmentItem.query.filter_by(run_id=run_id).order_by(AssignmentItem.id).all()
        ]
    assert len(after) == len(before)


def test_posted_week_cannot_be_regenerated_and_print_is_grouped(client, app):
    _login_manager(client)
    client.post("/api/weeks/2026-W30/generate")
    with app.app_context():
        task = TaskTemplate.query.filter_by(title="Clean Grill").one()
        task.master_list_number = 7
        db.session.commit()

    assert client.post("/api/weeks/2026-W30/post").status_code == 200
    assert client.post("/api/weeks/2026-W30/regenerate", json={"confirm": True}).status_code == 404
    printed = client.get("/manager/weeks/2026-W30/print", headers={"Accept": "text/html"})
    assert printed.status_code == 200
    assert b"TaskAssigner+ paper trail" in printed.data
    assert b"#7" in printed.data
    assert b"Signature:" in printed.data
    assert b"window.print" in printed.data


def test_task_number_is_optional_and_serialized(client, app):
    _login_manager(client)
    with app.app_context():
        task = TaskTemplate.query.filter_by(title="Clean Grill").one()
        assert task.master_list_number is None
    response = client.get("/manager/tasks", headers={"Accept": "application/json"})
    assert response.status_code == 200
    row = next(item for item in response.get_json() if item["title"] == "Clean Grill")
    assert row["master_list_number"] is None
