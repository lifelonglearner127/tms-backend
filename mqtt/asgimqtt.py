"""
# TODO:
 - Not sure why mqtt client automatically disconnect after receiving message
 - entry enter & exit event

"""
import argparse
import redis
import sys
import importlib
import requests
import json
import paho.mqtt.client as paho
import psycopg2
from asgiref.sync import async_to_sync
from geopy import distance


r = redis.StrictRedis(host='localhost', port=6379, db=15)


class Config:
    blackdots = []
    vehicles = {}
    PUSHY_SECRET_KEY = ''
    DB_URL = ''
    HOST = ''
    PORT = ''
    TOPIC = ''
    CLIENT_ID = ''
    USERNAME = ''
    PASSWORD = ''
    QOS = ''
    DEBUG = False
    TEST_MODE = False
    VEHICLE_OUT_AREA = 0
    VEHICLE_IN_AREA = 1
    ENTER_STATION_EVENT = 3
    EXIT_STATION_EVENT = 4
    ENTER_BLACK_DOT_EVENT = 5
    EXIT_BLACK_DOT_EVENT = 6

    CHANNEL_NAME_QUERY = """
        SELECT au.id, au.channel_name, au.device_token
        FROM account_user au
        LEFT JOIN order_vehicleuserbind ovub ON ovub.driver_id=au.id
        LEFT JOIN vehicle_vehicle vv ON vv.id=ovub.vehicle_id
        where vv.plate_num='{}'
        """

    VEHICLES_JOBS_QUERY1 = """
        SELECT vv.plate_num, tmp2.*, ovub.bind_method
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
                SELECT ojs.job_id, ojs.step, ist.id, ist.longitude,
                    ist.latitude, ist.radius
                FROM (
                    SELECT DISTINCT ON (job_id) job_id, step,
                        station_id
                    FROM order_jobstation
                    ORDER BY job_id, is_completed, step
                ) ojs
                LEFT JOIN info_station ist on ojs.station_id=ist.id
            ) tmp ON oj.id=tmp.job_id
        ) tmp2 ON vv.id=tmp2.vehicle_id
        LEFT JOIN order_vehicleuserbind ovub on vv.id=ovub.vehicle_id;
    """

    VEHICLES_JOBS_QUERY2 = """
        SELECT vv.plate_num, tmp2.*, ovub.bind_method
        FROM vehicle_vehicle vv
        LEFT JOIN (
            SELECT oj.vehicle_id, oo.is_same_station, oj.progress,
                tmp.*
            FROM (
                SELECT id, order_id, vehicle_id, progress
                FROM order_job
                WHERE progress > 1
            ) oj
            LEFT JOIN order_order oo ON oj.order_id=oo.id
            LEFT JOIN (
                SELECT ojs.job_id, ojs.step, ist.id, ist.longitude,
                    ist.latitude, ist.radius
                FROM (
                    SELECT DISTINCT ON (job_id) job_id, step,
                        station_id
                    FROM order_jobstation
                    ORDER BY job_id, is_completed, step
                ) ojs
                LEFT JOIN info_station ist on ojs.station_id=ist.id
            ) tmp ON oj.id=tmp.job_id
        ) tmp2 ON vv.id=tmp2.vehicle_id
        LEFT JOIN order_vehicleuserbind ovub on vv.id=ovub.vehicle_id;
    """

    @classmethod
    def read_env(cls, filename):
        with open(filename, 'r') as fd:
            line = fd.readline()
            while line:
                key_value = line.split('=')
                if key_value[0] == 'DATABASE_URL':
                    cls.DB_URL = key_value[1][:-1]
                if key_value[0] == 'PUSHY_SECRET_KEY':
                    cls.PUSHY_SECRET_KEY = key_value[1][:-1]
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

        if Config.DEBUG:
            print('DATABASE_URL', Config.DB_URL)
            print('PUSHY_SECRET_KEY', Config.PUSHY_SECRET_KEY)
            print('G7_MQTT_HOST', Config.HOST)
            print('G7_MQTT_PORT', Config.PORT)
            print('G7_MQTT_POSITION_TOPIC', Config.TOPIC)
            print('G7_MQTT_POSITION_CLIENT_ID', Config.CLIENT_ID)
            print('G7_MQTT_POSITION_ACCESS_ID', Config.USERNAME)
            print('G7_MQTT_POSITION_SECRET', Config.PASSWORD)
            print('G7_MQTT_QOS', Config.QOS)

    @classmethod
    def load_data_from_db(cls):
        is_blackdots_updated = r.get('blackdot') == b'updated'
        is_vehicles_updated = r.get('vehicle') == b'updated'
        updated_jobs = r.smembers('jobs')
        if not is_blackdots_updated and not is_vehicles_updated and\
           not updated_jobs:
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
                    cls.blackdots.append({
                        'station_id': row[0],
                        'latitude': row[1],
                        'longitude': row[2],
                        'radius': row[3]
                    })

                if Config.DEBUG:
                    print('[Load Data]: ', cls.blackdots)

                r.set('blackdot', 'read')

            if is_vehicles_updated or updated_jobs:
                if Config.DEBUG:
                    if is_vehicles_updated:
                        print('[Load Data]: Loading updated vehicles...')
                    else:
                        print('[Load Data]: Loading updated jobs...')

                current_updated_jobs = []
                for updated_job in updated_jobs:
                    current_updated_jobs.append(
                        updated_job.decode('utf-8')
                    )
                current_updated_job_ids = ', '.join(current_updated_jobs)
                if current_updated_job_ids:
                    query_str = Config.VEHICLES_JOBS_QUERY1.format(
                        current_updated_job_ids
                    )
                else:
                    query_str = Config.VEHICLES_JOBS_QUERY2
                cursor.execute(query_str)
                results = cursor.fetchall()
                for row in results:
                    cls.vehicles[row[0]] = {
                        'blackdotposition': cls.VEHICLE_OUT_AREA,
                        'stationposition': cls.VEHICLE_OUT_AREA,
                        'is_same_station': row[2],
                        'progress': row[3],
                        'job_id': row[4],
                        'step': row[5],
                        'station_id': row[6],
                        'longitude': row[7],
                        'latitude': row[8],
                        'radius': row[9],
                        'bind_method': row[10]
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


def sendPushNotification(data, to, options):
    apiKey = Config.PUSHY_SECRET_KEY

    # Default post data to provided options or empty object
    postData = options or {}

    # Set notification payload and recipients
    postData['to'] = to
    postData['data'] = data

    try:
        requests.post(
            'https://api.pushy.me/push?api_key=' + apiKey,
            data=json.dumps(postData),
            headers={
                'Content-Type': 'application/json'
            }
        )
    except requests.exceptions.HTTPError as e:
        err_str = "Pushy API returned HTTP error " + str(e.code) + \
            ": " + e.read()
        print(err_str)


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

    if len(positions):
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

    # area enter & exit event
    for vehicle in vehicles:
        if not Config.TEST_MODE:
            if int(vehicle['speed']) == 0:
                continue

        plate_num = vehicle['plateNum']

        if plate_num not in Config.vehicles:
            continue

        if Config.vehicles[plate_num]['bind_method'] is None:
            continue

        vehicle_pos = (vehicle['lat'], vehicle['lng'])
        if Config.DEBUG:
            print('[GeoPy]: Current {} Position - ({}, {})'.format(
                plate_num, vehicle['lat'], vehicle['lng']
            ))

        # check if the vehicle enter or exit black dot
        for blackdot in Config.blackdots:
            blackdot_pos = (blackdot['latitude'], blackdot['longitude'])
            enter_exit_event = 0

            if Config.TEST_MODE:
                try:
                    delta_distance = int(
                        r.get('blackdot_delta_distance').decode('utf-8')
                    )
                except Exception:
                    print('[Error]: Check redis "blackdot_delta_distance" key')
                    return

            else:
                delta_distance = distance.distance(vehicle_pos, blackdot_pos).m

            if Config.DEBUG:
                print('[GeoPy]: Distance with ({}, {}) is {}'.format(
                    blackdot['latitude'], blackdot['longitude'],
                    delta_distance
                ))
            if delta_distance < blackdot['radius'] and\
               Config.vehicles[plate_num]['blackdotposition'] ==\
               Config.VEHICLE_OUT_AREA:

                Config.vehicles[plate_num]['blackdotposition'] =\
                    Config.VEHICLE_IN_AREA
                enter_exit_event = Config.ENTER_BLACK_DOT_EVENT
                if Config.DEBUG:
                    print('[GeoPy]: {} enter into ({}, {})'.format(
                        plate_num, blackdot['latitude'], blackdot['longitude']
                    ))

            if delta_distance > blackdot['radius'] and\
               Config.vehicles[plate_num]['blackdotposition'] ==\
               Config.VEHICLE_IN_AREA:

                Config.vehicles[plate_num]['blackdotposition'] =\
                    Config.VEHICLE_OUT_AREA
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
                    if result is None and Config.DEBUG:
                        print('[Error]: Vehicle and user not bind')
                        break

                    driver_id = result[0]
                    channel_name = result[1]
                    device_token = result[2]

                    cursor.execute("""
                    SELECT notification_message
                    FROM info_station WHERE id={}
                    """.format(blackdot['station_id']))
                    notification_message = cursor.fetchone()[0]
                    message = {
                        'notification': notification_message
                    }

                    cursor.execute("""
                    INSERT INTO notification_notification
                        (msg_type, message, user_id, is_read, sent_on)
                    VALUES ('{}', '{}', '{}', False, now()) RETURNING sent_on;
                    """.format(
                        enter_exit_event, json.dumps(message), driver_id
                    ))
                    connection.commit()
                    sent_on = cursor.fetchone()[0]
                    data = {
                        'msg_type': enter_exit_event,
                        'message': message,
                        'is_read': False,
                        'sent_on': sent_on.strftime('%Y-%m-%d %H:%M')
                    }

                    if channel_name:
                        async_to_sync(channel_layer.send)(
                            channel_name,
                            {
                                'type': 'notify',
                                'data': data
                            }
                        )

                    if device_token:
                        to = [device_token]

                        options = {
                            'notification': {
                                'badge': 1,
                                'sound': 'ping.aiff',
                                'body': u'New job is assigned to you'
                            }
                        }
                        sendPushNotification(data, to, options)

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
        if Config.vehicles[plate_num]['progress'] is None:
            return

        next_station_pos = (
            Config.vehicles[plate_num]['latitude'],
            Config.vehicles[plate_num]['longitude']
        )
        next_station_radius = Config.vehicles[plate_num]['radius']
        enter_exit_event = 0

        if Config.TEST_MODE:
            try:
                delta_distance = int(
                    r.get('station_delta_distance').decode('utf-8')
                )
            except Exception:
                print('[Error]: Check redis "station_delta_distance" key')
                return
        else:
            delta_distance = distance.distance(vehicle_pos, next_station_pos).m

        if Config.DEBUG:
            print('[GeoPy]: Distance with ({}, {}) is {}'.format(
                Config.vehicles[plate_num]['latitude'],
                Config.vehicles[plate_num]['longitude'],
                delta_distance
            ))

        if delta_distance < next_station_radius and\
           Config.vehicles[plate_num]['stationposition'] ==\
           Config.VEHICLE_OUT_AREA:
            Config.vehicles[plate_num]['stationposition'] =\
                Config.VEHICLE_IN_AREA
            enter_exit_event = Config.ENTER_STATION_EVENT
            if Config.DEBUG:
                print('[GeoPy]: {} enter into ({}, {})'.format(
                    plate_num, Config.vehicles[plate_num]['latitude'],
                    Config.vehicles[plate_num]['longitude']
                ))

        if delta_distance > next_station_radius and\
           Config.vehicles[plate_num]['stationposition'] ==\
           Config.VEHICLE_IN_AREA:
            Config.vehicles[plate_num]['stationposition'] =\
                Config.VEHICLE_OUT_AREA
            enter_exit_event = Config.EXIT_STATION_EVENT
            if Config.DEBUG:
                print('[G7]: {} exit from ({}, {})'.format(
                    plate_num, Config.vehicles[plate_num]['latitude'],
                    Config.vehicles[plate_num]['longitude']
                ))

        if enter_exit_event:
            try:
                connection = psycopg2.connect(Config.DB_URL)
                cursor = connection.cursor()

                cursor.execute(
                    Config.CHANNEL_NAME_QUERY.format(plate_num)
                )
                result = cursor.fetchone()
                if result is None and Config.DEBUG:
                    print('[Error]: Vehicle and user not bind')
                    break

                driver_id = result[0]
                channel_name = result[1]
                device_token = result[2]

                # Get the current job progress
                cursor.execute("""
                SELECT progress FROM order_job WHERE id={}
                """.format(Config.vehicles[plate_num]['job_id']))
                current_progress = cursor.fetchone()[0]
                step = Config.vehicles[plate_num]['step']
                job_id = Config.vehicles[plate_num]['job_id']
                station_id = Config.vehicles[plate_num]['station_id']

                quality_station_exit = step == 0 and\
                    Config.vehicles[plate_num]['is_same_station']
                if enter_exit_event == Config.ENTER_STATION_EVENT:
                    expected_progress = step * 4 + 3
                elif enter_exit_event == Config.EXIT_STATION_EVENT:
                    expected_progress = step * 4 + 6
                    if quality_station_exit:
                        expected_progress += 4

                if expected_progress != current_progress:
                    if Config.DEBUG:
                        print("Driver didn't update the progress")

                    if enter_exit_event == Config.ENTER_STATION_EVENT:
                        # update jobstation model
                        cursor.execute("""
                        UPDATE order_jobstation
                        SET arrived_station_on=now()
                        WHERE job_id={} AND step={}
                        """.format(job_id, step))

                        # update job progress
                        cursor.execute("""
                        UPDATE order_job
                        SET progress={}
                        WHERE id={}
                        """.format(expected_progress, job_id))
                        Config.vehicles[plate_num]['progress'] =\
                            expected_progress
                        connection.commit()
                    elif enter_exit_event == Config.EXIT_STATION_EVENT:
                        next_step = step + 1
                        if quality_station_exit:
                            next_step = 2

                        cursor.execute("""
                        SELECT step, station_id
                        FROM order_jobstation
                        WHERE job_id={} and step={} and is_completed=False
                        """.format(job_id, next_step))
                        result = cursor.fetchone()

                        # update job station model
                        cursor.execute("""
                        UPDATE order_jobstation
                        SET departure_station_on=now(),
                            is_completed=True
                        WHERE job_id={} AND step={}
                        """.format(job_id, step))

                        if quality_station_exit:
                            cursor.execute("""
                            UPDATE order_jobstation
                            SET departure_station_on=now(),
                                is_completed=True
                            WHERE job_id={} AND step={}
                            """.format(job_id, step))
                            cursor.execute("""
                            UPDATE order_jobstation
                            SET departure_station_on=now(),
                                is_completed=True
                            WHERE job_id={} AND step={}
                            """.format(job_id, step+1))

                        if result is None:
                            cursor.execute("""
                            UPDATE order_job
                            SET progress=0,
                                finished_on=now()
                            WHERE id={}
                            """.format(job_id))
                            Config.vehicles[plate_num]['is_same_station'] =\
                                None
                            Config.vehicles[plate_num]['progress'] = None
                            Config.vehicles[plate_num]['job_id'] = None
                            Config.vehicles[plate_num]['step'] = None
                            Config.vehicles[plate_num]['longitude'] = None
                            Config.vehicles[plate_num]['latitude'] = None
                            Config.vehicles[plate_num]['radius'] = None
                        else:
                            next_step = result[0]
                            next_station_id = result[1]

                            cursor.execute("""
                            UPDATE order_job
                            SET progress={}
                            WHERE id={};
                            """.format(expected_progress, job_id))

                            cursor.execute("""
                            SELECT id, longitude, latitude, radius
                            FROM info_station
                            WHERE id={}
                            """.format(next_station_id))

                            station_info = cursor.fetchone()
                            Config.vehicles[plate_num]['progress'] =\
                                expected_progress
                            Config.vehicles[plate_num]['step'] = next_step
                            Config.vehicles[plate_num]['station_id'] =\
                                station_info[0]
                            Config.vehicles[plate_num]['longitude'] =\
                                station_info[1]
                            Config.vehicles[plate_num]['latitude'] =\
                                station_info[2]
                            Config.vehicles[plate_num]['radius'] =\
                                station_info[3]

                        connection.commit()

                # Notification
                cursor.execute("""
                SELECT address
                FROM info_station WHERE id={}
                """.format(station_id))

                notification_message = cursor.fetchone()[0]
                message = {
                    'notification': notification_message
                }

                cursor.execute("""
                INSERT INTO notification_notification
                    (msg_type, message, user_id, is_read, sent_on)
                VALUES ('{}', '{}', '{}', False, now()) RETURNING sent_on;
                """.format(
                    enter_exit_event, json.dumps(message), driver_id
                ))
                connection.commit()
                sent_on = cursor.fetchone()[0]
                data = {
                    'msg_type': enter_exit_event,
                    'message': message,
                    'is_read': False,
                    'sent_on': sent_on.strftime('%Y-%m-%d %H:%M')
                }
                if channel_name:
                    async_to_sync(channel_layer.send)(
                        channel_name,
                        {
                            'type': 'notify',
                            'data': data
                        }
                    )

                if device_token:
                    to = [device_token]

                    options = {
                        'notification': {
                            'badge': 1,
                            'sound': 'ping.aiff',
                            'body': u'New job is assigned to you'
                        }
                    }
                    sendPushNotification(data, to, options)

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
        '-t', '--test', help='Set test mode',
        action='store_true'
    )
    ap.add_argument(
        'channel_layer', help='ASGI channel layer instance'
    )
    args = ap.parse_args()

    channel_layer = get_channel_layer(args.channel_layer)

    Config.DEBUG = args.debug
    Config.TEST_MODE = args.test
    Config.read_env(args.settings)
    Config.load_data_from_db()

    asgi_client = ASGIMQTTClient(
        Config.HOST, Config.PORT, Config.CLIENT_ID, Config.USERNAME,
        Config.PASSWORD, Config.TOPIC, Config.QOS, channel_layer
    )
    asgi_client.run()
