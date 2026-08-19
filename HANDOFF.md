# HANDOFF — Datum, Milestone 1

**For:** a coding agent with no prior context on this project.
**Date:** 2026-08-09.

This packet is self-contained. It does not assume you can see any conversation.
Read this file, then `PLAN.md`, then the drafts in `governance/qm/adr/`, then
start at the work package **State on arrival** names as next. If this packet
and a decision record disagree, the record is right and this packet needs
fixing — say so rather than proceeding.

**State on arrival** is unnumbered on purpose: it is maintained by execution
sessions and is the part that changes as work lands. Everything from §0 down
is the standing brief, rewritten in place when a position changes rather than
annotated — this project's records are pre-ratification, and pre-ratification
documents carry no memory (`governance/qm/records/DRAFT-decision-record-discipline.md`,
clause 2).

---

## State on arrival

**WP-0, WP-1 and WP-2 are complete. WP-3 is under way and is not done.**
`main` is pushed and is the published state; work reaches it as pull requests.

WP-3's configuration exists and `esphome config` reports it valid on ESPHome
2026.7.4; `docs/firmware.md` checks its topics and payloads against the
constants. The compile itself has not been proven anywhere yet — `esphome
compile` reaches codegen and then fails installing the ESP-IDF framework on
Windows, so `firmware.yml` on Linux is what settles it. **Nothing has been
flashed.** WP-3
closes when a real device produces a real capture, and until it does, assertion
2 stays qualified exactly as it was — see below. Do not read a green firmware
build as a working button.

What exists:

| | |
|---|---|
| Project repository | `main`. Governance wiring, the schema package, the retrofit demo, the wire harness, and the ESPHome configuration at `firmware/`. No hardware, no geometry. |
| `governance/qm` submodule | Pinned to `project/datum`. |
| Decision records | Nine, numberless, at `governance/qm/adr/`. None is an adoption record. |
| CI | `adr-lint.yml`, `reuse-lint.yml` and `submodule-check.yml` (seed, verbatim), plus `schema.yml`, which runs the documentation against a Mosquitto service container, and `firmware.yml`, which validates and compiles the ESPHome configuration in a matrix. |
| Licensing | `LICENSE`, `LICENSES/` and `REUSE.toml` are in place and `reuse lint` is clean. **The dependency-manifest licence gate WP-6 owes is still unwired** — the REUSE gate is one of the two the org record asks for, not both. |

**Assertions green: 1, 2 and 3 of six.**

1. The emitted JSON Schema accepts all six valid vectors and rejects the three
   malformed ones a single-event schema can reach. The fourth takes a stateful
   gate; see below.
2. A captured firmware event round-trips the documented topic contract over a
   real broker and validates. Qualified: the captured event is a stand-in
   written against the contract until WP-3 produces a real capture. Everything
   else in that path — topic, encoding, retention, schema validation — runs
   against Mosquitto over a socket. `docs/firmware.md` narrows what the
   stand-in is standing in for: the bytes the firmware would send are checked
   against the bytes the stand-in carries, so the remaining gap is the device
   and the contact, not the payload.
3. A v1-pinned consumer parses a capability-extended event and yields an
   identical `action`. This is the one that matters, and it is demonstrated
   inside the demo rather than off in a test file.

**What the wire harness caught on its first run, worth knowing before you
touch retention.** MQTT clears the retain flag when delivering to a
subscription that was *already established*. A subscriber watching the publish
happen sees `retain=0` even for a message the broker retained — the flag means
"this is a stored message replayed to you because you just arrived," not "this
was published with retention." So retention is only observable to a subscriber
that joins afterwards, which is exactly the consumer the rule exists for. The
harness opens a second, late subscriber to check it. An in-process fixture
models none of this, which is the argument for the harness in one paragraph.

`schema/src/datum/bus.py` is a test fixture standing in for the broker. It
must never grow into an MQTT implementation. The broker is an engine.

**The documentation is the test suite.** `pytest` executes every example under
`docs/`, plus the module docstrings, so there is nowhere to write an example
that is not checked. There is no `tests/` directory and there should not be
one: a claim that stops being true fails the build instead of going stale.

`README.md` is a shallow onramp and a table of contents. `docs/` carries the
executable reference: `cookbook.md`, `envelope.md`, `topic-contract.md`,
`conformance.md`, `cli.md`, `wire.md`. Every one of them is a test.
`governance/qm/handbook/style-guide.md` is the rule that puts them there, and
the same rule keeps explanation out of them — inline comments carry clarifying
facts, `docs/` carries the contract, and a why belongs in a record or a
retrospective.

`docs/wire.md` is separate from the rest for one reason: it needs a broker.
Without one it is skipped with a stated reason and everything else still runs.
An external prerequisite for part of a suite is house-normal — apothecary's
own tests need the `openscad` CLI and browser binaries — but the skip is
announced rather than silent, because a skipped assertion 2 reported as a pass
is the failure mode worth guarding.

**Three malformed vectors are schema-rejectable, and the fourth is not.**
Non-monotonic `seq` cannot be: monotonicity is a property of a sequence, and no
single-event JSON Schema can express a relationship between one payload and the
one before it. Each event in that fixture is individually valid and should be.
The invariant is real, so it is enforced by a stateful check (`is_monotonic`)
and by `datum validate` on an array. Two kinds of guarantee, two kinds of gate,
both demonstrated in `docs/conformance.md`. A schema asserted to reject all
four would be a fabricated test.

Verified against a real fresh clone, not asserted: `CLAUDE.md` and
`.github/copilot-instructions.md` resolve to `AGENTS.md` in full; the ADR lint
is clean over all nine drafts; `git submodule update --remote` lands on the
branch tip with no drift.

**Before your first commit,** read `AGENTS.md`. Two rules there will catch you
out. Human-only contributorship: no `Co-Authored-By:` trailer naming a vendor
`noreply@` address, even if your tooling appends one by default. And delivery
is always a pull request — work on a branch, open a PR, and never merge your
own work, in this repo or in the submodule, however mechanical the change.

---

## 0. Orientation in ninety seconds

**What is being built.** A small physical button module. It reads dry contacts,
turns them into a versioned JSON event, and publishes that event over MQTT. It
does not switch any power itself; a listed device downstream does that. The
whole design premise is that the *event schema* is the durable artifact: the
same button can later report a dim level, a colour, or a position by adding
fields, and a consumer written today keeps working.

**Power.** USB-C bus power, 5 V, default sink. No battery. Do not design for
sleep, do not add a power budget, do not treat the indicator LED's quiescent
draw as a constraint.

**Two repositories.**
- `quaternionmedia/datum` — schema, firmware, KiCad,
  CI, docs.
- `quaternionmedia/apothecary` — **all** printable geometry, as pull requests.
  No `.scad` files land in the project repository.

**Governance.** This project adopts the `quaternionmedia/qm` constitution by
reference. Read this repository's own root `AGENTS.md` before your first
action, then `governance/qm/README.md` and `PRINCIPLES.md`; they are placed
in the paths you already walk for exactly this reason. The rules that will
bite you first:

- Decision records are numberless drafts (`ADR-XXXX`) until a human ratifies
  them. **You draft; humans ratify.** Never assign a number.
- Drafts have no memory. If a decision changes while drafting, rewrite the
  draft as though the final position were held from the start, rather than
  annotating what it used to say. `governance/qm/project-seed/ci/adr_lint.py`
  holds the authoritative banned vocabulary and enforces it over prose only, so
  quoting the list inside a code span is fine. The lint globs
  `governance/qm/adr/DRAFT-*.md`, so it does not reach this file; the rule
  still applies here, and this packet is written to it.
- One decision per record. If Consequences starts describing a second
  decision, split it.
- House stack is Python: Pydantic, Click, pytest, uv. A dependency outside that
  set needs a record before it appears in review. Two exist — `jsonschema` and
  `paho-mqtt` — each with a record, and both are development dependencies
  imported lazily inside functions so the runtime package loads without either.

---

## 1. Non-negotiables

These are settled. Do not re-open them, and do not work around them.

1. **No line voltage.** No mains, no conversion stage, no relay driving a line
   conductor. Dry contacts in, signal out.
2. **USB-C, 5 V, default sink.** CC1 and CC2 each terminate through 5.1 kΩ to
   ground. No power-delivery controller.
3. **The event envelope is the interface.** Every transport carries it or a
   documented projection of it. No transport's native device model becomes the
   interface.
4. **Additive schema only.** Fields are never removed and never repurposed.
   Unknown fields are ignored by consumers, never errors.
5. **T1 must be complete with zero expansion modules attached.** If a change
   only pays off once a second module exists, the change is wrong.
6. **All geometry goes to apothecary.** Parts must render coherently from their
   default parameters, with no knowledge of this project's PCB.
7. **ESPHome, Zigbee2MQTT, Home Assistant and the MQTT broker are engines.** Do
   not write replacements for them. The custom surface is the schema, a thin
   firmware layer, one PCB, and the parts.
8. **Every BOM line has two independent sources** or a documented drop-in
   alternate footprint.

---

## 2. Open questions — escalate, do not decide

If your work reaches one of these, stop and ask. Deciding one by stealth is a
governance violation, not a shortcut.

Numbering matches `PLAN.md` §9.

| # | Question | Blocks |
|---|---|---|
| Q1 | T4 untethered tier: nRF52840 with a BTHome broadcaster, or ESP32-C6 with deep sleep | Nothing in M1 |
| Q2 | Zigbee end-device firmware: wait for ESPHome's in-flight support, or ship against esp-zigbee and carry a patch | Nothing in M1 |
| Q3 | Hardware licensing: **the org corpus has no mechanism that can see a schematic** — see below | WP-6 can proceed either way; the record's Status cannot be settled |
| Q4 | Anything requiring USB-C power delivery negotiation | Nothing yet; if you find a reason, that is a finding worth reporting |
| Q5 | Remote detention: whether a controller may set a module's detent from off-device | Nothing in M1; it would add the first inbound path to the contract |

The project's name is **Datum**, and it is free to appear anywhere: the
package, the MQTT topic root, part directory names, prose, the governance
branch (`project/datum`) and the repository.

**On Q3.** The org open-license record fixes its criterion as OSI-approved or
FSF-free and its enforcement as a generated dependency-license report along one
of two paths, and both paths enumerate software dependencies. A schematic, a
layout, a footprint library and a BOM are copyrightable works that OSI does not
review and no dependency report can reach. This project can therefore run every
gate the org mandates, report zero violations, and publish its principal
deliverable with no grant on it at all — which under P1 means a recipient
holding the design cannot modify or redistribute it.

Precedence lets a project *add* constraints to an org record. What is missing
here is not a constraint but an enforcement mechanism, and a project cannot add
one to an org record, so this does not resolve by picking a venue. REUSE plus
SPDX headers is the candidate — it is generated rather than hand-compiled as
the record's clause 4 requires, and it is the only mechanism of the three that
sees a `.kicad_sch`. The argument is written up in
`governance/qm/perspectives/2026-08-08-hardware-onramp-invisible-artifacts.md`
with a proposed org amendment. Do not act on it: a perspective never graduates
on its own, and this remains a human decision. **Escalate when WP-6 reaches it;
do not settle the record's Status yourself.**

**On Q5.** Detention is local: a module is armed or detained, and the state
sits on a retained topic. A controller setting that state remotely means every
consumer becomes a potential publisher, which is a bigger change than the
feature looks. Nothing in M1 needs it.

---

## 3. Work packages

Order is fixed. WP-1 comes before everything with a payload in it, because the
schema is the artifact the rest conforms to and the most expensive thing to
change late.

### WP-0 — Repository bootstrap

**Goal:** a repository that a low-context reader can enter and find its own
rules in.

Follow `governance/qm/README.md` § "Forking a new project" verbatim. In short:

1. Add `quaternionmedia/qm` as a submodule at `governance/qm`.
2. Create branch `project/datum` on the qm repository from `main`. On that
   branch, copy `project-seed/adr/` to a top-level `adr/` (README and TEMPLATE,
   verbatim). Push.
3. Point the submodule at that branch tip; add `branch = project/datum` to
   `.gitmodules`.
4. Copy the seed's `adr-lint.yml`, `reuse-lint.yml` and `submodule-check.yml`
   into `.github/workflows/`, unmodified.

   **The dependency-manifest licence gate is a carried gap.** The fork
   procedure's step 4 requires the ADR lint *and* a licence gate at
   instantiation: "a project without both is not instantiated, it is
   improvised." The REUSE half is wired; the dependency-manifest half is not,
   and until it is, this repository is improvised by the org's own standard
   with nothing detecting it — an unwired gate is indistinguishable from a
   passing one. Closing it costs about forty lines: apothecary's
   `license-check.yml` is the precedent, and it needs only a package to point
   at, which `schema/` already provides.
5. Copy `project-seed/ide/` recursively onto the repository root **with
   symlinks preserved**. `CLAUDE.md` and `.github/copilot-instructions.md` are
   real symlinks to `AGENTS.md`, not copies. Fill in setup and test commands
   below `AGENTS.md`'s marked line; the governance section above it stays
   verbatim apart from replacing `<name>`.

   **On Windows, `cp -a`, `rsync -a` and `git checkout` are not
   interchangeable, and the fork procedure lists them as if they were.** Under
   MSYS, `cp -a` produced a *regular file* for `CLAUDE.md` holding `AGENTS.md`'s
   content, and failed outright on `.github/copilot-instructions.md`. The
   regular-file result is the dangerous one: it passes any check shaped like
   "does `CLAUDE.md` contain the governance text" while breaking the invariant
   the symlink exists for — that editing `AGENTS.md` keeps all three current.
   Write the entries into the index and materialize them, and assert the
   **mode**, not the content:

   ```bash
   git update-index --add --cacheinfo 120000,$(printf '%s' 'AGENTS.md'    | git hash-object -w --stdin),CLAUDE.md
   git update-index --add --cacheinfo 120000,$(printf '%s' '../AGENTS.md' | git hash-object -w --stdin),.github/copilot-instructions.md
   git checkout -- CLAUDE.md .github/copilot-instructions.md
   git ls-files -s CLAUDE.md .github/copilot-instructions.md   # must read 120000
   ```

   The blobs are content-addressed, so correct ones reproduce the seed's own
   SHAs — `47dc3e3d…` and `be77ac83…`. That equality is the real proof the
   target paths are right.
6. Check `.gitignore` for a blanket `.vscode/` rule. If present, replace with
   `.vscode/*` plus `!.vscode/settings.json` and `!.vscode/extensions.json`.
   A blanket rule silently prevents the checked-in workspace config from ever
   being committed.
7. Move this project's drafts onto the project branch as numberless drafts.
   Leave Status as-is.

**Acceptance:** `git ls-files -s` reports mode `120000` for `CLAUDE.md` and
`.github/copilot-instructions.md`; `adr-lint` passes over every draft;
`git submodule update --remote` tracks `project/datum`.

The mode check is the criterion rather than the file contents, because
`core.symlinks` is off by default on Windows: a fresh clone there materializes
both pointers as one-line text files holding the target path until the one-time
step in `AGENTS.md` runs (`git config core.symlinks true`, then
`git checkout -- .`). That degradation is documented and expected — the
committed tree is correct either way. Verified in both states.

---

### WP-1 — The event envelope (do this first)

**Goal:** the seam, as a Python package with machine-checked compatibility
guarantees.

**Path:** `schema/`

**Deliverables:**

- A uv-managed Python package. Pydantic models for the envelope:
  `src` (str, stable identity equal to the MQTT topic path), `seq` (int,
  monotonic), `caps` (list of capability strings), `action`
  (`press|single|double|triple|hold|release`), `ch` (int, default 0), and the
  optional axes `level` (float 0–1), `vec` (3 floats), `color` (hue and
  saturation), `batt` (int 0–100). Optional axes are **absent**, not null,
  when unused.
- A separate `Announce` model carrying schema version, `src`, `caps`, hardware
  and firmware identifiers.
- Model config that **ignores unknown fields** rather than rejecting them.
  This is the forward-compatibility mechanism; get it explicit in the model
  config, not implicit in a default.
- A Click CLI: emit JSON Schema to `schema/build/`, validate a file of events,
  print the current schema version.
- `schema/vectors/` — ten checked-in JSON files: six valid golden events
  spanning press-only through all-axes-populated, four malformed (missing
  `src`, non-monotonic `seq` in a sequence fixture, `level` out of range,
  `action` not in the enum).
- `schema/projections/README.md` — a stub documenting the projection contract
  for each transport, with a table of which axes each can carry and which it
  drops. Populate the MQTT row; leave the others named and empty.

**Acceptance (these are M1 assertions 1 and 3):**

- `pytest` passes; the emitted JSON Schema validates all six valid vectors and
  rejects all four malformed ones.
- A test constructs a v1-pinned parser, feeds it an event carrying a
  capability and fields the v1 schema does not define, and asserts the parse
  succeeds and yields an identical `action`. **This test is the project.** If
  it is awkward to write, the model config in deliverable 3 is wrong.

---

### WP-2 — Topic contract and MQTT harness

**Goal:** the documented wire contract, and a way to prove firmware conforms
without a lab.

**Path:** `schema/topics.py`, `docs/topic-contract.md`, `tests/harness/`

**Deliverables:**

- Topic layout, documented and constant-ised: an event topic, an announce
  topic, an availability topic. Retain announce and availability; do not retain
  events. Write down the reasoning in the doc, because the next person will
  wonder.
- A Home Assistant MQTT Discovery publisher that reads an `Announce` and emits
  discovery payloads for a device trigger per contact channel. Discovery is a
  **convenience over the contract, not the contract** — say so in the module
  docstring, and make sure the contract is usable by a subscriber that has
  never heard of Home Assistant.
- A host-side harness: spin an ephemeral broker (or a broker fixture), publish
  a captured firmware event, subscribe, validate against the schema.

**Acceptance (M1 assertion 2):** a captured firmware event round-trips the
documented topic and validates. Harness runs in CI with no hardware attached.

---

### WP-3 — Firmware

**Goal:** stock ESPHome doing the smallest real thing.

**Path:** `firmware/`

**Deliverables:**

- An ESPHome package YAML targeting an **ESP32-C6 devkit** (`framework: type:
  esp-idf` — the C6 does not support the Arduino framework path here). Four
  binary sensors on non-strapping GPIO with debounce filters, single/double/
  triple/hold gesture mapping, one `esp32_rmt_led_strip` SK6812 indicator.
- Envelope emission over MQTT on the WP-2 topics, with a monotonic `seq` that
  survives reconnection, and an `Announce` published on connect.
- No deep sleep. No battery sensor. No power gating.
- A README naming the exact devkit, the exact GPIO map, and the wiring for the
  T0 contact jig.

**Acceptance:** flashing a C6 devkit and shorting a contact publishes an event
that passes WP-2's harness. CI builds the ESPHome configuration in a matrix; a
build failure fails the branch.

**Watch for:** C6 and H2 component coverage in ESPHome is younger than the
classic ESP32's. If a component you expect is missing, that is a finding to
report and possibly an upstream contribution — per the org open-license
record, a capability gap is closed by a pull request to the closest layer of
the stack, never by a private workaround. Do not vendor a patched copy without
a carried-patch register entry.

---

### WP-4 — Hardware, T1-Core

**Goal:** a KiCad 9 project that passes its own checks in CI.

**Path:** `hardware/t1-core/`

**Deliverables:** schematic and layout per `PLAN.md` §5. The details that are
easy to get wrong and expensive to discover:

- **CC1 and CC2 each through 5.1 kΩ to ground.** Omitting these produces a
  board that works on a legacy A-to-C cable and draws nothing from a compliant
  Type-C source. It presents as an intermittent cable fault and costs a day.
- **3.3 V LDO rated ≥ 600 mA**, against a Wi-Fi transmit peak near 350 mA. An
  undersized regulator shows up as brownout resets under load and reads as a
  firmware bug.
- **Antenna keepout** per the ESP32-C6-MINI-1 datasheet: no copper, no ground
  pour, module placed at a board edge.
- SK6812-MINI-E on the **3.3 V rail**, so the C6's 3.3 V data line clears the
  0.7 × VDD logic-high threshold with no level shifter.
- Contact inputs: 10 kΩ pull-up, 100 nF to ground, 100 Ω series, TVS to a
  common ESD rail. Both screw-terminal and JST-PH landing patterns.
- Two JST-SH 1.0 mm 4-pin connectors in parallel, Qwiic/STEMMA QT pinout, bus
  pull-ups fitted **only** on the core and marked as such.
- USB ESD array on VBUS, D+ and D-; D+/D- as a 90 Ω differential pair.
- Board outline ≤ 40 × 40 mm.
- Libraries vendored or pinned; nothing resolves outside the repository.
  Project-local `datum.pretty` and `datum.kicad_sym` for custom parts.
- `.gitattributes` marking `.kicad_sch` and `.kicad_pcb` as text.
- `kibot.yaml` with `preflight: run_erc: true, run_drc: true`, plus outputs for
  gerbers, drill, position file, BOM and PDFs.

**Acceptance (M1 assertion 4):** `kibot` ERC and DRC exit 0 in CI. Fabrication
outputs are generated by CI and attached to tags as release artifacts, never
committed. A BOM check asserts every line has two or more sources.

---

### WP-5 — Enclosure, as apothecary pull requests

**Goal:** parts that are useful to apothecary's users, that happen to fit this
board.

**Path:** `quaternionmedia/apothecary`, not this repository.

**Deliverables:** `datum-core`, `datum-cap`, `datum-mount-desk`, each as
`parts/<name>/<name>.scad` plus `apothecary/projects/parts/<name>.py` with a
Pydantic `Params`, `category`, `tags`, `description`, `print_settings` and
`display_rotation`. Follow `parts/README.md` and `docs/parts-authoring.md`
exactly — folder name hyphenated, SCAD file matching the folder, wrapper module
underscored.

- **Inherit house constants** from `parts/footpedal/button.scad`: `walls = 3`,
  `tolerence = .4` (note the existing spelling — match it, do not fix it in
  passing), `r = 12.5`. These are print-validated on QM hardware. New magic
  numbers mean new failed first prints.
- **Every mount provides a cable exit and strain relief.** Bus power makes this
  mandatory, not optional.
- Reuse `button.scad`'s contact-as-subtracted-profile idea for the light pipe,
  the switch dome and the USB cutout.
- Defaults must render something coherent with no knowledge of this project.

**Acceptance (M1 assertion 5):** `apothecary parts info datum-core` returns
the part with non-null bounds; `apothecary parts generate-stl` exits 0;
apothecary's own test suite passes. In this repository, CI verifies the pinned
apothecary version renders each part it depends on.

---

### WP-6 — License and REUSE gates

**Goal:** the teeth.

**Deliverables:**

- `license-gate.yml` following the **dependency-manifest-plus-allowlist** path
  (not SBOM-per-image — the runtime shape is packages and firmware, not
  containers). The org open-license record provides for this explicitly.
- REUSE compliance: SPDX identifiers on every file, `LICENSES/` holding full
  texts. CERN-OHL-S-2.0 for `hardware/`, MIT for `schema/` and `firmware/`,
  CC-BY-SA-4.0 for `docs/`.
- CI fails on an unlicensed file or a non-allowlisted dependency license.

**Acceptance (M1 assertion 6):** both gates report zero violations.

---

## 4. Definition of done for Milestone 1

The smoke scenario: a T0 contact wired into a T1-Core dev jig, powered from
USB-C, toggles a lamp through an MQTT broker, with no cloud service in the path
and no vendor account.

All six assertions green in CI:

1. JSON Schema validates six golden vectors, rejects four malformed. (WP-1)
2. A firmware event round-trips the topic contract and validates. (WP-2, WP-3)
3. A v1-pinned consumer parses a capability-extended event and yields an
   identical `action`. (WP-1)
4. KiBot ERC and DRC exit 0; the CC-termination check passes. (WP-4)
5. `apothecary parts info datum-core` returns non-null bounds; STL generation
   exits 0. (WP-5)
6. License and REUSE gates report zero violations; every BOM line has two or
   more sources. (WP-4, WP-6)

Assertion 3 is the one that matters. The rest is hygiene. Assertion 3 is the
entire generational claim reduced to something CI can fail on — if you are
tempted to weaken it to make a test pass, that is the project failing, not the
test.

---

## 5. Anti-goals for M1

Do not build these. Each has a reason, and "it would be easy while I'm here" is
not a counter-argument.

- **T2 expansion peripherals.** The connector goes on the board; nothing plugs
  into it yet. T1 has to be complete alone.
- **Colour or position axes in firmware.** The schema carries them; the first
  board does not populate them. That gap is the forward-compatibility claim
  being demonstrated rather than asserted.
- **Matter.** Certification regime, one dominant SDK, ecosystem lag. It is an
  optional emission later, through a bridge.
- **Zigbee.** Blocked on Q3 and unnecessary on a bus-powered unit where Wi-Fi
  costs nothing.
- **Battery anything.** Deferred to T4 with its own record.
- **A web UI, dashboard, or configuration app.** Home Assistant is the engine.
- **A second parts library.** Apothecary is the engine.
- **Numbering an ADR.** Humans ratify.

---

## 6. What to report back

When M1 lands, or when you stop:

- Which of the six assertions are green, and the exact failure for any that are
  not.
- Any open question from §2 you reached, and what you did instead of deciding
  it.
- Any upstream gap found in ESPHome, apothecary, or KiCad libraries, with a
  recommendation on whether it warrants a pull request. Capability gaps close
  upstream; a private workaround is a debt against the commons this project
  stands on.
- Any place where this packet and the ADRs disagree. The ADRs win; the packet
  gets fixed.

### Upstream gaps already reported

Named here so they are not re-reported as new, and so the next session knows
where each one is being carried.

None in ESPHome, apothecary or KiCad, none of which the completed work touches.
Four are in the QM corpus itself, which is the closest layer of the stack for
governance and therefore where they belong:

| Gap | Where it is carried |
|---|---|
| The fork procedure's symlink-copy guidance is wrong on Windows | `perspectives/2026-08-08-hardware-onramp-invisible-artifacts.md` |
| The open-license record's enforcement cannot see hardware artifacts | Same perspective, with a proposed org amendment. Q3 above |
| Gate *absence* is undetectable, and the corpus demonstrates it on itself | Same perspective |
| The topic contract's retention terms have no record | Named in `docs/topic-contract.md`; drafting one is open work |

Per the org record a capability gap closes upstream, which is what those
perspectives are. A private workaround would be a debt against the commons this
project stands on.
