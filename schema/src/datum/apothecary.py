"""What this project depends on in apothecary, and whether that dependency is legal.

The enclosure lives in ``quaternionmedia/apothecary`` and nowhere else, so this
project depends on a specific state of it. The enclosure record is specific
about what kind of state that is allowed to be:

    5. **This project depends on a released apothecary version**, pinned, and
       consumes parts through apothecary's CLI or API rather than by path.

A commit pin satisfies "pinned" and misses "released". The difference is not
pedantry: a commit on an unmerged branch is a state nobody else can obtain,
which makes this project's geometry unreproducible for anyone but the person
who has both checkouts open. That is precisely the failure the clause exists to
prevent, and it is where this project stood while the clause read as satisfied.

So the discipline is checked rather than asserted, and the check arms itself.
While apothecary publishes no release at all the clause cannot be met by anyone
and the check says so without failing the build. The moment a release exists
the deviation stops being structural and becomes a choice, and the check
becomes a gate.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Tuple

APOTHECARY_REPO = "https://github.com/quaternionmedia/apothecary"

# The released version this project depends on, once apothecary publishes one.
# `None` means "no release exists upstream yet"; it is not a licence to leave
# this unset after one does, and `dependency_state` stops passing if it is.
APOTHECARY_VERSION: Optional[str] = None

# The commit standing in for a release until there is one. Bumping it is a
# reviewed commit here, the same way the governance submodule's pin is -- but a
# commit is the weaker form of this dependency and is meant to be temporary.
APOTHECARY_PIN = "2e7d57c"

# The parts this project depends on, by their names in apothecary's registry.
# CI renders each one from the pinned apothecary, so an upstream change that
# breaks geometry fails here rather than at a printer.
APOTHECARY_PARTS = ("datum_core",)

# States, ordered by how much they should worry a reader.
PASS = "pass"
WARN = "warn"
FAIL = "fail"
UNKNOWN = "unknown"

_SEMVER_TAG = re.compile(r"^v?\d+\.\d+\.\d+")


@dataclass(frozen=True)
class Dependency:
    """How this project's reference to apothecary stands against clause 5."""

    state: str
    summary: str
    fix: str = ""

    @property
    def ok(self) -> bool:
        """Whether the build should be allowed to go green on this.

        ``UNKNOWN`` counts as ok and ``WARN`` does too, for different reasons:
        one is a question this machine could not answer, the other a deviation
        that is recorded and cannot yet be closed by anybody. Neither is a
        pass, and :func:`dependency_state` says which it is rather than
        flattening them together.

            >>> Dependency(PASS, "x").ok, Dependency(FAIL, "x").ok
            (True, False)
            >>> Dependency(WARN, "x").ok, Dependency(UNKNOWN, "x").ok
            (True, True)
        """
        return self.state != FAIL


def released_versions(repo: str = APOTHECARY_REPO, timeout: int = 30) -> Optional[List[str]]:
    """Version tags published on the remote, or ``None`` if it could not be asked.

    ``None`` and ``[]`` mean different things and are kept apart: an empty list
    is "asked, and there are none", while ``None`` is "could not ask". Reading
    an unreachable network as an absence of releases would let this check pass
    for the wrong reason on a laptop with the wifi off.
    """
    if shutil.which("git") is None:
        return None
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--tags", "--refs", repo],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (subprocess.SubprocessError, OSError):
        return None
    if result.returncode != 0:
        return None

    tags = []
    for line in result.stdout.splitlines():
        _, _, ref = line.partition("refs/tags/")
        if ref and _SEMVER_TAG.match(ref.strip()):
            tags.append(ref.strip())
    return sorted(tags)


def dependency_state(
    version: Optional[str] = APOTHECARY_VERSION,
    pin: str = APOTHECARY_PIN,
    available: Optional[List[str]] = None,
    asked: bool = True,
) -> Dependency:
    """Judge this project's apothecary reference against clause 5.

    ``available`` is the published version list; ``asked`` records whether the
    remote could be reached at all, so the two kinds of "no versions" stay
    distinguishable.

    Nothing published upstream: the clause cannot be met by anybody, so the
    deviation is recorded rather than failed. This is the state the project has
    actually been in.

        >>> state = dependency_state(version=None, pin="27efaf7", available=[])
        >>> state.state, state.ok
        ('warn', True)
        >>> "no released version" in state.summary
        True

    A release exists and this project still points at a commit. Now the
    deviation is a choice somebody can close today, so it is a failure:

        >>> state = dependency_state(version=None, pin="27efaf7", available=["v0.2.0"])
        >>> state.state
        'fail'
        >>> "v0.2.0" in state.fix
        True

    Pinned to a version that was published:

        >>> dependency_state(version="v0.2.0", available=["v0.1.0", "v0.2.0"]).state
        'pass'

    Pinned to a version that was not -- a typo, or a tag that was deleted after
    this project came to depend on it:

        >>> state = dependency_state(version="v9.9.9", available=["v0.2.0"])
        >>> state.state
        'fail'
        >>> "not published" in state.summary
        True

    The remote could not be reached. Not a pass, and not a failure either: the
    question went unasked, and saying otherwise is the habit this repository
    keeps catching itself in.

        >>> dependency_state(version="v0.2.0", available=None, asked=False).state
        'unknown'
    """
    if not asked or available is None:
        return Dependency(
            UNKNOWN,
            f"could not reach {APOTHECARY_REPO} to see what it has released",
            "run again with a network, or read the enclosure job in CI",
        )

    if version:
        if version in available:
            return Dependency(PASS, f"depends on the released {version}")
        return Dependency(
            FAIL,
            f"depends on {version}, which apothecary has not published",
            f"published versions: {', '.join(available) or 'none'}",
        )

    if not available:
        return Dependency(
            WARN,
            f"at commit {pin}: apothecary has no released version to depend on yet",
            "clause 5 cannot be met until apothecary tags a release; "
            "set APOTHECARY_VERSION when it does",
        )

    newest = available[-1]
    return Dependency(
        FAIL,
        f"at commit {pin}, but apothecary has published {len(available)} version(s)",
        f"set APOTHECARY_VERSION to a released version, newest is {newest}",
    )


def checkout_ref(version: Optional[str] = APOTHECARY_VERSION, pin: str = APOTHECARY_PIN) -> str:
    """What CI should check out: the release if there is one, else the commit.

    One place decides, so the workflow and the local run cannot disagree about
    which apothecary was verified.

        >>> checkout_ref(version="v0.2.0", pin="abc1234")
        'v0.2.0'
        >>> checkout_ref(version=None, pin="abc1234")
        'abc1234'
    """
    return version or pin


def describe(version: Optional[str] = APOTHECARY_VERSION, pin: str = APOTHECARY_PIN) -> str:
    """The reference, in the form a report should name it.

        >>> describe(version="v0.2.0", pin="abc1234")
        'the released v0.2.0'
        >>> describe(version=None, pin="abc1234")
        'the pinned commit abc1234'
    """
    return f"the released {version}" if version else f"the pinned commit {pin}"


def current() -> Tuple[Dependency, Optional[List[str]]]:
    """Ask the remote, then judge. The pairing the callers actually want."""
    available = released_versions()
    return dependency_state(available=available, asked=available is not None), available
