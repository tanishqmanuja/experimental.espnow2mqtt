import json
from aiomqtt import Client
from aioserial import AioSerial

from utils.device import ParsedPacket


async def handle_update_message(
    serial: AioSerial, mqtt: Client | None, packet: ParsedPacket
):
    if not mqtt:
        return

    rssi = packet.rssi
    data = json.loads(packet.data.decode("utf-8"))

    platform = data["platform"]
    node_id = data["node_id"]
    component_id = data["id"]

    if platform == "binary_sensor":
        mqtt_topic = f"espnow/{node_id}/{platform}/{component_id}/state"
        mqtt_payload = {"state": data["state"], "rssi": rssi}
        await mqtt.publish(mqtt_topic, json.dumps(mqtt_payload))
