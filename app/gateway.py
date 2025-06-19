import asyncio
from dataclasses import dataclass

from aiomqtt import Client
from aioserial import AioSerial, SerialException

from mqtt_handlers.wizmote import handle_wizmote_message
from utils.device import parse_packet

ESPNOW_MQTT_TOPIC = "espnow/#"


@dataclass
class SerialConfig:
    port: str
    baudrate: int
    timeout: float = 0.1


@dataclass
class MQTTConfig:
    hostname: str
    port: int
    username: str | None = None
    password: str | None = None


class Gateway:
    def __init__(self, serial_cfg: SerialConfig, mqtt_cfg: MQTTConfig) -> None:
        self.serial_cfg = serial_cfg
        self.mqtt_cfg = mqtt_cfg

        self.serial: AioSerial | None = None
        self.mqtt: Client | None = None

        self.mqtt_handlers = {"espnow/wizmote/send": handle_wizmote_message}

    async def open_serial(self):
        while True:
            try:
                print(
                    f"[🔌] Trying to connect to serial port {self.serial_cfg.port}..."
                )
                self.serial = AioSerial(
                    port=self.serial_cfg.port,
                    baudrate=self.serial_cfg.baudrate,
                    timeout=self.serial_cfg.timeout,
                )
                print("[✅] Serial connected.")
                return
            except SerialException as e:
                print(f"[⚠️] Serial error: {e}. Retrying in 5 seconds...")
                await asyncio.sleep(5)

    async def handle_serial(self):
        buffer = bytearray()

        while True:
            if not self.serial:
                await self.open_serial()
            else:
                try:
                    # Read 1 byte at a time
                    byte = await self.serial.read_async(1)
                    if not byte:
                        await asyncio.sleep(0.01)
                        continue

                    buffer.extend(byte)

                    while True:
                        packet, buffer = parse_packet(buffer)
                        if not packet:
                            break
                        print("[SERIAL]", packet)
                        # Optionally publish to MQTT here
                        # await self.publish_mqtt(packet)

                except Exception as e:
                    print(f"[❌] Serial read error: {e}")
                    self.serial = None
                    await asyncio.sleep(1)

    async def handle_mqtt(self):
        async with Client(
            self.mqtt_cfg.hostname,
            port=self.mqtt_cfg.port,
            username=self.mqtt_cfg.username,
            password=self.mqtt_cfg.password,
        ) as client:
            self.mqtt = client
            await client.subscribe(ESPNOW_MQTT_TOPIC)
            async for message in client.messages:
                payload = message.payload
                if isinstance(payload, bytes):
                    payload_str = payload.decode("utf-8", errors="ignore")
                else:
                    payload_str = str(payload)
                print("[MQTT]", message.topic.value, payload_str)
                handler = self.mqtt_handlers.get(message.topic.value)
                if handler:
                    try:
                        handler(serial=self.serial, mqtt=self.mqtt, message=message)
                    except Exception as e:
                        print(f"[MQTT] Handler Failed: {e}")
                else:
                    print(
                        f"[MQTT] Unhandled topic {message.topic.value}: {message.payload}"
                    )

    async def run(self):
        await asyncio.gather(self.handle_serial(), self.handle_mqtt())
