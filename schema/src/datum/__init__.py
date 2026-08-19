"""The event envelope, and the pieces that exercise it.

Exports the envelope models (``Event``, ``Announce``, ``Action``, ``Color``),
the topic helpers, the conformance vector loaders, and the two stand-ins the
cookbook drives — ``Bus`` for the broker and ``Lamp`` for a subscribing
consumer.

``walkthrough/01-cookbook.md`` is the worked example; ``walkthrough/02-envelope.md`` documents the
payload.
"""

from .bus import Bus
from .conformance import accepts, closed_objects, load, report, vectors_dir
from .envelope import (
    SCHEMA_VERSION,
    Action,
    Announce,
    Color,
    Event,
    announce_json_schema,
    event_json_schema,
    is_monotonic,
)
from .retrofit import Contact, Lamp
from .topics import (
    ARMED,
    DETAINED,
    OFFLINE,
    ONLINE,
    TOPIC_ROOT,
    announce_topic,
    detained_topic,
    detent_topic,
    event_topic,
    is_retained,
    status_topic,
)

__all__ = [
    "ARMED",
    "DETAINED",
    "OFFLINE",
    "ONLINE",
    "SCHEMA_VERSION",
    "TOPIC_ROOT",
    "Action",
    "Announce",
    "Bus",
    "Color",
    "Contact",
    "Event",
    "Lamp",
    "accepts",
    "announce_json_schema",
    "announce_topic",
    "closed_objects",
    "detained_topic",
    "detent_topic",
    "event_json_schema",
    "event_topic",
    "is_monotonic",
    "is_retained",
    "load",
    "report",
    "status_topic",
    "vectors_dir",
]
