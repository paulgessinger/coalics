from coalics.models import CalendarSource, Event

from coalics.util import event_acceptor

def test_event_acceptor():
    
    checks = [
        ("ANYTHING", ".*", "", True),
        ("ANYTHING", ".*", "^ANY.*", False),
        ("OTHER", ".*", "^ANY.*", True),
        ("OTHER", ".*THING$", "^ANY.*", False),
        ("OTHERTHING", ".*THING$", "^ANY.*", True),
        ("ANYTHING", ".*THING$", "^ANY.*", False),
        ("SOME", ".*THING$", "^ANY.*", False),
        ("SOME", ".*THING$", "", False),
    ]

    for summary, pos, neg, res in checks:
        event = Event(summary=summary)
        src = CalendarSource(positive_pattern=pos, negative_pattern=neg)
        assert event_acceptor(src)(event) == res, (summary, pos, neg, res)
