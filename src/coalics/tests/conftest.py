import os

import pytest

import coalics
from coalics.models import CalendarSource, Calendar, User


@pytest.fixture
def app():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["EMAIL_SALT"] = "$2b$12$xePh6QJ0c06AcqCtGuWNbO"
    app = coalics.create_app()
    app.secret_key = "hurz"

    app.testing = True
    with app.app_context():
        coalics.db.create_all()
        # create fake data
        u = User(email="test@example.com", password="hallo")
        coalics.db.session.add(u)

        cal = Calendar(name="TestCal", owner=u)
        calsrc = CalendarSource(url="http://example.org/feed.ics", calendar=cal)

        coalics.db.session.add(cal)
        coalics.db.session.add(calsrc)
        coalics.db.session.commit()

        yield app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client
