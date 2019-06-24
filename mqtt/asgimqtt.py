"""
# TODO:
 - Not sure why mqtt client automatically disconnect after receiving message
 - entry enter & exit event

"""
import argparse
import redis
import sys
import importlib
import json
import paho.mqtt.client as paho
import psycopg2
from asgiref.sync import async_to_sync
from geopy import distance


r = redis.StrictRedis(host='localhost', port=6379, db=15)
# p = r.pubsub()
# p.subscribe('station')


class Config:
    stations = []
    db_url = ''
    host = ''
    port = ''
    topic = ''
    client_id = ''
    username = ''
    password = ''
    qos = ''

    @classmethod
    def read_env(cls, filename):
        with open(filename, 'r') as fd:
            line = fd.readline()
            while line:
                key_value = line.split('=')
                if key_value[0] == 'DATABASE_URL':
                    cls.db_url = key_value[1][:-1]
                elif key_value[0] == 'G7_MQTT_HOST':
                    cls.host = key_value[1][:-1]
                elif key_value[0] == 'G7_MQTT_PORT':
                    cls.port = int(key_value[1][:-1])
                elif key_value[0] == 'G7_MQTT_POSITION_TOPIC':
                    cls.topic = key_value[1][:-1]
                elif key_value[0] == 'G7_MQTT_POSITION_CLIENT_ID':
                    cls.client_id = key_value[1][:-1]
                elif key_value[0] == 'G7_MQTT_POSITION_ACCESS_ID':
                    cls.username = key_value[1][:-1]
                elif key_value[0] == 'G7_MQTT_POSITION_SECRET':
                    cls.password = key_value[1][:-1]
                elif key_value[0] == 'G7_MQTT_QOS':
                    cls.qos = int(key_value[1][:-1])

                line = fd.readline()

    @classmethod
    def load_station_data_from_db(cls):
        try:
            connection = psycopg2.connect(cls.db_url)
            cursor = connection.cursor()

            cursor.execute("""
                SELECT longitude, latitude, radius
                FROM info_station
            """)
            results = cursor.fetchall()
            for row in results:
                cls.stations.append([row[0], row[1], row[2]])
            print(cls.stations)
            r.set('station', 'read')
            cursor.close()
        except psycopg2.DatabaseError:
            pass
        finally:
            if connection is not None:
                connection.close()
                print('Database connection closed.')


def get_channel_layer(channel_name):
    sys.path.insert(0, ".")
    module_path, object_path = channel_name.split(":", 1)
    channel_layer = importlib.import_module(module_path)
    for bit in object_path.split("."):
        channel_layer = getattr(channel_layer, bit)

    return channel_layer


def _on_connect(client, userdata, flags, rc):
    print('connected')
    client.subscribe(userdata['topic'], userdata['qos'])


def _on_message(client, userdata, message):
    print('message_received')
    response = json.loads(message.payload.decode('utf-8'))
    vehicles = response.get('data', None)

    if vehicles is None:
        return

    positions = []
    for vehicle in vehicles:
        positions.append({
            'plateNum': vehicle['plateNum'],
            'lnglat': [vehicle['lng'], vehicle['lat']],
            'speed': vehicle['speed']
        })

    # send current vehicle position to position consumer
    # in order to display on frontend
    async_to_sync(channel_layer.group_send)(
        'position',
        {
            'type': 'notify_position',
            'data': positions
        }
    )

    if r.get('station') == b'updated':
        Config.load_station_data_from_db()

    # area enter & exit event
    for vehicle in vehicles:
        vehicle_pos = (vehicle['lat'], vehicle['lng'])
        for station in Config.stations:
            station_pos = (station[0], station[1])
            if distance.distance(vehicle_pos, station_pos).m < station[2]:
                pass


def _on_disconnect(client, userdata, rc):
    print('disconnected')


class ASGIMQTTClient(object):

    def __init__(self, host, port, client_id, username,
                 password, topic, qos, channel_layer):
        self.host = host
        self.port = port
        self.client = paho.Client(
            client_id=client_id,
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
        '-s', '--settings', help='MQTT broker host', default='localhost'
    )
    ap.add_argument(
        'channel_layer', help='ASGI channel layer instance'
    )
    args = ap.parse_args()

    channel_layer = get_channel_layer(args.channel_layer)

    Config.read_env(args.settings)

    asgi_client = ASGIMQTTClient(
        Config.host, Config.port, Config.client_id, Config.username,
        Config.password, Config.topic, Config.qos, channel_layer
    )
    asgi_client.run()
