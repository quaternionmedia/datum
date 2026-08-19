# HIL review checklist for Datum

## Status

This checklist tracks work that is ready to continue locally versus work that should be reviewed in a hardware-in-the-loop (HIL) pass once the BOM is available.

## Locally completed

- [x] Repo baseline confirmed with the project’s actual test suite
- [x] Local verification command: `uv run pytest`
- [x] Result: 11 passed, 1 skipped
- [x] Governance brief reviewed: `AGENTS.md`, `HANDOFF.md`, `PLAN.md`
- [x] Project constraints and non-negotiables reviewed against the existing design brief

## Ready for HIL review after BOM acquisition

### BOM and parts review

- [ ] Confirm BOM matches T1 Core architecture and USB-C bus-power assumption
- [ ] Verify that every BOM line has two independent sources or documented alternate footprint
- [ ] Check availability, lead time, and footprint compatibility for all parts
- [ ] Flag any single-source or high-risk parts before schematic signoff
- [ ] Confirm C6 module and USB connector choice match the intended radio and power plan

### Governance and compliance gate

- [ ] Review Q3 hardware licensing issue with human approver before release or public sharing
- [ ] Confirm REUSE compliance remains intact for hardware artifacts
- [ ] Confirm dependency-manifest license gate is tracked or added before final release
- [ ] Keep all code and hardware work on a branch and under PR flow per `AGENTS.md`
- [ ] Ensure no design decisions are made by stealth around open questions in `HANDOFF.md`

### Schematic and board validation

- [ ] Create KiCad project under `hardware/<board>/`
- [ ] Validate USB-C sink wiring, CC resistors, and D+/D- routing
- [ ] Validate 3.3 V regulator sizing and decoupling against C6 load assumptions
- [ ] Validate contact-input RC network and ESD strategy
- [ ] Validate indicator LED net and power routing
- [ ] Run ERC and DRC checks
- [ ] Review the BOM against the netlist and footprint mapping

### Firmware bring-up

- [ ] Implement or configure ESPHome path for T1 Core
- [ ] Confirm contact input handling, debounce, and event generation
- [ ] Confirm MQTT topic emission and retained-message behavior against the documented contract
- [ ] Validate event serialization against the schema plus the compatibility rules
- [ ] Capture a real firmware event and compare it to the contract

### Enclosure and integration

- [ ] Review the board outline against fit and mounting assumptions
- [ ] Publish or update apothecary-side geometry and envelope integration
- [ ] Keep all printable geometry in `quaternionmedia/apothecary` as required
- [ ] Validate fit between board, case, USB, and indicator opening

### Release and QA

- [ ] Re-run docs/tests after hardware changes are made
- [ ] Verify the MQTT contract still passes with the actual device output
- [ ] Review local build outputs and fabrication artifacts for reproducibility
- [ ] Confirm no open governance or Q-number escalations remain unresolved

## Suggested HIL review order

1. BOM and design assumptions
2. Schematic and ERC/DRC pass
3. Firmware bring-up and MQTT validation
4. Board fit and enclosure review
5. Compliance and release signoff

## Verified local command

```bash
cd /c/Users/peter/Documents/repos/qm/datum
uv run pytest
```

Observed result at last check: `11 passed, 1 skipped in 12.46s`.
