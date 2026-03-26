import socket
import threading
import asyncio
from bleak import BleakClient, BleakScanner
from pynput.keyboard import Key, Controller

keyboard = Controller()

KEY_MAP = {
    "W": "w",
    "S": "s",
    "A": "a",
    "D": "d",
    "SPACE": Key.space,
}

held = set()

def process_message(msg):
    global held
    for part in msg.split(","):
        if ":" in part:
            name, state = part.split(":")
            key = KEY_MAP.get(name)
            if not key: continue

            if state == "1" and name not in held:
                keyboard.press(key)
                held.add(name)
                print(f"▼ HOLD  {name}")
            elif state == "0" and name in held:
                keyboard.release(key)
                held.discard(name)
                print(f"▲ RELEASE {name}")

# --- Wi-Fi Receiver (UDP) ---
def udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 5005))
    print("🌐 Wi-Fi (UDP) Listener active on port 5005")
    while True:
        try:
            data, _ = sock.recvfrom(1024)
            process_message(data.decode().strip())
        except Exception as e:
            print("UDP Error:", e)

# --- Bluetooth Receiver (BLE) ---
UART_TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

def handle_ble_data(sender, data):
    process_message(data.decode("utf-8").strip())

async def ble_listener():
    print("📡 Bluetooth Listener scanning for 'Pico PC Controller'...")
    while True:
        device = await BleakScanner.find_device_by_name("Pico PC Controller", timeout=5.0)
        if device:
            print(f"✅ Found Pico Bluetooth! Connecting to {device.address}...")
            try:
                async with BleakClient(device) as client:
                    print("🚀 Bluetooth Connected!")
                    await client.start_notify(UART_TX_UUID, handle_ble_data)
                    while client.is_connected:
                        await asyncio.sleep(1)
            except Exception as e:
                print(f"Bluetooth connection lost. Retrying in 3s...")
        await asyncio.sleep(3)

if __name__ == "__main__":
    # Start the Wi-Fi listener in the background
    threading.Thread(target=udp_listener, daemon=True).start()
    
    # Start the Bluetooth listener in the main thread
    try:
        asyncio.run(ble_listener())
    except KeyboardInterrupt:
        for name in list(held):
            keyboard.release(KEY_MAP[name])
        print("\nStopped. All keys released.")