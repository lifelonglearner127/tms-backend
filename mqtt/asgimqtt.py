"""
# TODO: Not sure why mqtt client automatically disconnect
"""

import argparse
import sys
import importlib
import json
import paho.mqtt.client as paho
from asgiref.sync import async_to_sync


def get_channel_layer(channel_name):
    sys.path.insert(0, ".")
    module_path, object_path = channel_name.split(":", 1)
    channel_layer = importlib.import_module(module_path)
    for bit in object_path.split("."):
        channel_layer = getattr(channel_layer, bit)

    return channel_layer


def _on_connect(client, userdata, flags, rc):
    client.subscribe(userdata['topic'], userdata['qos'])


def _on_message(client, userdata, message):
    response = json.loads(message.payload.decode('utf-8'))
    data = response.get('data', None)
    async_to_sync(channel_layer.group_send)(
        'position',
        {
            'type': 'notify_position',
            'data': data
        }
    )


def _on_disconnect(client, userdata, rc):
    pass


class ASGIMQTTClient(object):

    def __init__(self, host, port, client_id, username,
                 password, topic, qos, channel_layer):
        self.host = host
        self.port = port
        self.client = paho.Client(
            client_id=client_id,
            clean_session=False,
            userdata={
                'channel': channel_layer,
                'topic': topic,
                'qos': qos
            }
        )
        self.client.on_connect = _on_connect
        self.client.on_message = _on_message
        self.client.on_disconnect = _on_disconnect
        self.username = username
        self.password = password

    def run(self):
        if self.username:
            self.client.username_pw_set(self.username, self.password)

        self.client.connect(self.host, self.port, keepalive=60)
        self.client.loop_forever()


if __name__ == '__main__':

    ap = argparse.ArgumentParser(description='MQTT bridge for our ASGI')
    ap.add_argument(
        '-H', '--host', help='MQTT broker host', default='localhost'
    )
    ap.add_argument(
        '-p', '--port', help='MQTT broker port', type=int, default=1883
    )
    ap.add_argument(
        '-i', '--id', help='MQTT Client Id', default=''
    )
    ap.add_argument(
        '-u', '--username', help='MQTT Username', default=''
    )
    ap.add_argument(
        '-P', '--password', help='MQTT password', default=''
    )
    ap.add_argument(
        '-t', '--topic', help='MQTT Topic', default=''
    )
    ap.add_argument(
        '-q', '--qos', help='Quality of Service', type=int, default=0
    )

    ap.add_argument(
        'channel_layer', help='ASGI channel layer instance'
    )

    args = ap.parse_args()

    channel_layer = get_channel_layer(args.channel_layer)

    asgi_client = ASGIMQTTClient(
        args.host, args.port, args.id, args.username,
        args.password, args.topic, args.qos, channel_layer
    )
    asgi_client.run()
