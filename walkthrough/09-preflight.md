# Running the checks before pushing

**Hermetic.**

CI is not a barrier on this repository. `main` is unprotected, no ruleset is
applied, and the governance corpus says so about itself: *"every gate in this
repository is a signal to whoever merges rather than a barrier."* A signal only
works if somebody reads it before it costs a round trip, so read it here:

```
uv run --group preflight datum preflight
```

The group has to be named on the command that runs. `uv run` re-syncs the
environment and drops it, so a `uv sync --group preflight` beforehand is undone
by the very next `uv run`.

## What it actually does

It delegates to the governance corpus's own runner, out of the submodule,
rather than restating what the workflows do. A second list of "what CI runs" is
a list that drifts, and the whole point is to find out what the runner will say
— which a paraphrase cannot tell you.

Each workflow gets its own invocation. That is not tidiness: the runner
executes every job in one environment where CI gives each job a fresh machine,
and `enclosure.yml`'s `uv sync --locked` was stripping the tools
`reuse-lint.yml` needed. The licensing gate failed for it, and the failure said
nothing about licensing.

It also runs against a scratch environment it owns, under `.preflight/`. The
workflows install their own tools, and `actions/setup-python` is an environment
step nothing reproduces — so `python -m pip install esphome` goes wherever
`python` points. On this machine that was the system interpreter, which refused
it for lack of permission. With permission it would have installed ESPHome into
the developer's global Python.

## What cannot run here, and what covers it

Three of the six gates cannot run on this machine. Each is named in the output
rather than dropped, and each names what stands in for it:

    >>> from datum.preflight import LOCAL_DIFFERENCES, partition
    >>> sorted(LOCAL_DIFFERENCES)
    ['enclosure.yml', 'firmware.yml', 'schema.yml']

`firmware.yml` is set aside before it runs, because the runner does not
evaluate `${{ matrix.* }}` and one such workflow would abort the whole pass:

    >>> runnable, set_aside = partition()
    >>> set_aside
    ['firmware.yml']

The other two run and fail, which is the honest outcome — a green report that
skipped them would be worth less than a red one that says why:

    >>> LOCAL_DIFFERENCES["enclosure.yml"].covered_by
    '`datum hil` -- it renders the pinned parts and compares declared bounds.'

`schema.yml` waits on an MQTT broker that CI starts as a service. One docker
line supplies it, and then that gate runs here too.

## The rule that keeps this honest

An excused gate must name what covers it locally. An excuse with no local
equivalent is a gap wearing a reason, and nothing would ever notice:

    >>> from datum.preflight import differences_are_current
    >>> differences_are_current()
    []

That check also catches the quieter failure: a workflow renamed or deleted
while its excuse stays behind, still claiming to describe a gate.

Every workflow is classified. One appearing in neither list would be a gate
nobody notices is missing:

    >>> from datum.preflight import WORKFLOWS
    >>> {p.name for p in WORKFLOWS.glob("*.yml")} == set(runnable) | set(set_aside)
    True

## A pass here is evidence, not proof

`uses:` steps are environment, not logic, and are not reproduced. The runner
image differs from this machine — which is the usual reason a locally green
step fails on a runner, and this project has been caught by it more than once.
Read the runner's own caveats; it prints them.
