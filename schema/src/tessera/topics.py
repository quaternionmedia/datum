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
"""

from __future__ import annotations

TOPIC_ROOT = "tessera"
"""Placeholder, pending the naming question. Confined to this constant."""

EVENT_SUFFIX = "event"
ANNOUNCE_SUFFIX = "announce"
STATUS_SUFFIX = "status"

ONLINE = "online"
OFFLINE = "offline"


def event_topic(src: str) -> str:
    """Where events go. Not retained.

    >>> event_topic("tessera/kitchen/north")
    'tessera/kitchen/north/event'
    """
    return f"{src}/{EVENT_SUFFIX}"


def announce_topic(src: str) -> str:
    """Where the capability advertisement goes. Retained.

    >>> announce_topic("tessera/kitchen/north")
    'tessera/kitchen/north/announce'
    """
    return f"{src}/{ANNOUNCE_SUFFIX}"


def status_topic(src: str) -> str:
    """Where availability goes. Retained, and the broker's last-will target.

    >>> status_topic("tessera/kitchen/north")
    'tessera/kitchen/north/status'
    """
    return f"{src}/{STATUS_SUFFIX}"


def is_retained(topic: str) -> bool:
    """Whether the contract retains this topic.

    >>> is_retained(announce_topic("tessera/desk/left"))
    True
    >>> is_retained(event_topic("tessera/desk/left"))
    False
    """
    return topic.rsplit("/", 1)[-1] in {ANNOUNCE_SUFFIX, STATUS_SUFFIX}
