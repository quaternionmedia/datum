# The CLI

Executable under `uv run pytest`.

    >>> from click.testing import CliRunner
    >>> from datum import vectors_dir
    >>> from datum.cli import cli
    >>> run = CliRunner()

## `datum version`

The schema version, not the package version.

    >>> print(run.invoke(cli, ["version"]).output.strip())
    1.0.0

## `datum validate`

Takes a single event or an array. Given an array it also checks the sequence
invariant, which no schema can express — see `docs/conformance.md`.

    >>> ok = run.invoke(cli, ["validate", str(vectors_dir() / "valid" / "6-all-axes.json")])
    >>> ok.exit_code
    0
    >>> print(ok.output.strip())
    1 event(s) valid

Optional: emit a machine-readable report for HIL workflows.

    >>> from pathlib import Path
    >>> report_path = Path("schema/build/validate-report.json")
    >>> rpt = run.invoke(
    ...     cli,
    ...     ["validate", str(vectors_dir() / "valid" / "6-all-axes.json"), "--report", str(report_path)],
    ... )
    >>> rpt.exit_code
    0
    >>> report_path.exists()
    True

    >>> bad = run.invoke(cli, ["validate", str(vectors_dir() / "invalid" / "4-seq-not-monotonic.json")])
    >>> bad.exit_code
    1

## `datum emit`

Writes the JSON Schema to `schema/build/`. That output is a build artifact and
is never committed: a schema in git can drift from the models, making two
sources of truth.
