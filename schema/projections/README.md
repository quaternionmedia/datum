# Projections

Every transport carries the envelope directly, or carries a **documented
projection** of it. A projection that cannot carry an axis says which axis it
drops. Documenting the loss is the obligation; pretending it does not exist is
the failure mode.

Only the MQTT row is populated. The rest are named and empty on purpose — a
transport gets a row when it gets an implementation and its own vectors, not
when someone thinks it might be nice to support.

| Transport | `action` | `ch` | `level` | `vec` | `color` | `batt` | Status |
|---|---|---|---|---|---|---|---|
| **MQTT / JSON** | yes | yes | yes | yes | yes | yes | The canonical form. Not a projection at all: the envelope goes on the wire verbatim as UTF-8 JSON, one event per message on `<src>/event`. Nothing is dropped, so there is nothing to document beyond the topic contract in the root `README.md`. |
| **USB MIDI** | | | | | | | Not written. |
| **Zigbee** | | | | | | | Not written. |
| **BTHome v2** | | | | | | | Not written. |
| **Matter** | | | | | | | Not written. |

## What a row owes when it is filled in

1. A statement of which axes survive and which are dropped, per the columns
   above.
2. Its own vectors under `schema/vectors/`, so the projection is checked in CI
   rather than described.
3. The reverse direction where one exists: whether a consumer can reconstruct
   an envelope from the projected form, and what it cannot recover.

The expectation is that some of these are lossy and say so. A BTHome
advertisement has a tight payload budget and will not carry a full colour
object and a position vector in one broadcast.
