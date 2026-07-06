from __future__ import annotations
from datetime import datetime
from urirun_connector_calendar import formats as f

def test_cron_to_rrule():
    assert f.cron_fields_to_rrule(["0","8","*","*","*"])=="RRULE:FREQ=DAILY"
    assert f.cron_fields_to_rrule(["30","17","*","*","1,3,5"])=="RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR"
    assert f.cron_fields_to_rrule(["0","*","*","*","*"])=="RRULE:FREQ=HOURLY"

def test_build_ics_uses_occ_fn():
    occ=lambda e,d,c:[datetime(2026,7,1,8,0,0)]
    e={"id":"x","schedule":"0 8 * * *","fields":["0","8","*","*","*"],"command":"/b.sh","label":"B"}
    ics=f.build_ics([e],"rrule",occ)
    assert "BEGIN:VCALENDAR" in ics and "RRULE:FREQ=DAILY" in ics and "DESCRIPTION:/b.sh" in ics

def test_build_google_csv():
    csv=f.build_google_csv([{"date":"2026-07-01","time":"08:00","label":"B","id":"x"}])
    assert csv.startswith("Subject,Start Date") and "\"B\",2026-07-01,08:00" in csv
