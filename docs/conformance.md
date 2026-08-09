# Conformance vectors

Ten checked-in files under `schema/vectors/`, validated against the **emitted
JSON Schema** rather than the Python models: a guarantee proved only through
the models is one a consumer in another language does not have. Executable
under `uv run pytest`.

Six valid, spanning press-only through every-axis-populated:

    >>> from datum import report
    >>> for line in report("valid"):
    ...     print(line)
    1-press-only: accepted
    2-multi-gang-channel: accepted
    3-hold: accepted
    4-level-axis: accepted
    5-color-axis: accepted
    6-all-axes: accepted

Three malformed, refused:

    >>> for line in report("invalid"):
    ...     print(line)
    1-missing-src: rejected
    2-level-out-of-range: rejected
    3-action-not-in-enum: rejected

## The fourth malformed vector takes a different gate

Non-monotonic `seq` is not schema-detectable. Monotonicity is a property of a
*sequence*, and a single-event JSON Schema cannot express a relationship
between one payload and the one before it. Each event in that fixture is
individually valid:

    >>> import json
    >>> from datum import Event, accepts, is_monotonic, vectors_dir
    >>> raw = json.loads(
    ...     (vectors_dir() / "invalid" / "4-seq-not-monotonic.json").read_text()
    ... )
    >>> [accepts(e) for e in raw]
    [True, True, True]

The invariant is real, and takes a stateful check:

    >>> is_monotonic([Event.model_validate(e) for e in raw])
    False

Two kinds of guarantee, two kinds of gate. `datum validate` applies the second
when given an array — see `docs/cli.md`.

`HANDOFF.md`'s "Correction to WP-1's acceptance" records why the packet asked
for four schema-rejected vectors and gets three.
