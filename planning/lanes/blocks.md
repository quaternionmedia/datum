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

Raised by reading the corpus rather than `AGENTS.md`'s summary of it. Two are
closed; the rest are for a human.

- [x] **The `governance/qm` submodule was never initialised in this clone.**
      `governance/qm` was an empty directory, so the entire corpus was
      unreadable and every governance claim made here came from `AGENTS.md`'s
      summary of documents nobody could open. Fixed, and the setup step is now
      in `AGENTS.md`. This was not an org-seed defect: `carlos` and `loopwall`
      already carry the line in their own project-specific sections and are the
      local checkouts where the submodule is populated. `apothecary` and
      `dossier` have the same gap; apothecary's is fixed.

- [x] **`governance/qm/handbook/style-guide.md` does not exist.** It does. The
      pin was 261 files and 49k lines behind `project/datum`, and the style
      guide landed in that window. The citations in `AGENTS.md` and `HANDOFF.md`
      are sound against the current corpus. Pin bumped.

- [ ] **The house-stack record names PDM; this project stands on uv.** Still
      true at the branch tip. It is a draft — `DRAFT-house-stack.md`, Status
      Proposed — and the corpus now ships a `uv.lock` of its own, so the record
      is behind its own practice. It should be updated at org level; the
      record's context paragraph already anticipates exactly this case and says
      how to answer it. Nothing here is blocked on it.

- [x] **`DRAFT-one-executable-walkthrough.md` now governs this repository.**
      Migrated: `docs/` is `walkthrough/`, pages are `NN-<slug>.md` in reading
      order, each declares its runtime in its opening line (01-07 hermetic,
      08 runtime-bound on a broker), the CI invocation names the directory
      explicitly rather than relying on `testpaths`, and the README table is
      checked against the directory instead of hand-maintained. Clause 7 is
      the one part that cannot be satisfied locally: it asks for the
      identifier of a job run on the default branch, and nothing is pushed.
      Original finding follows.

      **What it required.** It arrived in the propagation this pin bump
      picked up. Clause 1: every QM repository carries exactly one
      `walkthrough/` at its root, pages `NN-<slug>.md`, and it is the single
      path for development, onboarding and communication. This project's
      executable pages are in `walkthrough/`. Clause 2 also requires the test command
      to name the directory explicitly rather than rely on `testpaths`, which
      is precisely how `pyproject.toml` wires it today — the record measured
      that `testpaths` is ignored the moment pytest receives a path argument,
      so pages wired that way are collected by nobody and stay green forever.
      The record cites this project by name as the existence proof that the
      mechanism costs configuration rather than a toolchain. Next action:
      migrate `walkthrough/` to `walkthrough/` and name it in the CI invocation.

- [ ] **The pin was stale enough to change conclusions, and nothing reported
      it.** `submodule-check` is one of the three seed CI workflows and it did
      not catch a corpus 261 files behind. Whatever it checks, it is not
      freshness. Worth raising alongside the walkthrough migration.

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
