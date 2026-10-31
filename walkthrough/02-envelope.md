# The envelope

**Hermetic.**

The versioned payload every transport carries. Executable under
`uv run pytest`.

    >>> from datum import Action, Color, Contact, Event, SCHEMA_VERSION
    >>> SCHEMA_VERSION
    '1.0.0'

## Always-present fields

Five. `src` is the stable identity **and** the topic path, so a subscriber
needs no lookup table to know which physical object moved. `seq` is monotonic,
for loss and replay detection. `caps` lists everything the module can ever
emit, so a consumer can render an interface before seeing a rich event.

    >>> event = Event(
    ...     src="datum/kitchen/north", seq=1, caps=["press"], action="single"
    ... )
    >>> event.action.value
    'single'
    >>> print(event.wire_json())
    {"src":"datum/kitchen/north","seq":1,"caps":["press"],"action":"single","ch":0}

Optional axes are **absent when unused, never null**. A null claims the module
has a level whose value is unknown; absence says it carries none, which is what
a consumer branching on `caps` acts on.

    >>> sorted(event.wire())
    ['action', 'caps', 'ch', 'seq', 'src']

A module populating every axis carries the same five and four more — same
envelope, same consumer, more fields:

    >>> full = Event(
    ...     src="datum/bench/puck", seq=2048,
    ...     caps=["press", "level", "vec", "color", "batt"],
    ...     action=Action.TRIPLE, ch=2,
    ...     level=1.0, vec=(0.1, -0.4, 0.9),
    ...     color=Color(h=359.9, s=0.0), batt=87,
    ... )
    >>> sorted(full.wire())
    ['action', 'batt', 'caps', 'ch', 'color', 'level', 'seq', 'src', 'vec']
    >>> full.vec
    (0.1, -0.4, 0.9)
    >>> full.color.h
    359.9

## Where the compatibility guarantee lives

One line of model configuration, `extra="ignore"`, set explicitly rather than
inherited from a default.

It has to survive the trip out of Python: a consumer in another language holds
the emitted JSON Schema and nothing else.

    >>> from datum import announce_json_schema, closed_objects, event_json_schema
    >>> schema = event_json_schema()
    >>> sorted(schema["required"])
    ['action', 'caps', 'seq', 'src']

`additionalProperties: false` is absent, and its absence is the rule reaching
the artifact. Present, it would make every consumer written today reject
tomorrow's modules.

A nested object closed by a serialization default breaks the guarantee as
completely and less visibly, so both emitted schemas are checked all the way
down:

    >>> closed_objects(schema)
    []
    >>> closed_objects(announce_json_schema())
    []

The event schema has nested definitions for `Action` and `Color`, so that check
has something to find.

Additive-only schema evolution is a project non-negotiable (`AGENTS.md`) and a
decision with alternatives:
`governance/qm/adr/DRAFT-event-envelope-is-the-seam.md`.

## Announce

Published once on connect, retained, before any event, so a consumer arriving
late knows what the device is without waiting for a press.

    >>> import json
    >>> button = Contact("datum/kitchen/north")
    >>> print(json.dumps(button.announce().wire(), indent=2))
    {
      "schema_version": "1.0.0",
      "src": "datum/kitchen/north",
      "caps": [
        "press"
      ],
      "hw": "t1-core-r0",
      "fw": "0.1.0"
    }

The schema version travels with every announce, so a consumer identifies the
envelope generation without inferring it from which fields are present.
