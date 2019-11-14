"""
# TODO:
 - Not sure why mqtt client automatically disconnect after receiving message
 - entry enter & exit event

"""
import argparse
import sys
import importlib
import json
import paho.mqtt.client as paho
import psycopg2
from datetime import datetime


class Config:
    DB_URL = ''
    HOST = ''
    PORT = ''
    TOPIC = ''
    CLIENT_ID = ''
    USERNAME = ''
    PASSWORD = ''
    QOS = ''
    DEBUG = False

    @classmethod
    def read_env(cls, filename):
        with open(filename, 'r') as fd:
            line = fd.readline()
            while line:
                key_value = line.split('=')
                if key_value[0] == 'DATABASE_URL':
                    cls.DB_URL = key_value[1][:-1]
                elif key_value[0] == 'G7_MQTT_HOST':
                    cls.HOST = key_value[1][:-1]
                elif key_value[0] == 'G7_MQTT_PORT':
                    cls.PORT = int(key_value[1][:-1])
                elif key_value[0] == 'G7_MQTT_STOP_TOPIC':
                    cls.TOPIC = key_value[1][:-1]
                elif key_value[0] == 'G7_MQTT_STOP_CLIENT_ID':
                    cls.CLIENT_ID = key_value[1][:-1]
                elif key_value[0] == 'G7_MQTT_STOP_ACCESS_ID':
                    cls.USERNAME = key_value[1][:-1]
                elif key_value[0] == 'G7_MQTT_STOP_SECRET':
                    cls.PASSWORD = key_value[1][:-1]
                elif key_value[0] == 'G7_MQTT_QOS':
                    cls.QOS = int(key_value[1][:-1])

                line = fd.readline()

        if Config.DEBUG:
            print('DATABASE_URL', Config.DB_URL)
            print('G7_MQTT_HOST', Config.HOST)
            print('G7_MQTT_PORT', Config.PORT)
            print('G7_MQTT_STOP_TOPIC', Config.TOPIC)
            print('G7_MQTT_STOP_CLIENT_ID', Config.CLIENT_ID)
            print('G7_MQTT_STOP_ACCESS_ID', Config.USERNAME)
            print('G7_MQTT_STOP_SECRET', Config.PASSWORD)
            print('G7_MQTT_QOS', Config.QOS)


def get_channel_layer(channel_name):
    sys.path.insert(0, ".")
    module_path, object_path = channel_name.split(":", 1)
    channel_layer = importlib.import_module(module_path)
    for bit in object_path.split("."):
        channel_layer = getattr(channel_layer, bit)

    return channel_layer


def _on_connect(client, userdata, flags, rc):
    if Config.DEBUG:
        print('[G7]: Connected to MQTT Server')
    client.subscribe(userdata['topic'], userdata['qos'])


def _on_message(client, userdata, message):

    response = json.loads(message.payload.decode('utf-8'))
    if Config.DEBUG:
        print('[G7]: Received message', response)

    try:
        data = response.get('data')
        connection = psycopg2.connect(Config.DB_URL)
        cursor = connection.cursor()
        push_time = datetime.fromtimestamp(int(response['pushTime'])/1000).strftime('%Y-%m-%d %H:%M:%S')
        if data['startTime']:
            start_time = datetime.fromtimestamp(int(data['startTime'])/1000).strftime('%Y-%m-%d %H:%M:%S')
        else:
            start_time = None

        if data['endTime']:
            end_time = datetime.fromtimestamp(int(data['endTime'])/1000).strftime('%Y-%m-%d %H:%M:%S')
        else:
            end_time = None

        plate_num = data['plateNum']
        search_query = f"""
        SELECT vv.id, vvwb.worker_id
        FROM vehicle_vehicle vv
        LEFT JOIN (
            SELECT vehicle_id, worker_id FROM vehicle_vehicleworkerbind WHERE get_off IS NULL
            ORDER BY worker_type
        ) vvwb ON vv.id=vvwb.vehicle_id
        WHERE vv.plate_num='{plate_num}'
        """
        cursor.execute(search_query)

        if Config.DEBUG:
            print(f'[DB query]: {search_query}')

        row = cursor.fetchone()
        driver = None
        escort = None
        if row is not None:
            vehicle = row[0]
            driver = row[1]
            row = cursor.fetchone()
            if row is not None:
                escort = row[1]
        else:
            vehicle = None

        if vehicle is not None:
            insert_query = f"""INSERT INTO notification_g7mqttevent
            (event_type, push_time, vehicle_id, driver_id, escort_id, start_time, end_time, seconds,
            start_lng, start_lat, end_lng, end_lat, created, updated) VALUES
            (0, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now())
            """
            if Config.DEBUG:
                print(f'[DB query]: {insert_query}')

            cursor.execute(insert_query, (
                push_time, vehicle, driver, escort, start_time, end_time, data['seconds'],
                data['startLng'], data['startLat'], data['endlng'], data['endlat']
            ))
            connection.commit()
        else:
            if Config.DEBUG:
                print(f"[Error]: {plate_num} is not registered")

    except Exception as e:
        if Config.DEBUG:
            print(f'[DB]: {e}')
    finally:
        if connection is not None:
            connection.close()
            if Config.DEBUG:
                print('[DB]: Database connection closed.')


def _on_disconnect(client, userdata, rc):
    if Config.DEBUG:
        print('[G7]: Disconnected')


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
        '-s', '--settings', help='Location to django env file, .env'
    )
    ap.add_argument(
        '-d', '--debug', help='Set debug mode', action='store_true'
    )
    ap.add_argument(
        'channel_layer', help='ASGI channel layer instance'
    )
    args = ap.parse_args()

    channel_layer = get_channel_layer(args.channel_layer)

    Config.DEBUG = args.debug
    Config.read_env(args.settings)

    asgi_client = ASGIMQTTClient(
        Config.HOST, Config.PORT, Config.CLIENT_ID, Config.USERNAME,
        Config.PASSWORD, Config.TOPIC, Config.QOS, channel_layer
    )
    asgi_client.run()
