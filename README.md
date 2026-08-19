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

The docs below are the test suite. Every `>>>` in `walkthrough/` executes, and module
docstrings are collected too, so a claim that stops being true fails the build.
There is no `tests/` directory, and adding one is a regression — see
`AGENTS.md`.

`walkthrough/08-wire.md` needs a broker. Without one it skips with a stated reason:

```
docker run -d --rm -p 11883:1883 eclipse-mosquitto:2
uv run pytest
```

## Where to go

The pages are ordinal and read in order. `01` through `07` are hermetic; `08`
needs a broker and says so in its opening line.

| | |
|---|---|
| [`walkthrough/01-cookbook.md`](walkthrough/01-cookbook.md) | Wire a switch, toggle a lamp, and watch a v1 consumer read a 2031 event. Start here |
| [`walkthrough/02-envelope.md`](walkthrough/02-envelope.md) | The payload: required fields, optional axes, and where the compatibility guarantee lives |
| [`walkthrough/03-topic-contract.md`](walkthrough/03-topic-contract.md) | Topics, what each carries, and which are retained |
| [`walkthrough/04-firmware.md`](walkthrough/04-firmware.md) | The seam between the ESPHome YAML and these constants |
| [`walkthrough/05-conformance.md`](walkthrough/05-conformance.md) | The ten checked-in vectors and the two gates they take |
| [`walkthrough/06-cli.md`](walkthrough/06-cli.md) | `datum version`, `validate`, `emit`, `hil` |
| [`walkthrough/07-hil.md`](walkthrough/07-hil.md) | One command that proves everything provable without hardware, and names what is left |
| [`walkthrough/08-wire.md`](walkthrough/08-wire.md) | The same contract over a real MQTT broker |

That table is the registry's only rendering, and a rendering that disagrees
with the directory is how a page stops being read. So it is checked rather
than maintained:

    >>> import re
    >>> from datum.hil import find_repo_root
    >>> root = find_repo_root()
    >>> rows = [line for line in (root / "README.md").read_text(encoding="utf-8").splitlines()
    ...         if line.startswith("| [`walkthrough/")]
    >>> listed = [re.search(r"\(walkthrough/(.+?)\)", row).group(1) for row in rows]
    >>> listed == sorted(page.name for page in (root / "walkthrough").glob("*.md"))
    True

Elsewhere: [`schema/projections/README.md`](schema/projections/README.md) says
which axes each transport carries and which it drops.

## Not here yet

- **Hardware.** No KiCad project. `firmware/` holds an ESPHome configuration
  that `esphome config` reports valid and that CI is set up to compile, but no
  compile has run anywhere yet and nothing here has been flashed to a board, so
  milestone assertion 2 still rides on a captured stand-in.
- **The license gate.** REUSE is wired; the dependency-manifest gate is not.
- **Enclosure.** All printable geometry lives in `quaternionmedia/apothecary`.
  No `.scad` files land here.
- **Remote detention.** A module can be detained locally, not from a phone.

## Governance

This project adopts the Quaternion Media constitution, vendored at
`governance/qm`. Read `AGENTS.md` before your first commit, then `HANDOFF.md`'s
**State on arrival** — what is built, what is verified, what is next.

Decision records live in `governance/qm/adr/`. Assistants draft; humans ratify.
