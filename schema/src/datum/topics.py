"""The topic contract.

The wire layout, as constants, so firmware and consumers cannot drift apart by
someone retyping a string. ``src`` is the topic path, so every topic derives
from the identity rather than being configured alongside it.

Retention is the part worth writing down, because the next person will wonder:

- **announce — retained.** A consumer that subscribes after the device booted
  still learns the device exists and what axes it can ever emit. Without
  retention, a dashboard restart shows nothing until somebody presses a button.
- **availability — retained.** Same reason, plus the broker's last-will
  overwrites it on an ungraceful drop, so "offline" is the state a late
  subscriber sees rather than silence it has to interpret.
- **events — not retained.** An event is a moment, not a state. A retained
  press would be redelivered to every new subscriber, and for a toggle that
  means the lamp flips every time a dashboard reloads. This is the one that
  bites, and it is why retention is a contract term rather than a broker
  setting.
- **detent — retained.** Whether the module is accepting input is state, and a
  late subscriber needs it or it will read a deliberately deaf button as a
  broken one.
- **detained — not retained.** Same reasoning as events: a press is a moment,
  even a press nobody acted on.

**Detention suppresses at the topic, never in the payload**, and the reason is
the envelope's own compatibility rule. Consumers ignore fields they do not
recognise — that is the forward-compatibility mechanism and it is absolute. So
a ``"detained": true`` field added to an event would be ignored by exactly the
consumers most needing to honour it: every one written before the field
existed. They would toggle the light anyway. A suppression semantic cannot be
carried additively in a payload whose readers are guaranteed to discard what
they do not know. Routing the press to a different topic makes old consumers
correct by construction, because they never receive it at all.
"""

from __future__ import annotations

TOPIC_ROOT = "datum"
"""Placeholder, pending the naming question. Confined to this constant."""

EVENT_SUFFIX = "event"
ANNOUNCE_SUFFIX = "announce"
STATUS_SUFFIX = "status"
DETENT_SUFFIX = "detent"
DETAINED_SUFFIX = "detained"

ONLINE = "online"
OFFLINE = "offline"

ARMED = "armed"
DETAINED = "detained"


def event_topic(src: str) -> str:
    """Where events go. Not retained.

    >>> event_topic("datum/kitchen/north")
    'datum/kitchen/north/event'
    """
    return f"{src}/{EVENT_SUFFIX}"


def announce_topic(src: str) -> str:
    """Where the capability advertisement goes. Retained.

    >>> announce_topic("datum/kitchen/north")
    'datum/kitchen/north/announce'
    """
    return f"{src}/{ANNOUNCE_SUFFIX}"


def status_topic(src: str) -> str:
    """Where availability goes. Retained, and the broker's last-will target.

    >>> status_topic("datum/kitchen/north")
    'datum/kitchen/north/status'
    """
    return f"{src}/{STATUS_SUFFIX}"


def detent_topic(src: str) -> str:
    """Where the module's detent position goes. Retained.

    A detent is the position a mechanism rests in. This module has two:
    ``armed``, accepting input, and ``detained``, ignoring it. Retained for the
    same reason availability is — a consumer arriving late needs to know a
    button is deliberately deaf, or it will report a fault that is a setting.

    >>> detent_topic("datum/kitchen/north")
    'datum/kitchen/north/detent'
    """
    return f"{src}/{DETENT_SUFFIX}"


def detained_topic(src: str) -> str:
    """Where presses that happened during detention go. Not retained.

    Detention suppresses *actuation*, not *observation*. The cat still pressed
    the button, and a system that silently discards that makes "why did nothing
    happen" unanswerable. Nothing subscribed to the event topic sees these.

    >>> detained_topic("datum/kitchen/north")
    'datum/kitchen/north/detained'
    """
    return f"{src}/{DETAINED_SUFFIX}"


def is_retained(topic: str) -> bool:
    """Whether the contract retains this topic.

    >>> is_retained(announce_topic("datum/desk/left"))
    True
    >>> is_retained(detent_topic("datum/desk/left"))
    True
    >>> is_retained(event_topic("datum/desk/left"))
    False
    >>> is_retained(detained_topic("datum/desk/left"))
    False
    """
    return topic.rsplit("/", 1)[-1] in {ANNOUNCE_SUFFIX, STATUS_SUFFIX, DETENT_SUFFIX}
