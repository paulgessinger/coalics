import tempfile

import pytest

import coalics
from coalics.models import CalendarSource, Calendar, User


@pytest.fixture
def app():
    app = coalics.create_app()
    app.secret_key = "hurz"

    db_fd, db_fn = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fn
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
