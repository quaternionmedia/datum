# Depending on apothecary

**Hermetic.**

No printable geometry lands in this repository. The enclosure lives in
`quaternionmedia/apothecary`, which makes this project a consumer of another
repository — and the enclosure record is specific about what that is allowed to
look like:

> 5. **This project depends on a released apothecary version**, pinned, and
>    consumes parts through apothecary's CLI or API rather than by path.
>    Geometry changes land upstream and arrive here by version bump, which is a
>    reviewed commit rather than an ambient change.

Three requirements, and they are not equally easy. *Pinned* and *through the
CLI* have been true for a while. *Released* has not, and for most of that time
nothing said so.

## The declaration

One module owns what this project depends on, so the workflow, the pre-HIL run
and this page cannot disagree about it:

    >>> from datum.apothecary import APOTHECARY_REPO, APOTHECARY_PARTS
    >>> APOTHECARY_REPO
    'https://github.com/quaternionmedia/apothecary'
    >>> APOTHECARY_PARTS
    ('datum_core',)

`checkout_ref` decides what CI actually clones — the released version when
there is one, the commit standing in for it when there is not:

    >>> from datum.apothecary import checkout_ref
    >>> checkout_ref(version="v0.2.0", pin="abc1234")
    'v0.2.0'
    >>> checkout_ref(version=None, pin="abc1234")
    'abc1234'

## A gate that arms itself

The interesting part is what happens while the clause cannot be met. Apothecary
publishes no release today, so demanding one would be demanding that this
project fix something it does not own. The check records the deviation and lets
the build go green:

    >>> from datum.apothecary import dependency_state
    >>> nothing_published = dependency_state(version=None, pin="abc1234", available=[])
    >>> nothing_published.state, nothing_published.ok
    ('warn', True)

The moment apothecary publishes anything, that same deviation stops being
structural and becomes a choice — so the same check fails:

    >>> a_release_exists = dependency_state(version=None, pin="abc1234", available=["v0.2.0"])
    >>> a_release_exists.state, a_release_exists.ok
    ('fail', False)
    >>> a_release_exists.fix
    'set APOTHECARY_VERSION to a released version, newest is v0.2.0'

Nobody has to remember to tighten it later. That is the point: a deviation
documented in prose relies on someone re-reading the prose at the moment the
world changes, and nobody does.

Pinning a version that was never published fails too — a typo, or a tag deleted
after this project came to depend on it:

    >>> dependency_state(version="v9.9.9", available=["v0.2.0"]).state
    'fail'

## An unreachable network is not a pass

The check asks a remote what it has published, and that question can go
unanswered. "Could not ask" and "there is nothing" are different facts and are
kept apart, because reading the first as the second would let this pass on a
laptop with the wifi off:

    >>> dependency_state(version="v0.2.0", available=None, asked=False).state
    'unknown'

## On the command line

`datum apothecary` prints the dependency; `--check` is what CI runs. The exit
status is the part that matters, so it is exercised rather than described:

    >>> from click.testing import CliRunner
    >>> from datum import apothecary as dep
    >>> from datum.cli import cli
    >>> def published(versions):
    ...     return lambda *a, **k: versions
    >>> original = dep.released_versions

Nothing published upstream — the deviation is reported, and the exit status is
still zero:

    >>> dep.released_versions = published([])
    >>> result = CliRunner().invoke(cli, ["apothecary", "--check"])
    >>> result.exit_code
    0
    >>> "no released version to depend on yet" in result.output
    True

A release exists and this project still points at a commit — non-zero, and the
output names the version to move to:

    >>> dep.released_versions = published(["v0.2.0"])
    >>> result = CliRunner().invoke(cli, ["apothecary", "--check"])
    >>> result.exit_code
    1
    >>> "v0.2.0" in result.output
    True
    >>> dep.released_versions = original

## What CI does with it

`.github/workflows/enclosure.yml` runs `datum apothecary --check`, then clones
apothecary at `checkout_ref()` and renders every part in `APOTHECARY_PARTS`
through apothecary's CLI. So the dependency is verified in two independent
senses on every push: that it is the kind the record allows, and that the
geometry it names still matches what this project declares.

`datum hil` carries the same check as a step, where it reports as a skip with
its reason rather than a pass — this repository's rule that a skip is never a
pass applies to its own deviations too.

## Where this actually stands

Apothecary has no tags and no releases, and the commit pinned here has only
ever existed on an unmerged branch. Clause 5 is not met, the check says so on
every run, and closing it needs two things from apothecary rather than from
here: a merge to `main` and a tag. When that lands, set `APOTHECARY_VERSION`
and this check turns green on its own.
