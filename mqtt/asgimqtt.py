"""
# TODO:
 - Not sure why mqtt client automatically disconnect after receiving message
 - entry enter & exit event

"""
import argparse
import os
import sys
import importlib
import json
import paho.mqtt.client as paho
import psycopg2
from asgiref.sync import async_to_sync
from geopy import distance


db_url = ''
black_dots = []
loading_stations = []
unloading_stations = []
quality_stations = []


def get_db_url():
    pwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_file_name = os.path.join(pwd, '.env')
    if not os.path.exists(env_file_name):
        raise Exception('Not Found .env file')

    with open(env_file_name, 'r') as fd:
        line = fd.readline()
        while line:
            key_value = line.split('=')
            if key_value[0] == 'DATABASE_URL':
                global db_url
                db_url = key_value[1]
                break

            line = fd.readline()


def load_data_from_db(db_url):
    try:
        connection = psycopg2.connect(
            'postgres://dev:gibupjo127@localhost:5432/tms'
        )
        cursor = connection.cursor()

        dot_query = """
            SELECT id, longitude, latitude, notification_message
            FROM road_point
            WHERE category='{}'
        """

        # select balck dots
        global black_dots
        cursor.execute(dot_query.format('B'))
        results = cursor.fetchall()
        for row in results:
            black_dots.append(row)

        # select loading station dots
        global loading_stations
        cursor.execute(dot_query.format('L'))
        results = cursor.fetchall()
        for row in results:
            loading_stations.append(row)

        # select unloading station dots
        global unloading_stations
        cursor.execute(dot_query.format('U'))
        results = cursor.fetchall()
        for row in results:
            unloading_stations.append(row)

        # select quality station dots
        global quality_stations
        cursor.execute(dot_query.format('Q'))
        results = cursor.fetchall()
        for row in results:
            quality_stations.append(row)

        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
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
    client.subscribe(userdata['topic'], userdata['qos'])


def _on_message(client, userdata, message):
    response = json.loads(message.payload.decode('utf-8'))
    data = response.get('data', None)

    print(data)
    # send current vehicle position to position consumer
    # in order to display on frontend
    async_to_sync(channel_layer.group_send)(
        'position',
        {
            'type': 'notify_position',
            'data': data
        }
    )

    # area enter & exit event
    # plate_num = data[0]['plateNum']

    # global black_dots
    current_position = (data[0]['lat'], data[1]['lng'])
    for dot in black_dots:
        dot_position = (dot[2], dot[1])
        if distance.distance(current_position, dot_position).m < 100:
            pass


def _on_disconnect(client, userdata, rc):
    pass


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

    # load black dots from db into local variables
    load_data_from_db(db_url)

    asgi_client = ASGIMQTTClient(
        args.host, args.port, args.id, args.username,
        args.password, args.topic, args.qos, channel_layer
    )
    asgi_client.run()
