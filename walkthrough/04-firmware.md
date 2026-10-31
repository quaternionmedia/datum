# The firmware

**Hermetic.**

`firmware/t1-core.yaml` is stock ESPHome on an ESP32-C6. It reads four dry
contacts and publishes the envelope on the topics `walkthrough/03-topic-contract.md`
documents. This page is the seam between that YAML and the Python: every
string the firmware puts on the wire is checked here against the constant a
consumer compiles against.

    >>> from datum import Action, Announce, Event, SCHEMA_VERSION
    >>> from datum import announce_topic, event_topic, status_topic
    >>> from datum.firmware import config_text, contact_pins, emitted_actions
    >>> from datum.firmware import RESERVED_GPIO, substitution

`walkthrough/08-wire.md` proves the contract over a real broker, and names the one
failure that harness cannot reach: a topic that is right in the constant and
wrong in the firmware. A broker sees only what it is sent. Catching that needs
the firmware and the constant compared directly, which is what follows.

## The topics derive from the contract

The firmware never spells a topic out. It writes `${src}` and the suffix, and
the suffix has to be the one the contract generates:

    >>> config = config_text()
    >>> event_topic("${src}") in config
    True
    >>> announce_topic("${src}") in config
    True
    >>> status_topic("${src}") in config
    True

The availability topic is declared twice — once as the birth message, once as
the last will — so asking whether it *appears* passes even when one of the two
has drifted. Each is checked:

    >>> from datum.firmware import declared_topics
    >>> declared_topics()
    ['${src}/status', '${src}/status']
    >>> all(topic == status_topic("${src}") for topic in declared_topics())
    True

Rename a suffix in `datum.topics` and this page fails until the firmware is
renamed with it. That is the entire point of the check: the two cannot drift
without the build going red.

## The payload is byte-identical

The firmware fills a `printf` template inside a C++ raw string literal rather
than building JSON through a library, so the bytes are fixed by this file
rather than by a serializer's spacing and key order.

Filling the same template in Python has to produce exactly what Pydantic
produces:

    >>> src = substitution("src")
    >>> event = Event(src=src, seq=1, caps=["press"], action="single", ch=0)
    >>> substitution("event_format") % (src, 1, "single", 0) == event.wire_json()
    True

    >>> announce = Announce(
    ...     src=src, caps=["press"], hw=substitution("hw"), fw=substitution("fw")
    ... )
    >>> substitution("announce_format") % (
    ...     SCHEMA_VERSION, src, substitution("hw"), substitution("fw")
    ... ) == announce.wire_json()
    True

`walkthrough/08-wire.md` compares the round-tripped payload byte for byte rather than
field by field, because a comparison that re-parses both sides passes on an
encoding change that breaks every consumer that does not re-parse. The same
argument applies one layer earlier, here, where the bytes are written.

The version the firmware announces is the schema's, not its own:

    >>> substitution("schema_version") == SCHEMA_VERSION
    True

## The gestures are envelope actions

`Action` is a closed set. Every gesture the per-channel package emits has to be
a member of it, so a firmware that grew a `quadruple` would fail here rather
than at a consumer:

    >>> {Action(name).value for name in emitted_actions()} == emitted_actions()
    True
    >>> sorted(emitted_actions())
    ['double', 'hold', 'release', 'single', 'triple']

`press` is a member and is not emitted. It is the *capability* — what the
module advertises it can ever report — and it is what `caps` carries in both
payloads above. A gesture is what happened; a capability is what could.

A hold and its release are two events, not one:

    >>> "hold" in emitted_actions() and "release" in emitted_actions()
    True

## No contact lands on a spoken-for pin

    >>> contact_pins()
    {0: 2, 1: 3, 2: 10, 3: 11}

    >>> {ch: RESERVED_GPIO[pin] for ch, pin in contact_pins().items() if pin in RESERVED_GPIO}
    {}

The indicator is the deliberate exception. It sits on GPIO8, which *is* a
strapping pin, and is where the DevKitC-1 puts its own addressable LED — an
output driven after boot reads no strap:

    >>> substitution("indicator_pin")
    'GPIO8'
    >>> RESERVED_GPIO[8]
    'strapping'

## What this page does not prove

It does not prove the configuration compiles. Nothing here runs ESPHome; the
build in `.github/workflows/firmware.yml` does that, and a compile failure
fails the branch.

It does not prove a real contact produces a real event. That is milestone
assertion 2, and it stays qualified — `schema/vectors/captured/` holds a
stand-in written against the contract until a flashed device replaces it. The
checks above are what make that substitution safe to reason about: the bytes
this firmware would send are the bytes the stand-in already carries.
