"""The wire harness: prove the contract over a real broker, with no hardware.

The in-process bus proves the envelope and the retention rules. It cannot
prove the wire, and the failures it cannot see are the ones worth catching — a
topic that is right in the constant and wrong in the firmware, a retained flag
on the wrong topic, a payload that is valid JSON in the wrong encoding, a
last-will that never fires.

This module talks to any broker reachable at a configured address. It depends
on no broker-specific behaviour: a harness that would fail against EMQX,
NanoMQ or VerneMQ is a defective harness, not a configuration detail.

``paho-mqtt`` is a development dependency and is imported inside functions
rather than at module scope, so importing this module does not require it.
"""

from __future__ import annotations

import json
import os
import socket
import time
from contextlib import closing
from dataclasses import dataclass, field
from typing import Any

from .envelope import Announce, Event
from .topics import ONLINE, announce_topic, event_topic, is_retained, status_topic

DEFAULT_BROKER = "127.0.0.1:11883"


def broker_address() -> tuple[str, int]:
    """Broker host and port, from ``DATUM_BROKER`` or the default."""
    raw = os.environ.get("DATUM_BROKER", DEFAULT_BROKER)
    host, _, port = raw.partition(":")
    return host or "127.0.0.1", int(port or 1883)


def broker_reachable(timeout: float = 1.0) -> bool:
    """Whether a TCP connection to the broker succeeds.

    Used to decide whether the wire cookbook is collected at all. A test that
    silently passes without a broker would be worse than one that is skipped.
    """
    host, port = broker_address()
    try:
        with closing(socket.create_connection((host, port), timeout=timeout)):
            return True
    except OSError:
        return False


@dataclass
class Captured:
    """What a subscriber saw, in arrival order."""

    topic: str
    payload: str
    retained: bool


@dataclass
class Roundtrip:
    """The result of publishing an event and reading it back off the broker.

    ``late_*`` fields are what a subscriber that arrives *after* everything was
    published sees. That distinction is the whole point of the retention rules,
    and it is invisible to an in-process fixture: MQTT clears the retain flag on
    delivery to an already-established subscription, so retention can only be
    observed by joining late.
    """

    published: Event
    received: Captured | None = None
    late_announce: Captured | None = None
    late_status: Captured | None = None
    late_event: Captured | None = None
    problems: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems

    def verdict(self) -> str:
        """One line, stable enough to assert on in documentation."""
        return "round-trip ok" if self.ok else "; ".join(self.problems)


def _client(client_id: str) -> Any:
    from paho.mqtt import client as mqtt

    return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)


def roundtrip(event: Event, announce: Announce | None = None, timeout: float = 5.0) -> Roundtrip:
    """Publish an event over the documented topic and validate what comes back.

    Checks the whole contract rather than just delivery: that the payload
    arrives on the documented topic, survives JSON decoding, validates against
    the emitted schema, is byte-identical to what was sent, and that retention
    matches what the contract says for each topic.
    """
    from .conformance import accepts

    host, port = broker_address()
    result = Roundtrip(published=event)
    ev_topic = event_topic(event.src)
    an_topic = announce_topic(event.src)
    st_topic = status_topic(event.src)

    publisher = _client("datum-harness-pub")
    publisher.connect(host, port, keepalive=30)
    publisher.loop_start()

    # Retained topics outlive a run. Clear them so the late-subscriber phase
    # observes this run's publishes rather than a previous one's.
    _clear_retained(publisher, [an_topic, st_topic], timeout)

    live: list[Captured] = []
    subscriber = _client("datum-harness-sub")
    subscriber.on_message = lambda _c, _u, msg: live.append(
        Captured(msg.topic, msg.payload.decode("utf-8"), bool(msg.retain))
    )
    subscriber.connect(host, port, keepalive=30)
    subscriber.subscribe([(ev_topic, 1), (an_topic, 1)])
    subscriber.loop_start()

    try:
        if announce is not None:
            publisher.publish(
                an_topic, announce.wire_json(), qos=1, retain=is_retained(an_topic)
            ).wait_for_publish(timeout)
            publisher.publish(
                st_topic, ONLINE, qos=1, retain=is_retained(st_topic)
            ).wait_for_publish(timeout)
        publisher.publish(
            ev_topic, event.wire_json(), qos=1, retain=is_retained(ev_topic)
        ).wait_for_publish(timeout)
        _wait_for(live, ev_topic, timeout)
    finally:
        subscriber.loop_stop()
        subscriber.disconnect()

    result.received = next((c for c in live if c.topic == ev_topic), None)

    # A subscriber that arrives after the fact. Only retained topics reach it,
    # and only here does the retain flag mean what the contract says it means.
    late = _late_subscriber_view(host, port, [ev_topic, an_topic, st_topic], timeout)
    result.late_announce = next((c for c in late if c.topic == an_topic), None)
    result.late_status = next((c for c in late if c.topic == st_topic), None)
    result.late_event = next((c for c in late if c.topic == ev_topic), None)

    try:
        _clear_retained(publisher, [an_topic, st_topic], timeout)
    finally:
        publisher.loop_stop()
        publisher.disconnect()

    if result.received is None:
        result.problems.append(f"no message arrived on {ev_topic}")
        return result

    try:
        decoded = json.loads(result.received.payload)
    except json.JSONDecodeError as exc:
        result.problems.append(f"payload is not JSON: {exc}")
        return result

    if not accepts(decoded):
        result.problems.append("payload rejected by the emitted schema")
    if result.received.payload != event.wire_json():
        result.problems.append("payload differs from what was published")

    # The contract's retention rules, checked where they are observable.
    if result.late_event is not None:
        result.problems.append(
            f"{ev_topic} was retained; a late subscriber replayed a press it never saw happen"
        )
    if announce is not None:
        if result.late_announce is None:
            result.problems.append("announce did not reach a late subscriber; it must be retained")
        elif not result.late_announce.retained:
            result.problems.append("announce reached a late subscriber unretained")
        if result.late_status is None:
            result.problems.append("availability did not reach a late subscriber; it must be retained")

    return result


def _wait_for(seen: list[Captured], topic: str, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if any(c.topic == topic for c in seen):
            return
        time.sleep(0.02)


def _clear_retained(publisher: Any, topics: list[str], timeout: float) -> None:
    """A zero-byte retained publish removes a retained message."""
    for topic in topics:
        publisher.publish(topic, payload=None, qos=1, retain=True).wait_for_publish(timeout)


def _late_subscriber_view(
    host: str, port: int, topics: list[str], timeout: float, settle: float = 0.5
) -> list[Captured]:
    """What a subscriber joining now receives: retained topics only."""
    seen: list[Captured] = []
    client = _client("datum-harness-late")
    client.on_message = lambda _c, _u, msg: seen.append(
        Captured(msg.topic, msg.payload.decode("utf-8"), bool(msg.retain))
    )
    client.connect(host, port, keepalive=30)
    client.subscribe([(t, 1) for t in topics])
    client.loop_start()
    try:
        time.sleep(settle)
    finally:
        client.loop_stop()
        client.disconnect()
    return seen
