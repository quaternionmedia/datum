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
- Why now: walkthrough/08-wire.md names a topic that is right in Python and wrong in the
  firmware as the failure its broker harness cannot reach. Literals in a
  substitutions block can be read back as text and compared to the constants;
  literals buried in a lambda cannot, and a JSON library's spacing and key
  order are not ours to fix.
- Evidence: walkthrough/04-firmware.md fills the firmware's own templates in Python and
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

- Date: 2026-08-18
- Scope: Datum
- Decision: Write the firmware in block-style YAML, never flow style.
- Why now: `${...}` contains a brace and a brace is a flow indicator, so an
  ESPHome substitution cannot appear unquoted inside a flow mapping. The whole
  file was written in flow style and none of it parsed. This is not a style
  preference; flow style and substitutions are incompatible.
- Evidence: `esphome config` failed with a YAML syntax error at the first
  `packages:` include, then reported the configuration valid after the rewrite.
- Consequences: Contact channels and script calls read as blocks. The gesture
  reader in datum.firmware matches on `action:` alone rather than on a line
  that also carries `script.execute:`.
- Follow-up: None. The CI job now catches this class before review does.
- Governance impact: none

- Date: 2026-08-18
- Scope: Datum
- Decision: The event payload's `ch` uses `%d`, not `%u`.
- Why now: Generated code passes the script parameter as a C++ `int`. Feeding
  a signed int to `%u` is a format mismatch the compiler may warn on, and the
  values are 0..3 so nothing is gained by the unsigned specifier.
- Evidence: `firmware/.esphome/build/.../main.cpp` shows
  `StatelessLambdaAction<int, std::string>` and `set_args` returning `int`.
  The byte-identity check in walkthrough/04-firmware.md still passes.
- Consequences: None on the wire. The bytes are unchanged.
- Follow-up: None.
- Governance impact: none

- Date: 2026-08-18
- Scope: Integration
- Decision: The enclosure lands in apothecary as `datum_core`, parameterised
  against a generic 40 x 40 mm board rather than against this project's PCB.
- Why now: The user asked for a parts iteration view with datum loaded. The
  geometry non-negotiable puts all of it in apothecary and requires a part to
  render coherently from its defaults knowing nothing about the PCB.
- Evidence: `apothecary parts info datum_core` reports 45.6 x 45.6 x 15.6 mm;
  STL generation exits 0; the part appears in the `parts_library` site tree.
- Consequences: This is WP-5 work arriving before WP-4, so every dimension is
  an assumption. The part README says which ones must be checked against a
  schematic before anyone prints it.
- Follow-up: Re-fit against the real board outline when WP-4 produces one.
- Governance impact: review needed -- WP order is fixed and this is out of it.

- Date: 2026-08-18
- Scope: Apothecary
- Decision: `apothecary parts info` reports the part's bounding box.
- Why now: Datum's milestone assertion 5 is "`apothecary parts info datum_core`
  returns the part with non-null bounds", and the command reported no bounds at
  all, so the assertion was not satisfiable as written.
- Evidence: `--json-out` now carries a `bounds` object; a regression test pins
  the datum_core envelope.
- Consequences: Parts that set neither `get_bounds` nor `default_bounds` report
  null, which is honest rather than a guess.
- Follow-up: Wire the assertion into datum CI at WP-5/WP-6.
- Governance impact: none

- Date: 2026-08-19
- Scope: Datum
- Decision: The pre-HIL runner is a Click subcommand, `datum hil`, not a script
  under a new top-level `demo/`.
- Why now: The first draft was `demo/hil.py` built on argparse. The house-stack
  record blesses Click for CLIs and requires an org-level record for anything
  outside the set, so argparse was an out-of-set choice for a job the blessed
  set already covers. A new top-level directory also sits outside the work
  package path table in `AGENTS.md`.
- Evidence: `uv run datum hil` -> 6 proved, 0 failed, 1 skipped. `datum --help`
  lists it. `walkthrough/07-hil.md` is the reference and carries its own doctests.
- Consequences: One surface rather than two. The runner ships with the package,
  so it degrades honestly outside a checkout rather than crashing — it looks
  for `pyproject.toml` and `schema/vectors` and says what it needs.
- Follow-up: None. The `demo/` directory is gone.
- Governance impact: none — this removes a deviation rather than adding one.

- Date: 2026-08-19
- Scope: Integration
- Decision: The list of hardware-only IRL cases lives beside the runner, and
  the documentation checks it against the test matrix.
- Why now: A case added to the matrix and not to the runner, or the reverse, is
  a case nobody runs. That is the same drift the firmware seam gate exists to
  catch, applied to the review checklist instead of the wire.
- Evidence: `walkthrough/07-hil.md` compares `irl_case_ids()` to every `IRL-NNN` found in
  `planning/IRL_TEST_MATRIX.md`, and it runs under `uv run pytest`.
- Consequences: The seven cases cannot silently disagree.
- Follow-up: None.
- Governance impact: none
