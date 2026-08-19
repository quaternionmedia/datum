# Blocks and risks lane

Use this file for blockers that can prevent HIL completion or release readiness.

## Open blocks

- [ ] Q3 hardware licensing path still needs human governance resolution before release-signoff.
- [ ] BOM not yet acquired; hardware validation steps are staged but not executable.
      Scope correction: this blocks WP-4, not WP-3. WP-3 needs one ESP32-C6
      devkit, which is not a BOM item.
- [ ] No ESP32-C6-DevKitC-1 on hand. This is the only thing between the
      firmware configuration and closing milestone assertion 2.
- [ ] Firmware compile is unverified. `esphome config` passes locally, but
      `esphome compile` fails on this Windows machine installing the ESP-IDF
      5.5.5 framework -- an environment failure, reached after codegen and
      before the compiler. CI on Linux is what settles it.
- [ ] datum-core enclosure dimensions are assumptions. No schematic exists to
      check the footprint, connector height, indicator position or the tallest
      component that sets headroom.

## Risk template

- Risk:
- Trigger:
- Impact:
- Owner:
- Next action:
- Target date:

## Risk log

- Risk: a green firmware CI build is mistaken for a working button
- Trigger: WP-3 looks complete in the tree while nothing has been flashed
- Impact: assertion 2 reported green when it is still riding a stand-in vector
- Owner: planning loop
- Next action: HANDOFF.md State on arrival says so in bold; keep it there until
  a real capture replaces schema/vectors/captured/t1-core-single-press.json
- Target date: when a devkit is available


- Risk: IRL validation scope creep
- Trigger: Matrix exists but may expand without a minimum pass set guard
- Impact: Delayed HIL signoff
- Owner: planning loop
- Next action: Keep IRL-001..IRL-004 as minimum required set; treat all additions as optional until promoted
- Target date: next iteration
