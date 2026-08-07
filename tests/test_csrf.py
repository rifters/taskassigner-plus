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

    app = create_app(TestConfig)
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = True
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


def test_post_without_csrf_is_blocked(client):
    res = client.post("/auth/login-password", json={"name": "eric", "password": "pass123"})
    assert res.status_code == 400
