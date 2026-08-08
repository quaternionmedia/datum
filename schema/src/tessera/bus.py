"""An in-process stand-in for the broker, implementing the topic contract.

This is **not** an MQTT implementation and must never become one. The broker is
an engine and gets selected, not written. What this class exists for is to make
the contract's retention semantics executable in the cookbook without a running
broker, so the demo is a test rather than a screenshot.

The over-the-wire proof against a real broker is WP-2, and it needs an MQTT
client library — a dependency outside the blessed house-stack set, so it needs
a record before it appears in review. Until then the seam is exercised here and
the wire is not, and the cookbook says so rather than implying coverage it does
not have.
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
