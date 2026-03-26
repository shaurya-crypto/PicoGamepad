# ============================================================
#   Pico PC Controller — main.py
#   GitHub : https://github.com/YOUR_USERNAME/PicoGamepad
#   Author : SHAURYA
#   License: MIT
# ============================================================
#
#   What this does:
#     Reads 5 buttons (W, A, S, D, SPACE) and sends their
#     state to your PC wirelessly so they act as real keypresses.
#
#   Transport priority:
#     1. Tries Wi-Fi (UDP) — fast, low latency
#     2. If Wi-Fi fails → falls back to Bluetooth (BLE UART)
#
#   Wiring:
#     W     button → GP2  + GND
#     SPACE button → GP3  + GND   (handbrake)
#     D     button → GP4  + GND
#     A     button → GP5  + GND
#     S     button → GP6  + GND
#     LED          → GP9  + 220Ω resistor + GND
#
# ============================================================

from machine import Pin, PWM
import network
import socket
import time
import bluetooth
from ble_helper import BLEUART


# ============================================================
#   ★  YOUR SETTINGS — fill these in before flashing  ★
# ============================================================

# ADD IF YOU WANT TO CONNECT WITH WIFI AND IF WANT TO CONNECT WITH BLUETOOTH THEN LEAVE IT AS IT IS !
WIFI_SSID = "YOUR_WIFI_NAME"        # Your Wi-Fi network name
WIFI_PASS = "YOUR_WIFI_PASSWORD"   # Your Wi-Fi password

# Your PC's local IP address.
# On Windows run:  ipconfig | findstr "IPv4"
# On Mac/Linux:    ip a | grep "inet "
PC_IP   = "YOUR_PC_IP"
PC_PORT = 5005   # Must match the port in receiver.py (default 5005)

# How long to wait for Wi-Fi before giving up and using Bluetooth.
# 35 × 0.3s = ~10 seconds. Increase if your router is slow to respond.
WIFI_TIMEOUT_TICKS = 35



IDLE_GLOW   = 0       # No buttons held   → LED fully off
DIM_GLOW    = 8000    # One button held    → faint glow
BRIGHT_GLOW = 30000   # Two+ buttons held  → bright glow (e.g. W+A combo)


# Status LED on GP9 — using PWM so we can dim it smoothly
led = PWM(Pin(9))
led.freq(1000)
led.duty_u16(0)   # Start with LED off

# Button list — each entry has the Pin object and a name that
# gets sent over the network. Names must match KEY_MAP in receiver.py.
BUTTONS = [
    {"pin": Pin(2, Pin.IN, Pin.PULL_UP), "name": "W"},
    {"pin": Pin(6, Pin.IN, Pin.PULL_UP), "name": "S"},
    {"pin": Pin(5, Pin.IN, Pin.PULL_UP), "name": "A"},
    {"pin": Pin(4, Pin.IN, Pin.PULL_UP), "name": "D"},
    {"pin": Pin(3, Pin.IN, Pin.PULL_UP), "name": "SPACE"},   # Handbrake
]

# PULL_UP means: pin reads HIGH (1) normally, LOW (0) when button pressed.
# So   value() == 0   means the button IS being pressed.


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)

print("Attempting Wi-Fi connection...", end="")

timeout = 0
blink = False

while not wlan.isconnected() and timeout < WIFI_TIMEOUT_TICKS:
    blink = not blink
    led.duty_u16(15000 if blink else 0)   # Fast blink = "still trying"
    print(".", end="")
    time.sleep(0.3)
    timeout += 1


# ============================================================
#   Step 2 — Decide which transport to use based on result
# ============================================================

MODE     = ""     # Will be "WIFI" or "BLUETOOTH"
sock     = None   # UDP socket (Wi-Fi mode only)
ble_uart = None   # BLE UART object (Bluetooth mode only)


if wlan.isconnected():
    # ── Wi-Fi succeeded ──────────────────────────────────────
    print("\n Connected to Wi-Fi! Entering PC MODE.")
    print("   Pico IP :", wlan.ifconfig()[0])
    print("   Sending to PC at", PC_IP, "port", PC_PORT)

    MODE = "WIFI"

    # Confirmation: hold LED bright for 1 second, then turn off
    led.duty_u16(50000)
    time.sleep(1)
    led.duty_u16(IDLE_GLOW)

    # Open a UDP socket — we'll reuse this every loop iteration
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

else:
    # ── Wi-Fi failed → fall back to Bluetooth ────────────────
    print("\n❌ Wi-Fi not found or timed out. Entering BLUETOOTH MODE.")

    MODE = "BLUETOOTH"

    # Cleanly shut down the Wi-Fi chip to save power and avoid
    # interference with the Bluetooth radio
    wlan.disconnect()
    wlan.active(False)

    # Three slow pulses = "switched to BT" signal on the LED
    for _ in range(3):
        led.duty_u16(30000)
        time.sleep(0.5)
        led.duty_u16(0)
        time.sleep(0.5)

    # Start BLE UART and begin advertising so receiver.py can find us.
    # The name here must match BLE_DEVICE_NAME in receiver.py.
    ble = bluetooth.BLE()
    ble_uart = BLEUART(ble, name="Pico PC Controller")

    print("Bluetooth broadcasting as 'Pico PC Controller'.")
    print("Make sure receiver.py is running on your PC.")


# ============================================================
#   Main loop — runs forever at ~100Hz (every 10ms)
# ============================================================

prev_states = [False] * len(BUTTONS)   # Tracks last known button state

while True:

    # Read all buttons: True = pressed, False = released
    current_states = [btn["pin"].value() == 0 for btn in BUTTONS]
    press_count    = sum(current_states)

    # Only send a packet if something actually changed.
    # This keeps traffic minimal and avoids spamming the PC.
    if current_states != prev_states:

        # Build the message, e.g.  "W:1,S:0,A:0,D:1,SPACE:0"
        msg = ",".join(
            f"{BUTTONS[i]['name']}:{'1' if current_states[i] else '0'}"
            for i in range(len(BUTTONS))
        )

        if MODE == "WIFI":
            try:
                sock.sendto(msg.encode(), (PC_IP, PC_PORT))
            except Exception as e:
                print("Wi-Fi send error:", e)

        elif MODE == "BLUETOOTH":
            try:
                ble_uart.send(msg.encode())
            except Exception as e:
                print("BLE send error:", e)

        prev_states = current_states[:]   # Remember this state for next loop

    # ── LED feedback ─────────────────────────────────────────
    # Gives a visual cue about how many buttons are being held.
    if press_count == 0:
        led.duty_u16(IDLE_GLOW)     # Off — nothing pressed
    elif press_count == 1:
        led.duty_u16(DIM_GLOW)      # Faint — single key held
    else:
        led.duty_u16(BRIGHT_GLOW)   # Bright — combo held (e.g. W+A turning)

    time.sleep_ms(10)   # 10ms = 100Hz polling rate
