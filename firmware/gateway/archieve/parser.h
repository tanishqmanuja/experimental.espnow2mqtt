#ifndef ESPNOW_SERIAL_PARSER_H
#define ESPNOW_SERIAL_PARSER_H

#include <Arduino.h>

#define MAX_PAYLOAD_SIZE 250
#define SYNC_BYTE 0xAA

class SerialParser {
public:
  const uint8_t* getMAC() const { return mac; }
  const uint8_t* getPayload() const { return payload; }
  uint8_t getPayloadLength() const { return payload_length; }

  bool parse();
  
  
  private:
  enum State { WAIT_SYNC, READ_LEN, READ_DATA, READ_CHK } state = WAIT_SYNC;
  uint8_t len = 0, chk = 0, pos = 0;
  uint8_t buf[MAX_PAYLOAD_SIZE];
  
  uint8_t packet[MAX_PAYLOAD_SIZE];  // full parsed packet
  uint8_t packet_length = 0;          // total length (MAC + payload)

  uint8_t mac[6];                    // extracted MAC
  uint8_t* payload = nullptr;        // pointer to payload inside `packet`
  uint8_t payload_length = 0;         // length of payload (packet_length - 6)
};

extern SerialParser parser;


#endif
