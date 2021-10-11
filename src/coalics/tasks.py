import requests
import icalendar as ics
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from flask import current_app

from coalics import db
from coalics.models import CalendarSource, Event
from coalics.util import wait_for, event_acceptor, timeout, TimeoutException


def update_sources():
    update_ping_url = current_app.config["UPDATE_PING_URL"]

    if update_ping_url is not None:
        current_app.logger.info("Sending start ping to %s", update_ping_url)
        requests.get(f"{update_ping_url}/start")

    calendar_sources = CalendarSource.query.all()
    current_app.logger.info("Update {} sources".format(len(calendar_sources)))
    tasks = []
    start = datetime.now()

    # with ThreadPoolExecutor() as ex:
    #    results = ex.map(update_source, calendar_sources)
    for source in calendar_sources:
        update_source(source)

    #  wait_for(tasks)
    # db.session.close()

    end = datetime.now()

    delta = end - start
    current_app.logger.info(
        "Task update_sources successful after {}s".format(delta.seconds)
    )

    if update_ping_url is not None:
        current_app.logger.info("Sending ping to %s", update_ping_url)
        requests.get(update_ping_url)

    return True


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

    nevents_prev = Event.query.filter_by(source=source).count()
    current_app.logger.info("Updating source url {}".format(source.url))
    res = _update_source(build_ics(source), source)

    nevents = Event.query.filter_by(source=source).count()
    current_app.logger.info(
        "Source %s had %d events now has %d events", source.url, nevents_prev, nevents
    )
    return res


class ICSEvent:
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

    def __str__(self):
        return "Event('{}', {}, {})".format(self.summary, self.start, self.uid)


def _update_source(cal: ics.Calendar, source: CalendarSource):

    upstream_events = [ICSEvent(e) for e in cal.subcomponents if e.name == "VEVENT"]

    if len(upstream_events) == 0:
        current_app.logger.debug("Source did not contain any events")
        return True

    first_event = min(upstream_events, key=lambda e: e.start)
    upstream_uids = [e.uid for e in upstream_events]

    matching_stored_events = Event.query.filter(
        Event.start >= first_event.start, Event.source == source
    ).all()

    for event in matching_stored_events:
        if not event.uid in upstream_uids:
            current_app.logger.debug(
                "Event with uid %s was deleted upstream", event.uid
            )
            # was deleted upstream
            db.session.delete(event)

    accept_event = event_acceptor(source, to=current_app.config["REGEX_TIMEOUT"])

    try:
        for event in upstream_events:
            dbevent = Event.query.filter_by(uid=event.uid, source=source).one_or_none()
            if not dbevent:
                current_app.logger.debug("New event %s", event)
                # this is a new one
                if accept_event(event):
                    current_app.logger.debug("Event %s is accepted, adding", event)
                    dbevent = Event(**event.__dict__)
                    dbevent.source = source
                    db.session.add(dbevent)
            else:
                # this one exists
                # check if event is still accepted by filters
                if accept_event(event):
                    # yes: update
                    current_app.logger.debug(
                        "Event %s exists and is accepted, update", event
                    )
                    event.populate_obj(dbevent)
                else:
                    # no: remove it
                    current_app.logger.debug(
                        "Event %s exists and is NOT accepted, remove", event
                    )
                    db.session.delete(dbevent)
        current_app.logger.debug("Commit to database")
        db.session.commit()
    except TimeoutException:
        current_app.logger.error(
            "Timeout on regex execution. Discontinue event checking for this one"
        )
        db.session.rollback()
        # db.session.close()

    return True
