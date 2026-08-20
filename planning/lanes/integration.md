# Integration lane

## Objective

Keep Datum and Apothecary in lockstep by managing explicit cross-repo contracts.

## Cross-repo contracts to track

- Board outline dimensions and tolerances
- USB connector opening and clearance envelope
- Indicator LED line-of-sight and light-pipe assumptions
- Mounting hole pattern and standoff strategy

## Next actions

- [x] Rank contract freeze order for earliest risk reduction.
- [x] Give the contracts a real artifact to argue against: `datum-core` in
      apothecary carries all four as named parameters.
- [ ] Define change-impact notes for each contract.
- [ ] Add a simple compatibility checklist for every iteration.
- [ ] Replace the assumed board dimensions with measured ones at WP-4.

## Contract freeze stance (cycle 1)

- Freeze order is modular rather than strict linear: board/mounting, connector opening, and indicator path can advance in parallel as long as lane deltas capture dependencies.

## Dependency notes from apothecary backlog

- Parts/template packaging coverage affects reproducible enclosure iteration.
- Path sanitization affects whether local artifacts can be shared safely in review.
- OpenSCAD availability checks affect confidence in geometry validation loops.

## The seam standard (2026-08-20)

`docs/fitting-a-part.md` in apothecary states it: **the consumer owns
requirements and interfaces; apothecary owns realization and
manufacturability.** The test for which side a number belongs to is whether it
would change on a different printer (apothecary's) or on a different board
(ours).

Three objects recur at every rung of assembly complexity, from an unfitted part
to a build with third-party interfaces: a **fit profile** the consumer
publishes, a **`Params` model** the part accepts, and a **validator**
apothecary runs. Nothing new appears as the assembly grows; the tree gets
deeper.

What that changed here:

- `walls` and `tolerence` are apothecary's, carrying the house constants from
  `parts/footpedal/button.scad`. The tray envelope is 46.8 mm square, not 45.6.
- The board footprint, connector, indicator and contact pitch stay in the SCAD
  as defaults (a part must render knowing nothing about us) but they are ours
  to assert once a profile exists.
- **The fit profile is not built.** It is the one gate the standard names as
  missing, and the next step after the standard is agreed.

## The apothecary pin

`APOTHECARY_REPO`, `APOTHECARY_PIN` and `APOTHECARY_PARTS` live in
`schema/src/datum/hil.py`. `.github/workflows/enclosure.yml` reads them, checks
out that apothecary, and renders and verifies each part this project depends
on. `datum hil` reports which state it actually verified, and says so when a
local checkout has drifted off the pin.

**The pinned commit is not published.** apothecary has not been pushed, so the
CI job cannot pass yet; it will report "reference is not a tree", which is the
true statement that this project depends on a state of apothecary nobody else
can obtain.

## Where each contract currently lives

| Contract | Parameter in `datum-core` | Value | Status |
|---|---|---|---|
| Board outline and tolerance | `board_x`, `board_y`, `board_clearance` | 40, 40, 0.4 | assumed |
| Connector opening and clearance | `connector_w`, `connector_h`, `connector_margin` | 9.4, 3.6, 0.6 | assumed |
| Indicator line of sight | `indicator_x`, `indicator_y`, `indicator_d` | 0, 14, 4.0 | assumed |
| Mounting pattern and standoffs | `mount_inset`, `boss_d`, `screw_d`, `standoff_h` | 3.5, 5.0, 2.2, 4.0 | assumed |

Every row is a placeholder chosen to render coherently. None has been checked
against a schematic, because none exists yet. The enclosure is the cheap half
of each contract; the board is the expensive half and it is not built.

## Compatibility checklist (delta style)

- [ ] Board outline assumptions changed?
- [ ] Enclosure opening assumptions changed?
- [ ] Mounting assumptions changed?
- [ ] Any change requires governance escalation?
