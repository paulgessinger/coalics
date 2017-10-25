import requests
import icalendar as ics
import time

from coalics import db, app, q
from coalics.models import CalendarSource, Event
from coalics.util import wait_for, event_acceptor, timeout, TimeoutException

def update_sources():
    calendar_sources = CalendarSource.query.all()
    app.logger.info("Update {} sources".format(len(calendar_sources)))
    tasks = []
    for source in calendar_sources:
        t = q.enqueue(update_source, source)
        tasks.append(t)


def build_ics(source):
    r = requests.get(source.url)
    cal = ics.Calendar.from_ical(r.text)
    return cal

def update_source_id(id):
    return update_source(CalendarSource.query.get(id))

def update_source(source):

    # we might have to attach
    # state = inspect(source)
    # if state.detached:
        # db.session.add(source)

    app.logger.debug("Updating source url {}".format(source.url))
    res = _update_source(build_ics(source), source)

    app.logger.debug("Source now has {} events".format(source.events.count()))
    return res

class ICSEvent():
    def __init__(self, event):
        self.uid = event.get("UID")
        self.summary = event.get("SUMMARY")
        self.description = event.get("DESCRIPTION")
        self.url = event.get("URL")
        self.location = event.get("LOCATION")
        self.start = event.decoded("DTSTART")
        self.end = event.decoded("DTEND")
        self.timestamp = event.decoded("DTSTAMP")

    def populate_obj(self, obj):
        for k, v in self.__dict__.items():
            setattr(obj, k, v)


def _update_source(cal, source):

    upstream_events = [ICSEvent(e) for e in cal.subcomponents]

    first_event = min(upstream_events, key=lambda e: e.start)
    upstream_uids = [e.uid for e in upstream_events]

    
    matching_stored_events = Event.query.filter(Event.start >= first_event.start, Event.source == source).all()
                      
    for event in matching_stored_events:
        if not event.uid in upstream_uids:
            # was deleted upstream
            db.session.delete(event)
                      
    accept_event = event_acceptor(source, to=app.config["REGEX_TIMEOUT"])

    try:
        for event in upstream_events:
            dbevent = Event.query.filter_by(uid=event.uid).one_or_none()
            if not dbevent:
                # this is a new one
                if accept_event(event):
                    dbevent = Event(**event.__dict__)
                    dbevent.source = source
                    db.session.add(dbevent)
            else:
                # this one exists
                # check if event is still accepted by filters
                if accept_event(event):
                    # yes: update
                    event.populate_obj(dbevent)
                else:
                    # no: remove it
                    db.session.delete(dbevent)
        db.session.commit()
    except TimeoutException:
        app.logger.error("Timeout on regex execution. Discontinue event checking for this one")
        db.session.rollback()
        db.session.close()

        

    return True
