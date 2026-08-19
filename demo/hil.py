"""Prove everything this project can prove without hardware, and name the rest.

Run before a hardware-in-the-loop pass. It exercises the contract end to end
against whatever is installed, writes report artifacts for the parts that
produce them, and finishes by listing the IRL cases that a bench and a board
are the only way to close.

Nothing here is a substitute for ``uv run pytest``, which is the actual test
suite. This is the reviewer's entry point: one command, one table, and an
explicit account of what was skipped and why.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "schema" / "build" / "reports"

# The apothecary checkout, if it is a sibling. The enclosure lives there and
# nowhere else -- no printable geometry lands in this repository.
APOTHECARY = ROOT.parent / "apothecary"


@dataclass
class Step:
    name: str
    detail: str = ""
    state: str = "pending"  # pass | fail | skip
    notes: list[str] = field(default_factory=list)

    def passed(self, detail: str = "") -> "Step":
        self.state, self.detail = "pass", detail or self.detail
        return self

    def failed(self, detail: str) -> "Step":
        self.state, self.detail = "fail", detail
        return self

    def skipped(self, detail: str) -> "Step":
        self.state, self.detail = "skip", detail
        return self


def run(args: list[str], cwd: Path = ROOT, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
        encoding="utf-8",
        errors="replace",
    )


def broker_from_env() -> tuple[str, int] | None:
    """``DATUM_BROKER`` as host and port, the variable the wire cookbook reads."""
    raw = os.environ.get("DATUM_BROKER", "").strip()
    if not raw:
        return None
    host, _, port = raw.partition(":")
    return host or "127.0.0.1", int(port or 1883)


def reachable(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def tail_of(result: subprocess.CompletedProcess, lines: int = 3) -> str:
    text = (result.stdout or "") + (result.stderr or "")
    kept = [line.strip() for line in text.strip().splitlines() if line.strip()][-lines:]
    return " / ".join(kept) or "no output"


# --------------------------------------------------------------------- steps


def step_schema(steps: list[Step]) -> None:
    s = Step("Schema emits", "the JSON Schema a consumer in another language validates against")
    steps.append(s)
    result = run([sys.executable, "-m", "datum", "emit"])
    if result.returncode != 0:
        s.failed(tail_of(result))
        return
    built = sorted((ROOT / "schema" / "build").glob("*.json"))
    s.passed(f"{len(built)} schema file(s) in schema/build/")


def step_vectors(steps: list[Step]) -> None:
    """Every checked-in vector, each leaving a report behind."""
    s = Step("Vectors validate", "valid accepted, malformed rejected")
    steps.append(s)
    REPORTS.mkdir(parents=True, exist_ok=True)

    vectors = ROOT / "schema" / "vectors"
    good = sorted((vectors / "valid").glob("*.json"))
    bad = sorted((vectors / "invalid").glob("*.json"))
    if not good or not bad:
        s.skipped("no vectors found")
        return

    wrong = []
    cases = [(p, True) for p in good] + [(p, False) for p in bad]
    for path, expect_ok in cases:
        report = REPORTS / f"{path.parent.name}-{path.stem}.json"
        result = run(
            [sys.executable, "-m", "datum", "validate", str(path), "--report", str(report)]
        )
        if (result.returncode == 0) is not expect_ok:
            verdict = "was rejected" if expect_ok else "was accepted"
            wrong.append(f"{path.parent.name}/{path.name} {verdict}")

    if wrong:
        s.failed("; ".join(wrong))
        return
    s.passed(f"{len(good)} valid, {len(bad)} malformed, {len(cases)} reports written")


def step_stdin(steps: list[Step]) -> None:
    """The path a live capture takes: piped in, not written to a file first."""
    s = Step("Piped capture validates", "mosquitto_sub | datum validate -")
    steps.append(s)
    event = json.dumps(
        {"src": "datum/lab/jig", "seq": 1, "caps": ["press"], "action": "single", "ch": 0}
    )
    result = subprocess.run(
        [sys.executable, "-m", "datum", "validate", "-"],
        cwd=str(ROOT),
        input=event,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        s.failed(tail_of(result))
        return
    s.passed(result.stdout.strip())


def step_wire(steps: list[Step], broker: tuple[str, int] | None) -> None:
    """Topic, encoding and retention, over a real broker."""
    s = Step("Wire contract", "topics, retention, and a late subscriber")
    steps.append(s)
    if broker is None:
        s.skipped("DATUM_BROKER not set -- see demo/README.md for the one docker line")
        return
    host, port = broker
    if not reachable(host, port):
        s.skipped(f"nothing accepting connections on {host}:{port}")
        return

    result = run([sys.executable, "-m", "pytest", "docs/wire.md", "-q", "-rs"])
    if result.returncode != 0:
        s.failed(tail_of(result))
        return
    s.passed(f"round-trip ok against {host}:{port}")


def step_firmware(steps: list[Step]) -> None:
    s = Step("Firmware configuration", "esphome config resolves every wire-critical string")
    steps.append(s)

    # ESPHome is not a dependency of this package and should not become one:
    # it is the engine the firmware runs on, not something this repository
    # wraps. Use it if it is installed, and otherwise let uv fetch it for the
    # length of one command.
    if shutil.which("esphome"):
        args = ["esphome", "config", "firmware/t1-core.yaml"]
    elif shutil.which("uv"):
        args = ["uv", "run", "--with", "esphome", "esphome", "config", "firmware/t1-core.yaml"]
    else:
        s.skipped("neither esphome nor uv on PATH -- see demo/README.md")
        return

    result = run(args, timeout=900)
    if result.returncode != 0:
        s.failed(tail_of(result, 2))
        return
    s.passed("configuration is valid")


def step_firmware_seam(steps: list[Step]) -> None:
    """The check that the YAML and the Python constants still agree."""
    s = Step("Firmware seam", "topics and payloads read back out of the YAML")
    steps.append(s)
    result = run([sys.executable, "-m", "pytest", "docs/firmware.md", "-q"])
    if result.returncode != 0:
        s.failed(tail_of(result))
        return
    s.passed("YAML and constants agree")


def step_enclosure(steps: list[Step]) -> None:
    s = Step("Enclosure bounds", "datum-core declared envelope vs rendered geometry")
    steps.append(s)
    if not APOTHECARY.is_dir():
        s.skipped(f"no apothecary checkout at {APOTHECARY}")
        return
    if shutil.which("uv") is None:
        s.skipped("uv not on PATH")
        return
    result = run(
        ["uv", "run", "apothecary", "parts", "verify", "datum-core"],
        cwd=APOTHECARY,
        timeout=600,
    )
    if result.returncode != 0:
        if "OpenSCAD not found" in (result.stdout + result.stderr):
            s.skipped("OpenSCAD not installed")
            return
        s.failed(tail_of(result, 4))
        return
    s.passed("declared bounds match the geometry")


# ------------------------------------------------------------------ reporting

NEEDS_HARDWARE = [
    ("IRL-001", "Single press emits one event, action=single"),
    ("IRL-002", "Hold then release emits two events, in that order"),
    ("IRL-003", "Ordered multi-press keeps seq monotonic across a run"),
    ("IRL-004", "seq survives a reconnect without going backwards"),
    ("IRL-005", "Announce is retained and reaches a late subscriber"),
    ("IRL-006", "Availability is retained, and last-will fires on an ungraceful drop"),
    ("IRL-007", "An event is NOT retained -- a late subscriber sees nothing"),
]

MARK = {"pass": "PASS", "fail": "FAIL", "skip": "SKIP", "pending": "????"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--broker",
        help="host:port of an MQTT broker. Overrides DATUM_BROKER for this run.",
    )
    args = parser.parse_args()
    if args.broker:
        os.environ["DATUM_BROKER"] = args.broker

    broker = broker_from_env()
    steps: list[Step] = []

    print("Datum -- pre-HIL proof run")
    print(f"repository: {ROOT}")
    print("")

    step_schema(steps)
    step_vectors(steps)
    step_stdin(steps)
    step_wire(steps, broker)
    step_firmware(steps)
    step_firmware_seam(steps)
    step_enclosure(steps)

    width = max(len(s.name) for s in steps)
    for s in steps:
        print(f"  [{MARK[s.state]}] {s.name.ljust(width)}  {s.detail}")

    failed = [s for s in steps if s.state == "fail"]
    skipped = [s for s in steps if s.state == "skip"]
    passed = [s for s in steps if s.state == "pass"]

    print("")
    print(f"{len(passed)} proved, {len(failed)} failed, {len(skipped)} skipped")
    if REPORTS.exists():
        print(f"reports: {REPORTS.relative_to(ROOT)}")

    print("")
    print("Still needs a board on a bench. Nothing above can close these:")
    for case, description in NEEDS_HARDWARE:
        print(f"  {case}  {description}")
    print("")
    print("  planning/IRL_TEST_MATRIX.md carries the stimulus and expected result")
    print("  for each. firmware/README.md has the GPIO map and the jig wiring.")

    if skipped:
        print("")
        print("Skipped, and why:")
        for s in skipped:
            print(f"  {s.name}: {s.detail}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
