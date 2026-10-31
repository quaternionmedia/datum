# The wire

**Runtime-bound** — needs an MQTT broker.

`README.md` proves the envelope and the contract in-process. This file proves
them over a real broker, and it is collected only when one is reachable.

```
docker run -d --rm -p 11883:1883 eclipse-mosquitto:2
uv run pytest
```

Without a broker, pytest prints why this file was skipped and runs everything
else. A silently skipped test is worse than an absent one.

Any MQTT broker works. Mosquitto is used because it is the reference
implementation of the seam protocol, not because anything here needs it — a
harness that would fail against EMQX, NanoMQ or VerneMQ is a defective
harness, not a configuration detail.

---

## What an in-process fixture cannot tell you

The fixture in `README.md` models publish and subscribe faithfully enough to
demonstrate a toggle. It cannot catch the failures that live between the
constant and the socket: a topic that is right in Python and wrong in the
firmware, a payload that is valid JSON in the wrong encoding, a last-will that
never fires, or a retained flag on the wrong topic.

That last one deserves its own section, because it is the one that surprised
this harness on its first run.

## Retention is only observable if you arrive late

MQTT clears the retain flag when it delivers a message to a subscription that
was already established. A subscriber watching when the publish happens sees
`retain=0` **even for a message the broker retained**. The flag means "this is
a stored message being replayed to you because you just arrived," not "this
message was published with retention."

So retention cannot be checked by the subscriber that watched it happen. It
has to be checked by one that joins afterwards — which is exactly the consumer
the retention rules exist for. The harness does both.

    >>> import json
    >>> from datum import Announce, Event, vectors_dir
    >>> from datum.harness import roundtrip

A captured firmware event. This one is a stand-in written against the topic
contract; it becomes a genuinely captured payload when firmware exists at
WP-3, and the file is the only thing that changes.

    >>> raw = json.loads(
    ...     (vectors_dir() / "captured" / "t1-core-single-press.json").read_text()
    ... )
    >>> event = Event.model_validate(raw)
    >>> announce = Announce(src=event.src, caps=event.caps, hw="t1-core-r0", fw="0.1.0")
    >>> event.src
    'datum/lab/jig'

Publish the announce, the availability and the event, then read them back:

    >>> result = roundtrip(event, announce=announce)
    >>> print(result.verdict())
    round-trip ok

That single line covers the whole contract. Spelled out:

**The event arrived on the documented topic, and arrived unchanged.**

    >>> result.received.topic
    'datum/lab/jig/event'
    >>> result.received.payload == event.wire_json()
    True

The payload is compared byte for byte, not field by field. A comparison that
re-parses both sides would pass on an encoding change that breaks every
consumer that does not re-parse.

**It validates against the emitted schema after a round trip through the
broker** — checked inside `roundtrip`, which is why `verdict()` above is
`round-trip ok` rather than a delivery confirmation.

**Announce and availability reach a subscriber that arrives afterwards, and
carry the retain flag when they do.**

    >>> result.late_announce.retained
    True
    >>> result.late_status.payload
    'online'

This is the dashboard-restart case. A consumer that subscribes hours after the
device booted still learns the device exists and what axes it can ever emit,
without waiting for someone to walk over and press it.

**The event does not reach that late subscriber at all.**

    >>> result.late_event is None
    True

This is the one that bites. Retain an event and every new subscriber is
handed a press that never happened — for a toggle, the lamp flips every time a
dashboard reloads. The harness asserts the absence, because the absence is the
contract.

## Milestone assertion 2

> A firmware-emitted event, captured in a host-side test, round-trips the
> documented topic contract and validates against that schema.

    >>> result.ok
    True

Green, with one honest qualification: the captured event is a stand-in until
WP-3 exists. Everything else in this file — the topic, the encoding, the
retention rules, the schema validation — is being exercised against a real
broker over a real socket.

## Cleaning up

The harness clears the retained topics it sets, at the start of a run and
again at the end, so a run observes its own publishes rather than a previous
one's. Retained state outliving a test is a slow way to make a suite lie.
