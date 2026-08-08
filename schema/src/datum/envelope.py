"""The event envelope — the project's interface.

Every transport carries this or a documented projection of it. The
compatibility guarantee lives here and nowhere else: fields are added, never
removed and never repurposed, and unknown fields are ignored rather than
rejected.

That last rule is one line of model config (``extra="ignore"``) and it is the
entire forward-compatibility mechanism. It is stated explicitly rather than
inherited from a default, because a default can be changed by an upgrade
without anyone deciding to change it.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "1.0.0"
"""Versioned independently of firmware and hardware; appears in every announce."""


class Action(str, Enum):
    """What the contact did. Closed set; new members are additive."""

    PRESS = "press"
    SINGLE = "single"
    DOUBLE = "double"
    TRIPLE = "triple"
    HOLD = "hold"
    RELEASE = "release"


class _Envelope(BaseModel):
    # The forward-compatibility mechanism, stated rather than defaulted.
    model_config = ConfigDict(extra="ignore")

    def wire(self) -> dict[str, Any]:
        """The form that goes on the transport.

        Optional axes are *absent* when unused, never null. A null would say
        "this module has a level and it is unknown"; absence says "this module
        does not carry a level," which is the true statement and the one a
        consumer branching on ``caps`` can act on.
        """
        return self.model_dump(mode="json", exclude_none=True)

    def wire_json(self) -> str:
        """``wire()`` as a JSON string, which is what a publisher sends."""
        return self.model_dump_json(exclude_none=True)


class Color(_Envelope):
    """The optional colour axis. Hue in degrees, saturation as a fraction."""

    h: float = Field(ge=0, le=360)
    s: float = Field(ge=0, le=1)


class Event(_Envelope):
    """One thing a control surface did.

    ``src`` doubles as the identity and the topic path, so a subscriber never
    needs a lookup table to know which physical object moved.
    """

    src: str = Field(min_length=1)
    seq: int = Field(ge=0)
    caps: list[str]
    action: Action
    ch: int = Field(default=0, ge=0)

    # Optional axes. A module populates one only if it advertised it in caps.
    level: float | None = Field(default=None, ge=0, le=1)
    vec: tuple[float, float, float] | None = None
    color: Color | None = None
    batt: int | None = Field(default=None, ge=0, le=100)


class Announce(_Envelope):
    """Published once on connect, retained, before any event.

    Retained so a consumer joining late can render an appropriate interface
    without waiting for someone to press the button.
    """

    schema_version: str = SCHEMA_VERSION
    src: str = Field(min_length=1)
    caps: list[str]
    hw: str
    fw: str


def event_json_schema() -> dict[str, Any]:
    """The JSON Schema a consumer in another language validates against.

    Note what is *absent* from the output: no ``additionalProperties: false``.
    That absence is the forward-compatibility rule surviving the trip from
    Python into a language-neutral artifact.
    """
    return Event.model_json_schema()


def announce_json_schema() -> dict[str, Any]:
    return Announce.model_json_schema()


def is_monotonic(events: list[Event]) -> bool:
    """Whether ``seq`` never goes backwards across a run of events.

    This is a property of a *sequence*, so no single-event JSON Schema can
    express it — see the cookbook's note on the fourth malformed vector.
    """
    return all(b.seq > a.seq for a, b in zip(events, events[1:]))
