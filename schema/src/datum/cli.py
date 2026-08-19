"""The schema CLI: emit the artifact, validate a file, report the version."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import click

from .conformance import accepts
from .envelope import SCHEMA_VERSION, Event, announce_json_schema, event_json_schema, is_monotonic


@click.group()
def cli() -> None:
    """Tools for the event envelope."""


@cli.command()
@click.option(
    "--out",
    type=click.Path(path_type=Path),
    default=Path("schema/build"),
    show_default=True,
    help="Directory to write the emitted JSON Schema into.",
)
def emit(out: Path) -> None:
    """Emit JSON Schema for the envelope and the announce payload.

    The output is a build artifact and is never committed: a schema in git that
    can drift from the models is a second source of truth.
    """
    out.mkdir(parents=True, exist_ok=True)
    for name, schema in (("event", event_json_schema()), ("announce", announce_json_schema())):
        path = out / f"{name}.schema.json"
        path.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        click.echo(f"wrote {path}")


@cli.command()
@click.argument("path", type=click.Path(exists=True, allow_dash=True, path_type=Path))
@click.option(
    "--report",
    type=click.Path(path_type=Path),
    default=None,
    help="Write a JSON validation report to this path.",
)
def validate(path: Path, report: Path | None) -> None:
    """Validate a JSON file of events against the emitted schema.

    Accepts a single event object or an array of them. An array is additionally
    checked for monotonic ``seq``, which is a property of a sequence and which
    no single-event schema can express.

    ``-`` reads stdin, so a live capture can be checked without landing in a
    file first: ``mosquitto_sub -C 1 -t 'datum/+/+/event' | datum validate -``.
    """
    source = "<stdin>" if str(path) == "-" else str(path)
    raw = sys.stdin.read() if str(path) == "-" else path.read_text(encoding="utf-8")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        # A truncated capture is the common case here, and "Expecting value:
        # line 1 column 1" on its own does not say which input was bad.
        click.echo(f"{source}: not JSON: {exc}", err=True)
        sys.exit(1)
    payloads = data if isinstance(data, list) else [data]

    failures = [i for i, payload in enumerate(payloads) if not accepts(payload)]
    monotonic_ok: bool | None = None
    for i in failures:
        click.echo(f"event {i}: rejected by the emitted schema", err=True)

    if not failures and isinstance(data, list):
        events = [Event.model_validate(payload) for payload in payloads]
        monotonic_ok = is_monotonic(events)
        if not monotonic_ok:
            click.echo("sequence: seq is not monotonic", err=True)

    exit_code = 1 if (failures or monotonic_ok is False) else 0

    if report is not None:
        doc = {
            "path": source,
            "events": len(payloads),
            "schema_failures": failures,
            "monotonic_checked": isinstance(data, list),
            "monotonic_ok": monotonic_ok,
            "ok": exit_code == 0,
        }
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        click.echo(f"wrote report {report}")

    if exit_code != 0:
        sys.exit(1)
    click.echo(f"{len(payloads)} event(s) valid")


@cli.command()
@click.option(
    "--broker",
    default=None,
    metavar="HOST:PORT",
    help="An MQTT broker for the wire contract. Overrides DATUM_BROKER.",
)
def hil(broker: str | None) -> None:
    """Prove what is provable without hardware, and name what is left.

    The entry point for a hardware-in-the-loop review. Runs the contract end
    to end against whatever is installed, writes report artifacts, and lists
    the IRL cases only a board on a bench can close. Starts nothing, and
    leaves nothing running.

    This is not the test suite -- ``uv run pytest`` is. See ``walkthrough/07-hil.md``.
    """
    from datum.hil import MARK, NEEDS_HARDWARE, find_repo_root, parse_broker, run_all

    root = find_repo_root()
    if root is None:
        raise click.ClickException(
            "run this from a datum checkout: it needs schema/vectors, walkthrough/ and firmware/"
        )

    steps = run_all(root, parse_broker(broker or os.environ.get("DATUM_BROKER")))

    click.echo("Datum -- pre-HIL proof run")
    click.echo(f"repository: {root}")
    click.echo("")

    width = max(len(s.name) for s in steps)
    for s in steps:
        click.echo(f"  [{MARK[s.state]}] {s.name.ljust(width)}  {s.detail}")

    failed = [s for s in steps if s.state == "fail"]
    skipped = [s for s in steps if s.state == "skip"]
    passed = [s for s in steps if s.state == "pass"]

    click.echo("")
    click.echo(f"{len(passed)} proved, {len(failed)} failed, {len(skipped)} skipped")
    click.echo(f"reports: {(root / 'schema' / 'build' / 'reports')}")

    click.echo("")
    click.echo("Still needs a board on a bench. Nothing above can close these:")
    for case, description in NEEDS_HARDWARE:
        click.echo(f"  {case}  {description}")
    click.echo("")
    click.echo("  planning/IRL_TEST_MATRIX.md carries the stimulus and expected result")
    click.echo("  for each. firmware/README.md has the GPIO map and the jig wiring.")

    if skipped:
        click.echo("")
        click.echo("Skipped, and why:")
        for s in skipped:
            click.echo(f"  {s.name}: {s.detail}")

    if failed:
        sys.exit(1)


@cli.command()
def version() -> None:
    """Print the schema version carried in every announce."""
    click.echo(SCHEMA_VERSION)
