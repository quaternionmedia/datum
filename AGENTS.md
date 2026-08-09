# AGENTS.md

This project is governed by the Quaternion Media constitution, vendored at
`governance/qm` (a submodule pinned to this project's `project/datum`
branch of that repo). If you are an AI coding agent opening this repo with
no other briefing, read this file fully before your first commit or edit.

## Before you do anything

1. Read `governance/qm/README.md` and `governance/qm/PRINCIPLES.md` in full
   — the namespaces/precedence rules and the charter. Both are short.
2. This project's own decision records live in `governance/qm/adr/` — inside
   the submodule, on this project's own branch, not at this repo's root — as
   `ADR-NNNN` (numbered locally, at ratification) or `DRAFT-*.md` before
   ratification. A human ratifies; you draft.
3. **Everything you produce arrives as a pull request.** Work on a branch and
   open a PR for human review — in this repo, and in the `governance/qm`
   submodule when you touch this project's records there. Never commit to,
   merge into, or push a shared branch directly, and never merge your own
   work, however small or mechanical the change looks. If you cannot open a
   PR, hand the branch back rather than merging it.
4. **Human-only contributorship applies to every commit you make here** (see
   `governance/qm/records/DRAFT-human-only-contributorship.md`): do not add
   yourself, your model name, or any co-author trailer naming an unmonitored
   address (e.g. a vendor `noreply@` address) to any commit. If your default
   tooling normally appends a `Co-Authored-By:` trailer, suppress it for
   this repo. Tool involvement is disclosed as a `Tools:` note where the
   artifact calls for one, never as a byline.
5. Follow the drafting-session handoff contract in
   `governance/qm/adr/README.md` before writing or amending any record.
6. A QM record may be tightened by this project's own records, never
   relaxed — see `governance/qm/README.md`'s "Namespaces and precedence."
7. Banned in any pre-ratification `DRAFT-*.md` record: "previously",
   "originally", "earlier draft", "re-review", "renumber", "retroactive",
   "supersedes the ... (stance|finding)", "corrected". Drafts are rewritten
   in place, not narrated. The ADR lint enforces this over prose only, so
   quoting the list in a code span is fine.

## One-time setup on a fresh clone (Windows)

`CLAUDE.md` and `.github/copilot-instructions.md` are real symlinks to this
file, not copies — POSIX checkouts resolve them with no setup. On Windows,
enable Developer Mode (Settings → For developers) and run `git config
core.symlinks true` once per clone, then `git checkout -- .` if the files
were already checked out before that. Skipping this doesn't break
anything — the files degrade to one-line pointers containing just the
target path — but it isn't the intended, tested experience; see the
IDE-integrated governance discovery record in `governance/qm/records/` for
what was actually verified.

<!-- Project-specific setup commands, test commands, and conventions belong
     below this line; this seed only carries the governance-discovery part. -->

## What this project is

A small physical button module. It reads dry contacts, turns them into a
versioned JSON event, and publishes that event over MQTT. It switches no
power itself; a listed device downstream does that.

The event schema is the durable artifact. The same button can later report a
dim level, a colour or a position by adding fields, and a consumer written
today keeps working. That claim is the project, and it is reduced to a single
CI assertion — see "Definition of done" below.

Read `HANDOFF.md` before starting work, then `PLAN.md`, then the five drafts
in `governance/qm/adr/`. If `HANDOFF.md` and a decision record disagree, the
record is right and the packet needs fixing — say so rather than proceeding.

`HANDOFF.md`'s **State on arrival** section is the only part of that file
execution sessions maintain. It says what is built, what is verified, and
which work package is next. Read it first; it is shorter than the packet and
it is the part that goes stale.

## Setup and test commands

```bash
uv sync                                    # install
uv run pytest                              # run the documentation
uv run datum version                     # schema version
uv run datum emit                        # JSON Schema -> schema/build/ (never committed)
uv run datum validate <file.json>        # an event, or an array of them

# docs/wire.md needs a broker. Without one it skips, with a stated reason.
docker run -d --rm -p 11883:1883 eclipse-mosquitto:2
DATUM_BROKER=host:port uv run pytest     # or point at your own
```

**`uv run pytest` runs the documentation, and that is not a turn of phrase.**
Every `>>>` under `docs/` executes, and module docstrings are collected too.
There is no `tests/` directory and adding one would be a regression: it
reintroduces the gap between what the docs claim and what the code does. Write
the example where a reader needs it, and it is a test.

`README.md` is a shallow onramp and a table of contents; the executable
reference lives in `docs/`, per `governance/qm/handbook/style-guide.md`. That
page also fixes where explanation goes: inline comments carry clarifying facts
about the code, `docs/` carries the contract, and every why belongs in a
record or a retrospective rather than beside the thing it describes.

The stack is fixed by `governance/qm/records/DRAFT-house-stack.md`: Python,
Pydantic, Click, pytest, uv. A dependency outside the blessed set needs a
record before it appears in review. Two exist — `jsonschema` and `paho-mqtt` —
and both are development dependencies imported lazily inside functions, so the
runtime package loads without either. A runtime import of either is a review
failure. Both records name the same underlying reason: a project whose seam is
a wire protocol needs protocol tooling a web stack never does. A third
instance of that pattern is worth raising at org level rather than arguing
from scratch again.

## Work package order, and it is fixed

| WP | What | Where | State |
|---|---|---|---|
| WP-0 | Repository bootstrap | this file, `governance/` | done |
| WP-1 | The event envelope | `schema/`, `docs/` | done |
| WP-2 | Topic contract and MQTT harness | `schema/topics.py`, `schema/harness.py`, `docs/wire.md` | done |
| WP-3 | Firmware, stock ESPHome on ESP32-C6 | `firmware/` | next |
| WP-4 | Hardware, T1-Core, KiCad 9 | `hardware/t1-core/` | |
| WP-5 | Enclosure | **`quaternionmedia/apothecary`**, not here | |
| WP-6 | License and REUSE gates | `.github/workflows/` | |

WP-1 comes before everything with a payload in it: the schema is what the
rest conforms to and the most expensive thing to change late.

## Non-negotiables

Settled. Do not re-open them and do not work around them. `HANDOFF.md` §1
carries the full list with reasons; the ones that bite first:

- **No line voltage.** Dry contacts in, signal out. No mains, no conversion
  stage, no relay driving a line conductor.
- **Additive schema only.** Fields are never removed and never repurposed.
  Unknown fields are ignored by consumers, never errors.
- **T1 must be complete with zero expansion modules attached.** If a change
  only pays off once a second module exists, the change is wrong.
- **All geometry goes to apothecary.** No `.scad` files land here. Parts must
  render coherently from their defaults, knowing nothing about this PCB.
- **ESPHome, Zigbee2MQTT, Home Assistant and the broker are engines.** Do not
  write replacements. The custom surface is the schema, a thin firmware
  layer, one PCB, and the parts.

## Open questions — escalate, do not decide

`HANDOFF.md` §2 holds the table. Reaching one of these means stopping and
asking; deciding one by stealth is a governance violation, not a shortcut.

The naming question that used to head this list is settled: the project is
**Datum**, and the name is free to appear anywhere. What remains open is Q4
(hardware licensing, which is a missing org mechanism rather than a venue
choice) and whether a controller may set a module's detent remotely, which
would add the first inbound path to an otherwise outbound contract.

## Definition of done for Milestone 1

Six assertions green in CI. The third is the one that matters: a consumer
pinned to the v1 schema parses a capability-extended event and yields an
identical `action`. That is the whole generational claim reduced to something
CI can fail on. If you are tempted to weaken it to make a test pass, that is
the project failing, not the test.
