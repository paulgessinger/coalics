import icalendar as ics
from flask import url_for

from coalics.models import CalendarSource, Event, Calendar


def test_ics_get(client):
    cal = Calendar.query.get(1)
    calsrc = CalendarSource.query.get(1)
    assert calsrc.url == "https://indico.cern.ch/export/categ/3249.ics?from=-31d"

    events = Event.query.filter(Event.source == calsrc).all()
    assert len(events) == 8

    client.get("/")  # this makes a request context
    r = client.get(
        url_for("calendar_ics", slug=cal.slug, name=cal.name, **{"from": "-31d"})
    )

    ical = ics.Calendar.from_ical(r.data.decode("utf-8"))
    assert len([i for i in ical.subcomponents if i.name == "VEVENT"]) == 8
