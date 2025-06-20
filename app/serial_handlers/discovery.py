import json
from aiomqtt import Client
from aioserial import AioSerial

from utils.device import ParsedPacket


async def handle_discovery_message(
    serial: AioSerial, mqtt: Client | None, packet: ParsedPacket
):
    if not mqtt:
        return

    mac = packet.mac.upper()
    rssi = packet.rssi
    data = json.loads(packet.data.decode("utf-8"))

    platform = data["platform"]
    node_id = data["node_id"]
    component_id = data["id"]
    schema = data.get("schema", "json")

    discovery_topic = f"homeassistant/device/{node_id}/config"
    discovery_payload = {
        "dev": {
            "ids": node_id,
            "name": node_id.replace("-", " ").title(),
            "mf": "ESP-NOW Gateway",
            "mdl": "ESP8266",
            "sw": "1.0",
            "cns": [["mac", mac]],
            "hw": "v1",
        },
        "o": {
            "name": "espnow2mqtt",
            "sw": "0.1",
            "url": "https://github.com/tanishqmanuja/espnow-mqtt-gateway",
        },
        "cmps": {
            f"{component_id}": {
                "p": platform,
                "name": f"{node_id} {component_id}",
                "value_template": "{{ value_json.state }}",
                "unique_id": f"{node_id}_{component_id}",
            },
            f"{node_id}_rssi": {
                "p": "sensor",
                "device_class": "signal_strength",
                "unit_of_measurement": "dBm",
                "value_template": "{{ value_json.rssi }}",
                "name": f"{node_id} RSSI",
                "unique_id": f"{node_id}_rssi",
                "ent_cat": "diagnostic",
            },
        },
        "stat_t": f"espnow/{node_id}/{platform}/{component_id}/state",
        "qos": 1,
    }

    await mqtt.publish(
        discovery_topic, json.dumps(discovery_payload), qos=1, retain=True
    )
    await mqtt.publish(
        f"espnow/{node_id}/{platform}/{component_id}/state",
        json.dumps({"state": "OFF", "rssi": rssi}),
    )
