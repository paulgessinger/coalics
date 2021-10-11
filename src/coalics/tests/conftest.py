import os
from pathlib import Path

import pytest
import icalendar as ics

import coalics
from coalics.models import CalendarSource, Calendar, User
import coalics.tasks as t


@pytest.fixture
def app():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["COALICS_CSRF_KEY"] = "abc"
    os.environ["SECRET_KEY"] = "abc"
    os.environ["REGISTER_ENABLED"] = "True"
    app = coalics.create_app()

    app.testing = True
    with app.app_context():
        coalics.db.create_all()
        # create fake data
        u = User(email="test@example.com", password="hallo")
        coalics.db.session.add(u)

        cal = Calendar(name="CERN Seminars", owner=u)

        with (Path(__file__).parent / "cern_seminars.ics").open() as fh:
            caldata = ics.Calendar.from_ical(fh.read())
        calsrc = CalendarSource(
            url="https://indico.cern.ch/export/categ/3249.ics?from=-31d", calendar=cal
        )
        t._update_source(caldata, calsrc)

        coalics.db.session.add(cal)
        coalics.db.session.add(calsrc)
        coalics.db.session.commit()

        yield app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client
