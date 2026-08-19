# IRL test matrix (post-BOM)

This matrix is for first-device hardware-in-the-loop validation once BOM-backed hardware is available.

## Scope

- Validate that physical input behavior maps to the documented Datum envelope.
- Validate topic and retention contract over a real broker.
- Produce machine-readable validation evidence per run.

## Preconditions

- Device hardware assembled from approved BOM
- Firmware configured to emit Datum envelope
- Broker reachable via DATUM_BROKER
- Local toolchain available in this repo

## Before any of this

Run `uv run datum hil`. Everything provable without hardware is proven
there, and the cases below are what it reports as still open. Starting here
means a failure at the bench is a hardware or firmware finding rather than
something that was already broken on the desk.

## Retention is only observable if you arrive late

IRL-005 through IRL-007 all depend on this and it is the thing that surprises
people. MQTT clears the retain flag when delivering to a subscription that was
*already established*. A subscriber watching the publish happen sees `retain=0`
even for a message the broker retained. So every retention case has to be
checked by a subscriber that connects **after** the publish, which is exactly
the consumer the rule exists for.

## Evidence artifacts

- CLI report: `schema/build/reports/<case>.json` via `datum validate --report`
- Raw captured payload: `schema/build/captures/<case>.json`
- Test notes: append result line to planning/lanes/datum.md evidence log

## Test cases

| ID | Category | Stimulus | Expected | Validation command |
|---|---|---|---|---|
| IRL-001 | Event schema | Single press | One valid event, `action=single`, required fields present | `uv run datum validate schema/build/captures/irl-001-single.json --report schema/build/reports/irl-001-single.json` |
| IRL-002 | Event schema | Hold then release | Two valid events with expected actions | `uv run datum validate schema/build/captures/irl-002-hold-release.json --report schema/build/reports/irl-002-hold-release.json` |
| IRL-003 | Sequence rule | Ordered multi-press | Array validates and monotonic sequence passes | `uv run datum validate schema/build/captures/irl-003-seq-ok.json --report schema/build/reports/irl-003-seq-ok.json` |
| IRL-004 | Sequence rule | Intentionally reordered replay sample | Validation fails with monotonic violation | `uv run datum validate schema/build/captures/irl-004-seq-bad.json --report schema/build/reports/irl-004-seq-bad.json` |
| IRL-005 | Topic contract | Announce publish | Announce topic payload retained and replayed to late subscriber | `mosquitto_sub -h $BROKER -t 'datum/lab/jig/announce' -C 1 -v` from a *late* subscriber, after the device booted |
| IRL-006 | Topic contract | Status publish | Status topic retained and replayed to late subscriber | `mosquitto_sub -h $BROKER -t 'datum/lab/jig/status' -C 1 -v`, then pull power and repeat -- expect `offline` |
| IRL-007 | Topic contract | Event publish | Event topic not retained for late subscriber | press, then `mosquitto_sub -h $BROKER -t 'datum/lab/jig/event' -W 3` -- expect nothing, and a timeout is the pass |

## Pass criteria

- Required schema tests IRL-001..IRL-004 pass/fail exactly as expected.
- Retention contract in IRL-005..IRL-007 matches `walkthrough/03-topic-contract.md`.
- Every test case produces a report artifact and capture file.

## Failure handling

- Record failing case ID and attach report JSON path.
- Add blocker entry in planning/lanes/blocks.md with trigger and next action.
- Do not change contract behavior without documenting a decision in planning/lanes/decisions.md.
