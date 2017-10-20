import requests
import icalendar as ics

from coalics import db, app, q
from coalics.models import CalendarSource, Event
from coalics.util import wait_for

def update_sources():
    calendar_sources = CalendarSource.query.all()
    app.logger.info("Update {} sources".format(len(calendar_sources)))
    tasks = []
    for source in calendar_sources:
        t = q.enqueue(_update_source, source)
        tasks.append(t)

    # wait_for(tasks, timeout=3)
    app.logger.debug("done waiting")

def build_ics(source):
    r = requests.get(source.url)
    cal = ics.Calendar.from_ical(r.text)
    return cal

def _update_source(source):
    app.logger.debug("Updating source url {}".format(source.url))
    return update_source(build_ics(source), source)

class ICSEvent():
    def __init__(self, event):
        self.uid = event.decoded("UID")
        self.summary = event.decoded("SUMMARY")
        self.description = event.decoded("DESCRIPTION")
        self.url = event.decoded("URL")
        self.location = event.decoded("LOCATION")
        self.start = event.decoded("DTSTART")
        self.end = event.decoded("DTEND")
        self.timestamp = event.decoded("DTSTAMP")

    def populate_obj(self, obj):
        for k, v in self.__dict__.items():
            setattr(obj, k, v)


def update_source(cal, source):

    upstream_events = [ICSEvent(e) for e in cal.subcomponents]

    # print("ICS", cal)
    first_event = min(upstream_events, key=lambda e: e.start)
    upstream_uids = [e.uid for e in upstream_events]

    
    matching_stored_events = Event.query.filter(Event.start >= first_event.start, Event.source == source).all()
                      
    for event in matching_stored_events:
        if not event.uid in upstream_uids:
            # was deleted upstream
            db.session.delete(event)
                      

    for event in upstream_events:
        # # print(event["SUMMARY"])

        dbevent = Event.query.filter_by(uid=event.uid).one_or_none()
        if not dbevent:
            # this is a new one
            dbevent = Event(**event.__dict__)
            dbevent.source = source
            db.session.add(dbevent)
        else:
            event.populate_obj(dbevent)

    db.session.commit()

    return True
