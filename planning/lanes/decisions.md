# Decisions lane

Record high-discipline decisions with context and consequences.

## Template

- Date:
- Scope: Datum | Apothecary | Integration
- Decision:
- Why now:
- Evidence:
- Consequences:
- Follow-up:
- Governance impact: none | review needed | draft record candidate

## Decision log

- Date: 2026-08-18
- Scope: Integration
- Decision: Use a lane-based, question-first dual-repo loop with checklist-delta reviews.
- Why now: Need a methodical planning and iteration system before BOM-driven HIL work.
- Evidence: Existing repo baseline is green and HIL checklist is present.
- Consequences: Iterations are tracked by lane and must carry verification evidence.
- Follow-up: Populate each lane with one active objective per cycle.
- Governance impact: review needed

- Date: 2026-08-18
- Scope: Datum
- Decision: Add `datum validate --report` to emit machine-readable validation summaries.
- Why now: HIL and IRL loops need script-friendly proof artifacts, not only terminal text.
- Evidence: Datum suite remains green after docs and CLI update.
- Consequences: First device captures can be archived with validation metadata.
- Follow-up: Standardize report location in HIL workflow notes.
- Governance impact: none

- Date: 2026-08-18
- Scope: Apothecary
- Decision: Extend `apothecary check` to report OpenSCAD readiness and version.
- Why now: Fast diagnosis of geometry toolchain readiness is needed for iteration cadence.
- Evidence: Targeted CLI tests pass after command change.
- Consequences: Setup failures are surfaced earlier before STL tasks are attempted.
- Follow-up: Decide if check output should become machine-readable later.
- Governance impact: none

- Date: 2026-08-18
- Scope: Apothecary
- Decision: Sanitize part metadata/include path fields to avoid absolute local path leakage.
- Why now: Backlog item was actionable locally and directly improves safe sharing in reviews.
- Evidence: Focused API and CLI tests pass after update.
- Consequences: `/parts` responses now expose repository-relative paths.
- Follow-up: Confirm whether any additional endpoints expose local absolute paths.
- Governance impact: none

- Date: 2026-08-18
- Scope: Datum
- Decision: Introduce a formal post-BOM IRL test matrix artifact for HIL execution.
- Why now: Enables methodical execution once hardware is available and aligns with lane-based loop.
- Evidence: Matrix added and local repo tests remain green.
- Consequences: HIL runs have explicit case IDs, expected outcomes, and report paths.
- Follow-up: Add capture automation helper when first device events are available.
- Governance impact: review needed

- Date: 2026-08-18
- Scope: Datum
- Decision: Proceed to WP-3 firmware rather than continue IRL staging.
- Why now: The work package order is fixed by AGENTS.md and WP-3 is next. The
  BOM blocks WP-4, not WP-3 — an ESPHome configuration, its README and a CI
  build need no BOM line. The previous cycle treated the BOM as blocking more
  than it blocks.
- Evidence: firmware/ landed; `uv run pytest` -> 19 passed, 1 skipped; `reuse
  lint` compliant.
- Consequences: WP-3 is open rather than next. Assertion 2 stays qualified
  until a flashed device produces a real capture.
- Follow-up: Acquire one ESP32-C6-DevKitC-1 and replace the stand-in vector.
- Governance impact: none

- Date: 2026-08-18
- Scope: Datum
- Decision: Keep every wire-critical string in the firmware's `substitutions:`
  block, and build payloads from printf templates rather than a JSON library.
- Why now: docs/wire.md names a topic that is right in Python and wrong in the
  firmware as the failure its broker harness cannot reach. Literals in a
  substitutions block can be read back as text and compared to the constants;
  literals buried in a lambda cannot, and a JSON library's spacing and key
  order are not ours to fix.
- Evidence: docs/firmware.md fills the firmware's own templates in Python and
  they match Event.wire_json() and Announce.wire_json() byte for byte.
- Consequences: Renaming a topic suffix or reordering an envelope field turns
  the build red until the firmware is changed with it. The firmware may not
  adopt a JSON builder without replacing this gate with an equivalent one.
- Follow-up: Extend the gate to the detent topics if detention is ever emitted.
- Governance impact: draft record candidate

- Date: 2026-08-18
- Scope: Datum
- Decision: Do not implement detention in WP-3 firmware.
- Why now: Detention is local today and Q5 asks whether a controller may set it
  remotely. Emitting detent state from firmware would answer a live question by
  stealth, which AGENTS.md names a governance violation rather than a shortcut.
- Evidence: The detent and detained topics exist in datum.topics and are
  unreferenced by firmware/.
- Consequences: The firmware publishes announce, status and events only.
- Follow-up: Revisit once Q5 is decided by a human.
- Governance impact: review needed

- Date: 2026-08-18
- Scope: Datum
- Decision: Restore `seq` from the ESPHome preference store rather than hold it
  in RAM.
- Why now: WP-3 asks for a seq that survives reconnection. A reboot is the
  harder case and the cheaper one to cover now: a consumer that saw seq 40
  before a power cycle would otherwise see seq 1 after one, and is_monotonic
  would be correct to reject the pair.
- Evidence: Configuration only; unverified on hardware.
- Consequences: A flash write per preference flush interval. Confirm the wear
  is acceptable when a device runs continuously.
- Follow-up: Watch it on the first flashed device.
- Governance impact: none

- Date: 2026-08-18
- Scope: Datum
- Decision: Leave the ESPHome toolchain unpinned in CI.
- Why now: HANDOFF.md's WP-3 note says C6 component coverage in ESPHome is
  younger than the classic ESP32's and that a gap is a finding to report
  upstream. A pin would hide exactly the breakage that note asks to surface.
- Evidence: .github/workflows/firmware.yml installs esphome unpinned.
- Consequences: An upstream release can turn the branch red without a local
  change. That is the intended signal, up to the point it becomes noise.
- Follow-up: Pin it if it goes red for reasons unrelated to this repository.
- Governance impact: none
