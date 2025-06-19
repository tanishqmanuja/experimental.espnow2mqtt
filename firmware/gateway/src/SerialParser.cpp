#include "SerialParser.h"

bool SerialParser::parse() {
  while (Serial.available()) {
    uint8_t byte = Serial.read();

    if (state != WAIT_SYNC && millis() - lastByteTime > TIMEOUT_MS) {
      state = WAIT_SYNC;
    }

    lastByteTime = millis();

    switch (state) {
      case WAIT_SYNC:
        if (byte == SYNC_BYTE) {
          state = READ_LEN;
        }
        break;

      case READ_LEN:
        len = byte;
        if (len < 7 || len > MAX_PAYLOAD_SIZE) {
          state = WAIT_SYNC;
        } else {
          pos = 0;
          chk = len;
          state = READ_DATA;
        }
        break;

      case READ_DATA:
        buf[pos++] = byte;
        chk ^= byte;
        if (pos == len) {
          state = READ_CHK;
        }
        break;

      case READ_CHK:
        state = WAIT_SYNC;
        if (byte == chk) {
          memcpy(packet, buf, len);
          memcpy(mac, packet, 6);
          payload = packet + 6;
          payload_length = len - 6;
          return true;
        }
        break;
    }
  }
  return false;
}

SerialParser parser;