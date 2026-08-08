"""Running the golden vectors against the emitted JSON Schema.

The check that matters is against the *emitted artifact*, not against the
Pydantic models. A consumer in another language holds the JSON Schema and
nothing else, so a guarantee proved only through the models is a guarantee that
consumer does not have.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .envelope import event_json_schema


def vectors_dir() -> Path:
    """Locate ``schema/vectors/`` from inside the package, in a source checkout."""
    for parent in Path(__file__).resolve().parents:
        if parent.name == "schema" and (parent / "vectors").is_dir():
            return parent / "vectors"
    raise FileNotFoundError("schema/vectors/ not found; run from a source checkout")


def load(kind: str) -> list[tuple[str, Any]]:
    """Load every vector of a kind, sorted by name so output is stable."""
    directory = vectors_dir() / kind
    return [
        (path.stem, json.loads(path.read_text(encoding="utf-8")))
        for path in sorted(directory.glob("*.json"))
    ]


def accepts(data: Any, schema: dict[str, Any] | None = None) -> bool:
    """Whether the emitted JSON Schema accepts this payload.

    ``jsonschema`` is imported here rather than at module scope: it is a
    development dependency, so importing it eagerly would make the runtime
    package fail to load without it.
    """
    from jsonschema import Draft202012Validator

    validator = Draft202012Validator(schema if schema is not None else event_json_schema())
    return validator.is_valid(data)


def closed_objects(node: Any, path: str = "root") -> list[str]:
    """Every place the schema closes an object with ``additionalProperties: false``.

    Must always be empty, at the top level and on every nested object. The
    ignore-unknown-fields rule is a property of the models in one language and
    a property of the *artifact* in every other, and a consumer written
    elsewhere holds only the artifact. A closed object makes every consumer
    built against this schema reject the next generation of modules — the
    exact failure the envelope exists to prevent, arriving through a
    serialization default rather than through a decision.
    """
    found: list[str] = []
    if isinstance(node, dict):
        if node.get("additionalProperties") is False:
            found.append(path)
        for key, value in node.items():
            found += closed_objects(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found += closed_objects(value, f"{path}[{index}]")
    return found


def report(kind: str) -> list[str]:
    """One line per vector: its name and whether the schema accepted it."""
    schema = event_json_schema()
    return [
        f"{name}: {'accepted' if accepts(data, schema) else 'rejected'}"
        for name, data in load(kind)
        if isinstance(data, dict)  # sequence fixtures are checked separately
    ]
