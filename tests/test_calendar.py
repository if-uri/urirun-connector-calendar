"""Tests for urirun-connector-calendar. Run from INSIDE this dir (namespace shadow otherwise)."""
from __future__ import annotations

SAMPLE_ICS = (
    "BEGIN:VCALENDAR\r\n"
    "VERSION:2.0\r\n"
    "PRODID:-//test//EN\r\n"
    "BEGIN:VEVENT\r\n"
    "UID:evt-1@test\r\n"
    "SUMMARY:Team standup\r\n"
    "DTSTART:20260706T090000Z\r\n"
    "DTEND:20260706T093000Z\r\n"
    "DESCRIPTION:Daily sync\r\n"
    "END:VEVENT\r\n"
    "END:VCALENDAR\r\n"
)


def test_connector_imports():
    import urirun_connector_calendar as pkg
    assert pkg.CONNECTOR_ID == "calendar"
    assert callable(pkg.urirun_bindings)
    assert callable(pkg.main)


def test_all_three_routes_exposed():
    from urirun_connector_calendar import urirun_bindings
    bindings = urirun_bindings()
    routes = set(bindings.get("routes", bindings).keys()) if isinstance(bindings, dict) else set()
    blob = str(bindings)
    for route in ("events/query/list", "event/command/create", "ics/query/parse"):
        assert route in routes or route in blob, f"missing route {route}"


def test_ics_parse_sample():
    from urirun_connector_calendar.core import ics_query_parse
    res = ics_query_parse(ics_text=SAMPLE_ICS)
    assert res.get("ok") is True or res.get("count") is not None, res
    events = res.get("events", [])
    assert len(events) == 1, res
    ev = events[0]
    assert ev["uid"] == "evt-1@test"
    assert ev["summary"] == "Team standup"
    assert ev["dtstart"].startswith("20260706T090000Z")


def test_handlers_return_fail_not_raise_on_empty():
    from urirun_connector_calendar.core import (
        events_query_list,
        event_command_create,
        ics_query_parse,
    )
    for res in (events_query_list(), event_command_create(), ics_query_parse()):
        assert isinstance(res, dict), res
        assert res.get("ok") is False or res.get("error"), res


def test_handlers_return_fail_on_bad_ics_path():
    from urirun_connector_calendar.core import events_query_list
    res = events_query_list(ics_path="/nonexistent/nope.ics")
    assert isinstance(res, dict)
    assert res.get("ok") is False or res.get("error"), res


def test_create_then_parse_roundtrip(tmp_path):
    from urirun_connector_calendar.core import event_command_create, ics_query_parse
    ics = tmp_path / "cal.ics"
    r1 = event_command_create(ics_path=str(ics), summary="Dentist",
                              start="20260710T140000Z", end="20260710T143000Z")
    assert r1.get("ok") is True, r1
    r2 = ics_query_parse(ics_path=str(ics))
    events = r2.get("events", [])
    assert any(e["summary"] == "Dentist" for e in events), r2
