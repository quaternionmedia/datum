"""The pre-HIL proof run: everything provable without hardware, and what is left.

``datum hil`` exercises the contract end to end against whatever is installed,
writes the report artifacts, and finishes by naming the IRL cases that a board
on a bench is the only way to close. It starts nothing and leaves nothing
running.

This is not the test suite. ``uv run pytest`` is, and it runs every example
under ``walkthrough/`` plus these docstrings. This orchestrates across two
repositories and a firmware toolchain, which no doctest can reach — so what
lives here is the orchestration, and the pieces that can be checked in-process
carry their own examples below.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MQTT_PORT = 1883

# The enclosure lives in quaternionmedia/apothecary and nowhere else, so this
# project depends on a specific state of it. Pinned rather than "whatever is
# checked out next door": a sibling directory is a convenience for a developer
# with both repositories open, and no statement at all about what CI verified.
#
# Bumping the pin is a reviewed commit here, the same way the governance
# submodule's pin is.
APOTHECARY_REPO = "https://github.com/quaternionmedia/apothecary"
APOTHECARY_PIN = "94b62cc"
APOTHECARY_PARTS = ("datum-core",)

# The cases nothing on a desk can close. Kept beside the runner so the list a
# reviewer is told to work through is the list the code prints; walkthrough/07-hil.md
# checks these against planning/IRL_TEST_MATRIX.md.
NEEDS_HARDWARE: tuple[tuple[str, str], ...] = (
    ("IRL-001", "Single press emits one event, action=single"),
    ("IRL-002", "Hold then release emits two events, in that order"),
    ("IRL-003", "Ordered multi-press keeps seq monotonic across a run"),
    ("IRL-004", "seq survives a reconnect without going backwards"),
    ("IRL-005", "Announce is retained and reaches a late subscriber"),
    ("IRL-006", "Availability is retained, and last-will fires on an ungraceful drop"),
    ("IRL-007", "An event is NOT retained -- a late subscriber sees nothing"),
)

MARK = {"pass": "PASS", "fail": "FAIL", "skip": "SKIP"}


def irl_case_ids() -> list[str]:
    """The hardware-only case identifiers, in order.

    >>> irl_case_ids()[0], irl_case_ids()[-1]
    ('IRL-001', 'IRL-007')
    >>> len(irl_case_ids())
    7
    """
    return [case for case, _ in NEEDS_HARDWARE]


def parse_broker(raw: str | None) -> tuple[str, int] | None:
    """A ``host:port`` string as its parts, defaulting the port.

    ``DATUM_BROKER`` is the same variable the wire cookbook reads, so a bench
    that already has one exported needs no argument here.

    >>> parse_broker("10.0.0.2:1883")
    ('10.0.0.2', 1883)
    >>> parse_broker("localhost")
    ('localhost', 1883)
    >>> parse_broker(":11883")
    ('127.0.0.1', 11883)
    >>> parse_broker("") is None
    True
    >>> parse_broker(None) is None
    True
    """
    if not raw or not raw.strip():
        return None
    host, _, port = raw.strip().partition(":")
    return host or "127.0.0.1", int(port or DEFAULT_MQTT_PORT)


def find_repo_root(start: Path | None = None) -> Path | None:
    """The checkout this command is being run inside, or None.

    Walks up looking for the two things every step needs: the project file and
    the vectors. An installed wheel has neither, and saying so is better than
    reporting seven skips with seven different reasons.
    """
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "schema" / "vectors").is_dir():
            return candidate
    return None


def pin_state(local: str | None, pin: str = APOTHECARY_PIN, dirty: bool = False) -> str:
    """How a checked-out apothecary relates to the pin, in one clause.

    A developer is entitled to work against a newer apothecary, so drift is not
    a failure. Reporting the run as proving the pin when it proved something
    else would be, and so would claiming the pin when the commit could not be
    read at all.

    >>> pin_state("abc1234", pin="abc1234")
    'at the pinned abc1234'

    A longer hash from ``git rev-parse`` is the same commit:

    >>> pin_state("abc1234def", pin="abc1234")
    'at the pinned abc1234'

    >>> pin_state("deadbee", pin="abc1234")
    'at deadbee, not the pinned abc1234'

    Not knowing is its own answer, and never the pin:

    >>> pin_state("", pin="abc1234")
    'at an undetermined commit, pinned abc1234'
    >>> pin_state(None, pin="abc1234")
    'at an undetermined commit, pinned abc1234'

    A working tree with uncommitted changes is not the commit it names. What
    ran was that commit plus something nobody else has:

    >>> pin_state("abc1234", pin="abc1234", dirty=True)
    'at the pinned abc1234, plus uncommitted changes'
    >>> pin_state("deadbee", pin="abc1234", dirty=True)
    'at deadbee, not the pinned abc1234, plus uncommitted changes'
    """
    local = (local or "").strip()
    edited = ", plus uncommitted changes" if dirty else ""
    if not local:
        return f"at an undetermined commit, pinned {pin}"
    if pin.startswith(local) or local.startswith(pin):
        return f"at the pinned {pin}{edited}"
    return f"at {local}, not the pinned {pin}{edited}"


def reachable(host: str, port: int, timeout: float = 2.0) -> bool:
    """Whether something is accepting connections there."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


@dataclass
class Step:
    """One line of the report.

    A skip is never a pass. The distinction is the whole point of the table —
    this project has been careful elsewhere about not reporting a skipped
    assertion as green, and the same rule applies here.

    >>> s = Step("Wire contract")
    >>> s.state
    'pending'
    >>> s.skipped("no broker").state
    'skip'
    >>> Step("Vectors").passed("10 reports").detail
    '10 reports'
    """

    name: str
    detail: str = ""
    state: str = "pending"

    def passed(self, detail: str = "") -> "Step":
        self.state, self.detail = "pass", detail or self.detail
        return self

    def failed(self, detail: str) -> "Step":
        self.state, self.detail = "fail", detail
        return self

    def skipped(self, detail: str) -> "Step":
        self.state, self.detail = "skip", detail
        return self


def tail_of(result: subprocess.CompletedProcess, lines: int = 3) -> str:
    """The last few meaningful lines of a failed run, joined for one table cell.

    >>> done = subprocess.CompletedProcess([], 1, "first\\n\\nsecond\\n", "")
    >>> tail_of(done, 2)
    'first / second'
    """
    text = (result.stdout or "") + (result.stderr or "")
    kept = [line.strip() for line in text.strip().splitlines() if line.strip()][-lines:]
    return " / ".join(kept) or "no output"


def _run(args: list[str], cwd: Path, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
        encoding="utf-8",
        errors="replace",
    )


# --------------------------------------------------------------------- steps


def step_schema(root: Path) -> Step:
    s = Step("Schema emits", "the JSON Schema a consumer in another language validates against")
    result = _run([sys.executable, "-m", "datum", "emit"], root)
    if result.returncode != 0:
        return s.failed(tail_of(result))
    built = sorted((root / "schema" / "build").glob("*.json"))
    return s.passed(f"{len(built)} schema file(s) in schema/build/")


def step_vectors(root: Path) -> Step:
    """Every checked-in vector, each leaving a report behind."""
    s = Step("Vectors validate", "valid accepted, malformed rejected")
    reports = root / "schema" / "build" / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    vectors = root / "schema" / "vectors"
    good = sorted((vectors / "valid").glob("*.json"))
    bad = sorted((vectors / "invalid").glob("*.json"))
    if not good or not bad:
        return s.skipped("no vectors found")

    wrong = []
    cases = [(p, True) for p in good] + [(p, False) for p in bad]
    for path, expect_ok in cases:
        report = reports / f"{path.parent.name}-{path.stem}.json"
        result = _run(
            [sys.executable, "-m", "datum", "validate", str(path), "--report", str(report)], root
        )
        if (result.returncode == 0) is not expect_ok:
            wrong.append(
                f"{path.parent.name}/{path.name} "
                f"{'was rejected' if expect_ok else 'was accepted'}"
            )

    if wrong:
        return s.failed("; ".join(wrong))
    return s.passed(f"{len(good)} valid, {len(bad)} malformed, {len(cases)} reports written")


def step_stdin(root: Path) -> Step:
    """The path a live capture takes: piped in, not written to a file first."""
    s = Step("Piped capture validates", "mosquitto_sub | datum validate -")
    event = json.dumps(
        {"src": "datum/lab/jig", "seq": 1, "caps": ["press"], "action": "single", "ch": 0}
    )
    result = subprocess.run(
        [sys.executable, "-m", "datum", "validate", "-"],
        cwd=str(root),
        input=event,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        return s.failed(tail_of(result))
    return s.passed(result.stdout.strip())


def step_wire(root: Path, broker: tuple[str, int] | None) -> Step:
    """Topic, encoding and retention, over a real broker."""
    s = Step("Wire contract", "topics, retention, and a late subscriber")
    if broker is None:
        return s.skipped("DATUM_BROKER not set -- see walkthrough/07-hil.md for the one docker line")
    host, port = broker
    if not reachable(host, port):
        return s.skipped(f"nothing accepting connections on {host}:{port}")

    env_before = os.environ.get("DATUM_BROKER")
    os.environ["DATUM_BROKER"] = f"{host}:{port}"
    try:
        result = _run([sys.executable, "-m", "pytest", "walkthrough/08-wire.md", "-q", "-rs"], root)
    finally:
        if env_before is None:
            os.environ.pop("DATUM_BROKER", None)
        else:
            os.environ["DATUM_BROKER"] = env_before

    if result.returncode != 0:
        return s.failed(tail_of(result))
    return s.passed(f"round-trip ok against {host}:{port}")


def step_firmware(root: Path) -> Step:
    s = Step("Firmware configuration", "esphome config resolves every wire-critical string")

    # ESPHome is the engine the firmware runs on, not something this package
    # wraps, so it is not a dependency here. Use it if it is installed, and
    # otherwise let uv fetch it for the length of one command.
    if shutil.which("esphome"):
        args = ["esphome", "config", "firmware/t1-core.yaml"]
    elif shutil.which("uv"):
        args = ["uv", "run", "--with", "esphome", "esphome", "config", "firmware/t1-core.yaml"]
    else:
        return s.skipped("neither esphome nor uv on PATH -- see walkthrough/07-hil.md")

    result = _run(args, root, timeout=900)
    if result.returncode != 0:
        return s.failed(tail_of(result, 2))
    return s.passed("configuration is valid")


def step_firmware_seam(root: Path) -> Step:
    """The check that the YAML and the Python constants still agree."""
    s = Step("Firmware seam", "topics and payloads read back out of the YAML")
    result = _run([sys.executable, "-m", "pytest", "walkthrough/04-firmware.md", "-q"], root)
    if result.returncode != 0:
        return s.failed(tail_of(result))
    return s.passed("YAML and constants agree")


def step_enclosure(root: Path) -> Step:
    """The enclosure lives in apothecary and nowhere else, so this reaches across."""
    s = Step("Enclosure bounds", "datum-core declared envelope vs rendered geometry")
    apothecary = root.parent / "apothecary"
    if not apothecary.is_dir():
        return s.skipped(f"no apothecary checkout at {apothecary}")
    if shutil.which("uv") is None:
        return s.skipped("uv not on PATH")

    head = _run(["git", "rev-parse", "--short", "HEAD"], apothecary, timeout=60)
    edits = _run(["git", "status", "--porcelain"], apothecary, timeout=60)
    state = pin_state(
        head.stdout if head.returncode == 0 else "",
        dirty=bool(edits.returncode == 0 and (edits.stdout or "").strip()),
    )

    result = _run(
        ["uv", "run", "apothecary", "parts", "verify", "datum-core"], apothecary, timeout=600
    )
    if result.returncode != 0:
        if "OpenSCAD not found" in (result.stdout + result.stderr):
            return s.skipped("OpenSCAD not installed")
        return s.failed(tail_of(result, 4))

    return s.passed(f"declared bounds match the geometry, {state}")


def run_all(root: Path, broker: tuple[str, int] | None) -> list[Step]:
    """Every step, in the order a reviewer should read them."""
    return [
        step_schema(root),
        step_vectors(root),
        step_stdin(root),
        step_wire(root, broker),
        step_firmware(root),
        step_firmware_seam(root),
        step_enclosure(root),
    ]
