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
| IRL-005 | Topic contract | Announce publish | Announce topic payload retained and replayed to late subscriber | `uv run python -c "from datum.harness import roundtrip; print('manual harness step in docs/wire.md')"` |
| IRL-006 | Topic contract | Status publish | Status topic retained and replayed to late subscriber | `uv run python -c "from datum.harness import roundtrip; print('manual harness step in docs/wire.md')"` |
| IRL-007 | Topic contract | Event publish | Event topic not retained for late subscriber | `uv run python -c "from datum.harness import roundtrip; print('manual harness step in docs/wire.md')"` |

## Pass criteria

- Required schema tests IRL-001..IRL-004 pass/fail exactly as expected.
- Retention contract in IRL-005..IRL-007 matches `docs/topic-contract.md`.
- Every test case produces a report artifact and capture file.

## Failure handling

- Record failing case ID and attach report JSON path.
- Add blocker entry in planning/lanes/blocks.md with trigger and next action.
- Do not change contract behavior without documenting a decision in planning/lanes/decisions.md.
