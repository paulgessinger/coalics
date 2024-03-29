from coalics.models import CalendarSource, Event

from coalics.util import event_acceptor, string_shorten, parse_from

from datetime import timedelta
import pytest


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


def test_string_shorten():

    assert string_shorten(100 * "a", 10, "x") == 4 * "a" + "x" + 5 * "a"
    assert len(string_shorten(100 * "a", 10, "x")) == 10

    assert string_shorten(100 * "a", 11, "x") == 4 * "a" + "x" + 6 * "a"
    assert len(string_shorten(100 * "a", 11, "x")) == 11

    assert string_shorten(100 * "a", 11, 2 * "x") == 4 * "a" + 2 * "x" + 5 * "a"
    assert len(string_shorten(100 * "a", 11, 2 * "x")) == 11

    assert string_shorten(100 * "a", 11, 3 * "x") == 3 * "a" + 3 * "x" + 5 * "a"
    assert len(string_shorten(100 * "a", 11, 3 * "x")) == 11

    assert string_shorten(10 * "a", 10, 3 * "x") == 10 * "a"
    assert string_shorten(11 * "a", 10, 3 * "x") == 11 * "a"
    assert string_shorten(12 * "a", 10, 3 * "x") == 12 * "a"
    assert string_shorten(13 * "a", 10, 3 * "x") == 13 * "a"
    assert string_shorten(14 * "a", 10, 3 * "x") == 3 * "a" + 3 * "x" + 4 * "a"


def test_parse_from():

    assert parse_from("-31d") == timedelta(days=-31)
    assert parse_from("31d") == timedelta(days=31)
    assert parse_from("-14d") == timedelta(days=-14)
    assert parse_from("14d") == timedelta(days=14)
    assert parse_from("-24h") == timedelta(hours=-24)
    assert parse_from("24h") == timedelta(hours=24)

    with pytest.raises(ValueError):
        parse_from("abc")
    with pytest.raises(ValueError):
        parse_from("-14c")
