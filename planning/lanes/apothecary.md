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
- [ ] Check the datum-core dimensions against a real schematic when WP-4 exists.
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
- 2026-08-18: added the `datum-core` part: parametric tray and lid, four
  standoffs, edge-connector cutout, indicator light pipe, four contact openings.
- 2026-08-18: `apothecary parts info datum-core` reports bounds 45.6 x 45.6 x
  15.6 mm; `apothecary parts generate-stl datum-core` exits 0.
- 2026-08-18: `uv run pytest tests/test_api.py tests/test_cli.py -q` -> 15 passed.
- 2026-08-18: server up on :8765, `datum-core` present in `/parts`, in the
  `parts_library` site tree, and reachable at
  `/viewer/sites/parts_library?focus=datum-core`.

## Done criteria for this lane

- Functional enclosure requirements are explicit and testable.
- Cross-repo dependency on board assumptions is documented.
