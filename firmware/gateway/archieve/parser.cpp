#include "parser.h"

SerialParser parser;

bool SerialParser::parse() {
  while (Serial.available()) {
    uint8_t byte = Serial.read();

    switch (state) {
      case WAIT_SYNC:
        if (byte == SYNC_BYTE) state = READ_LEN;
        break;

      case READ_LEN:
        len = byte;
        if (len < 7 || len > MAX_PAYLOAD_SIZE) { // Must have 6-byte MAC + at least 1 payload byte
          state = WAIT_SYNC;
          break;
        }
        pos = 0;
        chk = len;
        state = READ_DATA;
        break;

      case READ_DATA:
        buf[pos++] = byte;
        chk ^= byte;
        if (pos == len) state = READ_CHK;
        break;

      case READ_CHK:
        if (byte == chk) {
          memcpy(packet, buf, len);
          packet_length = len;

          memcpy(mac, packet, 6);
          payload = packet + 6;
          payload_length = len - 6;

          state = WAIT_SYNC;
          return true;
        } else {
          state = WAIT_SYNC;
        }
        break;
    }
  }

  return false;
}
