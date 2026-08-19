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

## Governance findings, 2026-08-19

Raised by reading the corpus rather than `AGENTS.md`'s summary of it. All three
are for a human; none is a project-level call, and two are org-level by
construction — a project may tighten an org record, never relax or amend one.

- [ ] **The `governance/qm` submodule was never initialised in this clone.**
      `git submodule status` showed `-9f92119`, so `governance/qm` was an empty
      directory and the entire corpus — `PRINCIPLES.md`, the ten org records,
      the nine project drafts — was unreadable. Every governance claim made in
      this repository's sessions up to now came from `AGENTS.md`'s summary of
      documents nobody could open. `AGENTS.md`'s "One-time setup on a fresh
      clone" covers the Windows symlink case and says nothing about
      `git submodule update --init`. The same omission is in `project-seed/`,
      so fixing only this copy would hide an org-level defect in nine adopting
      projects. Next action: raise at org level; do not patch locally.

- [ ] **`governance/qm/handbook/style-guide.md` does not exist.** `AGENTS.md`
      cites it twice and `HANDOFF.md` once, as the authority for README being
      an onramp, for `docs/` carrying the executable reference, and for where
      explanation goes. The org `README.md` says plainly: "Style guide
      (minimal, legible deliverables) is named by the charter and not yet
      written." The practice is sound and this project follows it; the citation
      is to a document that has never existed. Next action: either write the
      page at org level or drop the citations.

- [ ] **The house-stack record names PDM. This project stands on uv.**
      `AGENTS.md` says "The stack is fixed by
      `governance/qm/records/DRAFT-house-stack.md`: Python, Pydantic, Click,
      pytest, uv." The record's blessed set reads "pytest (tests), PDM
      (packaging, with a committed lockfile)" and its context paragraph
      anticipates exactly this: "a project standing on uv would be the same
      trigger firing in the other direction, and would be answered the same
      way." So uv is not blessed, it is a named revision trigger, and clause 2
      says an out-of-set choice without a linked record fails review. Both
      datum and apothecary stand on uv. Next action: an org-level record
      answering the trigger, the way PDM's own adoption was answered.

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
