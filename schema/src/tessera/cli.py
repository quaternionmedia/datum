"""The schema CLI: emit the artifact, validate a file, report the version."""

from __future__ import annotations

import json
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
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def validate(path: Path) -> None:
    """Validate a JSON file of events against the emitted schema.

    Accepts a single event object or an array of them. An array is additionally
    checked for monotonic ``seq``, which is a property of a sequence and which
    no single-event schema can express.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    payloads = data if isinstance(data, list) else [data]

    failures = [i for i, payload in enumerate(payloads) if not accepts(payload)]
    for i in failures:
        click.echo(f"event {i}: rejected by the emitted schema", err=True)

    if not failures and isinstance(data, list):
        events = [Event.model_validate(payload) for payload in payloads]
        if not is_monotonic(events):
            click.echo("sequence: seq is not monotonic", err=True)
            sys.exit(1)

    if failures:
        sys.exit(1)
    click.echo(f"{len(payloads)} event(s) valid")


@cli.command()
def version() -> None:
    """Print the schema version carried in every announce."""
    click.echo(SCHEMA_VERSION)
