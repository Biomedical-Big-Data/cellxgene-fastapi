import aiomqtt
import asyncio
from conf.config import MQTT_BROKER_URL, MQTT_BROKER_PORT, MQTT_TOPIC


async def on_message(client, userdata, message):
    print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")


class Consumer:

    def __init__(self):
        self._consumer = None
        self.url = MQTT_BROKER_URL
        self.port = MQTT_BROKER_PORT
        self.topic = MQTT_TOPIC

    async def initialize(self):
        print(self.url)
        self._consumer = aiomqtt.Client(
            hostname=self.url,  # The only non-optional parameter
            port=self.port,
        )
        await self._consumer.connect()
        await self._consumer.subscribe(self.topic)
        self._consumer.on_message = on_message

    async def shutdown(self):
        await self._consumer.disconnect()


async def main():
    consumer = Consumer()
    await consumer.initialize()


if __name__ == "__main__":
    renwu = [main()]
    loops = asyncio.get_event_loop()
    loops.run_until_complete(asyncio.wait(renwu))
