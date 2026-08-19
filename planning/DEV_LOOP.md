# Dual-repo dev loop

This file defines the working loop for coordinated iteration across Datum and Apothecary.

## Working posture

- Cadence: time-agnostic, mostly now
- Scope split: balanced across Datum and Apothecary
- Decision discipline: heavy documentation
- Review output: checklist deltas only
- Immediate unknowns: IRL test path, apothecary functionality

## Loop steps (repeat)

1. Intake questions
- Add or refine open questions in planning/lanes/questions.md.
- Promote urgent unknowns into the active cycle section.

2. Pick one small objective per lane
- Datum lane: one concrete verification or implementation objective.
- Apothecary lane: one concrete enclosure or integration objective.
- Integration lane: one cross-repo compatibility objective.

3. Execute locally
- Implement the smallest useful change.
- Run the proving command or check for that change.

4. Record evidence
- Capture command output, decisions, and blockers in lane notes.
- Keep evidence factual and concise.

5. Review in checklist deltas
- Only log what changed, what is blocked, and what is next.

## Promotion rules

- Any design decision that changes interfaces, invariants, or release criteria is recorded in planning/lanes/decisions.md.
- Any unresolved risk that can block HIL goes to planning/lanes/blocks.md with an owner and next action.
- If a decision belongs in governance records, add a handoff note that points to the target draft location.

## Definition of a good iteration

- At least one lane moved with verified evidence.
- No silent assumptions were introduced.
- Next step is explicit for each active lane.

## Current cycle focus

- Datum: prepare IRL validation staging for post-BOM hardware and firmware checks.
- Apothecary: define functional fit criteria for enclosure and interface geometry.
- Integration: align board-fit assumptions with enclosure parameter contracts.
