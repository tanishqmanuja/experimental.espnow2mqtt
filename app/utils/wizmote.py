import struct


BUTTON_CODES = {
    "on": 1,
    "off": 2,
    "night": 3,
    "down": 8,
    "up": 9,
    "scene1": 16,
    "scene2": 17,
    "scene3": 18,
    "scene4": 19,
    "smart_on": 100,
    "smart_off": 101,
    "smart_up": 102,
    "smart_down": 103,
}

sequence_number = 1


def get_wizmote_payload(button_code: int) -> bytes:
    global sequence_number
    sequence_number += 1

    program = 0x91 if button_code in (1, 100) else 0x81

    payload = struct.pack(
        "<13B",
        program,
        sequence_number & 0xFF,
        (sequence_number >> 8) & 0xFF,
        (sequence_number >> 16) & 0xFF,
        (sequence_number >> 24) & 0xFF,
        0x32,  # dt1
        button_code,  # button
        0x01,  # dt2
        90,  # batLevel
        0x00,
        0x00,
        0x00,
        0x00,  # unknown bytes
    )

    return payload
