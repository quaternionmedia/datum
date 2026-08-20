# The pre-HIL run

**Hermetic.**

One command. It proves everything this project can prove without hardware,
writes the report artifacts, and then names the cases a board on a bench is the
only way to close.

```
uv run datum hil
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
  [PASS] Enclosure bounds         declared bounds match the geometry, at the pinned <commit>

6 proved, 0 failed, 1 skipped
```

Exit status is 0 only if nothing that ran failed. **A skip is never counted as
a pass**, and every skip is repeated at the end with its reason — a skipped
assertion reported as green is the failure mode this whole layout exists to
prevent, and `walkthrough/08-wire.md` already says so about itself.

## What each line is

| | |
|---|---|
| **Schema emits** | The language-neutral JSON Schema a consumer in another stack validates against |
| **Vectors validate** | All ten checked-in vectors: six accepted, four rejected, each leaving a report in `schema/build/reports/` |
| **Piped capture validates** | `mosquitto_sub \| datum validate -`, the path a live capture takes at the bench |
| **Wire contract** | Topics, encoding, retention and a late subscriber, over a real broker |
| **Firmware configuration** | `esphome config` resolves every wire-critical string in the YAML |
| **Firmware seam** | The topics and payload templates read back out of the YAML and compared to the constants |
| **Enclosure bounds** | `datum-core`'s declared envelope measured against the geometry OpenSCAD emits, and which apothecary that was |

## Getting the wire contract to run

It needs a broker, and skips with a reason without one:

```
docker run -d --rm -p 11883:1883 eclipse-mosquitto:2
uv run datum hil --broker 127.0.0.1:11883
```

`DATUM_BROKER` works too — the same variable `walkthrough/08-wire.md` reads, so a bench
with one already exported needs no argument:

    >>> from datum.hil import parse_broker
    >>> parse_broker("10.0.0.2:1883")
    ('10.0.0.2', 1883)
    >>> parse_broker("localhost")
    ('localhost', 1883)

Any broker works. Mosquitto is the reference implementation of the seam
protocol; a harness that would fail against EMQX or NanoMQ is a defective
harness, not a configuration detail.

## The other prerequisites

Each is optional, and its absence is a skip rather than a failure.

| | |
|---|---|
| **ESPHome** | Used if on `PATH`, otherwise fetched for the length of one command. It is the engine the firmware runs on, not a dependency of this package |
| **OpenSCAD** | Needed for the enclosure check. The part lives in `quaternionmedia/apothecary`, expected as a sibling checkout — no printable geometry lands here |

The enclosure step names the apothecary commit it actually verified. The pin is
`APOTHECARY_PIN` in `datum.hil`, and `.github/workflows/enclosure.yml` is what
checks it in CI:

    >>> from datum.hil import pin_state
    >>> pin_state("abc1234", pin="abc1234")
    'at the pinned abc1234'
    >>> pin_state("deadbee", pin="abc1234")
    'at deadbee, not the pinned abc1234'

Working against a newer apothecary is allowed. Reporting the run as proving the
pin when it proved something else is not, and neither is claiming the pin when
the commit could not be read, nor when the tree it read has uncommitted changes.

The sample above says `<commit>` rather than a hash. A pin written into prose
is a second copy of the constant, and this page had to be hand-corrected three
times in one session before that was obvious. What the run prints is checked
here instead:

    >>> from datum.hil import APOTHECARY_PIN, pin_state
    >>> pin_state(APOTHECARY_PIN) == f"at the pinned {APOTHECARY_PIN}"
    True

## The cases only hardware can close

Seven, and the run prints them. They are kept beside the runner rather than in
prose, so what a reviewer is told to work through is what the code knows:

    >>> from datum.hil import irl_case_ids
    >>> irl_case_ids()
    ['IRL-001', 'IRL-002', 'IRL-003', 'IRL-004', 'IRL-005', 'IRL-006', 'IRL-007']

That list has to be the matrix's list. A case added to one and not the other
is a case nobody runs, so the two are compared here rather than trusted:

    >>> import re
    >>> from datum.hil import find_repo_root
    >>> matrix = (find_repo_root() / "planning" / "IRL_TEST_MATRIX.md").read_text(encoding="utf-8")
    >>> sorted(set(re.findall(r"IRL-\d+", matrix))) == irl_case_ids()
    True

`planning/IRL_TEST_MATRIX.md` carries the stimulus, the expected result and the
validation command for each. `firmware/README.md` has the exact devkit, the
GPIO map, and how to wire the T0 contact jig.

## What this is not

Not the test suite. `uv run pytest` is, and it runs every example under `walkthrough/`
plus the module docstrings. This orchestrates across two repositories and a
firmware toolchain, which no doctest can reach — so the orchestration lives in
`datum.hil` and the pieces that *can* be checked in-process carry their own
examples, including the ones on this page.

## After the board arrives

```
esphome run firmware/t1-core.yaml -s mqtt_broker 10.0.0.2 -s src datum/lab/jig
mosquitto_sub -h 10.0.0.2 -t 'datum/lab/jig/event' -C 1 | uv run datum validate -
```

When a real capture replaces `schema/vectors/captured/t1-core-single-press.json`,
milestone assertion 2 stops being qualified. That one file is the only thing
standing between the stand-in and a genuine firmware capture.
