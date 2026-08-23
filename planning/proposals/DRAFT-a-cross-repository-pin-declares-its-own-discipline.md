# ADR-XXXX — A cross-repository pin declares and checks its own discipline

> **Drafted here, not ratified.** Records live in `quaternionmedia/qm` under
> `adr/`, and this project vendors that corpus read-only. This file is a
> proposal for a human to carry upstream; it binds nothing while it sits here.
> Assistants draft, humans decide.

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-08-22 |

## Context

Projects in this corpus depend on each other across repository boundaries. The
enclosure record already governs one such dependency in detail, and its clause
5 is the shape the corpus wants generally: depend on a **released** version,
**pinned**, consumed through the upstream's **CLI or API rather than by path**.

Three requirements, and they fail differently. *Pinned* and *through the CLI*
are satisfied by writing the dependency down and calling it correctly — a
single act, visible in review. *Released* is not, because it depends on the
upstream having done something. A consumer can want to satisfy it and be unable
to, and there is no moment at which anybody is told that the situation changed.

That is what happened between `datum` and `apothecary`. The pin was consumed
through the CLI and bumped by reviewed commits, so the dependency looked
disciplined from every angle a reader checked. It pointed at a commit that
existed only on an unmerged branch of a repository that had never published
anything — a state nobody outside one developer's machine could obtain. The gap
was recorded in prose, in the upstream repository, in a document the consuming
project's contributors had no reason to open.

Prose does not survive this. A note saying "we will depend on a release once
there is one" relies on a person re-reading the note at the moment the first
release appears. Nobody re-reads notes on that schedule. The corpus has the
same finding elsewhere: a policy whose only preventer was never applied and
whose detector was never written enforces nothing, and `ci/policy-registry.yaml`
names that as its clearest instance.

## Decision

A cross-repository pin is declared in code, in one module, and that module
answers three questions with commands rather than prose.

1. **One declaration.** The upstream repository, the reference depended on, and
   the artefacts consumed live in a single module. Every consumer of those
   facts — CI workflows, local runners, documentation — reads them from there.
   A second copy is how a workflow and a check come to disagree about which
   upstream state was verified.

2. **The reference distinguishes a release from a stand-in.** A released
   version and a commit standing in for one are separate fields, and one
   function decides which is checked out. A project may depend on a commit
   while the upstream publishes nothing; it may not do so silently.

3. **The discipline check arms itself.** The check reads what the upstream has
   actually published and grades the dependency against it:

   - upstream publishes nothing → **record the deviation, do not fail**. The
     clause cannot be met by anybody, and failing here demands that the
     consumer fix something it does not own.
   - upstream publishes a version and the consumer still pins a commit →
     **fail**. The deviation stopped being structural and became a choice.
   - the consumer pins a version the upstream never published → **fail**.
   - the upstream could not be reached → **neither**. An unanswered question is
     not a pass, and reporting one as a pass is the failure mode this corpus
     keeps rediscovering.

4. **The upstream states its half.** A repository that is pinned by a
   downstream says so where its own contributors will find it, and answers
   whether the current commit is something a downstream may legitimately pin.
   This creates no dependency in the other direction: the upstream's artefacts
   stay ignorant of consumers, as the enclosure record's clause 2 requires. It
   records only who is affected when it publishes.

5. **A deviation names what covers it.** Where a check cannot run or a clause
   cannot be met, the record of that says which command answers the question
   instead. A deviation with no named equivalent is a gap wearing a reason.

## Consequences

- **The moment of change is caught, not scheduled.** No one has to notice that
  an upstream published its first release; the consumer's own gate fails on the
  next run and names the version to move to.
- **The gap is visible where it is owned.** Both sides carry the statement, so
  neither a consuming contributor nor an upstream contributor has to read the
  other repository to learn the obligation exists.
- **Obligation created:** a consuming project's CI runs the discipline check on
  every push, and its pre-flight or equivalent local runner carries it as a
  step that reports as a skip rather than a pass while the deviation stands.
- **Accepted cost: a network question in the check.** Reading what an upstream
  has published needs the network, so the check has a third answer besides pass
  and fail. That is a real cost — an offline machine learns less — and it is
  cheaper than the alternative, which is a check that reports an unreachable
  remote as an absence of releases and passes for the wrong reason.
- **Accepted cost: friction on the fast loop.** Depending on a release means a
  geometry fix needs an upstream review, an upstream release, and a version
  bump downstream. The enclosure record already accepted this cost for one
  dependency; this generalises the accounting rather than adding to it.

## Alternatives considered

1. **Document the deviation and rely on review.** It lost because it is what
   was already being done, and it failed in the specific way documentation
   fails: the note was accurate, sat in the upstream repository, and no reader
   of the consuming project encountered it. Review catches a bad change; it
   does not catch a correct state becoming stale because the world moved.

2. **Fail the build until the clause is met.** It lost because it demands that
   a consumer fix something owned by another repository. A red build nobody can
   turn green teaches people to ignore red builds, and the corpus has a
   standing objection to gates that cannot report — a permanent block is the
   same defect arriving from the other side.

3. **A shared library both projects depend on.** It lost on weight. Two
   projects and one boundary do not justify a third repository with its own
   release cycle, and the seam being described is thirty lines of policy, not
   an engine.

4. **Require the upstream to publish before a consumer may pin at all.** It
   lost because it forbids the situation that actually arises during early
   development, when two projects are being built together and neither has
   released. Making that state illegal produces a rule people route around
   rather than a rule people keep.

## Revision triggers

- A third project takes a cross-repository pin, making a shared implementation
  cheaper than two.
- An upstream in this corpus publishes releases on a cadence fast enough that
  the stand-in commit case stops arising, at which point clause 2 of this
  decision may be simplified away.
- A consuming project needs to pin something that is not a git repository — a
  package index, a container registry — where "what has been published" is
  asked a different way.
- The enclosure record is ratified, amended, or withdrawn.

## Amendments

*None.*
