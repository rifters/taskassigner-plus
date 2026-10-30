import pytest

from taskassigner.app import create_app
from taskassigner.extensions import db
from taskassigner.models import User


@pytest.fixture
def app():
    class TestConfig:
        SECRET_KEY = "test"
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        LOCKOUT_THRESHOLD = 5
        LOCKOUT_MINUTES = 15
        AUTH_RATE_LIMIT_PER_MINUTE = 5
        PASSWORD_RESET_TOKEN_MINUTES = 30

    app = create_app(TestConfig)
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        manager = User(name="eric", role="manager")
        manager.set_password("pass123")
        crew = User(name="alice", role="crew")
        crew.set_pin("1234")
        lead = User(name="lead", role="shift_lead")
        lead.set_password("pass123")
        owner = User(name="owner", role="owner")
        owner.set_password("pass123")
        db.session.add_all([manager, crew, lead, owner])
        db.session.commit()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_password_login_rejects_crew_role(client):
    res = client.post("/auth/login-password", json={"name": "alice", "password": "1234"})
    assert res.status_code in (401, 403)


def test_pin_login_accepts_crew_and_sets_ttl(client):
    res = client.post("/auth/login-pin", json={"name": "alice", "pin": "1234"})
    assert res.status_code == 200
    assert res.json["role"] == "crew"
    assert res.json["session_ttl_hours"] == 12


def test_password_login_sets_ttl_for_manager(client):
    res = client.post("/auth/login-password", json={"name": "eric", "password": "pass123"})
    assert res.status_code == 200
    assert res.json["session_ttl_hours"] == 8


def test_session_lifetime_policy_applies_by_role(app, client):
    crew_login = client.post("/auth/login-pin", json={"name": "alice", "pin": "1234"})
    assert crew_login.status_code == 200
    assert int(app.permanent_session_lifetime.total_seconds()) == 12 * 3600

    client.post("/auth/logout")
    manager_login = client.post("/auth/login-password", json={"name": "eric", "password": "pass123"})
    assert manager_login.status_code == 200
    assert int(app.permanent_session_lifetime.total_seconds()) == 8 * 3600


def test_pin_login_rejects_manager_role(client):
    res = client.post("/auth/login-pin", json={"name": "eric", "pin": "1234"})
    assert res.status_code in (401, 403)


def test_auth_rate_limit_triggers(client):
    # 5 failed attempts allowed in window, 6th attempt should rate-limit.
    for _ in range(5):
        res = client.post("/auth/login-password", json={"name": "eric", "password": "wrong"})
        assert res.status_code in (401, 429)

    res = client.post("/auth/login-password", json={"name": "eric", "password": "wrong"})
    assert res.status_code == 429
    assert res.json["error"] in ("rate_limited", "locked_out")


def test_password_reset_request_and_confirm_for_privileged_target(client):
    login = client.post("/auth/login-password", json={"name": "eric", "password": "pass123"})
    assert login.status_code == 200
    req = client.post(
        "/auth/reset-password/request",
        json={"actor_name": "not-eric", "target_name": "lead"},
    )
    assert req.status_code == 200
    token = req.json["reset_token"]

    confirm = client.post(
        "/auth/reset-password/confirm",
        json={"token": token, "new_password": "newpass456"},
    )
    assert confirm.status_code == 200

    login = client.post(
        "/auth/login-password",
        json={"name": "lead", "password": "newpass456"},
    )
    assert login.status_code == 200


def test_password_reset_request_rejects_crew_target(client):
    login = client.post("/auth/login-password", json={"name": "eric", "password": "pass123"})
    assert login.status_code == 200
    req = client.post(
        "/auth/reset-password/request",
        json={"actor_name": "not-eric", "target_name": "alice"},
    )
    assert req.status_code == 400
    assert req.json["error"] == "target_invalid"


def test_password_reset_token_cannot_be_reused(client):
    login = client.post("/auth/login-password", json={"name": "eric", "password": "pass123"})
    assert login.status_code == 200
    req = client.post(
        "/auth/reset-password/request",
        json={"actor_name": "not-eric", "target_name": "owner"},
    )
    token = req.json["reset_token"]

    ok1 = client.post(
        "/auth/reset-password/confirm",
        json={"token": token, "new_password": "ownernew1"},
    )
    assert ok1.status_code == 200

    again = client.post(
        "/auth/reset-password/confirm",
        json={"token": token, "new_password": "ownernew2"},
    )
    assert again.status_code == 400
    assert again.json["error"] == "token_already_used"


def test_password_reset_request_requires_authenticated_manager(client):
    anonymous = client.post(
        "/auth/reset-password/request",
        json={"actor_name": "eric", "target_name": "lead"},
    )
    assert anonymous.status_code in (401, 302)

    crew_login = client.post("/auth/login-pin", json={"name": "alice", "pin": "1234"})
    assert crew_login.status_code == 200
    crew_attempt = client.post(
        "/auth/reset-password/request",
        json={"actor_name": "eric", "target_name": "lead"},
    )
    assert crew_attempt.status_code == 403


def test_reset_pin_requires_authenticated_manager_and_ignores_actor_name(client):
    anonymous = client.post(
        "/auth/reset-pin",
        json={"actor_name": "eric", "target_name": "alice", "new_pin": "5678"},
    )
    assert anonymous.status_code in (401, 302)

    login = client.post("/auth/login-password", json={"name": "eric", "password": "pass123"})
    assert login.status_code == 200
    forged = client.post(
        "/auth/reset-pin",
        json={"actor_name": "not-eric", "target_name": "alice", "new_pin": "5678"},
    )
    assert forged.status_code == 200

    client.post("/auth/logout")
    crew_login = client.post("/auth/login-pin", json={"name": "alice", "pin": "5678"})
    assert crew_login.status_code == 200
