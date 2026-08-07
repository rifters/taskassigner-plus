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
        SESSION_TTL_HOURS = {"crew": 12, "shift_lead": 8, "manager": 8, "owner": 24}

    app = create_app(TestConfig)
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        manager = User(name="eric", role="manager")
        manager.set_password("pass123")
        db.session.add(manager)
        db.session.commit()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_sensitive_payload_is_not_logged_in_cleartext(client, caplog):
    caplog.clear()
    client.post(
        "/auth/login-password",
        json={"name": "eric", "password": "pass123", "new_pin": "9999"},
    )

    # We log dict objects as strings; verify redaction markers appear and cleartext secrets do not.
    logs = "\n".join(record.getMessage() for record in caplog.records)
    assert "[REDACTED]" in logs
    assert "pass123" not in logs
    assert "9999" not in logs
