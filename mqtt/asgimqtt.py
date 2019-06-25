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
    vehicles = {}
    DB_URL = ''
    HOST = ''
    PORT = ''
    TOPIC = ''
    CLIENT_ID = ''
    USERNAME = ''
    PASSWORD = ''
    QOS = ''
    DEBUG = False
    VEHICLE_OUT_AREA = 0
    VEHICLE_IN_AREA = 1
    VEHICLE_ENTER_EVENT = 1
    VEHICLE_EXIT_EVENT = 2

    CHANNEL_NAME_QUERY = """
        SELECT id, channel_name
        FROM account_user
        RIGHT JOIN(
            SELECT bind.driver_id as driver_id
            FROM vehicle_vehicleuserbind AS bind
            LEFT JOIN vehicle_vehicle AS vehicle
            ON bind.vehicle_id = vehicle.id
            WHERE vehicle.plate_num='{}'
        ) AS vehiclebind
        ON account_user.id = vehiclebind.driver_id;
        """

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
                elif key_value[0] == 'G7_MQTT_POSITION_TOPIC':
                    cls.TOPIC = key_value[1][:-1]
                elif key_value[0] == 'G7_MQTT_POSITION_CLIENT_ID':
                    cls.CLIENT_ID = key_value[1][:-1]
                elif key_value[0] == 'G7_MQTT_POSITION_ACCESS_ID':
                    cls.USERNAME = key_value[1][:-1]
                elif key_value[0] == 'G7_MQTT_POSITION_SECRET':
                    cls.PASSWORD = key_value[1][:-1]
                elif key_value[0] == 'G7_MQTT_QOS':
                    cls.QOS = int(key_value[1][:-1])

                line = fd.readline()

    @classmethod
    def load_data_from_db(cls,
                          updated_stations=True,
                          updated_vehicles=True):
        if not updated_stations and not updated_vehicles:
            return

        try:
            connection = psycopg2.connect(cls.DB_URL)
            cursor = connection.cursor()
            if updated_stations:
                if Config.DEBUG:
                    print('[Load Data]: Loading updated station...')
                cursor.execute("""
                    SELECT latitude, longitude, radius
                    FROM info_station
                """)
                results = cursor.fetchall()
                for row in results:
                    cls.stations.append([row[0], row[1], row[2]])

                if Config.DEBUG:
                    print('[Load Data]: ', cls.stations)

                r.set('station', 'read')

            if updated_vehicles:
                if Config.DEBUG:
                    print('[Load Data]: Loading updated vehicles...')
                cursor.execute("""
                    SELECT plate_num
                    FROM vehicle_vehicle
                """)
                results = cursor.fetchall()
                for row in results:
                    cls.vehicles[row[0]] = cls.VEHICLE_OUT_AREA

                if Config.DEBUG:
                    print('[Load Data]: ', cls.vehicles)

                r.set('vehicle', 'read')

            cursor.close()
        except psycopg2.DatabaseError:
            pass
        finally:
            if connection is not None:
                connection.close()
                if Config.DEBUG:
                    print('[Load Data]: Database connection closed.')


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
    if Config.DEBUG:
        print('[G7]: Received message')

    response = json.loads(message.payload.decode('utf-8'))
    vehicles = response.get('data', None)

    if Config.DEBUG:
        print('[G7]: ', vehicles)

    if vehicles is None:
        return

    positions = []
    for vehicle in vehicles:
        if int(vehicle['speed']) == 0:
            continue

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

    Config.load_data_from_db(
        r.get('station') == b'updated',
        r.get('vehicle') == b'updated',
    )

    if Config.DEBUG:
        try:
            connection = psycopg2.connect(Config.DB_URL)
            cursor = connection.cursor()
            cursor.execute(
                Config.CHANNEL_NAME_QUERY.format('鲁UG2802')
            )
            result = cursor.fetchone()
            print('[Enter & Exit]: User ', result)

            if result is not None and result[1] is not None:
                async_to_sync(channel_layer.send)(
                    result[1],
                    {
                        'type': 'notify',
                        'data': json.dumps({
                            'msg_type': Config.VEHICLE_ENTER_EVENT,
                            'plate_num': '鲁UG2802',
                            'station_pos': (39.90923, 117.397428)
                        })
                    }
                )
                async_to_sync(channel_layer.send)(
                    result[1],
                    {
                        'type': 'notify',
                        'data': json.dumps({
                            'msg_type': Config.VEHICLE_EXIT_EVENT,
                            'plate_num': '鲁UG2802',
                            'station_pos': (39.90923, 117.397428)
                        })
                    }
                )

                # black dot
                async_to_sync(channel_layer.send)(
                    result[1],
                    {
                        'type': 'notify',
                        'data': json.dumps({
                            'msg_type': Config.VEHICLE_ENTER_EVENT,
                            'plate_num': '鲁UG2802',
                            'station_pos': (49.90923, 106.357428)
                        })
                    }
                )
                async_to_sync(channel_layer.send)(
                    result[1],
                    {
                        'type': 'notify',
                        'data': json.dumps({
                            'msg_type': Config.VEHICLE_EXIT_EVENT,
                            'plate_num': '鲁UG2802',
                            'station_pos': (49.90923, 106.357428)
                        })
                    }
                )

            cursor.close()
        except psycopg2.DatabaseError:
            pass
        finally:
            if connection is not None:
                connection.close()
                print('[Enter & Exit]: Database connection closed.')

    # area enter & exit event
    for vehicle in vehicles:
        if int(vehicle['speed']) == 0:
            continue
        plate_num = vehicle['plateNum']
        vehicle_pos = (vehicle['lat'], vehicle['lng'])
        if Config.DEBUG:
            print('[GeoPy]: Current {} Position - ({}, {})'.format(
                plate_num, vehicle['lat'], vehicle['lng']
            ))
        for station in Config.stations:
            station_pos = (station[0], station[1])
            enter_exit_event = 0
            delta_distance = distance.distance(vehicle_pos, station_pos).m

            if Config.DEBUG:
                print('[GeoPy]: Distance with ({}, {}) is {}'.format(
                    station[0], station[1], delta_distance
                ))
            if delta_distance < station[2] and\
               Config.vehicles[plate_num] == Config.VEHICLE_OUT_AREA:
                Config.vehicles[plate_num] = Config.VEHICLE_IN_AREA
                enter_exit_event = Config.VEHICLE_ENTER_EVENT
                if Config.DEBUG:
                    print('[GeoPy]: {} enter into ({}, {})'.format(
                        plate_num, station[0], station[1]
                    ))

            if delta_distance > station[2] and\
               Config.vehicles[plate_num] == Config.VEHICLE_IN_AREA:
                Config.vehicles[plate_num] = Config.VEHICLE_OUT_AREA
                enter_exit_event = Config.VEHICLE_EXIT_EVENT
                if Config.DEBUG:
                    print('[G7]: {} exit from ({}, {})'.format(
                        plate_num, station[0], station[1]
                    ))

            if enter_exit_event:
                try:
                    connection = psycopg2.connect(Config.DB_URL)
                    cursor = connection.cursor()
                    cursor.execute(
                        Config.CHANNEL_NAME_QUERY.format(plate_num)
                    )
                    result = cursor.fetchone()
                    if result is not None:
                        async_to_sync(channel_layer.send)(
                            result[1],
                            {
                                'type': 'notify',
                                'data': json.dumps({
                                    'msg_type': enter_exit_event,
                                    'plate_num': plate_num,
                                    'station_pos': station_pos
                                })
                            }
                        )
                    cursor.close()
                except psycopg2.DatabaseError:
                    pass
                finally:
                    if connection is not None:
                        connection.close()
                        if Config.DEBUG:
                            print(
                                '[Enter & Exit]: Database connection closed.'
                            )


def _on_disconnect(client, userdata, rc):
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

    Config.read_env(args.settings)
    Config.DEBUG = args.debug
    Config.load_data_from_db()

    asgi_client = ASGIMQTTClient(
        Config.HOST, Config.PORT, Config.CLIENT_ID, Config.USERNAME,
        Config.PASSWORD, Config.TOPIC, Config.QOS, channel_layer
    )
    asgi_client.run()
