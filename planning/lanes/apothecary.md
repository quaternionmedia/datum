# Apothecary lane

## Objective

Drive enclosure and fit functionality as a first-class iteration partner to Datum.

## Current state

- Work is planned as a balanced split with Datum.
- Functional requirements are not yet decomposed into verifiable checks.
- Known upstream backlog exists in apothecary TODO and can be used directly.

## Next actions

- [ ] Define first-pass enclosure functionality checklist (fit, USB opening, indicator visibility, mounting).
- [ ] Identify minimum parameter contract needed from Datum board assumptions.
- [ ] Propose one iteration that can be validated before full hardware availability.
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

## Done criteria for this lane

- Functional enclosure requirements are explicit and testable.
- Cross-repo dependency on board assumptions is documented.
