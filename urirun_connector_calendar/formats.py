# Author: Tom Sapletta · Part of the ifURI solution — IFURI-035 shared format source.
"""Wspólne źródło formatów kalendarzowych (ics/RRULE/Google-CSV) — quirki platform w JEDNYM miejscu.

cron:// = scheduler systemowy (dopasowanie pól, ekspansja wystąpień). calendar:// = formaty platform.
cron:// **deleguje** budowanie ics/csv/rrule tutaj, żeby quirki (BYDAY, INTERVAL, escaping, CRLF) nie
były zduplikowane. Funkcje są CZYSTE (bez I/O, bez schedulera) — scheduler zostaje po stronie cron.
"""
from __future__ import annotations

from typing import Any

_CRON_DOW_TO_ICS = {"0": "SU", "1": "MO", "2": "TU", "3": "WE", "4": "TH", "5": "FR", "6": "SA", "7": "SU"}


def cron_fields_to_rrule(fields: list[str]) -> str:
    """5-pole cron → iCalendar RRULE (best-effort: weekly/hourly/daily)."""
    mn, hr, dom, mon, dow = fields
    if dow != "*" and dom == "*":
        by = ",".join(_CRON_DOW_TO_ICS.get(d, "MO") for d in dow.split(",") if d in _CRON_DOW_TO_ICS)
        return f"RRULE:FREQ=WEEKLY;BYDAY={by or 'MO'}"
    if hr == "*":
        return "RRULE:FREQ=HOURLY"
    return "RRULE:FREQ=DAILY"


def build_ics(entries: list[dict], mode: str, occ_fn) -> str:
    """Zbuduj dokument iCalendar z wpisów. ``occ_fn(entry, days, cap)`` = ekspansja wystąpień
    (dostarczana przez scheduler cron — format nie zna schedulera). mode: 'rrule'|'events'."""
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//ifURI//urirun-connector-cron//PL", "CALSCALE:GREGORIAN"]
    for e in entries:
        if len(e.get("fields") or []) != 5:
            continue
        uid_base = f"cron-{e.get('id') or abs(hash(e['schedule']))}@urirun"
        summary = (e.get("label") or e.get("command", "")[:60]).replace("\n", " ")
        if mode == "events":
            for i, t in enumerate(occ_fn(e, 30, 30)):
                lines += ["BEGIN:VEVENT", f"UID:{uid_base}-{i}", f"DTSTART:{t.strftime('%Y%m%dT%H%M%S')}",
                          "DURATION:PT1M", f"SUMMARY:{summary}",
                          f"DESCRIPTION:{e.get('command','')}", "END:VEVENT"]
        else:
            occ = occ_fn(e, 2, 1)
            if not occ:
                continue
            lines += ["BEGIN:VEVENT", f"UID:{uid_base}", f"DTSTART:{occ[0].strftime('%Y%m%dT%H%M%S')}",
                      "DURATION:PT1M", f"SUMMARY:{summary}", f"DESCRIPTION:{e.get('command','')}",
                      cron_fields_to_rrule(e["fields"]), "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def build_google_csv(occurrences: list[dict]) -> str:
    """Wystąpienia → Google Calendar CSV (Subject,Start Date,Start Time,End Date,End Time,Description)."""
    rows = ["Subject,Start Date,Start Time,End Date,End Time,Description"]
    for o in occurrences:
        d = o["date"]
        rows.append(f"\"{o['label']}\",{d},{o['time']},{d},{o['time']},\"cron {o.get('id') or ''}\"")
    return "\n".join(rows) + "\n"
