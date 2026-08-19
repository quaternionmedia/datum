# Firmware

Stock ESPHome on an ESP32-C6. Four dry contacts in, one versioned JSON event
out over MQTT. No deep sleep, no battery sensor, no power gating — the module
is USB-C bus powered and always on.

| | |
|---|---|
| `t1-core.yaml` | The device configuration. Every wire-critical string lives in its `substitutions:` block |
| `contact.yaml` | One contact, included four times with a different channel and pin |

The contract these files implement is in [`walkthrough/03-topic-contract.md`](../walkthrough/03-topic-contract.md).
The check that they still implement it is [`walkthrough/04-firmware.md`](../walkthrough/04-firmware.md),
which reads the topics and payloads back out of the YAML and compares them to
the Python constants. It runs under `uv run pytest` with everything else.

## The board

**ESP32-C6-DevKitC-1**, carrying an ESP32-C6-WROOM-1 module. It has two USB-C
ports: the one marked `USB` is the chip's native USB Serial/JTAG on GPIO12 and
GPIO13, and the one marked `UART` goes through the bridge. Either flashes.

`framework: type: esp-idf` is not a preference. The C6 has no Arduino
framework path in ESPHome.

## The GPIO map

| Channel | GPIO | |
|---|---|---|
| 0 | GPIO2 | contact |
| 1 | GPIO3 | contact |
| 2 | GPIO10 | contact |
| 3 | GPIO11 | contact |
| — | GPIO8 | indicator, SK6812 |

No contact is on a strapping pin (4, 5, 8, 9, 15), a USB pin (12, 13), a UART0
pin (16, 17) or a flash pin (24–30). A contact closed across a strapping pin at
reset picks a boot mode instead of reporting a press, which presents as a board
that boots differently depending on whether someone is touching it.

GPIO8 is a strapping pin and carries the indicator anyway: it is where the
DevKitC-1 puts its own addressable LED, and an output driven after boot reads
no strap.

## Wiring the T0 contact jig

Each contact is a bare dry closure between its GPIO and any `GND` pin.
Nothing else. No external pull-up, no supply rail on the contact, and no
voltage of any kind across it.

```
GPIO2  ──────┐
             │  (contact 0)
GND    ──────┘
```

The pin is configured `input: true, pullup: true, inverted: true`, so an open
contact reads OFF and a closed one reads ON. A 20 ms `delayed_on_off` filter
covers switch bounce.

The T1-Core board does this properly in copper — 10 kΩ pull-up, 100 Ω series,
100 nF to ground and a TVS to a common ESD rail — and that is WP-4. On a bare
devkit the internal pull-up and the debounce filter are what you get, which is
enough to develop against and not enough to put on a wall.

## Gestures

| | |
|---|---|
| `single` | one closure, then 400 ms of quiet |
| `double` | two closures inside 400 ms of each other |
| `triple` | three, same window |
| `hold` | held closed for 900 ms — emitted while still closed |
| `release` | the opening that ends a hold, and only a hold |

Every gesture ends in a physical release. Only a hold emits one, so a single
press is one event rather than two.

## Building and flashing

```
pip install esphome
esphome config firmware/t1-core.yaml
esphome run firmware/t1-core.yaml
```

`esphome config` resolves the substitutions and prints the assembled
configuration, which is the fastest way to see what a change did.

Real credentials are substitution overrides rather than a secrets file, so the
configuration compiles in CI unmodified:

```
esphome run firmware/t1-core.yaml \
  -s wifi_ssid "$SSID" -s wifi_password "$PSK" \
  -s mqtt_broker 10.0.0.2 -s src datum/kitchen/north
```

`src` is the identity and the topic path both. Changing it moves every topic
the module publishes on, which is the intent — a second module on the same
broker differs by that one string.

## Watching it

```
mosquitto_sub -h 10.0.0.2 -t 'datum/#' -v
```

On connect you should see a retained announce and a retained `online`, then one
event per gesture and nothing between them.
