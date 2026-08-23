# Datum — modular physical-control system

**Name.** A *datum* is the fixed reference a machinist or surveyor measures
everything else from — a mark you can return to and trust — and it is the
singular of *data*: one complete unit of it. Both senses are true of this
system at once. A module is a stable, identified point that emits one unit of
data, and the smallest complete one already solves something by itself, which
is the §1 test in a word.

**Status:** planning draft. Nothing here is ratified. Assistants draft; humans
ratify (QM README, "Ratification").

**Power baseline:** USB-C bus power. Battery variants are a later tier with
their own record. This is the decision that shapes most of what follows.

---

## 1. The problem, stated so it can be tested

A physical control surface — a button — should be installable today against a
need that exists today (turn this light on), without foreclosing the richer
thing it will need to do in three years (set this light's colour; report where
the knob is; drive a scene; drive something not yet invented).

The industry's answer is to sell a new button each time the need grows. That
answer fails QM's P1: the customer owns nothing that survives the vendor.

The failure mode of the *open* answer is equally well documented: a DIY button
project ships a beautiful expansion connector, and dies at the second module,
because the first module was never useful on its own.

**Design test carried through every decision below:** *does the smallest,
cheapest, zero-expansion version of this system solve a real need completely
and by itself?* If a decision only pays off once someone buys the second
module, the decision is wrong.

---

## 2. What already exists in-house

`quaternionmedia/apothecary` contains `parts/footpedal/`, holding
`button.scad`, `footpedal.scad`, and `footpedal.ino`. That part establishes
house conventions this project inherits rather than invents:

- Tolerance and wall vocabulary: `tolerence = .4`, `walls = 3`, `brim`,
  `bottom`, contact-profile subtraction, mounting posts on an outer radius.
- A contact element modelled as a *profile to subtract*, not a part to model —
  the right abstraction for "any conductive thing goes here."
- The firmware precedent is MIDI over USB (`Control_Surface`, `NoteButton`)
  with FastLED indication. MIDI is a genuine multi-implementation open protocol
  and stays a first-class transport in §4, not a legacy footnote.

Apothecary is also the physical-design toolchain: Pydantic `BasePart`
wrappers, `params_model`, `category`, `tags`, `print_settings`,
`display_rotation`, one folder per part, STL generation via CLI and API.
**All enclosure work for this project lands in apothecary**, not in a second
parts library. See draft ADR *Enclosure parts live in apothecary*.

---

## 3. Architecture: three layers, one seam

```
  CONTACT              SENSE / ENCODE                TRANSPORT
  (dumb, physical)     (the module)                  (the seam)

  momentary switch  ->  debounce, gesture,        ->  MQTT / Zigbee /
  rocker                capability advertisement       MIDI / HID / BTHome
  existing wall SW      expansion sensor read
  encoder / slider      event envelope emit
```

The three layers are separable on purpose. Per QM's *Build the seam, buy the
engines*: **the seam QM builds is the event envelope plus the physical
modularity. Radios, firmware frameworks, brokers and home-automation platforms
are engines, and are selected rather than written.**

The engines are ESPHome, Zigbee2MQTT / ZHA, an MQTT broker of the deployer's
choosing, and Home Assistant (or anything else subscribing). The custom
surface is a schema, a small firmware layer, one PCB family, and a parametric
enclosure family. That is small enough for one person to hold, which is the
size test the doctrine asks for.

### 3.1 The capability ladder is a payload, not a product line

The scale-up path — toggle, then colour, then position, then whatever follows —
is expressed as **additive fields on one envelope**, with the module
advertising which fields it will ever populate. It is emphatically *not* a
family of incompatible products.

```jsonc
{
  "src": "datum/kitchen/north",   // stable identity == topic path
  "seq": 41,                        // monotonic; replay + loss detection
  "caps": ["press", "level"],       // what this module can ever emit
  "action": "single",               // press | double | triple | hold | release
  "ch": 0,                          // which contact, for multi-gang
  "level": 0.62,                    // OPTIONAL scalar axis
  "vec": [0.1, -0.4, 0.9],          // OPTIONAL positional axis
  "color": { "h": 210, "s": 0.8 },  // OPTIONAL colour axis
  "batt": 87                        // OPTIONAL, unused on bus-powered units
}
```

Compatibility rules, enforced by conformance vectors in CI:

1. **Additive only.** A field is never repurposed and never removed.
2. **Unknown fields are ignored, not errors.** A consumer written against v1
   must parse a v3 event and produce the same `action`.
3. **`caps` is advertised at announce time**, so a consumer can render an
   appropriate interface before ever seeing a rich event.

This is the whole "path up for the next generation" mechanism. A 2026 consumer
keeps working against a 2031 module; a 2031 consumer degrades gracefully
against a 2026 module because `caps` told it what to expect.

Schema lives in the house stack: Pydantic models, JSON Schema emitted as a
build artifact, golden vectors checked in. See draft ADR *The event envelope
is the seam*.

### 3.2 Hardware tiers

| Tier | What it is | Cost of entry | Solves alone? |
|---|---|---|---|
| **T0 — Contact** | No electronics. Printed actuator, two wires into a screw terminal. Also: an existing dumb wall switch, rewired signal-only. | ~$0 | Yes, once paired with any T1 nearby |
| **T1 — Core** | ESP32-C6 + USB-C + 4 contact inputs + 1 indicator. The whole product. | one board | **Yes — this is the deliverable** |
| **T2 — Expansion** | I2C peripherals on a standard connector: encoder, hall angle sensor, capacitive slider, accelerometer | one cable | Adds axes to T1's envelope |
| **T3 — Bridge** | Same envelope from a foreign origin: MIDI pedal, phone, wall plate | software only | Proves the seam is real |
| **T4 — Untethered** | Battery or energy-harvested variant, BTHome broadcast tier | later | Deferred; own record |

T1 must be complete without T2 existing. That is the §1 test applied.

### 3.3 What USB-C bus power buys, and what it costs

**Buys:** no power budget to design around, so no deep sleep, no wake latency,
no duty-cycle compromises in gesture detection. The radio can stay associated,
which makes a press-to-light round trip a Wi-Fi round trip rather than a
reassociation. ESPHome is usable as shipped rather than fought. The BOM loses
a charger, a fuel gauge, a battery divider and its gating MOSFET, and an LED
power gate. The first board is meaningfully easier to get right.

**Costs, stated:** a cable has to reach every button. That makes the desk,
bench, rack and instrument-stand placements natural and the mid-wall placement
awkward — a wall installation needs an in-box receptacle or a Class 2 supply
run to it, and neither is a printed part. It also means the untethered tier is
a genuinely different board, not a stuff option, and its firmware story is
different too (see §9.1). The plan does not pretend otherwise: T4 is deferred
with its reasons named, rather than half-supported.

### 3.4 The retrofit path, which is the actual pitch

The system's most valuable single behaviour: **put a physical switch back on a
smart device that lost one.** A smart bulb with no wall control, a lamp on a
plug, a scene that only exists in an app. T0 + T1 solves that in an afternoon,
with a switch that looks like a switch, and the same hardware later drives
colour and position without being replaced.

---

## 4. Transport selection, against the replaceability test

QM's *Seams on standard protocols* asks: *could this component be replaced by a
from-scratch implementation of the seam protocol alone, with no change on our
side of the seam?*

| Transport | Independent implementations | Verdict |
|---|---|---|
| **MQTT over Wi-Fi** | Mosquitto, EMQX, NanoMQ, HiveMQ, VerneMQ; clients everywhere | **Primary, and the M1 target.** Named explicitly in the QM seams record. Home Assistant MQTT Discovery is the auto-configuration convention, not a dependency — the topic contract is documented and any subscriber can implement it |
| **USB MIDI / HID** | Universally implemented | **Adopted for the desk tier**, and effectively free given a USB-C connector already exists for power. Inherits the footpedal precedent; direct bridge to performance tooling |
| **Zigbee** | Multiple stacks (zigpy, Zigbee2MQTT, ZHA, EmberZNet, esp-zigbee); ESPHome Zigbee end-device support is in flight, not landed | **Adopted where a Zigbee mesh already exists.** Exits to MQTT via Zigbee2MQTT, so the seam is unchanged. Less compelling on a bus-powered unit, where Wi-Fi costs nothing |
| **BTHome v2** | Open format under the Open Home Foundation; open firmware and hardware implementations; public, user-extensible decoder library; consumed natively by Home Assistant | **Held for T4.** Its advantage is power, which a bus-powered unit does not need. Its stated limit is real: one-way sensor broadcast, no control path back |
| **Matter over Thread** | One dominant SDK; the specification is public and the SDK is Apache-licensed, but logo and interoperability are gated by CSA certification and membership. Matter 1.6 shipped 17 June 2026; ecosystem implementation reliably lags specification by months to a year, and generic-switch device types are unevenly exposed by the large platforms | **Optional emission, never the only seam.** Speaking Matter is a feature; depending on it is a single-implementation dependency plus a certification gate, and would need an exception record under the seams doctrine |
| **Zigbee Green Power** (batteryless, EnOcean PTM 21x class) | Specification is CSA; ZGP frames need a *translator* node on the mesh, and the reliably-working translators are a narrow vendor set | **Rejected as a default.** Genuinely attractive for T4 — no battery, ever — but it makes correct operation depend on a specific vendor's hardware being in radio range. That is the lock-in the seams doctrine exists to refuse. Revisit if translator support broadens |

**Net:** every transport lands on the same envelope. Swapping the radio is a
component swap, not a redesign, which is what the doctrine is buying.

---

## 5. Circuitry — T1-Core, for KiCad

**Radio/MCU: ESP32-C6-MINI-1 (pre-certified module).** One part covers Wi-Fi 6,
BLE 5, Thread and Zigbee 3.0 on 802.15.4, which keeps the transport decision
reversible in firmware rather than in copper. Using a *pre-certified module*
rather than a bare SoC is the hardware form of "buy the engines": it moves
intentional-radiator certification onto the module vendor, which is the
difference between a project that can ship and one that cannot.

Known cost, stated: C6 and H2 require the ESP-IDF framework in ESPHome, and
their component coverage is younger than the classic ESP32's.

### Block-level netlist intent

- **USB-C receptacle, 16-pin.** Full receptacle rather than power-only, because
  the C6's native USB-Serial-JTAG makes D+/D- worth having: it gives flashing,
  logging and the MIDI/HID transport with no USB-UART bridge on the BOM. CC1
  and CC2 each get **5.1 kΩ to ground** — the sink declaration; omitting it is
  the classic reason a board draws nothing from a Type-C source. D+/D- routed
  as a 90 Ω differential pair, kept short. ESD array (USBLC6-2SC6 class) on
  VBUS, D+ and D-.
- **Power.** 5 V VBUS into a 3.3 V LDO rated for **≥ 600 mA** — the C6's Wi-Fi
  transmit peak is in the 300–350 mA region and an undersized regulator shows
  up as brownout resets under load, which reads as a firmware bug for a week.
  22 µF bulk close to the module, plus decoupling per the module datasheet, and
  the datasheet's antenna keepout honoured (no copper, no ground pour, board
  edge preferred).
- **Contact inputs ×4.** Each: 10 kΩ pull-up to 3.3 V, 100 nF to ground for RC
  debounce, 100 Ω series resistor, TVS to a common ESD rail. Strapping pins
  avoided. Terminals presented as both 2.54 mm screw terminal and JST-PH, so
  T0 wiring is a screwdriver job, not a soldering job.
- **Indicator.** One SK6812-MINI-E, powered from the **3.3 V rail** so the C6's
  3.3 V data line clears the 0.7 × VDD logic-high threshold with no level
  shifter. No power gate — bus power makes the LED's quiescent draw irrelevant,
  which is one part and one net class removed from the design.
- **Expansion (T2).** Two JST-SH 1.0 mm 4-pin connectors in parallel,
  Qwiic/STEMMA QT pinout (GND / 3V3 / SDA / SCL), for daisy-chain. Bus
  pull-ups fitted on the core and marked as the only set. Plus a 2.54 mm 6-pin
  header breaking out two spare GPIO for interrupt and strap use, so the
  expansion path is not I2C-only.
- **User controls.** BOOT and RESET, plus one recessed COMMISSION button.
- **Test and fab.** Named test points on 5 V, 3.3 V and every contact input;
  fiducials; a `TP_` net class; single-sided assembly.
- **Board outline.** Target ≤ 40 × 40 mm so one core fits a 1-gang plate, a
  desk puck and a DIN clip without a second layout.

### KiCad discipline

- KiCad 9 project per board under `hardware/<board>/`. Files are S-expression
  text and diff legibly; `.gitattributes` marks them text.
- **KiBot** in CI with `preflight: run_erc: true, run_drc: true`. ERC or DRC
  failure fails the build. That is the hardware analogue of the ADR lint — the
  teeth this project needs to be worth ratifying.
- Fabrication outputs (gerbers, drill, BOM, CPL, PDFs) are generated by CI and
  attached to a tag as release artifacts. Generated files are not committed.
- Symbol and footprint libraries: KiCad official libraries, vendored or pinned,
  plus a project-local `datum.pretty` and `datum.kicad_sym` for anything
  custom. Nothing resolves to a path outside the repository — P1's
  ownable-offline requirement applied to CAD.
- **Sourcing rule** (the replaceability test in hardware): every BOM line has
  at least two independent sources or a documented drop-in alternate footprint.
  A single-source part needs an exception record naming its exit plan.

---

## 6. Physical design — in apothecary

Parts land upstream in `quaternionmedia/apothecary`, in its existing
`parts/<name>/` plus wrapper idiom:

```
parts/datum/datum.scad                     # the core body: PCB tray, USB opening,
                                           #   antenna thinning, light pipe, cap seat
apothecary/projects/parts/datum.py         # BasePart wrapper + Params
```

`parts/datum/` exists and is parametric in the board it carries: its dimensions
come from a `BlackBoxProvider`, so the same part serves a hand-entered stub
today and a real KiCad outline later with no change to the part. That is what
lets the defaults render a coherent object knowing nothing about this PCB,
which is apothecary's own requirement.

Mounts are separate parts as they arrive — a weighted desk puck for M1, then a
1-gang plate carrier and a DIN clip. Whether the pressed cap is a second part
or a parameter of the core is open until the first one is printed.

The modularity claim has to hold physically as well as in the schema: **one
core body, many mount adapters.** The mount is what changes between a wall, a
desk, a rack and a music stand; the core does not.

USB-C changes one geometric requirement: **every mount needs a cable exit**,
and the core body needs a receptacle cutout with strain relief. The desk puck
is the M1 mount because it is the one where a cable is expected rather than
tolerated.

Parameters (Pydantic `Params`, per the parts-authoring convention):

```python
class Params(BaseModel):
    pcb_x: float = 40.0
    pcb_y: float = 40.0
    wall: float = 3.0          # inherits button.scad's walls = 3
    tolerance: float = 0.4     # inherits button.scad's tolerence = .4
    cap_r: float = 12.5        # inherits button.scad's r = 12.5
    travel: float = 1.2
    light_pipe_d: float = 3.0
    cable_exit: Literal["side", "rear", "none"] = "side"
    gang: int = 1
```

Reusing the footpedal's existing tolerance and radius constants is deliberate:
those numbers are already print-validated on QM's own printers, and a new set
of magic numbers is a new set of failed first prints. `button.scad`'s
contact-as-subtracted-profile idea carries over directly for the light pipe,
the switch dome and the USB cutout.

Enclosure caveat, stated plainly: a printed enclosure is not a listed
enclosure. Wall installations mount the core inside a listed box or behind a
listed plate. See the signal-only ADR.

---

## 7. Repository shape

Two repositories, and the split is a decision rather than an accident:
enclosure work goes to apothecary as pull requests; everything else lives in
the project repository.

Following the QM fork procedure verbatim — submodule at `governance/qm`,
branch `project/datum` on the qm repo carrying this project's `adr/`,
`adr-lint.yml` copied unmodified, `project-seed/ide/` copied recursively with
symlinks preserved, license gate wired.

```
datum/
├── governance/qm/              # submodule, branch project/datum
├── AGENTS.md, CLAUDE.md, .github/copilot-instructions.md
├── .vscode/{settings,extensions}.json
├── .github/workflows/
│     adr-lint.yml              # verbatim from the seed
│     reuse-lint.yml            # verbatim from the seed
│     submodule-check.yml       # verbatim from the seed
│     license-gate.yml          # dependency-manifest path (non-container shape)
│     schema.yml                # conformance vectors, JSON Schema emit
│     hardware.yml              # KiBot: ERC, DRC, fab artifacts on tag
│     firmware.yml              # ESPHome build matrix
├── schema/                     # the seam
├── firmware/                   # ESPHome packages + external components
├── hardware/t1-core/           # KiCad 9
├── walkthrough/                # the executable pages; README.md is an onramp
└── README.md, AGENTS.md, HANDOFF.md
```

Three of the six workflows are wired: `adr-lint`, `reuse-lint` and
`submodule-check`, all copied from the seed without edit, plus `schema.yml`
which runs the documentation against a Mosquitto service container.
`license-gate`, `hardware` and `firmware` arrive with the work packages that
give them something to check.

The license gate follows the **dependency-manifest-plus-allowlist** path, not
the SBOM-per-image path, since the runtime shape is firmware and packages
rather than containers. The open-license record explicitly provides for this.

---

## 8. Milestone 1 — "one button, one light, no cloud, one afternoon"

Scope excludes: T2 expansion, colour, position, Matter, Zigbee, battery, and
any mount beyond the desk puck.

**Smoke scenario.** A T0 contact wired into a T1-Core dev jig, powered from
USB-C; pressing it toggles a lamp through an MQTT broker, with no cloud service
in the path and no vendor account.

**Machine-checked assertions:**

1. The emitted JSON Schema validates six golden event vectors and rejects three
   malformed ones. The fourth malformed vector, non-monotonic `seq`, is refused
   by a stateful check instead: monotonicity is a property of a sequence, and a
   single-event schema cannot express a relationship between one payload and
   the one before it. Two kinds of guarantee, two kinds of gate.
2. A firmware-emitted event, captured in a host-side test, round-trips the
   documented topic contract and validates against that schema.
3. A consumer pinned to the v1 schema parses a capability-extended event
   without error and yields an identical `action` — the forward-compatibility
   claim, tested rather than asserted.
4. `kibot` ERC and DRC both exit 0 for `hardware/t1-core`, and the design rule
   set includes a check that CC1 and CC2 each terminate through 5.1 kΩ.
5. `apothecary parts info datum_core` returns the part with non-null bounds,
   and STL generation exits 0.
6. The license and REUSE gates report zero violations, and every hardware BOM
   line carries two or more sources.

Assertion 3 is the one that matters. Everything else is hygiene; assertion 3 is
the entire "path up for the next generation" claim, reduced to something CI can
fail on.

---

## 9. Open questions — named, not decided

1. **T4 untethered tier.** Whether it is an nRF52840 with a Zephyr or NimBLE
   BTHome broadcaster, or an ESP32-C6 with deep sleep. Decided by a measured
   power budget, and not blocking anything in M1. The honest expectation is
   that it becomes a second board with a second firmware story rather than a
   variant of this one.
2. **Zigbee timing.** Whether a Zigbee end-device build waits on ESPHome's
   in-flight Zigbee support landing, or ships against esp-zigbee directly and
   carries a patch. The latter creates a carried-patch register entry, which is
   an org-level commitment.
3. **Hardware licensing has no org mechanism.** The open-license record fixes
   its criterion as OSI-approved or FSF-free and its enforcement as a generated
   dependency-licence report along one of two paths, and both paths enumerate
   *software* dependencies. A schematic, a layout, a footprint library and a
   BOM are copyrightable works that OSI does not review and no dependency
   report can reach. This project can therefore run every gate the org mandates,
   report zero violations, and publish its principal deliverable with no grant
   on it at all — which under P1 means a recipient holding the design cannot
   modify or redistribute it.

   Precedence lets a project *add* constraints to an org record. What is
   missing here is not a constraint but an enforcement mechanism, and a project
   cannot add one to an org record, so this does not resolve by choosing a
   venue. REUSE plus SPDX headers is the candidate: it is generated rather than
   hand-compiled as the record's clause 4 requires, and it is the only one of
   the three mechanisms that can see a `.kicad_sch`. The argument is written up
   in `governance/qm/perspectives/2026-08-08-hardware-onramp-invisible-artifacts.md`
   with a proposed org amendment, which a human decides.
4. **USB-C source expectations.** Whether the board declares anything beyond
   default 5 V sink behaviour. A 5.1 kΩ CC termination gets 5 V at whatever the
   source advertises, which is sufficient. Any PD negotiation would add a
   controller and a reason to justify it, and no such reason exists yet.
5. **Remote detention.** Whether a controller may set a module's detent from
   off-device. Detention is local today. Anything remote adds the first inbound
   path to a contract that is otherwise outbound-only, which is a larger change
   than the feature looks — every consumer becomes a potential publisher, and
   the topic contract grows a direction it does not currently have.

---

## 10. Honest risks

- **The expansion connector graveyard.** Modular systems die when tier 1 is
  incomplete without tier 2. Mitigated structurally by the §1 test and by M1's
  scope, not by intention.
- **The cable is the product's ceiling.** Bus power makes the first board easy
  and makes half the installation stories awkward. If the untethered tier never
  ships, the system is a desk and bench control, which is a smaller claim than
  the pitch in §3.4. Naming this now is cheaper than discovering it at T4.
- **The schema outliving its usefulness.** A capability ladder that grows
  without discipline becomes a union type nobody can implement. Revision
  trigger: a third optional axis added within one year means the envelope needs
  a subtype mechanism, not another field.
- **Regulatory drift.** Any move toward switching line voltage changes this
  from an open-hardware project into a listed-product project, with a cost
  structure that has killed comparable efforts. The signal-only ADR exists to
  make that a decision rather than a slide.
- **Certification gravity.** Pressure to "just get the Matter logo" will
  recur. It is a membership-and-certification regime, and adopting it as the
  primary seam inverts the doctrine. Emitting Matter through a bridge keeps the
  option without the dependency.
- **Cross-repository coupling.** Enclosure in apothecary is the right call by
  the commons-first ordering rule and it introduces a release-cadence
  dependency between two repositories. The mitigation is that apothecary parts
  are parametric and standalone: a core body is useful to apothecary's users
  even if this project stalls.

---

## 11. Immediate next actions

1. Breadboard a C6 devkit with four contacts and one LED, running stock
   ESPHome, publishing envelope JSON over MQTT. That validates the whole seam
   before a single pad is placed, and it is what turns assertion 2 from a
   stand-in capture into a real one.
2. Wire the dependency-manifest licence gate. It needs only a package to point
   at, which the schema already provides, and until it exists this repository
   is improvised by the fork procedure's own standard — an unwired gate is
   indistinguishable from a passing one.
3. Populate the non-MQTT rows of `schema/projections/README.md`: which axes
   each transport carries, and which it drops.

The nine drafts on `project/datum` are ratified by a human, not by this
project. Ratification waits on a second active code owner at org level, so the
drafts stay unratified and the work below them proceeds regardless — the
discipline is enforced by CI today, and a Status field is what is pending.
