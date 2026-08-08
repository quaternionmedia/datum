"""Collection gate for the wire cookbook.

`WIRE.md` documents behaviour that only exists over a real broker. Without one
it is skipped with a stated reason rather than failing, and rather than being
quietly dropped — a silently skipped test is worse than an absent one, so this
reports what did not run and how to run it.

`collect_ignore` is not used: entries in `testpaths` are treated like explicit
command-line arguments, and explicit arguments bypass it.
"""

from pathlib import Path

import pytest

WIRE_COOKBOOK = "WIRE.md"


def pytest_collection_modifyitems(config, items):
    from tessera.harness import broker_address, broker_reachable

    if broker_reachable():
        return

    host, port = broker_address()
    reason = (
        f"no MQTT broker at {host}:{port}: "
        f"start one with `docker run -d --rm -p {port}:1883 eclipse-mosquitto:2`, "
        f"or set TESSERA_BROKER=host:port"
    )
    skip = pytest.mark.skip(reason=reason)
    for item in items:
        if Path(str(item.fspath)).name == WIRE_COOKBOOK:
            item.add_marker(skip)
