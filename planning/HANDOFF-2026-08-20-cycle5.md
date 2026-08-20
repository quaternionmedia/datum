# Handoff — 2026-08-20 (cycle 5)

For an agent picking this up cold, across `datum` and `quaternionmedia/apothecary`.

Both branches are pushed, both pull requests are open, every check is green,
and **nothing is merged**. Merging is a human's act and the merge order matters.

## Where to start

```bash
cd /c/Users/peter/Documents/repos/qm/datum
git submodule update --init          # the corpus, or AGENTS.md cites nothing
uv sync
uv run datum hil                     # one command, no servers, nothing left running
```

That prints what is proven and what still needs a bench. Then read
`walkthrough/` in order — the pages are the test suite.

## The two pull requests

| | Branch | PR |
|---|---|---|
| datum | `wp3-firmware` | [#2](https://github.com/quaternionmedia/datum/pull/2) |
| apothecary | `prototype/site-structure-hierarchy` | [#18](https://github.com/quaternionmedia/apothecary/pull/18) |

Both were green when this was written. `gh pr checks` is the current answer;
a status copied into prose is stale the next time anyone pushes.

**Merge apothecary first.** `datum.hil.APOTHECARY_PIN` names an apothecary
commit, and `.github/workflows/enclosure.yml` checks it out. Merging datum
first leaves its pin naming a commit that exists only on an unmerged branch.

After apothecary merges, the pin should move to whatever lands on its `main`,
and that is a reviewed commit here — not an ambient update.

## What became true this cycle

**The firmware compiled.** `build (t1-core.yaml)` passed in CI, 4m42s. It had
never compiled on any machine before; `esphome compile` fails locally on
Windows installing ESP-IDF, which is an environment limit and not a finding.
Milestone assertion 2 is still qualified — see below.

**The enclosure is checked by machine.** `datum hil` used to find apothecary by
guessing a sibling directory and skip silently. It reads a pin now and reports
which apothecary it actually verified, and CI renders every part this project
depends on against that pin.

**Everything the firmware claims is gated.** `walkthrough/04-firmware.md` reads
the topics and payload templates back out of the YAML and compares them to the
Python constants, byte for byte.

## What to distrust

Written plainly because the last four cycles each found something the previous
one had asserted rather than checked.

- **Nothing has been flashed.** Assertion 2 rides on
  `schema/vectors/captured/t1-core-single-press.json`, a stand-in. One real
  capture replaces it and the qualification goes away.
- **The enclosure has never been fitted to anything.** Every dimension in
  `datum-core` is an assumption; no schematic exists. Three of them are
  actively disputed — see the decisions below.
- **Local runs lie about CI.** Three defects this cycle passed locally and
  failed in CI, all because the developer machine already had things installed:
  tests reading gitignored STLs, a viewer needing `npm install`, and `npm ci`
  failing on a postinstall. The habit that caught the third was testing in a
  **clean directory from the committed lockfile**. Do that before trusting a
  fix to an environment problem.
- **`uv run pytest` is not what CI runs** in apothecary. CI runs
  `apothecary test all`, which includes the Playwright E2E phase. Running with
  `--ignore=tests/e2e` hides ten viewer tests.

## Decisions waiting on a human

Neither is mine to take, and both are now judgeable by looking rather than by
argument — start the viewer and turn the numbers.

**1. Two datum enclosure parts exist.**

| | `parts/datum/` | `parts/datum-core/` |
|---|---|---|
| Origin | apothecary `main`, authored after this branch forked | this branch |
| Board | 40 × 30 | 40 × 40 |
| Wall / tolerance | 2.4 / 0.2 | 3 / .4 |

They describe one object. One should absorb the other, and which is a design
call. `HANDOFF.md`'s WP-5 names `datum-core`, `datum-cap` and
`datum-mount-desk`, so the naming favours `datum-core`; the geometry in
`parts/datum/` is good and newer.

**2. The house constants disagree, and one side misquotes the record.**

`governance/qm/adr/DRAFT-enclosure-parts-live-in-apothecary.md` clause 3 says
`walls = 3`, `tolerence = .4`, `r = 12.5`, print-validated on QM hardware, and
requires a part that differs to say why in its docstring.
`parts/datum/datum.scad` uses 2.4 and 0.2 and **cites that record for values it
does not contain**. `datum-core` ships the record's values.

Both are on sliders in the viewer with their provenance, so the choice can be
made by seeing what it costs: 0.6 mm of wall is 1.2 mm of envelope.

## Open work, in the order it unblocks things

1. **Merge both PRs** (apothecary, then datum), then bump the pin.
2. **Settle the two decisions above.** Everything about the enclosure is
   provisional until they are.
3. **Build the fit profile.** `apothecary/docs/fitting-a-part.md` states the
   seam standard — the consumer owns requirements and interfaces, apothecary
   owns realization and manufacturability — and names the one gate that is
   missing: nothing compares a profile to a part's parameters, because no
   profile exists. It is the next step after the standard is agreed.
4. **Flash a devkit.** `firmware/README.md` has the exact board, the GPIO map
   and the T0 jig wiring. `planning/IRL_TEST_MATRIX.md` has the seven cases.
5. **WP-4**, which unblocks re-fitting the enclosure against a real outline.
6. **WP-6's dependency-manifest licence gate**, still a carried gap.

## Governance

- Both branches carry no co-author trailer. Neither has been merged by its
  author. Nothing was pushed to `main`.
- The corpus is current in both repositories, at each project's branch tip.
- **One finding stands and is a draft to update, not to work around:** the
  house-stack record names PDM as the packaging tool; this project and
  apothecary both stand on uv, and the record's own context paragraph
  anticipates exactly that case and says it should be answered with a record.
- **Clause 5 of the enclosure record is only half met.** It requires depending
  on a *released* apothecary version consumed through its CLI or API rather
  than by path. The pin is a commit, and `datum hil` still reaches across by
  path. Closing it properly waits on apothecary being packaged for release.

## Apothecary, in one paragraph

The fractal viewer is the only entry point. `/viewer/parts/<name>` redirects
into it; the JSCAD viewer assets are mounted by no route and the CLI no longer
claims otherwise. A part is a folder plus a wrapper, an assembly is a site
registration, and a disputed number is candidates declared on a wrapper —
none of those adds a page. three.js is vendored and served from the app, so the
viewer works with no access to any CDN, which is asserted by a test that aborts
every off-origin request.

## Verification, as of this handoff

```
datum        uv run pytest              green, one skip
             uv run datum hil           6 proved, 0 failed, 1 skipped
             reuse lint                 compliant
apothecary   pytest walkthrough tests   green, two skips (from a cold checkout
                                        with every STL deleted)
```

Counts are deliberately absent. Both suites grow, and a number written here is
a second copy of what running them reports — this page had one that was stale
within the hour.

The one skip in datum is `walkthrough/08-wire.md`, which needs a broker and
says so. Start one and it runs:

```bash
docker run -d --rm -p 11883:1883 eclipse-mosquitto:2
uv run datum hil --broker 127.0.0.1:11883
```

Nothing is running. No server was left up.
