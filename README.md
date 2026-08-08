# A switch for the light that lost one

A smart bulb with no wall control. A lamp on a plug. A scene that only exists
inside an app. This project puts a physical switch back on all three, without
touching a line conductor and without a vendor account — and the switch you
install today keeps working when the thing it controls grows a colour axis in
2031.

The durable artifact is not the button. It is the **event envelope**: one
versioned payload that every transport carries, to which fields are only ever
added. A consumer written against it this afternoon is still correct against a
module built years later. That claim is the whole project, and this file
proves it rather than asserting it.

---

## This file is the test suite

Every `>>>` below is executed by `pytest`. There is no separate test
directory, no separate documentation, and no cookbook that drifts from the
code — a claim in this README that stops being true fails the build.

```
uv sync          # install
uv run pytest    # run this file
```

Nothing here is a hardware requirement. The demo below runs on a laptop with
no board attached, no broker installed and no bulb in the room.

**[`WIRE.md`](WIRE.md) is the other half**, and it is also a test suite. It
proves the same contract over a real MQTT broker, and is skipped with a stated
reason when there is no broker to prove it against:

```
docker run -d --rm -p 11883:1883 eclipse-mosquitto:2
uv run pytest
```

`Bus` below is an in-process fixture. It must never grow into an MQTT
implementation — the broker is an engine, and engines get selected, not
written.

---

## The demo: toggle a light that has no switch

You have a smart pendant in the kitchen. It has no physical control, so the
only way to turn it on is an app. Wire a dumb momentary switch — two wires
into a screw terminal — and give it an identity.

    >>> from tessera import Bus, Contact, Lamp
    >>> from tessera import announce_topic, event_topic, status_topic

    >>> lamp = Lamp("kitchen pendant")
    >>> lamp
    <kitchen pendant: off>

`Bus` stands in for the MQTT broker, which is an engine this project selects
rather than writes. `Lamp` stands in for the listed bulb plus whatever
automation platform subscribes on its behalf. The half this project actually
builds is `Contact`: the dry contact, and the module that debounces it and
emits the envelope.

    >>> bus = Bus()
    >>> button = Contact("tessera/kitchen/north")
    >>> button.attach(bus)

Now subscribe the lamp to the button's event topic and press it.

    >>> bus.subscribe(event_topic(button.src), lamp.handle)
    >>> _ = button.press()
    >>> lamp
    <kitchen pendant: on>

    >>> _ = button.press()
    >>> lamp
    <kitchen pendant: off>

That is the product. No cloud service was in the path, no account was
required, and no mains was switched — the contact is dry, the output is a
signal, and the actuation stayed inside the listed bulb where it belongs.

### The part that makes it still work in 2031

Suppose the button is later replaced by a module that also reports a torque
axis and a grip object — fields this schema does not define and nobody has
thought of yet. The lamp's consumer is the one written today, pinned to v1.

    >>> from_2031 = '''{
    ...   "src": "tessera/kitchen/north", "seq": 3,
    ...   "caps": ["press", "level", "torque", "grip"],
    ...   "action": "single", "ch": 0,
    ...   "level": 0.5,
    ...   "torque": 0.81,
    ...   "grip": {"fingers": 4, "pattern": "pinch"}
    ... }'''
    >>> bus.publish(event_topic(button.src), from_2031)
    >>> lamp
    <kitchen pendant: on>

The lamp toggled. A consumer that knows nothing about torque or grip read the
`action` it does understand, ignored the rest, and did the right thing.

This is the one assertion that matters. Everything else in this repository is
hygiene. If it is ever tempting to weaken this to make a test pass, that is
the project failing, not the test.

---

## The envelope

    >>> from tessera import Action, Color, Event, SCHEMA_VERSION
    >>> SCHEMA_VERSION
    '1.0.0'

Five fields are always present. `src` is the stable identity **and** the topic
path, so a subscriber never needs a lookup table to know which physical object
moved. `seq` is monotonic, for loss and replay detection. `caps` is everything
this module can ever emit, so a consumer can render an interface before seeing
a rich event.

    >>> event = Event(
    ...     src="tessera/kitchen/north", seq=1, caps=["press"], action="single"
    ... )
    >>> event.action.value
    'single'
    >>> print(event.wire_json())
    {"src":"tessera/kitchen/north","seq":1,"caps":["press"],"action":"single","ch":0}

Note what is *missing* from that payload: no `level`, no `color`, no `batt`.
Optional axes are **absent when unused, never null**. A null would claim the
module has a level whose value is unknown; absence says it does not carry one,
which is the true statement and the one a consumer branching on `caps` can act
on.

    >>> sorted(event.wire())
    ['action', 'caps', 'ch', 'seq', 'src']

A module that populates every axis carries those same five and four more. The
difference between these two key lists is the capability ladder — same
envelope, same consumer, more fields:

    >>> full = Event(
    ...     src="tessera/bench/puck", seq=2048,
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

### Where the compatibility guarantee physically lives

It is one line of model configuration — `extra="ignore"` — and it is stated
explicitly rather than inherited from a default, because a default can change
under an upgrade without anyone deciding to change it.

It has to survive the trip out of Python, because a consumer in another
language holds the emitted JSON Schema and nothing else:

    >>> from tessera import announce_json_schema, closed_objects, event_json_schema
    >>> schema = event_json_schema()
    >>> sorted(schema["required"])
    ['action', 'caps', 'seq', 'src']

The absence of `additionalProperties: false` is the forward-compatibility rule
reaching the artifact. If it ever appears there, every consumer written today
starts rejecting tomorrow's modules, and the generational claim is gone.

Checking the top level is not enough — a nested object closed by a
serialization default breaks the guarantee just as completely, and less
visibly. Both emitted schemas are checked all the way down:

    >>> closed_objects(schema)
    []
    >>> closed_objects(announce_json_schema())
    []

The event schema has nested definitions for `Action` and `Color`, so that
check has something to find and finds nothing.

### Announce

Published once on connect, retained, before any event — so a consumer arriving
late knows what the device is without waiting for someone to press it.

    >>> import json
    >>> print(json.dumps(button.announce().wire(), indent=2))
    {
      "schema_version": "1.0.0",
      "src": "tessera/kitchen/north",
      "caps": [
        "press"
      ],
      "hw": "t1-core-r0",
      "fw": "0.1.0"
    }

The schema version travels with every announce, so a consumer can tell which
generation of the envelope it is looking at without inferring it from the
fields present.

---

## The topic contract

Any subscriber can implement this. Home Assistant's MQTT Discovery is a
convenience layered over it, never the contract itself.

| Topic | Retained | Carries |
|---|---|---|
| `<src>/event` | no | one `Event` |
| `<src>/announce` | yes | one `Announce` |
| `<src>/status` | yes | `online` / `offline` |

    >>> event_topic("tessera/kitchen/north")
    'tessera/kitchen/north/event'
    >>> announce_topic("tessera/kitchen/north")
    'tessera/kitchen/north/announce'
    >>> status_topic("tessera/kitchen/north")
    'tessera/kitchen/north/status'

**Why announce and status are retained.** A consumer that subscribes after the
device booted still learns the device exists and what it can emit. Without
retention a dashboard restart shows nothing until somebody presses a button.
Watch a late subscriber receive it immediately:

    >>> seen = []
    >>> bus.subscribe(announce_topic(button.src), seen.append)
    >>> len(seen)
    1

**Why events are not.** An event is a moment, not a state. A retained press
would be redelivered to every new subscriber — and for a toggle that means the
lamp flips every single time a dashboard reloads. This is the one that bites,
which is why retention is a term of the contract rather than a broker setting
someone gets to choose:

    >>> late = []
    >>> bus.subscribe(event_topic(button.src), late.append)
    >>> late
    []

---

## Conformance vectors

Ten checked-in files under `schema/vectors/`. They are validated against the
**emitted JSON Schema**, not against the Python models — a guarantee proved
only through the models is a guarantee a consumer in another language does not
have.

Six valid, spanning press-only through every-axis-populated:

    >>> from tessera import report
    >>> for line in report("valid"):
    ...     print(line)
    1-press-only: accepted
    2-multi-gang-channel: accepted
    3-hold: accepted
    4-level-axis: accepted
    5-color-axis: accepted
    6-all-axes: accepted

Malformed, and correctly refused:

    >>> for line in report("invalid"):
    ...     print(line)
    1-missing-src: rejected
    2-level-out-of-range: rejected
    3-action-not-in-enum: rejected

### The fourth malformed vector, and an honest correction

The plan asks for four malformed vectors all rejected by the schema. Three are.
The fourth — non-monotonic `seq` — **cannot be**, and the gap is worth stating
rather than papering over. Monotonicity is a property of a *sequence*; a
single-event JSON Schema has no way to express a relationship between one
payload and the one before it. Each event in that fixture is individually
valid, and should be:

    >>> import json
    >>> from tessera import accepts, is_monotonic, vectors_dir
    >>> raw = json.loads(
    ...     (vectors_dir() / "invalid" / "4-seq-not-monotonic.json").read_text()
    ... )
    >>> [accepts(e) for e in raw]
    [True, True, True]

The invariant is real, so it needs a stateful check rather than a schema:

    >>> is_monotonic([Event.model_validate(e) for e in raw])
    False

Two kinds of guarantee, two kinds of gate. Pretending the schema covers both
would have meant either a weaker claim or a fabricated test.

---

## The CLI

    >>> from click.testing import CliRunner
    >>> from tessera.cli import cli
    >>> run = CliRunner()

    >>> print(run.invoke(cli, ["version"]).output.strip())
    1.0.0

`validate` takes a single event or an array, and checks the sequence invariant
when given an array:

    >>> ok = run.invoke(cli, ["validate", str(vectors_dir() / "valid" / "6-all-axes.json")])
    >>> ok.exit_code
    0
    >>> print(ok.output.strip())
    1 event(s) valid

    >>> bad = run.invoke(cli, ["validate", str(vectors_dir() / "invalid" / "4-seq-not-monotonic.json")])
    >>> bad.exit_code
    1

`tessera emit` writes the JSON Schema to `schema/build/`. That output is a
build artifact and is never committed: a schema in git that can drift from the
models is a second source of truth.

---

## What is not here yet

Stated plainly, because a README that implies coverage it does not have is
worse than no README.

- **Firmware and hardware.** No ESPHome configuration, no KiCad project. The
  demo models a T1-Core; it does not flash one. The captured firmware event the
  wire cookbook replays is a stand-in written against the topic contract, and
  becomes a real capture at WP-3.
- **The license gate.** Not wired. The org fork procedure wants it at
  instantiation; see `HANDOFF.md` for the open conflict and the decision it is
  waiting on.
- **Enclosure.** All printable geometry lives in `quaternionmedia/apothecary`,
  never here. There are no `.scad` files in this repository by design.
- **The name.** `tessera` is a placeholder, confined to the package name, the
  topic root constant and part directory names.

Projection contracts for the other transports are stubbed at
`schema/projections/README.md`: which axes each can carry, and which it drops.

---

## Governance

This project adopts the Quaternion Media constitution, vendored at
`governance/qm`. Read `AGENTS.md` before your first commit — the rule that
catches people out is that decision records are drafted by assistants and
ratified only by humans, and that no commit carries a co-author trailer naming
an unmonitored address.

Start at `HANDOFF.md`'s **State on arrival** section: it says what is built,
what is verified, and which work package is next.
