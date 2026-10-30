from io import BytesIO

from taskassigner.extensions import db
from taskassigner.models import JobCode, TaskTemplate
from taskassigner.numbered_imports import apply_numbered_task_rows

from test_workflow_pages import _login_manager, _login_owner, app, client


def test_apply_numbered_task_rows_updates_csv_matches_and_creates_active_rows(app):
    with app.app_context():
        cooks = JobCode.query.one()
        existing = TaskTemplate.query.filter_by(title="Clean Grill").one()
        existing.master_list_number = 1
        existing.notes = "old"
        existing.active = False
        db.session.commit()

        result = apply_numbered_task_rows(
            [
                {"line": 2, "number": 1, "title": " clean   grill ", "notes": "new", "active": "true"},
                {"line": 3, "number": 2, "title": "New Task", "notes": "fresh"},
            ],
            [],
            selected_job_code=cooks.name,
            source_format="csv",
        )

        db.session.expire_all()
        assert result["created"] == 1
        assert result["updated"] == 1
        assert result["reviews"] == []
        assert existing.notes == "new"
        assert existing.active is True
        created = TaskTemplate.query.filter_by(master_list_number=2).one()
        assert created.active is True
        assert created.notes == "fresh"


def test_apply_numbered_task_rows_preserves_txt_match_fields_and_flags_mismatch(app):
    with app.app_context():
        cooks = JobCode.query.one()
        existing = TaskTemplate.query.filter_by(title="Clean Grill").one()
        existing.master_list_number = 1
        existing.notes = "keep"
        existing.active = False
        db.session.commit()

        result = apply_numbered_task_rows(
            [{"line": 2, "number": 1, "title": "Different title"}],
            [],
            selected_job_code=cooks.name,
            source_format="txt",
        )

        db.session.expire_all()
        assert result["created"] == 0
        assert result["updated"] == 0
        assert result["reviews"][0]["error"] == "number_title_mismatch"
        assert existing.title == "Clean Grill"
        assert existing.notes == "keep"
        assert existing.active is False


def test_apply_numbered_task_rows_requires_confirmation_for_legacy_match(app):
    with app.app_context():
        cooks = JobCode.query.one()
        result = apply_numbered_task_rows(
            [{"line": 2, "number": 9, "title": " stock   freezer "}],
            [],
            selected_job_code=cooks.name,
            source_format="txt",
        )

        assert result["created"] == 0
        assert result["reviews"][0]["error"] == "legacy_number_confirmation_required"
        assert TaskTemplate.query.filter_by(master_list_number=9).count() == 0


def test_manager_can_import_numbered_txt_and_export_combined_csv(client, app):
    _login_manager(client)

    imported = client.post(
        "/manager/imports/task-templates",
        data={"mode": "numbered_txt", "selected_job_code": "Cooks", "text": "1. New Imported\n2. New Task"},
        headers={"Accept": "application/json"},
    )
    assert imported.status_code == 200
    assert imported.json["created"] == 2

    exported = client.get("/manager/exports/task-templates.csv")
    assert exported.status_code == 200
    assert exported.mimetype == "text/csv"
    assert b"job_code,number,title,notes,active" in exported.data
    assert b"Cooks,1,New Imported" in exported.data


def test_manager_can_import_combined_csv_and_export_job_code_txt(client, app):
    _login_manager(client)

    imported = client.post(
        "/manager/imports/task-templates",
        data={
            "mode": "numbered_csv",
            "text": "job_code,number,title,notes,active\nCooks,3,Combined Task,notes,false\nCooks,4,Active Combined,,true\n",
        },
        headers={"Accept": "application/json"},
    )
    assert imported.status_code == 200
    assert imported.json["created"] == 2

    exported = client.get("/manager/exports/task-templates.txt?job_code=Cooks")
    assert exported.status_code == 200
    assert b"3. Combined Task" not in exported.data
    assert b"4. Active Combined" in exported.data


def test_task_list_import_export_is_manager_only(client):
    _login_owner(client)

    assert client.get("/manager/exports/task-templates.csv").status_code == 403
    assert client.post(
        "/manager/imports/task-templates",
        data={"mode": "numbered_txt", "selected_job_code": "Cooks", "text": "1. Nope"},
        headers={"Accept": "application/json"},
    ).status_code == 403


def test_manager_can_confirm_legacy_number_candidate(client, app):
    _login_manager(client)
    with app.app_context():
        legacy = TaskTemplate.query.filter_by(title="Stock Freezer").one()
        task_id = legacy.id

    confirmed = client.post(
        "/manager/imports/task-templates/confirm-legacy",
        json={"task_id": task_id, "number": 7},
    )

    assert confirmed.status_code == 200
    with app.app_context():
        assert TaskTemplate.query.get(task_id).master_list_number == 7


def test_manager_task_page_exposes_numbered_import_and_export_controls(client):
    _login_manager(client)

    page = client.get("/manager/tasks", headers={"Accept": "text/html"})

    assert page.status_code == 200
    assert b"Numbered TXT" in page.data
    assert b"Download combined CSV" in page.data
    assert b"multipart/form-data" in page.data


def test_manager_can_import_uploaded_numbered_txt_file(client):
    _login_manager(client)

    response = client.post(
        "/manager/imports/task-templates",
        data={
            "mode": "numbered_txt",
            "selected_job_code": "Cooks",
            "file": (BytesIO(b"1. Uploaded Task"), "tasks.txt"),
        },
        content_type="multipart/form-data",
        headers={"Accept": "application/json"},
    )

    assert response.status_code == 200
    assert response.json["created"] == 1
