import json
from aiomqtt import Client, Message
from aioserial import AioSerial

from utils.device import build_packet
from utils.wizmote import BUTTON_CODES, get_wizmote_payload


def handle_wizmote_message(serial: AioSerial | None, mqtt: Client, message: Message):
    if not serial:
        return

    try:
        payload = message.payload
        if isinstance(payload, bytes):
            payload_str = payload.decode("utf-8", errors="ignore")
        else:
            payload_str = str(payload)

        mac = "FF:FF:FF:FF:FF:FF"
        payload_str = payload_str.strip()

        if payload_str.startswith("{"):
            payload = json.loads(payload_str)
            cmd = payload.get("cmd", "").strip().lower()
            mac = payload.get("mac", mac).upper()
        else:
            cmd = payload_str.lower()

        if cmd in BUTTON_CODES:
            wizmote_payload = get_wizmote_payload(BUTTON_CODES[cmd])
            serial_packet = build_packet(wizmote_payload, mac)
            serial.write(serial_packet)
            serial.flush()

            print(f"[WIZMOTE] Sent button {BUTTON_CODES[cmd]} to {mac}")
        else:
            print(f"[WIZMOTE] Unknown command: {cmd}")

    except json.JSONDecodeError as e:
        print(f"[WIZMOTE] Invalid JSON payload: {e}")
    except Exception as e:
        print(f"[WIZMOTE] Error: {e}")
