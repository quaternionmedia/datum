# Datum lane

## Objective

Advance schema-to-firmware-to-HIL readiness with verifiable local checkpoints.

## Current state

- Local baseline is green: 19 passed, 1 skipped via uv run pytest.
- HIL checklist exists and is ready for BOM-driven execution.
- WP-3 firmware configuration exists and is checked against the constants.
  Nothing has been flashed, so WP-3 is open and assertion 2 stays qualified.

## Next actions

- [x] Define post-BOM IRL test matrix (event validity, topic contract, retained semantics).
- [x] Author the WP-3 ESPHome configuration for the ESP32-C6 devkit.
- [x] Gate firmware/Python wire drift as an executable check (`docs/firmware.md`).
- [x] Build the firmware configuration in CI (`.github/workflows/firmware.yml`).
- [x] Validate the configuration locally: `esphome config` on ESPHome 2026.7.4.
- [ ] Confirm the CI firmware build is green. `esphome compile` fails on this
      Windows machine at ESP-IDF 5.5.5 framework installation, before it reaches
      the code, so the compile itself is still unproven.
- [ ] Flash a devkit, capture a real event, replace the stand-in vector.
- [ ] Prepare firmware evidence checklist for first real device capture.
- [ ] Define acceptance criteria for schematic validation before board fab.
- [ ] Exercise `datum validate --report` on first captured firmware payload.
- [ ] Decide whether a capture helper may use paho-mqtt from the CLI, or
      whether capture stays a `mosquitto_sub` step outside the package.

## Working artifacts

- IRL test matrix: planning/IRL_TEST_MATRIX.md
- Firmware: firmware/t1-core.yaml, firmware/contact.yaml, firmware/README.md
- Drift gate: docs/firmware.md, schema/src/datum/firmware.py

## Evidence log

- 2026-08-18: uv run pytest -> 11 passed, 1 skipped.
- 2026-08-18: added `datum validate --report` for machine-readable validation output.
- 2026-08-18: `uv run pytest` -> 11 passed, 1 skipped.
- 2026-08-18: added planning/IRL_TEST_MATRIX.md for post-BOM first-device validation.
- 2026-08-18: `uv run pytest` -> 11 passed, 1 skipped.
- 2026-08-18: added firmware/t1-core.yaml and firmware/contact.yaml (WP-3).
- 2026-08-18: added docs/firmware.md; firmware topics and payloads verified
  byte-identical to datum.topics and Event/Announce.wire_json().
- 2026-08-18: `uv run pytest` -> 19 passed, 1 skipped.
- 2026-08-18: `reuse lint` -> compliant, 59/59 files covered, no REUSE.toml change needed.
- 2026-08-18: installed ESPHome 2026.7.4 and ran `esphome config` for the first
  time. It failed: `${...}` contains a brace, and a brace is a flow indicator,
  so no substitution inside a flow mapping parsed. Every `packages:` include and
  every `script.execute:` call was affected. Rewritten in block style.
- 2026-08-18: `esphome config firmware/t1-core.yaml` -> Configuration is valid.
  Topics, payload templates, birth/will and `topic_prefix: null` all resolve as
  intended; one expected warning, GPIO8 is a strapping pin.
- 2026-08-18: `esphome compile` reached codegen and then failed installing the
  ESP-IDF 5.5.5 framework on Windows. The generated main.cpp was inspected:
  `script::Script<int, std::string>`, `set_args` returning a real `int`, and
  `seq->value()++` into `str_sprintf`. `ch` changed from `%u` to `%d` to match.
- 2026-08-18: `uv run pytest` -> 19 passed, 1 skipped after all of the above.

## Done criteria for this lane

- A BOM-backed HIL test matrix exists.
- First real firmware event can be validated against documented contract.
