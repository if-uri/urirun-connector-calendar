# urirun-connector-calendar

`calendar://` — headless CalDAV/ICS calendar events. No GUI calendar app required.

Part of the [ifURI](https://github.com/if-uri) solution. Generated to satisfy a
capability the reasoner found blocked (no connector served the `calendar://` scheme).
Built to the URI-native connector checklist: **lazy imports** (imports icalendar/caldav
inside handlers, so the package imports even without them installed), **handlers never
raise** (every result is a urirun envelope), **queries run in-process**.

## Routes

| Route | Isolated | Description |
|-------|----------|-------------|
| `events/query/list` | no (read-only) | List events from a local `.ics` file **or** a CalDAV URL. |
| `event/command/create` | yes (**gated**) | Append a `VEVENT` to an `.ics` file. Reversible/append-only. |
| `ics/query/parse` | no | Parse an `.ics` string/file into structured events (uid, summary, dtstart, dtend). Pure, no network. |

## Install

```bash
pip install -e . --no-deps
# optional richer parsing / CalDAV:
pip install icalendar caldav
```

## Usage

```python
from urirun_connector_calendar import urirun_bindings
bindings = urirun_bindings()
```

Or via the URI scheme once served: `calendar://events/query/list?ics_path=/path/cal.ics`.

## License

Apache-2.0 · Author: Tom Sapletta
