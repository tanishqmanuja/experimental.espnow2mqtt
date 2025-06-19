from dataclasses import dataclass
import struct
from typing import Optional, Tuple

SYNC_BYTE = 0xAA
MAX_PACKET_SIZE = 255


@dataclass
class ParsedPacket:
    mac: str
    rssi: int
    data: bytes


def parse_packet(buffer: bytearray) -> Tuple[Optional[ParsedPacket], bytearray]:
    if len(buffer) < 9:
        return None, buffer  # Minimum = SYNC(1)+LEN(1)+MAC(6)+RSSI(1)+CHK(1)

    # Look for SYNC byte
    sync_index = buffer.find(SYNC_BYTE.to_bytes(1, "little"))
    if sync_index == -1:
        return None, bytearray()

    if sync_index > 0:
        buffer = buffer[sync_index:]  # Discard junk before SYNC

    if len(buffer) < 2:
        return None, buffer  # Not enough to read LEN

    length = buffer[1]
    total_len = 1 + 1 + 6 + 1 + length + 1  # SYNC + LEN + MAC + RSSI + DATA + CHK

    if len(buffer) < total_len:
        return None, buffer  # Wait for more bytes

    pkt = buffer[:total_len]
    chk = length
    for b in pkt[2:-1]:  # exclude SYNC, LEN, CHK
        chk ^= b

    if pkt[-1] != chk:
        print("[❌] Checksum mismatch")
        return None, buffer[1:]  # Skip bad SYNC and try again

    mac = pkt[2:8]
    rssi = struct.unpack("b", pkt[8:9])[0]  # signed int
    data = bytes(pkt[9:-1])  # from byte 9 to before last (CHK)

    parsed = ParsedPacket(mac=":".join(f"{b:02X}" for b in mac), rssi=rssi, data=data)

    return parsed, buffer[total_len:]


def build_packet(data: bytes, mac: str = "ff:ff:ff:ff:ff:ff") -> bytes:
    """
    Build a framed packet: [SYNC][LEN][MAC (6)][DATA][CHK]

    - SYNC: 1 byte
    - LEN: 1 byte (length of MAC + DATA)
    - MAC: 6 bytes
    - DATA: N bytes (>= 1)
    - CHK: 1 byte (XOR of LEN + all payload bytes)

    :param data: Payload data as bytes
    :param mac: MAC address as human-readable string (default: broadcast)
    :return: Complete framed packet
    """
    try:
        mac_bytes = bytes(int(part, 16) for part in mac.split(":"))
    except ValueError:
        raise ValueError("Invalid MAC format. Use format like '8C:4F:00:3A:6A:48'")

    if len(mac_bytes) != 6:
        raise ValueError("MAC must be 6 bytes after parsing")

    payload = mac_bytes + data
    length = len(payload)

    if length < 7 or length > MAX_PACKET_SIZE:
        raise ValueError(
            f"Payload length (MAC + data) must be in [7, 255], got {length}"
        )

    chk = length
    for b in payload:
        chk ^= b

    packet = bytes([SYNC_BYTE, length]) + payload + bytes([chk])
    return packet
