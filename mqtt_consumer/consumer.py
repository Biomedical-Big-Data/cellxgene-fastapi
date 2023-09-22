import json
import uuid

from gmqtt import Client as MQTTClient
from conf.config import MQTT_BROKER_URL, MQTT_BROKER_PORT, MQTT_TOPIC
import asyncio


SERVER_STATUS_DICT = {}


class Consumer:
    def __init__(self):
        self.client = None
        self._consumer = None
        self.url = MQTT_BROKER_URL
        self.port = MQTT_BROKER_PORT
        self.topic = MQTT_TOPIC
        self.stop = asyncio.Event()

    async def initialize(self):
        self.client = MQTTClient(uuid.uuid4().hex)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe
        await self.client.connect(self.url, self.port)

    def on_connect(self, client, flags, rc, properties):
        print("Connected")
        client.subscribe(self.topic, qos=0)

    def on_message(self, client, topic, payload, qos, properties):
        # print('RECV MSG:', payload)
        payload_dict = json.loads(payload)
        SERVER_STATUS_DICT[payload_dict["ip"]] = payload_dict
        print(SERVER_STATUS_DICT)

    def on_disconnect(self, client, packet, exc=None):
        print("Disconnected")

    def on_subscribe(self, client, mid, qos, properties):
        print("SUBSCRIBED")

    async def shutdown(self):
        await self.client.disconnect()


# async def main():
#     consumer = Consumer()
#     consumer.initialize()


if __name__ == "__main__":
    consumer = Consumer()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consumer.initialize())
