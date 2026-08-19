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
