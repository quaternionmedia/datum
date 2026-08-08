# AGENTS.md

This project is governed by the Quaternion Media constitution, vendored at
`governance/qm` (a submodule pinned to this project's `project/<name>`
branch of that repo). If you are an AI coding agent opening this repo with
no other briefing, read this file fully before your first commit or edit.

## Before you do anything

1. Read `governance/qm/README.md` and `governance/qm/PRINCIPLES.md` in full
   — the namespaces/precedence rules and the charter. Both are short.
2. This project's own decision records live in `adr/`, as `ADR-NNNN`
   (numbered locally, at ratification) or `DRAFT-*.md` before ratification.
   A human ratifies; you draft.
3. **Human-only contributorship applies to every commit you make here** (see
   `governance/qm/records/DRAFT-human-only-contributorship.md`): do not add
   yourself, your model name, or any co-author trailer naming an unmonitored
   address (e.g. a vendor `noreply@` address) to any commit. If your default
   tooling normally appends a `Co-Authored-By:` trailer, suppress it for
   this repo. Tool involvement is disclosed as a `Tools:` note where the
   artifact calls for one, never as a byline.
4. Follow the drafting-session handoff contract in `adr/README.md` before
   writing or amending any record.
5. A QM record may be tightened by this project's own `adr/`, never
   relaxed — see `governance/qm/README.md`'s "Namespaces and precedence."

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

## Setup and test commands

None yet. This repository is at WP-0: governance wiring only, no payload.
Setup and test commands land with WP-1 and belong in this section when they
do. The stack is fixed in advance by `governance/qm/records/DRAFT-house-stack.md`:
Python, Pydantic, Click, pytest, uv. A dependency outside the blessed set
needs a record before it appears in review.

## Work package order, and it is fixed

| WP | What | Where | State |
|---|---|---|---|
| WP-0 | Repository bootstrap | this file, `governance/` | done |
| WP-1 | The event envelope | `schema/` | next |
| WP-2 | Topic contract and MQTT harness | `schema/`, `tests/harness/` | |
| WP-3 | Firmware, stock ESPHome on ESP32-C6 | `firmware/` | |
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

The one you will meet first: **the project name is unsettled.** Use the
literal placeholder `tessera`, confined to the package name, the MQTT topic
root constant, and part directory names. Keep it out of prose that would need
editing later.

## Definition of done for Milestone 1

Six assertions green in CI. The third is the one that matters: a consumer
pinned to the v1 schema parses a capability-extended event and yields an
identical `action`. That is the whole generational claim reduced to something
CI can fail on. If you are tempted to weaken it to make a test pass, that is
the project failing, not the test.
