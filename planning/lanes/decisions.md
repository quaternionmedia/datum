# Decisions lane

Record high-discipline decisions with context and consequences.

## Template

- Date:
- Scope: Datum | Apothecary | Integration
- Decision:
- Why now:
- Evidence:
- Consequences:
- Follow-up:
- Governance impact: none | review needed | draft record candidate

## Decision log

- Date: 2026-08-18
- Scope: Integration
- Decision: Use a lane-based, question-first dual-repo loop with checklist-delta reviews.
- Why now: Need a methodical planning and iteration system before BOM-driven HIL work.
- Evidence: Existing repo baseline is green and HIL checklist is present.
- Consequences: Iterations are tracked by lane and must carry verification evidence.
- Follow-up: Populate each lane with one active objective per cycle.
- Governance impact: review needed

- Date: 2026-08-18
- Scope: Datum
- Decision: Add `datum validate --report` to emit machine-readable validation summaries.
- Why now: HIL and IRL loops need script-friendly proof artifacts, not only terminal text.
- Evidence: Datum suite remains green after docs and CLI update.
- Consequences: First device captures can be archived with validation metadata.
- Follow-up: Standardize report location in HIL workflow notes.
- Governance impact: none

- Date: 2026-08-18
- Scope: Apothecary
- Decision: Extend `apothecary check` to report OpenSCAD readiness and version.
- Why now: Fast diagnosis of geometry toolchain readiness is needed for iteration cadence.
- Evidence: Targeted CLI tests pass after command change.
- Consequences: Setup failures are surfaced earlier before STL tasks are attempted.
- Follow-up: Decide if check output should become machine-readable later.
- Governance impact: none

- Date: 2026-08-18
- Scope: Apothecary
- Decision: Sanitize part metadata/include path fields to avoid absolute local path leakage.
- Why now: Backlog item was actionable locally and directly improves safe sharing in reviews.
- Evidence: Focused API and CLI tests pass after update.
- Consequences: `/parts` responses now expose repository-relative paths.
- Follow-up: Confirm whether any additional endpoints expose local absolute paths.
- Governance impact: none

- Date: 2026-08-18
- Scope: Datum
- Decision: Introduce a formal post-BOM IRL test matrix artifact for HIL execution.
- Why now: Enables methodical execution once hardware is available and aligns with lane-based loop.
- Evidence: Matrix added and local repo tests remain green.
- Consequences: HIL runs have explicit case IDs, expected outcomes, and report paths.
- Follow-up: Add capture automation helper when first device events are available.
- Governance impact: review needed
