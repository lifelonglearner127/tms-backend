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


class Config:
    blackdots = []
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
    ENTER_STATION_EVENT = 1
    EXIT_STATION_EVENT = 2
    ENTER_BLACK_DOT_EVENT = 3
    EXIT_BLACK_DOT_EVENT = 4

    CHANNEL_NAME_QUERY = """
        SELECT channel_name
        FROM account_user au
        LEFT JOIN order_vehicleuserbind ovub ON ovub.driver_id=au.id
        LEFT JOIN vehicle_vehicle vv ON vv.id=ovub.vehicle_id
        where vv.plate_num='{}'
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
    def load_data_from_db(cls):
        is_blackdots_updated = r.get('blackdot') == b'updated'
        is_vehicles_updated = r.get('vehicle') == b'updated'
        updated_jobs = r.smember('jobs')
        if not is_blackdots_updated and not is_vehicles_updated and\
           updated_jobs is None:
            return

        try:
            connection = psycopg2.connect(cls.DB_URL)
            cursor = connection.cursor()
            if is_blackdots_updated:
                if Config.DEBUG:
                    print('[Load Data]: Loading blackdots...')
                cursor.execute("""
                    SELECT id, latitude, longitude, radius
                    FROM info_station
                    WHERE station_type='B'
                """)
                results = cursor.fetchall()
                for row in results:
                    cls.stations.append({
                        'station_id': row[0],
                        'latitude': row[1],
                        'longitude': row[2],
                        'radius': row[3]
                    })

                if Config.DEBUG:
                    print('[Load Data]: ', cls.stations)

                r.set('blackdot', 'read')

            if is_vehicles_updated or updated_jobs:
                if Config.DEBUG:
                    print('[Load Data]: Loading updated vehicles...')

                current_updated_jobs = []
                for updated_job in updated_jobs:
                    current_updated_jobs.append(
                        int(updated_job.decode('utf-8'))
                    )

                cursor.execute("""
                    SELECT vv.plate_num, tmp2.*
                    FROM vehicle_vehicle vv
                    LEFT JOIN (
                        SELECT oj.vehicle_id, oo.is_same_station, oj.progress,
                            tmp.*
                        FROM (
                            SELECT id, order_id, vehicle_id, progress
                            FROM order_job
                            WHERE id IN ({})
                        ) oj
                        LEFT JOIN order_order oo ON oj.order_id=oo.id
                        LEFT JOIN (
                            SELECT ojs.job_id, ojs.station_id,
                                ist.station_type, ist.longitude, ist.latitude,
                                ist.radius
                            FROM (
                                SELECT DISTINCT ON (job_id) job_id, station_id
                                FROM order_jobstation
                                ORDER BY job_id, is_completed, step
                            ) ojs
                            LEFT JOIN info_station ist on ojs.station_id=ist.id
                        ) tmp ON oj.id=tmp.job_id
                    ) tmp2 ON vv.id=tmp2.vehicle_id;
                """.format(', '.join(current_updated_jobs)))
                results = cursor.fetchall()
                for row in results:
                    cls.vehicles[row[0]] = {
                        'position': cls.VEHICLE_OUT_AREA,
                        'is_same_station': row[2],
                        'progress': row[3],
                        'job_id': row[4],
                        'station_id': row[5],
                        'station_type': row[6],
                        'longitude': row[7],
                        'latitude': row[9]
                    }

                if Config.DEBUG:
                    print('[Load Data]: ', cls.vehicles)

                if is_vehicles_updated:
                    r.set('vehicle', 'read')

                for job in current_updated_jobs:
                    r.srem('jobs', job)

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

    Config.load_data_from_db()

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
                print('[Enter & Exit]: Websocket exists')
                async_to_sync(channel_layer.send)(
                    result[0],
                    {
                        'type': 'notify',
                        'data': json.dumps({
                            'msg_type': Config.VEHICLE_ENTER_EVENT,
                            'plate_num': '鲁UG2802',
                            'station_pos': (39.90923, 117.397428)
                        })
                    }
                )
                print('[Enter & Exit]: Sent Vehicle Enter event')
                async_to_sync(channel_layer.send)(
                    result[0],
                    {
                        'type': 'notify',
                        'data': json.dumps({
                            'msg_type': Config.VEHICLE_EXIT_EVENT,
                            'plate_num': '鲁UG2802',
                            'station_pos': (39.90923, 117.397428)
                        })
                    }
                )
                print('[Enter & Exit]: Sent Vehicle Exit event')
                # black dot
                async_to_sync(channel_layer.send)(
                    result[0],
                    {
                        'type': 'notify',
                        'data': json.dumps({
                            'msg_type': Config.VEHICLE_ENTER_EVENT,
                            'plate_num': '鲁UG2802',
                            'station_pos': (49.90923, 106.357428)
                        })
                    }
                )
                print('[Enter & Exit]: Sent Vehicle Enter event')
                async_to_sync(channel_layer.send)(
                    result[0],
                    {
                        'type': 'notify',
                        'data': json.dumps({
                            'msg_type': Config.VEHICLE_EXIT_EVENT,
                            'plate_num': '鲁UG2802',
                            'station_pos': (49.90923, 106.357428)
                        })
                    }
                )
                print('[Enter & Exit]: Sent Vehicle Exit event')

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

        # check if the vehicle enter or exit black dot
        for blackdot in Config.blackdots:
            blackdot_pos = (blackdot['latitude'], blackdot['longitude'])
            enter_exit_event = 0
            delta_distance = distance.distance(vehicle_pos, blackdot_pos).m

            if Config.DEBUG:
                print('[GeoPy]: Distance with ({}, {}) is {}'.format(
                    blackdot['latitude'], blackdot['longitude'],
                    delta_distance
                ))

            if delta_distance < blackdot['radius'] and\
               Config.vehicles[plate_num]['position'] ==\
               Config.VEHICLE_OUT_AREA:

                Config.vehicles[plate_num]['position'] = Config.VEHICLE_IN_AREA
                enter_exit_event = Config.ENTER_BLACK_DOT_EVENT
                if Config.DEBUG:
                    print('[GeoPy]: {} enter into ({}, {})'.format(
                        plate_num, blackdot['latitude'], blackdot['longitude']
                    ))

            if delta_distance > blackdot['radius'] and\
               Config.vehicles[plate_num]['position'] ==\
               Config.VEHICLE_IN_AREA:

                Config.vehicles[plate_num] = Config.VEHICLE_OUT_AREA
                enter_exit_event = Config.EXIT_BLACK_DOT_EVENT
                if Config.DEBUG:
                    print('[G7]: {} exit from ({}, {})'.format(
                        plate_num, blackdot['latitude'], blackdot['longitude']
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
                            result[0],
                            {
                                'type': 'notify',
                                'data': json.dumps({
                                    'msg_type': enter_exit_event,
                                    'station_id': blackdot['station_id']
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

        # check if the vehicle enter or exit next station
        next_station_pos = (
            Config.vehicles[plate_num]['latitude'],
            Config.vehicles[plate_num]['longitude']
        )
        next_station_radius = Config.vehicles[plate_num]['radius']
        enter_exit_event = 0
        delta_distance = distance.distance(vehicle_pos, next_station_pos).m
        if delta_distance < next_station_radius and\
           Config.vehicles[plate_num]['position'] ==\
           Config.VEHICLE_OUT_AREA:
            Config.vehicles[plate_num]['position'] = Config.VEHICLE_IN_AREA
            enter_exit_event = Config.ENTER_STATION_EVENT

        if delta_distance > next_station_radius and\
           Config.vehicles[plate_num]['position'] ==\
           Config.VEHICLE_IN_AREA:
            Config.vehicles[plate_num] = Config.VEHICLE_OUT_AREA
            enter_exit_event = Config.EXIT_STATION_EVENT

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
                        result[0],
                        {
                            'type': 'notify',
                            'data': json.dumps({
                                'msg_type': enter_exit_event,
                                'job_id': Config.vehicles[plate_num]['job_id'],
                                'station_id':
                                Config.vehicles[plate_num]['station_id']
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
