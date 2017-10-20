import pytest
import os
import coalics
import tempfile
from flask_migrate import upgrade
import icalendar as ics
# import pytz
# from tzlocal import get_localzone

from coalics.models import User, Calendar, CalendarSource, Event


@pytest.fixture
def ics_str():
    with open(os.path.dirname(__file__)+"/event_fixtures.ics", "rt") as f:
        ics = f.read()
    return ics

@pytest.fixture
def app():
    db_fd, db_fn = tempfile.mkstemp()
    print(db_fn)
    coalics.app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + db_fn
    # coalics.app.config["SQLALCHEMY_ECHO"] = True
    coalics.app.testing = True
    with coalics.app.app_context():
        upgrade()
        # create fake data
        u = User(username="test", email="test@example.com", password="hallo")
        coalics.db.session.add(u)

        cal = Calendar(name="TestCal", owner=u)
        calsrc = CalendarSource(url="http://example.org/feed.ics", calendar=cal)

        coalics.db.session.add(cal)
        coalics.db.session.add(calsrc)
        coalics.db.session.commit()

    yield coalics.app

@pytest.fixture
def defsrc(app):
    with app.app_context():
        srcs = CalendarSource.query.one()
    return srcs

def test_update_events_import(ics_str, app, defsrc):

    import coalics.tasks as t
    
    cal = ics.Calendar.from_ical(ics_str)

    exp_uids = [e.get("uid") for e in cal.subcomponents]

    t.update_source(cal, defsrc)

    with app.app_context():
        events = Event.query.all()
    
    act_uids = [e.uid for e in events]

    assert len(events) == 5, "Not all events found"
    assert act_uids == exp_uids, "Not all events found"


def test_update_events_delete(ics_str, app, defsrc):
    import coalics.tasks as t

    cal = ics.Calendar.from_ical(ics_str)
    t.update_source(cal, defsrc)
   
    deleted_uid = cal.subcomponents[2].get("uid")

    with app.app_context():
        assert Event.query.filter_by(source=defsrc).count() == 5
        assert Event.query.filter_by(uid=deleted_uid).first(), "Deleted UID to test does not exist prior to update"
    
    del cal.subcomponents[2]

    # again with modified cal
    t.update_source(cal, defsrc)
    
    
    with app.app_context():
        assert Event.query.filter_by(source=defsrc).count() == 4
        assert not Event.query.filter_by(uid=deleted_uid).first(), "Deleted UID to test exists after update"
    


def test_update_events_update(ics_str, app, defsrc):
    import coalics.tasks as t

    cal = ics.Calendar.from_ical(ics_str)
    premod = cal.subcomponents[2]
    cal.subcomponents[2]["SUMMARY"] = ics.prop.vText("ORIGINAL")

    t.update_source(cal, defsrc)
   
    with app.app_context():
        assert Event.query.filter_by(source=defsrc).count() == 5
        assert Event.query.filter_by(uid=premod.get("uid")).one().summary == "ORIGINAL"
    
    cal.subcomponents[2]["SUMMARY"] = ics.prop.vText("MODIFIED")

    t.update_source(cal, defsrc)
    
    with app.app_context():
        assert Event.query.filter_by(source=defsrc).count() == 5
        assert Event.query.filter_by(uid=premod.get("uid")).one().summary == "MODIFIED"
