# Questions lane

Use this as the intake queue and active question tracker.

## Active questions

- [ ] May a capture helper import paho-mqtt from the CLI? It is a development
      dependency and AGENTS.md calls a runtime import of one a review failure,
      so this is a stack question rather than a design preference.
- [ ] Is a preference-store write per press acceptable flash wear for `seq`,
      or should restore be dropped to RAM-only between reboots?
- [x] What is the minimum IRL test matrix needed to validate T1 behavior after BOM arrival?
- [ ] Which apothecary capabilities are required first for Datum enclosure iteration?
- [ ] What cross-repo contract needs to be frozen first: board outline, connector opening, or mounting points?

## Newly captured from intake

- [x] IRL test — matrix staged at planning/IRL_TEST_MATRIX.md
- [ ] Apothecary functionality

## Parking lot

- [ ] Do we need an explicit pass/fail threshold for retained-message behavior in HIL?
- [ ] Should enclosure fit checks be automated from a board dimension export step?

## Weekly pruning rule

Keep only actionable questions in Active. Move stale items to Parking lot.
