<div align="center">

# Pico PC Controller

### A wireless gamepad built on the Raspberry Pi Pico W — no drivers, no dongles.
### Connects over **Wi-Fi (UDP)** with automatic fallback to **Bluetooth (BLE UART)**.

[![MicroPython](https://img.shields.io/badge/MicroPython-v1.23%2B-blue?logo=python&logoColor=white)](https://micropython.org/)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%20Pico%20W-red?logo=raspberrypi)](https://www.raspberrypi.com/products/raspberry-pi-pico/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-yellow?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-pink)](https://github.com/)

</div>

---

## ✨ What Is This?

> Press a physical button → your PC registers a real keypress. Instantly. Wirelessly.

**Pico PC Controller** turns a $6 microcontroller and 5 push buttons into a fully functional wireless keyboard/gamepad. It's perfect for gaming (W/A/S/D + handbrake), presentations, or any hands-free PC control.

No HID firmware hacks. No USB gadget mode. No complicated pairing. It just works.

---

## 🚀 Features

- 📶 **Dual transport** — Wi-Fi UDP primary, BLE UART automatic fallback
- ⚡ **125Hz polling** — 8ms loop, responsive enough for fast-paced driving games
- 💡 **Smart LED feedback** — dim on single press, bright on combos, blink on WiFi connect
- 🔄 **True hold support** — holding a button = key held on PC (essential for driving games)
- 🔁 **Auto-reconnect** — BLE rescans automatically if connection drops
- 🏢 **Works on restricted networks** — falls back to Bluetooth if workplace AP blocks UDP
- 🪶 **Lightweight** — ~120 lines of MicroPython, zero external Pico libraries

---

## 📁 Repository Structure

```
pico-pc-controller/
│
├── pico/
│   ├── main.py          ← Flash this to your Pico W
│   └── ble_helper.py    ← BLE UART class (required by main.py)
│
├── pc/
│   └── receiver.py      ← Run this on your PC
│
├── assets/
│   └── wiring.png       ← Connection diagram (see below)
│
├── README.md
└── LICENSE
```

> **Files to upload to GitHub:** All of the above. The `pico/` folder goes on the Pico W, the `pc/` folder runs on any Windows/Mac/Linux machine.

---

## 🔧 Hardware Required

| Component | Qty | Notes |
|-----------|-----|-------|
| Raspberry Pi Pico W | 1 | Must be **Pico W** (has WiFi/BT chip) |
| Push buttons (momentary) | 5 | Any standard 6mm tactile switch |
| LED | 1 | Any colour, 3mm or 5mm |
| Resistor 220Ω | 1 | Current limiter for LED |
| Breadboard | 1 | Half-size is enough |
| Jumper wires | ~15 | Male-to-male |
| Micro-USB cable | 1 | For power + flashing |

**Total cost: ~₹300–400 / ~$5–7**

---

## 🔌 Wiring Diagram

```
RASPBERRY PI PICO W
┌─────────────────────────────────────────┐
│                                         │
│  GP2  ──[W BTN]──────────────── GND    │
│                                         │
│  GP3  ──[SPACE BTN]──────────── GND    │
│       (Handbrake)                       │
│                                         │
│  GP4  ──[D BTN]──────────────── GND    │
│                                         │
│  GP5  ──[A BTN]──────────────── GND    │
│                                         │
│  GP6  ──[S BTN]──────────────── GND    │
│                                         │
│  GP9  ──[220Ω]──[LED+]──[LED-]── GND  │
│                                         │
│  GND  ────────────────────────── GND   │
│  VBUS (5V) or 3V3 for power            │
└─────────────────────────────────────────┘
```

### Button Wiring Detail

```
Each button is wired identically:

  Pico GP Pin ──┬── [Button] ──── GND
                │
            (internal
           PULL_UP keeps
           pin HIGH when
           not pressed)

When button pressed → pin pulled LOW → detected as press
```

### LED Wiring Detail

```
  GP9 ──── [220Ω resistor] ──── [LED Anode +] ──── [LED Cathode -] ──── GND
                                     (longer leg)       (shorter leg)
```

### Pin Reference Table

| GPIO Pin | Button/Component | Direction |
|----------|-----------------|-----------|
| GP2 | W (forward) | Input, PULL_UP |
| GP3 | SPACE (handbrake) | Input, PULL_UP |
| GP4 | D (right) | Input, PULL_UP |
| GP5 | A (left) | Input, PULL_UP |
| GP6 | S (backward) | Input, PULL_UP |
| GP9 | Status LED (PWM) | Output |
| GND | Common ground | — |

---

## ⚙️ Setup

### Step 1 — Flash MicroPython on Pico W

1. Hold **BOOTSEL** button on Pico W while plugging USB into PC
2. It mounts as a drive called `RPI-RP2`
3. Download the latest [MicroPython UF2 for Pico W](https://micropython.org/download/RPI_PICO_W/)
4. Drag and drop the `.uf2` file onto the drive
5. Pico reboots automatically

### Step 2 — Configure `main.py`

Open `pico/main.py` and edit the config block at the top:

```python
WIFI_SSID = "YourNetworkName"
WIFI_PASS = "YourPassword"
PC_IP     = "192.168.1.X"   # ← Your PC's local IP address
PC_PORT   = 5005
```

**Finding your PC's IP:**
```bash
# Windows
ipconfig | findstr "IPv4"

# Mac / Linux
ip a | grep "inet "
```

### Step 3 — Upload to Pico W

Using [Thonny IDE](https://thonny.org/) (recommended):
1. Open Thonny → select interpreter: `MicroPython (Raspberry Pi Pico)`
2. Open `pico/main.py` → File → Save as → select `Raspberry Pi Pico` → save as `main.py`
3. Open `pico/ble_helper.py` → save to Pico as `ble_helper.py`

### Step 4 — Install PC dependencies

```bash
pip install pynput bleak
```

### Step 5 — Run

```bash
# On your PC — run this FIRST
python receiver.py

# Then power on / reset the Pico W
# Watch the terminal for connection status
```

---

## 💡 LED Status Guide

| LED Behaviour | Meaning |
|--------------|---------|
| Fast blinking | Attempting Wi-Fi connection |
| Single bright flash (1 sec) | ✅ Wi-Fi connected |
| 3× slow pulses | ❌ Wi-Fi failed, switching to Bluetooth |
| Slow blinking | Waiting for BLE device to pair |
| Single flash | ✅ Bluetooth connected |
| **Off** | Idle — no buttons pressed |
| Dim glow | 1 button held |
| Bright glow | 2+ buttons held simultaneously |

---

## 📡 How It Works

```
┌─────────────────┐         UDP Packet          ┌──────────────────┐
│                 │  "W:1,S:0,A:0,D:0,SPACE:0"  │                  │
│   Pico W        │ ─────────────────────────►  │   receiver.py    │
│   (main.py)     │       Wi-Fi (primary)        │   (PC)           │
│                 │                              │                  │
│   Reads 5       │  ◄── Falls back if fails ──  │  Presses/holds/  │
│   buttons at    │                              │  releases real   │
│   125Hz         │  BLE UART (fallback)         │  keyboard keys   │
│                 │ ─────────────────────────►  │  via pynput      │
└─────────────────┘                              └──────────────────┘
```

### Transport Priority

```
Power on Pico W
      │
      ▼
Try Wi-Fi for 10 seconds
      │
   ┌──┴──────────────────┐
   │ Connected?           │
   YES                    NO
   │                      │
   ▼                      ▼
Use UDP           Shut down Wi-Fi chip
(fast, low        Start BLE advertising
latency)          Wait for PC to pair
                  Use BLE UART
```

### Message Format

Every state change sends a compact CSV packet:

```
W:1,S:0,A:0,D:1,SPACE:0
```

- `1` = button currently pressed (held)
- `0` = button released
- Only sent **on change** — no unnecessary traffic

---

## 🖥️ PC Receiver — receiver.py

The receiver runs two listeners in parallel:

```
receiver.py
├── Thread 1: UDP socket on port 5005  (Wi-Fi packets)
└── Thread 2: BLE async scanner         (Bluetooth packets)
          Both call → process_message() → pynput key press/release
```

Key behaviour:
- **Hold**: `keyboard.press(key)` is called once and held until release packet arrives
- **Combo**: W+A pressed simultaneously = both keys held at the same time
- **Clean exit**: `Ctrl+C` releases all currently held keys before quitting (no stuck keys)

---

## 🎮 Use Cases

| Game Type | Buttons Used |
|-----------|-------------|
| Driving games (GTA, BeamNG) | W/A/S/D + SPACE handbrake |
| Minecraft movement | W/A/S/D |
| Presentation clicker | Remap to arrow keys |
| Custom macros | Change `KEY_MAP` in receiver.py |

---

## 🔑 Remapping Keys

To use different keys, edit `KEY_MAP` in `receiver.py`:

```python
from pynput.keyboard import Key, Controller

KEY_MAP = {
    "W":     Key.up,        # Arrow keys instead
    "S":     Key.down,
    "A":     Key.left,
    "D":     Key.right,
    "SPACE": Key.shift,     # Shift instead of space
}
```

Any key from the [pynput Key reference](https://pynput.readthedocs.io/en/latest/keyboard.html) works.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---------|-----|
| Pico connects but PC gets nothing | Check `PC_IP` — run `ipconfig` and verify. Common mistake: Pico's own IP was used |
| Wi-Fi connects but packets blocked | Workplace/school networks isolate clients. Use phone hotspot or rely on BLE fallback |
| BLE device not found | Make sure `receiver.py` is running before Pico boots. Name must match: `"Pico PC Controller"` |
| Keys stuck after closing receiver | Press `Ctrl+C` gracefully — the script releases all held keys on exit |
| Buttons bouncing (double presses) | Add `time.sleep_ms(20)` after state change detection, or add a small capacitor across button |
| LED not lighting | Check 220Ω resistor is present. Verify GP9 connection. Try `led.duty_u16(65535)` in REPL |

**Windows Firewall** — if UDP packets are blocked, run once as Administrator:
```cmd
netsh advfirewall firewall add rule name="PicoW UDP" protocol=UDP dir=in localport=5005 action=allow
```

---

## 📦 Dependencies

### Pico W (MicroPython — built-in, no installs needed)
- `machine` — Pin, PWM control
- `network` — Wi-Fi
- `socket` — UDP
- `bluetooth` — BLE

### PC (install via pip)
```
pynput   — keyboard simulation
bleak    — Bluetooth BLE client
```

---

## 🤝 Contributing

Pull requests are welcome! Some ideas for contributions:

- [ ] Add analog-style input using multiple taps
- [ ] Web config page (served from Pico) to set Wi-Fi without reflashing
- [ ] Support for more buttons (GP10, GP11, etc.)
- [ ] Mouse movement via tilt sensor (MPU-6050)
- [ ] Android/iOS BLE receiver app

---

## 📄 License

MIT License — free to use, modify, and distribute. See [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ❤️ on a Raspberry Pi Pico W

**[⭐ Star this repo if it helped you!](https://github.com/)**

</div>
