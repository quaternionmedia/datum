# Apothecary lane

## Objective

Drive enclosure and fit functionality as a first-class iteration partner to Datum.

## Current state

- Work is planned as a balanced split with Datum.
- Functional requirements are not yet decomposed into verifiable checks.
- Known upstream backlog exists in apothecary TODO and can be used directly.

## Next actions

- [x] Define first-pass enclosure functionality checklist (fit, USB opening, indicator visibility, mounting).
- [x] Identify minimum parameter contract needed from Datum board assumptions.
- [x] Propose one iteration that can be validated before full hardware availability.
- [ ] Check the datum_core dimensions against a real schematic when WP-4 exists.
- [x] Build the tooling to iterate the enclosure without editing source between
      attempts: `-p name=value` overrides and a declared-vs-measured bounds gate.
- [x] Add OpenSCAD readiness output to `apothecary check` for faster local diagnosis.

## Imported upstream backlog (apothecary)

- [ ] Fix JSCAD import syntax and add regression test.
- [ ] Include parts/templates in packaging artifacts.
- [x] Sanitize parts endpoints to avoid absolute path leakage.
- [ ] Add OpenSCAD availability check to apothecary check command.

## Suggested near-term split

- Enclosure functionality: fit contract and geometry iteration hooks.
- Platform hygiene: packaging, JSCAD imports, path sanitization.

## Evidence log

- 2026-08-18: lane initialized from dual-repo planning intake.
- 2026-08-18: imported active backlog from apothecary TODO.
- 2026-08-18: updated check command to report OpenSCAD availability/version.
- 2026-08-18: `uv run pytest tests/test_cli.py -q` passed (3 tests).
- 2026-08-18: API path sanitization landed for part metadata/include fields.
- 2026-08-18: `uv run pytest tests/test_api.py tests/test_cli.py -q` passed (12 tests).
- 2026-08-18: `apothecary serve` and `apothecary check` both died on Windows --
  cp1252 cannot encode the check mark they print first. 45 call sites across
  check, serve, testing and parts now go through `_safe_echo`.
- 2026-08-18: added the `datum_core` part: parametric tray and lid, four
  standoffs, edge-connector cutout, indicator light pipe, four contact openings.
- 2026-08-18: `apothecary parts info datum_core` reports bounds 45.6 x 45.6 x
  15.6 mm; `apothecary parts generate-stl datum_core` exits 0.
- 2026-08-18: `uv run pytest tests/test_api.py tests/test_cli.py -q` -> 15 passed.
- 2026-08-18: server up on :8765, `datum_core` present in `/parts`, in the
  `parts_library` site tree, and reachable at
  `/viewer/sites/parts_library?focus=datum_core`.

## Done criteria for this lane

- Functional enclosure requirements are explicit and testable.
- Cross-repo dependency on board assumptions is documented.

## Iteration tooling (2026-08-19)

The loop is now `generate-stl -p` then `verify -p`, with the viewer reloading.
`docs/iterating-a-part.md` in apothecary carries the reference.

- Parameter overrides reach OpenSCAD as `-D`, on the CLI and over HTTP, and are
  validated against the part's own model first. OpenSCAD accepts any `-D` name
  whether the file defines it or not, so an unvalidated typo renders the
  defaults and exits 0 -- which reads as a successful render of the wrong thing.
- Each render records its inputs in a sidecar, because a variant lands at the
  canonical STL path and is otherwise indistinguishable from a default.
- `apothecary parts verify` measures the rendered bounding box against the
  wrapper's declared bounds and exits non-zero on drift.

### What the gate found

Four of the six parts declaring bounds are wrong. Only `calibration_cube` and
`datum_core` agree with their geometry.

| Part | Declared | Measured |
|---|---|---|
| V-Slot | 20 x 20 x 100 | 20 x 20 x 20 |
| couch_block | 40 x 40 x 20 | 152.4 x 101.6 x 50.8 |
| dryerknob | 30 x 30 x 15 | 33 x 33 x 20 |
| parametric_star | 40 x 40 x 2 | 27.14 x 28.53 x 3 |

Recorded in apothecary's `todo.md`, not fixed: which side is authoritative
belongs to whoever owns each part.

It also caught one of ours. `datum_core`'s exploded preview declared 32.6 mm and
measured 29.6 -- the lid's lip hung into the gap, so `explode_gap` was not the
separation it claimed. Fixed in the geometry rather than in the number.

