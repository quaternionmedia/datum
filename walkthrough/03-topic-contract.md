# The topic contract

**Hermetic.**

Any subscriber can implement this. Home Assistant's MQTT Discovery is a
convenience layered over it, never the contract itself. Executable under
`uv run pytest`.

| Topic | Retained | Carries |
|---|---|---|
| `<src>/event` | no | one `Event` |
| `<src>/announce` | yes | one `Announce` |
| `<src>/status` | yes | `online` / `offline` |
| `<src>/detained` | no | one `Event` that was suppressed |
| `<src>/detent` | yes | `armed` / `detained` |

    >>> from datum import announce_topic, event_topic, status_topic
    >>> event_topic("datum/kitchen/north")
    'datum/kitchen/north/event'
    >>> announce_topic("datum/kitchen/north")
    'datum/kitchen/north/announce'
    >>> status_topic("datum/kitchen/north")
    'datum/kitchen/north/status'

Retention is a term of this contract rather than a broker setting a deployment
chooses.

## Announce and status are retained

A subscriber arriving after the device booted still learns that the device
exists and what it can emit.

    >>> from datum import Bus, Contact
    >>> bus = Bus()
    >>> button = Contact("datum/kitchen/north")
    >>> button.attach(bus)

    >>> seen = []
    >>> bus.subscribe(announce_topic(button.src), seen.append)
    >>> len(seen)
    1

The subscription is made after `attach`, and still receives the announce.

## Events are not retained

An event is a moment, not a state. A retained press is redelivered to every new
subscriber, so a toggle would flip on every dashboard reload.

    >>> _ = button.press()
    >>> late = []
    >>> bus.subscribe(event_topic(button.src), late.append)
    >>> late
    []

A subscriber that arrives after a press receives nothing.

`walkthrough/08-wire.md` re-runs this against a real broker, where the retain *flag*
behaves in a way an in-process fixture does not model.

**No record covers these retention terms.** The envelope and detention records
do not reach them, so the reasoning behind this section lives only here and in
`HANDOFF.md`. Drafting one is open work.
