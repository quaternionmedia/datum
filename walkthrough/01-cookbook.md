# Cookbook — a switch for a light that has no switch

**Hermetic.**

Executable. Every `>>>` runs under `uv run pytest`.

Runs on a laptop: no board, no broker, no bulb. `Bus` is an in-process fixture
standing in for the MQTT broker; `Lamp` stands in for a listed bulb plus the
automation platform subscribing on its behalf. `Contact` is the half this
project builds — the dry contact, debounced, emitting the envelope.

`Bus` must never grow into an MQTT implementation. The broker is an engine
(`AGENTS.md`, "Non-negotiables"); `walkthrough/08-wire.md` runs the same contract against
a real one.

## Wiring a dumb momentary switch

Two wires into a screw terminal, and an identity.

    >>> from datum import Bus, Contact, Lamp
    >>> from datum import announce_topic, event_topic, status_topic

    >>> lamp = Lamp("kitchen pendant")
    >>> lamp
    <kitchen pendant: off>

    >>> bus = Bus()
    >>> button = Contact("datum/kitchen/north")
    >>> button.attach(bus)

Subscribe the lamp to the button's event topic and press it.

    >>> bus.subscribe(event_topic(button.src), lamp.handle)
    >>> _ = button.press()
    >>> lamp
    <kitchen pendant: on>

    >>> _ = button.press()
    >>> lamp
    <kitchen pendant: off>

No cloud service in the path, no account, no mains switched. The contact is
dry, the output is a signal, and actuation stayed inside the listed bulb.

## A consumer pinned to v1, reading an event from 2031

The module is later replaced by one reporting a torque axis and a grip object —
fields this schema does not define. The lamp's consumer is the one written
today.

    >>> from_2031 = '''{
    ...   "src": "datum/kitchen/north", "seq": 3,
    ...   "caps": ["press", "level", "torque", "grip"],
    ...   "action": "single", "ch": 0,
    ...   "level": 0.5,
    ...   "torque": 0.81,
    ...   "grip": {"fingers": 4, "pattern": "pinch"}
    ... }'''
    >>> bus.publish(event_topic(button.src), from_2031)
    >>> lamp
    <kitchen pendant: on>

The consumer read the `action` it understood, ignored the rest, and toggled.

This is Milestone 1's assertion 3 — the generational claim, reduced to
something CI fails on. `AGENTS.md`, "Definition of done", states what weakening
it would mean.

## Detention

A detent is the position a mechanism rests in. This one has two: **armed**,
accepting input, and **detained**, ignoring it.

Detention suppresses *actuation*, not *observation*: a detained press is still
published, on a different topic from the one the lamp listens to.

    >>> from datum import detained_topic, detent_topic
    >>> cat_log = []
    >>> bus.subscribe(detained_topic(button.src), cat_log.append)

    >>> button.detain()
    >>> bus.retained[detent_topic(button.src)]
    'detained'

Pressed twice while detained, the lamp does not move:

    >>> _ = button.press(); _ = button.press()
    >>> lamp
    <kitchen pendant: on>

Both presses are on the record:

    >>> len(cat_log)
    2

Arming restores the previous behaviour:

    >>> button.arm()
    >>> _ = button.press()
    >>> lamp
    <kitchen pendant: off>

`seq` advances through detention rather than pausing, so a gap in the sequence
means packet loss and nothing else:

    >>> import json
    >>> [json.loads(payload)["seq"] for payload in cat_log]
    [3, 4]

Detention is a topic rather than a payload field, and that is a decision with
alternatives: `governance/qm/adr/DRAFT-detention-suppresses-at-the-topic.md`.
