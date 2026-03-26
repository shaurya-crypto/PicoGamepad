import bluetooth
import struct
from micropython import const

_ADV_TYPE_FLAGS = const(0x01)
_ADV_TYPE_NAME = const(0x09)

_UART_UUID = bluetooth.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
_UART_TX = (bluetooth.UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E'), bluetooth.FLAG_NOTIFY)
_UART_RX = (bluetooth.UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E'), bluetooth.FLAG_WRITE | bluetooth.FLAG_WRITE_NO_RESPONSE)
_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX))

class BLEUART:
    def __init__(self, ble, name="Pico"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._connections = set()
        self._payload = self._build_payload(name)
        self._advertise()

    def _build_payload(self, name):
        payload = bytearray()
        payload += struct.pack("BB", 2, _ADV_TYPE_FLAGS) + struct.pack("B", 0x06)
        name_bytes = name.encode("utf-8")
        payload += struct.pack("BB", len(name_bytes) + 1, _ADV_TYPE_NAME) + name_bytes
        return payload

    def _irq(self, event, data):
        if event == 1: 
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
            print("\n✅ Bluetooth Connected!")
        elif event == 2: 
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            print("\n❌ Bluetooth Disconnected. Advertising again...")
            self._advertise()

    def _advertise(self):
        self._ble.gap_advertise(100000, adv_data=self._payload) 

    def send(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle_tx, data)
