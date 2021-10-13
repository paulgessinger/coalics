import pytest
import icalendar as ics
from pathlib import Path

from coalics.models import CalendarSource, Event

test_dir = Path(__file__).parent


@pytest.fixture
def ics_str():
    return (test_dir / "event_fixtures.ics").read_text()


@pytest.fixture
def ics_str_alt():
    return (test_dir / "fixture2.ics").read_text()


@pytest.fixture
def ics_str3():
    return (test_dir / "event_fixtures3.ics").read_text()


@pytest.fixture
def defsrc(app):
    with app.app_context():
        srcs = CalendarSource.query.get(1)
    return srcs


def test_update_events_import(ics_str, app, defsrc):

    import coalics.tasks as t

    cal = ics.Calendar.from_ical(ics_str)

    exp_uids = [e.get("uid") for e in cal.subcomponents if e.name == "VEVENT"]

    t._update_source(cal, defsrc)

    events = Event.query.all()

    act_uids = [e.uid for e in events]

    assert len(events) == 5, "Not all events found"
    assert act_uids == exp_uids, "Not all events found"


def test_update_events_delete(ics_str, app, defsrc):
    import coalics.tasks as t

    cal = ics.Calendar.from_ical(ics_str)
    t._update_source(cal, defsrc)

    deleted_uid = cal.subcomponents[2].get("uid")

    with app.app_context():
        assert Event.query.filter_by(source=defsrc).count() == 5
        assert Event.query.filter_by(
            uid=deleted_uid
        ).first(), "Deleted UID to test does not exist prior to update"

    del cal.subcomponents[2]

    # again with modified cal
    t._update_source(cal, defsrc)

    assert Event.query.filter_by(source=defsrc).count() == 4
    assert not Event.query.filter_by(
        uid=deleted_uid
    ).first(), "Deleted UID to test exists after update"


def test_update_events_update(ics_str, app, defsrc):
    import coalics.tasks as t

    cal = ics.Calendar.from_ical(ics_str)
    premod = cal.subcomponents[2]
    cal.subcomponents[2]["SUMMARY"] = ics.prop.vText("ORIGINAL")

    t._update_source(cal, defsrc)

    assert Event.query.filter_by(source=defsrc).count() == 5
    assert Event.query.filter_by(uid=premod.get("uid")).one().summary == "ORIGINAL"

    cal.subcomponents[2]["SUMMARY"] = ics.prop.vText("MODIFIED")

    t._update_source(cal, defsrc)

    assert Event.query.filter_by(source=defsrc).count() == 5
    assert Event.query.filter_by(uid=premod.get("uid")).one().summary == "MODIFIED"


def test_update_events_pattern(ics_str_alt, app, defsrc):
    import coalics.tasks as t

    cal = ics.Calendar.from_ical(ics_str_alt)

    defsrc.positive_pattern = ".*W'.*"

    t._update_source(cal, defsrc)

    assert Event.query.filter_by(source=defsrc).count() == 15


def test_update_events_scenario3(ics_str3, app, defsrc):
    import coalics.tasks as t

    cal = ics.Calendar.from_ical(ics_str3)

    exp_uids = [e.get("uid") for e in cal.subcomponents if e.name == "VEVENT"]

    t._update_source(cal, defsrc)

    events = Event.query.all()

    act_uids = [e.uid for e in events]

    assert len(events) == 177, "Not all events found"
    assert act_uids == exp_uids, "Not all events found"
