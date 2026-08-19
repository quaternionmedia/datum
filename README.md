# Datum

A physical switch for things that lost one — a smart bulb with no wall control,
a lamp on a plug, a scene that only exists inside an app. It reads dry contacts,
turns them into a versioned JSON event, and publishes that over MQTT. It
switches no power itself; a listed device downstream does that.

The durable artifact is the **event envelope**: one versioned payload to which
fields are only ever added, so a consumer written today stays correct against a
module built years later.

## Run it

```
uv sync          # install
uv run pytest    # run the documentation
```

The docs below are the test suite. Every `>>>` in `docs/` executes, and module
docstrings are collected too, so a claim that stops being true fails the build.
There is no `tests/` directory, and adding one is a regression — see
`AGENTS.md`.

`docs/wire.md` needs a broker. Without one it skips with a stated reason:

```
docker run -d --rm -p 11883:1883 eclipse-mosquitto:2
uv run pytest
```

## Where to go

| | |
|---|---|
| [`docs/cookbook.md`](docs/cookbook.md) | Wire a switch, toggle a lamp, and watch a v1 consumer read a 2031 event. Start here |
| [`docs/envelope.md`](docs/envelope.md) | The payload: required fields, optional axes, and where the compatibility guarantee lives |
| [`docs/topic-contract.md`](docs/topic-contract.md) | Topics, what each carries, and which are retained |
| [`docs/wire.md`](docs/wire.md) | The same contract over a real MQTT broker |
| [`docs/firmware.md`](docs/firmware.md) | The seam between the ESPHome YAML and these constants |
| [`docs/conformance.md`](docs/conformance.md) | The ten checked-in vectors and the two gates they take |
| [`docs/cli.md`](docs/cli.md) | `datum version`, `validate`, `emit` |
| [`schema/projections/README.md`](schema/projections/README.md) | Which axes each transport carries, and which it drops |

## Not here yet

- **Hardware.** No KiCad project. `firmware/` holds an ESPHome configuration
  that CI compiles, but nothing here has been flashed to a board, so milestone
  assertion 2 still rides on a captured stand-in.
- **The license gate.** REUSE is wired; the dependency-manifest gate is not.
- **Enclosure.** All printable geometry lives in `quaternionmedia/apothecary`.
  No `.scad` files land here.
- **Remote detention.** A module can be detained locally, not from a phone.

## Governance

This project adopts the Quaternion Media constitution, vendored at
`governance/qm`. Read `AGENTS.md` before your first commit, then `HANDOFF.md`'s
**State on arrival** — what is built, what is verified, what is next.

Decision records live in `governance/qm/adr/`. Assistants draft; humans ratify.
