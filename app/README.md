# ESPNow2MQTT Gateway

This app interfaces between the serial port and MQTT broker, and relays ESPNow packets to MQTT topics.

### Connections

[Other ESP Devices] <- via ESPNow -> [Gateway ESP Device] <- via Serial -> [Gateway App] <- via MQTT -> [MQTT Broker] <- via MQTT -> [ Home Assistant ]
