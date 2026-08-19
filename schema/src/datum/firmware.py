"""Read the wire-critical literals back out of the ESPHome configuration.

``walkthrough/08-wire.md`` names the failure an in-process fixture cannot see: a topic
that is right in the constant and wrong in the firmware. A real broker catches
it only once real firmware is flashed and someone is standing next to it.

The firmware keeps every string that reaches the wire in its ``substitutions:``
block rather than buried in a lambda, so this module can read them back as text
and ``walkthrough/04-firmware.md`` can check them against the same constants a consumer
compiles against. Nothing here parses YAML: the values under test are literal
wire strings, and reading them as text is what the check is about.

    >>> substitution("hw")
    't1-core-r0'
"""

from __future__ import annotations

from pathlib import Path

CONFIG = "t1-core.yaml"
"""The device configuration. The per-channel package it includes has no
substitutions of its own -- it inherits every one of them from this file."""


def firmware_dir() -> Path:
    """Locate ``firmware/`` from inside the package, in a source checkout.

    >>> firmware_dir().name
    'firmware'
    """
    for parent in Path(__file__).resolve().parents:
        if (parent / "firmware" / CONFIG).is_file():
            return parent / "firmware"
    raise FileNotFoundError("firmware/ not found; run from a source checkout")


def config_text() -> str:
    """The device configuration as text.

    >>> config_text().splitlines()[0]
    '# Datum T1-Core -- stock ESPHome on an ESP32-C6.'
    """
    return (firmware_dir() / CONFIG).read_text(encoding="utf-8")


def substitutions() -> dict[str, str]:
    """Every key under the configuration's ``substitutions:`` block.

    The block ends at the first line that starts a new top-level key, which is
    how a two-space-indented mapping ends in any YAML file.

    >>> substitutions()["src"]
    'datum/lab/jig'
    """
    found: dict[str, str] = {}
    inside = False

    for line in config_text().splitlines():
        stripped = line.strip()

        if not inside:
            inside = stripped == "substitutions:"
            continue
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith(" "):
            break

        key, _, value = stripped.partition(": ")
        # A quoted scalar keeps its quotes out of the value, and an unquoted
        # one has none to strip.
        found[key] = value.strip().strip("'\"")

    return found


def substitution(key: str) -> str:
    """One value from that block.

    >>> substitution("fw")
    '0.1.0'
    """
    return substitutions()[key]


PACKAGE = "contact.yaml"
"""The per-channel package, included once per contact."""

RESERVED_GPIO = {
    4: "strapping",
    5: "strapping",
    8: "strapping",
    9: "strapping",
    15: "strapping",
    12: "USB D-",
    13: "USB D+",
    16: "UART0 TX",
    17: "UART0 RX",
    **{pin: "SPI flash" for pin in range(24, 31)},
}
"""ESP32-C6 pins a contact must not land on, and what each is spoken for.

A strapping pin held by a closed contact at reset chooses a boot mode instead
of reporting a press, which presents as a board that boots differently
depending on whether someone is touching it.
"""


def contact_pins() -> dict[int, int]:
    """Channel number to GPIO number, from the configuration's GPIO map.

    >>> contact_pins()
    {0: 2, 1: 3, 2: 10, 3: 11}
    """
    return {
        int(key.split("_")[1]): int(value.removeprefix("GPIO"))
        for key, value in substitutions().items()
        if key.startswith("contact_") and key.endswith("_pin")
    }


def emitted_actions() -> set[str]:
    """Every ``action`` the per-channel package hands to the emit script.

    >>> "hold" in emitted_actions()
    True
    """
    text = (firmware_dir() / PACKAGE).read_text(encoding="utf-8")
    return {
        line.split("action:", 1)[1].strip()
        for line in text.splitlines()
        if line.strip().startswith("action:")
    }
