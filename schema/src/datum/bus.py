"""An in-process stand-in for the broker, implementing the topic contract.

Makes the contract's retention semantics executable in ``docs/cookbook.md``
with no broker running. It is **not** an MQTT implementation and must never
become one: the broker is an engine this project selects rather than writes.

It models delivery and retention only. A real broker also clears the retain
flag when delivering to an already-established subscription, which this does
not reproduce — ``datum.harness`` and ``docs/wire.md`` cover that against a
live Mosquitto.
"""

from __future__ import annotations

from collections.abc import Callable

from .topics import is_retained

Handler = Callable[[str], None]


class Bus:
    """Topic-addressed publish/subscribe with the contract's retention rules."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Handler]] = {}
        self.retained: dict[str, str] = {}

    def publish(self, topic: str, payload: str, retain: bool | None = None) -> None:
        """Publish a payload. Retention defaults to what the contract says.

        Passing ``retain`` explicitly is allowed so a test can demonstrate what
        the wrong choice would do, which is the only reason to ever pass it.
        """
        if retain is None:
            retain = is_retained(topic)
        if retain:
            self.retained[topic] = payload
        for handler in list(self._subscribers.get(topic, ())):
            handler(payload)

    def subscribe(self, topic: str, handler: Handler) -> None:
        """Subscribe, and immediately receive the retained payload if there is one.

        The immediate delivery is the whole point of retention: a consumer that
        arrives after the device booted still learns what the device is.
        """
        self._subscribers.setdefault(topic, []).append(handler)
        if topic in self.retained:
            handler(self.retained[topic])
