# Pre-HIL demo

One command. It proves everything this project can prove without hardware,
writes the report artifacts, and then names the cases a board on a bench is the
only way to close.

```bash
uv run python demo/hil.py
```

Nothing is running until you type that, and nothing keeps running after it
returns. It starts no servers and leaves no processes behind.

## What a clean run looks like

```
Datum -- pre-HIL proof run

  [PASS] Schema emits             3 schema file(s) in schema/build/
  [PASS] Vectors validate         6 valid, 4 malformed, 10 reports written
  [PASS] Piped capture validates  1 event(s) valid
  [SKIP] Wire contract            DATUM_BROKER not set
  [PASS] Firmware configuration   configuration is valid
  [PASS] Firmware seam            YAML and constants agree
  [PASS] Enclosure bounds         declared bounds match the geometry

6 proved, 0 failed, 1 skipped
```

Exit status is 0 only if nothing that ran failed. A skip is never counted as a
pass, and every skip is repeated at the end with its reason — a skipped
assertion reported as green is the failure mode this whole layout exists to
prevent.

## What each line is

| | |
|---|---|
| **Schema emits** | The language-neutral JSON Schema a consumer in another stack validates against |
| **Vectors validate** | All ten checked-in vectors: six accepted, four rejected, each leaving a report in `schema/build/reports/` |
| **Piped capture validates** | `mosquitto_sub \| datum validate -`, the path a live capture takes at the bench |
| **Wire contract** | Topics, encoding, retention and a late subscriber, over a real broker |
| **Firmware configuration** | `esphome config` resolves every wire-critical string in the YAML |
| **Firmware seam** | The topics and payload templates read back out of the YAML and compared to the Python constants |
| **Enclosure bounds** | `datum-core`'s declared envelope measured against the geometry OpenSCAD emits |

## Getting the wire contract to run

It needs a broker, and skips with a reason without one:

```bash
docker run -d --rm -p 11883:1883 eclipse-mosquitto:2
DATUM_BROKER=127.0.0.1:11883 uv run python demo/hil.py
```

Or point it at one you already have:

```bash
uv run python demo/hil.py --broker 10.0.0.2:1883
```

Any broker works. Mosquitto is the reference implementation of the seam
protocol; a harness that would fail against EMQX or NanoMQ is a defective
harness, not a configuration detail.

## The other prerequisites

Each is optional, and its absence is a skip rather than a failure.

| | |
|---|---|
| **ESPHome** | Used if on `PATH`, otherwise fetched by `uv` for the length of one command. It is the engine the firmware runs on, not a dependency of this package |
| **OpenSCAD** | Needed for the enclosure check. The part lives in `quaternionmedia/apothecary`, expected as a sibling checkout |

## What this is not

Not the test suite. `uv run pytest` is, and it runs every example under
`docs/` plus the module docstrings. This is a reviewer's entry point that
orchestrates across both repositories and the firmware toolchain, which no
doctest can reach.

## After the board arrives

The seven IRL cases the run prints are the whole remaining gap. Each has its
stimulus, expected result and validation command in
[`planning/IRL_TEST_MATRIX.md`](../planning/IRL_TEST_MATRIX.md).
[`firmware/README.md`](../firmware/README.md) has the exact devkit, the GPIO
map, and how to wire the T0 contact jig.

The loop at the bench:

```bash
esphome run firmware/t1-core.yaml -s mqtt_broker 10.0.0.2 -s src datum/lab/jig
mosquitto_sub -h 10.0.0.2 -t 'datum/lab/jig/event' -C 1 | uv run datum validate -
```

When a real capture replaces
`schema/vectors/captured/t1-core-single-press.json`, milestone assertion 2
stops being qualified — that one file is the only thing standing between the
stand-in and a genuine firmware capture.
