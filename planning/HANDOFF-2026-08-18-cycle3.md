# Handoff - 2026-08-18 (cycle 3)

Phased execution of WP-3 in Datum, on branch `wp3-firmware`. Not pushed, no
pull request opened.

## Session objective

Pick up the cycle-2 handoff and build the next round of improvements in phases,
each phase ending in a verifiable local check.

## The scope correction this cycle made

Cycle 2 recommended more IRL staging and treated the missing BOM as the gate on
everything hardware-adjacent. It is not. `AGENTS.md` fixes the work package
order and names WP-3 as next, and WP-3 needs one ESP32-C6 devkit — not a BOM
line. The ESPHome configuration, its README and its CI build were all
authorable now. That is what this cycle did.

The BOM still blocks WP-4. `planning/lanes/blocks.md` now says which.

## Phases completed

| Phase | Deliverable | Proof |
|---|---|---|
| 0 | Cycle-2 work committed to a branch | `uv run pytest` -> 11 passed, 1 skipped |
| 1 | `firmware/t1-core.yaml`, `firmware/contact.yaml`, `firmware/README.md` | not compiled locally; see below |
| 2 | `.github/workflows/firmware.yml` | not yet run; needs a pull request |
| 3 | `docs/firmware.md`, `schema/src/datum/firmware.py` | `uv run pytest` -> 19 passed, 1 skipped |
| 4 | State docs, lanes, decisions | this file |

## What Phase 3 is, and why it is the load-bearing part

`docs/wire.md` states the failure its broker harness cannot reach: a topic that
is right in the constant and wrong in the firmware. A broker only sees what it
was sent, so round-tripping never finds it.

`docs/firmware.md` compares the two directly and fails the build on drift:

- the topic suffixes in the YAML against `datum.topics`
- the firmware's own payload templates, filled in Python, byte for byte against
  `Event.wire_json()` and `Announce.wire_json()`
- every emitted gesture against the closed `Action` set
- every contact pin against the ESP32-C6 strapping, USB, UART and flash pins
- the announced `schema_version` against `SCHEMA_VERSION`

This is why the firmware keeps its wire strings in `substitutions:` and builds
payloads with `str_sprintf` instead of a JSON library. The gate is only
possible because the literals are readable as text.

## Verification evidence

```bash
cd /c/Users/peter/Documents/repos/qm/datum
uv run pytest
```

- `19 passed, 1 skipped` (`docs/wire.md` skipped, no local broker)
- Baseline at session start was `11 passed, 1 skipped`

```bash
uv run --with 'reuse[charset-normalizer]' reuse lint
```

- Compliant, 59 / 59 files carry copyright and licence information
- No `REUSE.toml` change needed: `firmware/*.yaml` takes MIT from the aggregate
  rule and `firmware/README.md` takes CC-BY-SA-4.0 from the `**.md` override,
  which is what WP-6 specifies for firmware and documentation

## What is not verified

- **The firmware does not compile here.** ESPHome is not installed locally and
  was not installed for this session. `esphome config` and `esphome compile`
  run only in `.github/workflows/firmware.yml`, which has not run because the
  branch is not pushed. Treat the configuration as unproven until it is green.
- **Nothing has been flashed.** Milestone assertion 2 still rides on the
  stand-in at `schema/vectors/captured/t1-core-single-press.json`.
- The ESPHome details most likely to be wrong on a first build, in order:
  `topic_prefix: null` with explicit birth and will messages; the
  `esp32_rmt_led_strip` options for a C6; script parameters reaching
  `str_sprintf`; the `on_multi_click` timing branches.

## Open blocks

- No ESP32-C6-DevKitC-1 on hand. The only thing between the configuration and
  a real capture.
- Q3 hardware licensing still needs human governance resolution.
- BOM not acquired — WP-4 only.

## Decisions recorded this cycle

Five, in `planning/lanes/decisions.md`. One is a draft record candidate: the
wire-literal discipline that makes the drift gate possible, which constrains
how the firmware may build payloads from here on.

Two questions were raised rather than decided:

- May a capture helper import `paho-mqtt` from the CLI? It is a development
  dependency and `AGENTS.md` calls a runtime import of one a review failure.
  This is why the capture helper cycle 2 recommended was not built.
- Is a preference-store write per press acceptable flash wear for `seq`?

Detention was deliberately not implemented. Q5 asks whether it may ever be
remote, and emitting detent state now would answer a live question by stealth.

## Recommended next actions

1. Push `wp3-firmware` and open the pull request. The firmware CI job has never
   run; that is the next real signal.
2. Fix whatever the ESPHome build reports.
3. Acquire one ESP32-C6-DevKitC-1, flash it, capture a real single press, and
   replace the stand-in vector. That closes WP-3 and unqualifies assertion 2.
4. In Apothecary, complete packaging inclusion for `parts/` and `templates/`.

## Notes for next operator

- `planning/DEV_LOOP.md` is still the session entrypoint.
- `HANDOFF.md` **State on arrival** was updated and says in bold that nothing
  has been flashed. Do not read a green firmware build as a working button.
- Branch is `wp3-firmware`, five commits, nothing pushed.
