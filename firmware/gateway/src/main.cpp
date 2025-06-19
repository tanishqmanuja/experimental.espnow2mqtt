#include <Arduino.h>
#include <ESP8266WiFi.h>

#include <QuickESPNow.h>

#include "SerialParser.h"
#include "LedBlinker.h"

#define ESPNOW_WIFI_CHANNEL 6
#define SERIAL_BAUD_RATE 9600

LedBlinker blinker(LED_BUILTIN);

void onDataRcvd(uint8_t *macaddr, uint8_t *data, uint8_t len, signed int rssi, bool broadcast) {
  blinker.blink(5);

  if(len == 0) return;

  // FORMAT -> [SYNC][LEN][MAC (6)][RSSI (1)][DATA (len)][CHK] and then [EOL]
  uint8_t checksum = len;
  
  Serial.write(SYNC_BYTE);  // SYNC
  Serial.write(len);                      // LEN
  
  for (int i = 0; i < 6; i++) {
    Serial.write(macaddr[i]);             // MAC
    checksum ^= macaddr[i];
  }
  
  Serial.write((uint8_t)rssi);            // RSSI
  checksum ^= (uint8_t)rssi;
  
  for (int i = 0; i < len; i++) {
    Serial.write(data[i]);                // DATA
    checksum ^= data[i];
  }
  
  Serial.write(checksum);                 // CHECKSUM
  Serial.write("\n");                     // EOL
}

void onDataSend(uint8_t *macaddr, uint8_t status) {
  if (status == 0) {
    blinker.blink(); 
  }
}

void setup() {
  Serial.begin(SERIAL_BAUD_RATE);

  delay(100);
  Serial.flush();

  blinker.setup(); 

  WiFi.mode(WIFI_STA);
  WiFi.disconnect(false);

  if (!quickEspNow.begin(ESPNOW_WIFI_CHANNEL)) {
    delay(1000);
    Serial.flush();
    ESP.restart();
  }

  quickEspNow.onDataSent(onDataSend);
  quickEspNow.onDataRcvd(onDataRcvd);
}

void loop() {
  blinker.update();

  if (parser.parse()) {
    quickEspNow.send(
      parser.getMAC(),
      parser.getPayload(),
      parser.getPayloadLength()
    );
  }
}
