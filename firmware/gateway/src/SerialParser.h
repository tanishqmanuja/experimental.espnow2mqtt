#pragma once
#include <Arduino.h>

#define SYNC_BYTE 0xAA
#define MAX_PAYLOAD_SIZE 255
#define TIMEOUT_MS 100

class SerialParser {
public:
  bool parse();
  const uint8_t* getMAC() const { return mac; }
  const uint8_t* getPayload() const { return payload; }
  uint8_t getPayloadLength() const { return payload_length; }

private:
  enum State {
    WAIT_SYNC,
    READ_LEN,
    READ_DATA,
    READ_CHK
  };

  State state = WAIT_SYNC;
  uint8_t buf[MAX_PAYLOAD_SIZE];
  uint8_t packet[MAX_PAYLOAD_SIZE];
  uint8_t len = 0;
  uint8_t pos = 0;
  uint8_t chk = 0;

  unsigned long lastByteTime = 0;

  uint8_t mac[6];
  uint8_t* payload = nullptr;
  uint8_t payload_length = 0;
};

extern SerialParser parser;