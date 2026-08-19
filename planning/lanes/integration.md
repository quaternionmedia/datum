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
- [ ] Define change-impact notes for each contract.
- [ ] Add a simple compatibility checklist for every iteration.

## Contract freeze stance (cycle 1)

- Freeze order is modular rather than strict linear: board/mounting, connector opening, and indicator path can advance in parallel as long as lane deltas capture dependencies.

## Dependency notes from apothecary backlog

- Parts/template packaging coverage affects reproducible enclosure iteration.
- Path sanitization affects whether local artifacts can be shared safely in review.
- OpenSCAD availability checks affect confidence in geometry validation loops.

## Compatibility checklist (delta style)

- [ ] Board outline assumptions changed?
- [ ] Enclosure opening assumptions changed?
- [ ] Mounting assumptions changed?
- [ ] Any change requires governance escalation?
