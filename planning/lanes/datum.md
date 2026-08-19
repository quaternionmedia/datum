# Datum lane

## Objective

Advance schema-to-firmware-to-HIL readiness with verifiable local checkpoints.

## Current state

- Local baseline is green: 11 passed, 1 skipped via uv run pytest.
- HIL checklist exists and is ready for BOM-driven execution.

## Next actions

- [x] Define post-BOM IRL test matrix (event validity, topic contract, retained semantics).
- [ ] Prepare firmware evidence checklist for first real device capture.
- [ ] Define acceptance criteria for schematic validation before board fab.
- [ ] Exercise `datum validate --report` on first captured firmware payload.

## Working artifacts

- IRL test matrix: planning/IRL_TEST_MATRIX.md

## Evidence log

- 2026-08-18: uv run pytest -> 11 passed, 1 skipped.
- 2026-08-18: added `datum validate --report` for machine-readable validation output.
- 2026-08-18: `uv run pytest` -> 11 passed, 1 skipped.
- 2026-08-18: added planning/IRL_TEST_MATRIX.md for post-BOM first-device validation.
- 2026-08-18: `uv run pytest` -> 11 passed, 1 skipped.

## Done criteria for this lane

- A BOM-backed HIL test matrix exists.
- First real firmware event can be validated against documented contract.
