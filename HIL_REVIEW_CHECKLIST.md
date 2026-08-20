# HIL review checklist

What is proven, what is proven only on paper, and what needs a board on a
bench. The split matters: this project has been careful about not reporting a
skipped assertion as a pass, and this file follows the same rule.

## Run this first

```bash
uv run datum hil
```

One command, no servers, nothing left running. It proves everything provable
without hardware and prints the remaining IRL cases. See
[`walkthrough/07-hil.md`](walkthrough/07-hil.md).

## Proven, locally and repeatably

- [x] `uv run pytest` is green. The count is not written here: a number beside
      a suite that grows is a second copy of what the suite already reports
- [x] The skip is `walkthrough/08-wire.md`, which needs a broker and says so
- [x] Ten checked-in vectors: six accepted, four rejected, each leaving a report
- [x] A v1-pinned consumer parses a capability-extended event and yields an
      identical `action` — milestone assertion 3, the one that matters
- [x] `esphome config firmware/t1-core.yaml` reports the configuration valid
      on ESPHome 2026.7.4
- [x] The firmware seam holds: topics and payload templates read back out of
      the YAML match the Python constants byte for byte
- [x] `apothecary parts verify datum-core` — declared bounds match geometry
- [x] `reuse lint` clean
- [x] Governance brief reviewed: `AGENTS.md`, `HANDOFF.md`, `PLAN.md`

## Proven only on paper

Written down, internally consistent, and never executed against the thing it
describes.

- [ ] **The firmware has never been compiled.** `esphome compile` reaches
      codegen and fails installing the ESP-IDF framework on Windows, before the
      compiler runs. `.github/workflows/firmware.yml` on Linux is the only
      thing that can settle it, and it has not run because nothing is pushed.
- [ ] **The enclosure has never been fitted to anything.** Every dimension in
      `datum-core` is an assumption; no schematic exists to check it against.
- [ ] **No BOM.** Every hardware line below is staged, not executable.

## Needs a board on a bench

### Firmware bring-up

- [x] ESPHome configuration written for T1-Core and validated
- [ ] Flash an ESP32-C6-DevKitC-1 and confirm it boots
- [ ] IRL-001 — single press emits one event, `action=single`
- [ ] IRL-002 — hold then release emits two events, in that order
- [ ] IRL-003 — ordered multi-press keeps `seq` monotonic across a run
- [ ] IRL-004 — `seq` survives a reconnect without going backwards
- [ ] IRL-005 — announce retained, reaches a late subscriber
- [ ] IRL-006 — availability retained, last-will fires on an ungraceful drop
- [ ] IRL-007 — an event is **not** retained; a late subscriber sees nothing
- [ ] Replace `schema/vectors/captured/t1-core-single-press.json` with a real
      capture. That one file is all that qualifies milestone assertion 2
- [ ] Confirm no contact sits on a strapping pin in practice, not just on paper

Stimulus and expected result for each case:
[`planning/IRL_TEST_MATRIX.md`](planning/IRL_TEST_MATRIX.md). GPIO map and jig
wiring: [`firmware/README.md`](firmware/README.md).

### BOM and parts review

- [ ] Confirm the BOM matches T1-Core architecture and the USB-C bus-power assumption
- [ ] Every BOM line has two independent sources or a documented alternate footprint
- [ ] Availability, lead time and footprint compatibility for all parts
- [ ] Flag single-source or high-risk parts before schematic signoff
- [ ] Confirm the C6 module and USB connector match the intended radio and power plan

### Schematic and board validation

- [ ] Create the KiCad project under `hardware/t1-core/`
- [ ] CC1 and CC2 each terminate through 5.1 kΩ — omitting these produces a
      board that works on a legacy A-to-C cable and draws nothing from a
      compliant Type-C source
- [ ] 3.3 V LDO rated ≥ 600 mA against a Wi-Fi transmit peak near 350 mA
- [ ] Antenna keepout per the module datasheet: no copper, no pour, board edge
- [ ] Contact-input RC network and ESD strategy
- [ ] SK6812 indicator on the 3.3 V rail, so no level shifter is needed
- [ ] `kibot` ERC and DRC exit 0 — milestone assertion 4
- [ ] BOM checked against the netlist and footprint mapping

### Enclosure and integration

- [x] Publish apothecary-side geometry — `datum-core`, tray and lid
- [x] `apothecary parts info datum-core` returns non-null bounds, STL exits 0 —
      milestone assertion 5
- [ ] Re-fit every assumed dimension against the real board outline
- [ ] Validate fit between board, case, USB opening and indicator opening
- [ ] Confirm the indicator is visible through its opening on a printed part

### Governance and compliance

- [ ] **Q3, hardware licensing** — a missing org mechanism, not a choice of
      venue. Needs a human. No dependency report can see a `.kicad_sch`
- [ ] Dependency-manifest licence gate wired — milestone assertion 6's other half
- [ ] Confirm REUSE compliance holds once hardware artifacts land
- [ ] All work stays on a branch and under PR flow per `AGENTS.md`
- [ ] No open question in `HANDOFF.md` §2 decided by stealth

## Suggested review order

1. Run `uv run datum hil` and read the table
2. Push, so CI compiles the firmware for the first time
3. BOM and design assumptions
4. Schematic, ERC/DRC
5. Flash a devkit, work IRL-001 through IRL-007
6. Board fit against the printed enclosure
7. Compliance and release signoff
