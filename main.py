from machine import Pin, PWM
import network
import socket
import time
import bluetooth
from ble_helper import BLEUART 

# ─── CONFIG 
WIFI_SSID = "WorkPlace"
WIFI_PASS = "Whitefield1947"
PC_IP     = "172.16.2.10"
PC_PORT   = 5005

# ─── LED & BUTTONS
led = PWM(Pin(9))
led.freq(1000)
led.duty_u16(0)

IDLE_GLOW   = 0    
DIM_GLOW    = 8000    
BRIGHT_GLOW = 30000   

BUTTONS = [
    {"pin": Pin(2, Pin.IN, Pin.PULL_UP), "name": "W"},
    {"pin": Pin(6, Pin.IN, Pin.PULL_UP), "name": "S"},
    {"pin": Pin(5, Pin.IN, Pin.PULL_UP), "name": "A"},
    {"pin": Pin(4, Pin.IN, Pin.PULL_UP), "name": "D"},
    {"pin": Pin(3, Pin.IN, Pin.PULL_UP), "name": "SPACE"},
]

# ─── AUTO-SWITCH LOGIC ────────────────────────────────────────
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)

print("Attempting Wi-Fi connection...", end="")
timeout = 0
blink = False

while not wlan.isconnected() and timeout < 35:
    blink = not blink
    led.duty_u16(15000 if blink else 0)
    print(".", end="")
    time.sleep(0.3)
    timeout += 1

MODE = ""
sock = None
ble_uart = None 

if wlan.isconnected():
    print("\n✅ Connected to Wi-Fi! Entering PC MODE.")
    MODE = "WIFI"
    led.duty_u16(50000) 
    time.sleep(1)
    led.duty_u16(IDLE_GLOW)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

else:
    print("\n❌ Wi-Fi Failed. Entering BLUETOOTH MODE.")
    MODE = "BLUETOOTH"
    wlan.disconnect()
    wlan.active(False) 
    
    # Fail Blink
    for _ in range(3):
        led.duty_u16(30000)
        time.sleep(0.5)
        led.duty_u16(0)
        time.sleep(0.5)
        
    ble = bluetooth.BLE()
    ble_uart = BLEUART(ble, name="Pico PC Controller")
    print("Bluetooth broadcasting! Run the PC Receiver script.")

# ─── MAIN LOOP ────────────────────────────────────────────────
prev_states = [False] * len(BUTTONS)

while True:
    current_states = [btn["pin"].value() == 0 for btn in BUTTONS]
    press_count = sum(current_states)

    if current_states != prev_states:
        msg = ",".join(
            f"{BUTTONS[i]['name']}:{'1' if current_states[i] else '0'}"
            for i in range(len(BUTTONS))
        )
        
        if MODE == "WIFI":
            try:
                sock.sendto(msg.encode(), (PC_IP, PC_PORT))
            except Exception:
                pass
                
        elif MODE == "BLUETOOTH":
            try:
                ble_uart.send(msg.encode())
            except Exception:
                pass

        prev_states = current_states[:]

    # ─── LED Logic
    if press_count == 0:
        led.duty_u16(IDLE_GLOW)        
    elif press_count == 1:
        led.duty_u16(DIM_GLOW)         
    else:
        led.duty_u16(BRIGHT_GLOW)      

    time.sleep_ms(10)
