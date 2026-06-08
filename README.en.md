# ESP8266 AI Light Hook

[中文版](./README.md)

Use an ESP8266 traffic light as a physical status indicator for `Codex` and `Claude Code`.

The device listens on `192.168.1.88:8899` over TCP. A local hook script sends a single uppercase command, and the ESP8266 updates the red, yellow, and green LEDs immediately.

## What It Does

- Turns AI agent state changes into visible hardware signals
- Works with `Codex` project hooks and `Claude Code` hooks
- Uses a simple TCP protocol with ACK (`OK\n`) and sender retries
- Keeps the firmware protocol small enough to change behavior by changing hook letters

## Demo Mapping

The current example hook mapping in this repo is:

- `SessionStart -> E`
- `UserPromptSubmit -> Q`
- `PermissionRequest -> G`
- `Stop -> A`

That gives you:

- `E`: fixed red-yellow-green alternating for standby
- `Q`: red-yellow-green alternating for active work
- `G`: red solid for approval needed
- `A`: green solid for round complete

## Hardware

- Board: `NodeMCU 1.0 (ESP-12E Module)`
- Light module: common-cathode red/yellow/green traffic light

### Wiring

- `R -> D1`
- `Y -> D2`
- `G -> D3`
- `GND -> GND`

## Network Defaults

- Wi-Fi SSID: `TP-LINK_2.4bbt`
- Wi-Fi password: `123584679`
- Device IP: `192.168.1.88`
- TCP port: `8899`

## Light Protocol

The protocol uses a single uppercase letter for each lighting scheme.

Accelerating flashing and alternating schemes use this rule:

- Initial step interval: `300ms`
- Speed-up: every `1` second, reduce by `1ms`
- Floor: `100ms`

Fixed slow flashing schemes use:

- Step interval: `500ms`
- Full on/off cycle: `1000ms`

### Solid Schemes

- `A`: green solid
- `D`: yellow solid
- `G`: red solid
- `T`: all off
- `U`: all on

### Flashing Schemes

- `B`: green accelerating flash
- `C`: green slow flash
- `E`: fixed red-yellow-green alternating, `500ms` per step, no acceleration
- `F`: yellow slow flash
- `H`: red accelerating flash
- `I`: red slow flash
- `V`: all lights accelerating flash
- `W`: all lights slow flash

### Alternating Schemes

- `J`: red-green alternating
- `L`: red-yellow alternating
- `N`: yellow-green alternating
- `Q`: red-yellow-green alternating
- `R`: green-yellow-red alternating

### Deprecated Letters

These letters were merged away and are no longer accepted:

- `K`
- `M`
- `O`
- `P`
- `S`

The device ignores `\r` and `\n`.

## Quick Start

### 1. Flash the Firmware

Open this sketch in Arduino IDE:

`firmware/esp8266_ai_light_hook/esp8266_ai_light_hook.ino`

Recommended board setting:

- `NodeMCU 1.0 (ESP-12E Module)`

### 2. Test the Sender Script

On Linux:

```bash
chmod +x send-light.sh
./send-light.sh E
./send-light.sh Q
./send-light.sh A
```

If your device address is different:

```bash
./send-light.sh Q 192.168.1.88 8899
```

### 3. Enable Hooks

Codex example:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "bash ./send-light.sh E"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ./send-light.sh Q"
          }
        ]
      }
    ],
    "PermissionRequest": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "bash ./send-light.sh G"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ./send-light.sh A"
          }
        ]
      }
    ]
  }
}
```

## Reliability

- The sender waits for `OK\n`
- The sender retries `3` times on failure
- The ESP8266 returns `ERR\n` for invalid letters
- The ESP8266 drops idle clients after `1500ms`

## Repository Layout

- `firmware/esp8266_ai_light_hook/`: ESP8266 firmware
- `tests/`: protocol and hook verification scripts
- `docs/linux-codex-claude-light-hooks-tutorial.md`: Linux setup tutorial
- `.codex/hooks.json`: Codex hook example
- `.claude/settings.json`: Claude Code hook example
- `send-light.sh`: Linux sender with ACK and retry
- `docs/archive/superpowers/`: archived internal plans and design notes

## Notes

- The current Codex setup reflects lifecycle states, not process exit codes
- If you change hook letters, re-flashing is not required as long as the target letter already exists in firmware
- If you add a brand-new light scheme, you still need a firmware update
