# Handoff - 2026-08-18 (cycle 4)

A review cycle across both repositories. Datum branch `wp3-firmware`,
apothecary branch `prototype/site-structure-hierarchy`. Neither is pushed and
no pull request is open.

## Session objective

Review the WP-3 firmware built in cycle 3 without assuming it was right, back
the review with tests and docs, and stand up an apothecary parts iteration view
with a datum enclosure loaded into it.

## What the review found

Two real defects. Both were in work that looked finished.

### 1. The firmware did not parse

Cycle 3 shipped an ESPHome configuration that had never been run through
ESPHome. Installing it and running `esphome config` produced a YAML syntax
error, not a warning.

`${...}` contains a brace, a brace is a flow indicator, and so an ESPHome
substitution cannot appear unquoted inside a flow mapping. Every `packages:`
include and every `script.execute:` call was written in flow style. None of
them parsed.

Rewritten in block style. `esphome config` now reports the configuration valid
on ESPHome 2026.7.4, and the rendered output confirms the wire contract:
`topic_prefix: ''`, birth and will on `datum/lab/jig/status` retained, and both
payload templates intact inside their raw string literals. One warning, GPIO8
is a strapping pin, which is the deliberate one `walkthrough/04-firmware.md` documents.

### 2. Apothecary could not start on Windows

`apothecary serve` died on its first status line, and so did `apothecary
check`. Windows still defaults to cp1252, and writing `✓` to that stream raises
rather than dropping the glyph.

A `_safe_echo` helper already existed for this and was used in roughly a third
of the places that needed it. It now takes styling keywords so a coloured line
can pass through it, and all 45 glyph-bearing call sites across `check`,
`serve`, `testing` and `parts` use it. The glyph is kept whenever the stream
can carry it — this is a fallback, not a downgrade — so the test drives the
fallback path directly rather than asserting the output is ASCII.

## The risk cycle 3 flagged, now settled

Cycle 3 listed script parameters reaching `str_sprintf` as a likely first-build
failure: the channel is declared `int` and the package passes the string `'0'`.

`esphome compile` reached codegen before failing, so the generated C++ answered
it directly:

```
StatelessLambdaAction<int, std::string>([](int ch, std::string action) -> void
script_scriptexecuteaction_id_5->set_args([]() -> int { return 0; }, ...)
str_sprintf(R"({"src":"%s","seq":%u,...,"ch":%d})", ..., seq->value()++, action.c_str(), ch)
```

ESPHome coerces correctly. One real nit: `ch` is a signed `int` and was being
fed to `%u`. It carries `%d` now, and the byte-identity check in
`walkthrough/04-firmware.md` still passes — which is the drift gate doing its job.

## Cross-repo work: the enclosure

`datum-core` is a new apothecary part. A printable tray with four standoffs and
an edge-connector cutout, and a printable lid with four contact openings and an
indicator light pipe. All three variants — `tray`, `lid`, `exploded` — render
manifold under OpenSCAD 2024.07.20.

`apothecary parts info` reported no bounds at all, which made datum's milestone
assertion 5 unsatisfiable as written. It reports them now, and a regression test
pins the datum-core envelope.

`planning/lanes/integration.md` carries a table of which cross-repo contract
maps to which parameter, and the value each currently holds.

## Verification evidence

### Datum

```bash
cd /c/Users/peter/Documents/repos/qm/datum
uv run pytest
uv run --with esphome esphome config firmware/t1-core.yaml
```

- `19 passed, 1 skipped` (`walkthrough/08-wire.md` skipped, no local broker)
- `INFO Configuration is valid!` on ESPHome 2026.7.4
- `reuse lint` compliant, 59 / 59 files

### Apothecary

```bash
cd /c/Users/peter/Documents/repos/qm/apothecary
uv run pytest tests/test_api.py tests/test_cli.py -q
uv run apothecary check
uv run apothecary parts info datum-core --json-out
uv run apothecary parts generate-stl datum-core
```

- `15 passed`, up from 12: the encoding fallback, the whole command over a
  narrow code page, and the datum-core bounds
- `check` completes, reporting OpenSCAD 2024.07.20 and 13 parts
- bounds `45.6 x 45.6 x 15.6` mm, non-null
- STL generation exits 0

### Server, while it was up

Served on `127.0.0.1:8765`, now stopped.

- `/health` 200
- `/parts` — 13 parts, `datum-core` among them
- `/parts/datum-core/stl` 200, 519745 bytes
- `/viewer/sites/parts_library?focus=datum-core` 200
- `datum-core` present in the `parts_library` site tree as one of 13 structures

## What is still not verified

- **The firmware has never been compiled.** `esphome compile` reaches codegen
  and then fails installing the ESP-IDF 5.5.5 framework on Windows — an
  environment failure, before the compiler runs. `.github/workflows/firmware.yml`
  on Linux is what settles it, and it has not run because nothing is pushed.
- **Nothing has been flashed.** Milestone assertion 2 still rides on the
  stand-in at `schema/vectors/captured/t1-core-single-press.json`.
- **The enclosure has never been fitted to anything.** Every dimension is an
  assumption; no schematic exists. `parts/datum-core/README.md` lists which
  numbers must be checked against real hardware.

## Servers

None running. The apothecary server started this session on port 8765 was
stopped.

A separate process is listening on port 8000 — `qm/carlos`, running
`tools.cli serve` and `src/main.py` since 17:20. It predates this session and
belongs to another project. It was left alone.

To bring the parts iteration view back up:

```bash
cd /c/Users/peter/Documents/repos/qm/apothecary
uv run apothecary serve --port 8765
# http://127.0.0.1:8765/viewer/sites/parts_library?focus=datum-core
```

Tune the geometry in `parts/datum-core/datum-core.scad`, then regenerate:

```bash
uv run apothecary parts generate-stl datum-core --force
```

`show="exploded"` is the variant to look at while tuning fit. It is a preview,
not a printable object.

## Governance notes

- The enclosure is WP-5 work arriving before WP-4, out of the fixed work
  package order, at explicit request. Logged in `planning/lanes/decisions.md`
  as needing governance review rather than slipped in quietly.
- Detention is still unimplemented. Q5 asks whether it may ever be remote.
- Q3, hardware licensing, still needs human resolution.
- No commit in either repository carries a co-author trailer.

## Recommended next actions

1. Push `wp3-firmware` and open the pull request. The firmware CI job has never
   run and is the only thing that can prove the configuration compiles.
2. Fix whatever the Linux build reports.
3. Push the apothecary branch and open its pull request.
4. Acquire one ESP32-C6-DevKitC-1, flash it, capture a real single press, and
   replace the stand-in vector. That closes WP-3 and unqualifies assertion 2.
5. Re-fit `datum-core` against a real board outline once WP-4 produces one.

## Notes for next operator

- `planning/DEV_LOOP.md` is still the session entrypoint.
- `HANDOFF.md` **State on arrival** is current: it says the configuration
  validates, that nothing has compiled it, and that nothing has been flashed.
- Datum branch `wp3-firmware`, 9 commits. Apothecary branch
  `prototype/site-structure-hierarchy`, 3 commits. Neither pushed.
- The lesson worth carrying: cycle 3 wrote a firmware configuration and
  described it as unverified, which was accurate but read as a small caveat.
  It did not parse. Run the tool before describing the artifact.
