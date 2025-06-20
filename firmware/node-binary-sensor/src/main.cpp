#include <Arduino.h>
#include <ESP8266WiFi.h>

#include <QuickESPNow.h>
#include <EasyButton.h>
#include <ArduinoJson.h>

#include "LedBlinker.h"

#define ESPNOW_WIFI_CHANNEL 6
#define SERIAL_BAUD_RATE 9600
#define MAX_PAYLOAD_SIZE 250

#define BUTTON_PIN 0

u8 GATEWAY_ADDRESS[6] = {0x8c, 0xaa, 0xb5, 0x52, 0xcf, 0x7a};

EasyButton button(BUTTON_PIN);
LedBlinker blinker(LED_BUILTIN);

#define NODE_ID "test-node"
#define BINARY_SENSOR_ID "flash-button"

bool onSent = false;

void onDataRcvd(uint8_t *macaddr, uint8_t *data, uint8_t len, signed int rssi, bool broadcast) {
  blinker.blink(5);
}

void onDataSend(uint8_t *macaddr, uint8_t status) {
  if (status == 0) {
    blinker.blink(); 
  }
}

bool sendJson(uint8_t* mac, const JsonDocument& doc) {
  String buffer;
  size_t len = serializeJson(doc, buffer);
  return esp_now_send(mac, (uint8_t *) buffer.c_str(), len) == 0;
}

bool sendDiscovery() {
  JsonDocument doc;
  doc["type"] = "discovery";
  doc["node_id"] = NODE_ID;
  doc["platform"] = "binary_sensor";
  doc["id"] = BINARY_SENSOR_ID;
  return sendJson(GATEWAY_ADDRESS, doc);
}

bool sendState(bool state) {
  JsonDocument doc;
  doc["node_id"] = NODE_ID;
  doc["platform"] = "binary_sensor";
  doc["id"] = BINARY_SENSOR_ID;
  doc["state"] = state ? "ON" : "OFF";
  onSent = sendJson(GATEWAY_ADDRESS, doc);
  return onSent;
}


void setup() {
  blinker.setup(); 
  button.begin();

  WiFi.mode(WIFI_STA);
  WiFi.disconnect(false);

  if (!quickEspNow.begin(ESPNOW_WIFI_CHANNEL)) {
    delay(1000);
    ESP.restart();
  }

  quickEspNow.onDataSent(onDataSend);
  quickEspNow.onDataRcvd(onDataRcvd);

  while(!sendDiscovery()){
    delay(1000);
  }
}

void loop() {
  button.read();
  blinker.update();

  if(!onSent && button.pressedFor(5)){
    onSent = sendState(true);
  }

  if(onSent && button.releasedFor(10)){
    onSent = !sendState(false);
  }
}
