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


@cli.command(
    context_settings={"ignore_unknown_options": True},
)
@click.argument("passthrough", nargs=-1, type=click.UNPROCESSED)
def preflight(passthrough: tuple[str, ...]) -> None:
    """Run this repository's CI workflows locally, before pushing.

    Delegates to the governance corpus's own runner rather than restating what
    the workflows do. A second list of "what CI runs" is a list that drifts,
    and the point of running them here is to find out what the runner will say
    -- which a paraphrase cannot tell you.

    Arguments pass straight through:

        datum preflight                          # a pull request into main
        datum preflight --event push --ref main

    A pass here is evidence, not proof. `uses:` steps and the runner image are
    not reproduced, this machine carries tools a fresh runner does not, and
    three of these gates cannot run on Windows at all -- each is named in the
    output rather than quietly skipped. `walkthrough/09-preflight.md` has the
    local equivalent for each one.
    """
    import shutil
    import subprocess

    root = Path(__file__).resolve()
    runner = repo = None
    for parent in root.parents:
        candidate = parent / "governance" / "qm" / "project-seed" / "ci" / "run_workflows_locally.py"
        if candidate.exists():
            runner, repo = candidate, parent
            break

    if runner is None:
        raise click.ClickException(
            """
The governance submodule is not checked out, so its workflow runner is
not here:
    git submodule update --init --recursive
This repository has been in that state before, and everything was read
out of a summary of documents nobody could open."""
        )

    try:
        import yaml  # noqa: F401
    except ImportError:
        raise click.ClickException(
            """
The runner needs pyyaml, and the workflows install their own tools with
pip:
    uv run --group preflight datum preflight
`uv run` re-syncs the environment and drops the group, so the group has
to be named on the command that runs, not on a sync beforehand."""
        ) from None

    # The workflows install their own tools, and `actions/setup-python` is an
    # environment step the runner does not reproduce -- so `python -m pip
    # install esphome` lands wherever `python` points. On this machine that was
    # the system interpreter, which refused it for lack of permission; with
    # permission it would have installed ESPHome into the user's global Python.
    # `uv sync --locked` is the same hazard aimed at .venv: it strips whatever
    # the project lockfile does not name, including the tools later jobs need.
    #
    # So preflight runs against a scratch environment it owns. Nothing it does
    # reaches the interpreter you work in.
    scratch = repo / ".preflight" / "venv"
    bin_dir = scratch / ("Scripts" if os.name == "nt" else "bin")

    def ensure_scratch() -> None:
        if not bin_dir.exists():
            click.echo(f"Creating the preflight environment in {scratch} ...")
            # --seed: the workflows call `python -m pip`, and a bare uv venv
            # has no pip at all.
            subprocess.check_call(["uv", "venv", "--seed", str(scratch)])
        # reuse-lint.yml installs plain `reuse`, which imports libmagic at
        # start-up and dies before it lints anything on a box with no `file`
        # command. Seeding the charset-normalizer extra leaves pip's later
        # `install reuse` satisfied, so the gate runs instead of reporting a
        # Windows fact as a licensing failure. Re-seeded every time because a
        # previous workflow's `uv sync --locked` strips it back out.
        subprocess.check_call(
            ["uv", "pip", "install", "--quiet", "--python", str(scratch),
             "reuse[charset-normalizer]"]
        )

    env = dict(os.environ)
    env["UV_PROJECT_ENVIRONMENT"] = str(scratch)
    env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
    env["VIRTUAL_ENV"] = str(scratch)

    # Honour an explicit --workflows and run exactly once: the caller has said
    # what they want executed.
    if any(a.startswith("--workflows") for a in passthrough):
        ensure_scratch()
        sys.exit(subprocess.call([sys.executable, str(runner), *passthrough], cwd=repo, env=env))

    # Otherwise one invocation per workflow. The runner executes every job in a
    # single environment; CI gives each job a fresh machine. That difference is
    # not cosmetic -- enclosure.yml's `uv sync --locked` was stripping the
    # tools reuse-lint.yml needed, and the licensing gate failed for it.
    source = repo / ".github" / "workflows"
    staged_root = repo / ".preflight" / "workflows"
    if staged_root.exists():
        shutil.rmtree(staged_root)

    # The split, and the reasons, live in datum.preflight so they can be
    # tested. A rule that only exists inside a CLI is a rule nothing checks.
    from .preflight import LOCAL_DIFFERENCES, partition

    names, set_aside = partition(source)
    runnable = []
    for name in names:
        staged = staged_root / Path(name).stem
        staged.mkdir(parents=True)
        shutil.copy2(source / name, staged / name)
        runnable.append((name, staged))

    if set_aside:
        click.echo("Not run here. CI still runs them:")
        for name in set_aside:
            difference = LOCAL_DIFFERENCES.get(name)
            click.echo(f"  {name} -- {difference.why if difference else 'the runner cannot execute it'}")
            if difference:
                click.echo(f"      covered here by: {difference.covered_by}")
        click.echo("")

    failed = []
    for name, staged in runnable:
        ensure_scratch()
        code = subprocess.call(
            [sys.executable, str(runner), *passthrough, "--workflows", str(staged)],
            cwd=repo,
            env=env,
        )
        if code != 0:
            failed.append(name)

    click.echo("")
    click.echo("=" * 60)
    if failed:
        click.echo(f"{len(failed)} workflow(s) reported a failure: {', '.join(failed)}")
        click.echo("")
        click.echo("A local failure is a question: a defect, or a difference between")
        click.echo("this machine and the runner. These are recorded as the second:")
        for name in failed:
            difference = LOCAL_DIFFERENCES.get(name)
            if difference:
                click.echo(f"  {name} -- {difference.why}")
                click.echo(f"      covered here by: {difference.covered_by}")
            else:
                click.echo(f"  {name} -- NOT a recorded difference. Read it as a defect.")
        sys.exit(1)
    click.echo(f"{len(runnable)} workflow(s) passed locally.")
    if set_aside:
        click.echo(f"{len(set_aside)} not run here, named above. A skip is not a pass.")


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
