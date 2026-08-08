"""The retrofit demo: put a physical switch back on a light that lost one.

The two objects here stand in for things this project does not build. ``Lamp``
stands in for a listed smart bulb plus whatever automation platform subscribes
on its behalf — Home Assistant is the engine and is not being reimplemented; a
toggle in nine lines is a stand-in so the cookbook can assert an outcome.
``Contact`` is the half this project does build: a dumb momentary switch on a
screw terminal, and the T1-Core that debounces it and emits the envelope.

No mains is switched anywhere in this file or the hardware it models. The
contact is dry, the output is a signal, and the actuation belongs to a listed
device downstream.
"""

from __future__ import annotations

from .bus import Bus
from .envelope import Action, Announce, Event
from .topics import OFFLINE, ONLINE, announce_topic, event_topic, status_topic


class Lamp:
    """A smart bulb with no physical control, and the consumer that toggles it.

    The consumer is pinned to v1 of the schema: it parses with the models as
    they exist today and branches on ``action`` alone. That pinning is what
    makes the forward-compatibility demonstration in the cookbook meaningful —
    an unpinned consumer proves nothing.
    """

    def __init__(self, name: str, on: bool = False) -> None:
        self.name = name
        self.on = on

    def __repr__(self) -> str:
        return f"<{self.name}: {'on' if self.on else 'off'}>"

    def handle(self, payload: str) -> None:
        """Toggle on a single press. Ignore every other gesture."""
        event = Event.model_validate_json(payload)
        if event.action is Action.SINGLE:
            self.on = not self.on


class Contact:
    """A dry contact and the module that reads it.

    ``seq`` is monotonic across the object's whole life, including across
    reconnection: ``attach`` does not reset it. A consumer detects loss and
    replay by watching for gaps, which only works if the counter survives the
    thing that most often causes gaps.
    """

    def __init__(
        self,
        src: str,
        caps: tuple[str, ...] = ("press",),
        ch: int = 0,
        hw: str = "t1-core-r0",
        fw: str = "0.1.0",
    ) -> None:
        self.src = src
        self.caps = list(caps)
        self.ch = ch
        self.hw = hw
        self.fw = fw
        self._seq = 0
        self._bus: Bus | None = None

    def announce(self) -> Announce:
        """What this module advertises before emitting anything."""
        return Announce(src=self.src, caps=self.caps, hw=self.hw, fw=self.fw)

    def attach(self, bus: Bus) -> None:
        """Come online: publish the retained announce and availability."""
        self._bus = bus
        bus.publish(announce_topic(self.src), self.announce().wire_json())
        bus.publish(status_topic(self.src), ONLINE)

    def detach(self) -> None:
        """Go offline. Stands in for the broker's last-will on an ungraceful drop."""
        if self._bus is not None:
            self._bus.publish(status_topic(self.src), OFFLINE)
            self._bus = None

    def emit(self, action: Action | str, **axes: object) -> Event:
        """Build the next event, publish it if attached, and return it."""
        self._seq += 1
        event = Event(
            src=self.src,
            seq=self._seq,
            caps=self.caps,
            action=Action(action),
            ch=self.ch,
            **axes,  # type: ignore[arg-type]
        )
        if self._bus is not None:
            self._bus.publish(event_topic(self.src), event.wire_json())
        return event

    def press(self) -> Event:
        """One deliberate press — the gesture a light switch makes."""
        return self.emit(Action.SINGLE)
