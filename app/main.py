import asyncio
import os
import sys
from gateway import Gateway, SerialConfig, MQTTConfig

# SERIAL CONFIG
SERIAL_PORT = "COM6"
SERIAL_BAUDRATE = 9600
SERIAL_TIMEOUT_SEC = 0.1

# MQTT CONFIG
MQTT_BROKER_HOSTNAME = "192.168.0.12"
MQTT_BROKER_PORT = 1883

MQTT_BROKER_USERNAME = "hass"
MQTT_BROKER_PASSWORD = "12345"

# if sys.platform == "win32":
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Change to the "Selector" event loop if platform is Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import WindowsSelectorEventLoopPolicy  # type: ignore
    from asyncio import set_event_loop_policy

    set_event_loop_policy(WindowsSelectorEventLoopPolicy())


async def main():
    gateway = Gateway(
        serial_cfg=SerialConfig(
            port=SERIAL_PORT, baudrate=SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT_SEC
        ),
        mqtt_cfg=MQTTConfig(
            hostname=MQTT_BROKER_HOSTNAME,
            port=MQTT_BROKER_PORT,
            username=MQTT_BROKER_USERNAME,
            password=MQTT_BROKER_PASSWORD,
        ),
    )
    await gateway.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Gateway shut down.")
