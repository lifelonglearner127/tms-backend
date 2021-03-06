"""
# TODO:
 - Not sure why mqtt client automatically disconnect after receiving message
 - entry enter & exit event

"""
import argparse
import redis
import sys
import datetime
import importlib
import json
import paho.mqtt.client as paho
import psycopg2
from asgiref.sync import async_to_sync
from geopy import distance
from aliyunsdkpush.request.v20160801 import PushRequest
from aliyunsdkcore import client


r = redis.StrictRedis(host='localhost', port=6379, db=15)


class Config:
    blackdots = []
    vehicles = {}
    aliyun_client = None
    aliyun_request = None
    ALIYUN_MOBILE_PUSH_APP_KEY = ''
    ALIYUN_MOBILE_PUSH_APP_SECRET = ''
    ALIYUN_ACCESS_KEY_ID = ''
    ALIYUN_ACCESS_KEY_SECRET = ''
    DB_URL = ''
    HOST = ''
    PORT = ''
    TOPIC = ''
    CLIENT_ID = ''
    USERNAME = ''
    PASSWORD = ''
    QOS = ''
    DEBUG = False
    LOG_FILEPATH = ''
    TEST_MODE = False
    VEHICLE_OUT_AREA = 0
    VEHICLE_IN_AREA = 1
    ENTER_STATION_EVENT = 4
    EXIT_STATION_EVENT = 5
    ENTER_BLACK_DOT_EVENT = 6
    EXIT_BLACK_DOT_EVENT = 7

    # this sql is used for retrieving vehicle-driving driver&escort channel and device token
    CHANNEL_NAME_QUERY = """
        SELECT au.id, au.channel_name, au.device_token
        FROM (
            SELECT *
            FROM vehicle_vehicleworkerbind vdb
            WHERE get_off IS NULL
        ) AS tmp
        LEFT JOIN vehicle_vehicle vv ON tmp.vehicle_id = vv.id
        LEFT JOIN account_user au ON tmp.worker_id = au.id
        WHERE vv.plate_num='{}'
        """

    # this sql is used for retriving job progress and next station location
    VEHICLES_JOBS_QUERY = """
        SELECT vv.plate_num, tmp.*
        FROM vehicle_vehicle vv
        LEFT JOIN (
            SELECT oo.is_same_station, oj.progress, oj.id, ojs.step, ist.id,
            ist.longitude, ist.latitude, ist.radius,oj.vehicle_id
            FROM (
                SELECT id, order_id, vehicle_id, progress
                FROM order_job
                WHERE id IN ({})
            ) oj
            LEFT JOIN order_order oo ON oj.order_id=oo.id
            LEFT JOIN (
                SELECT DISTINCT ON (job_id) job_id, step,
                    station_id
                FROM order_jobstation
                ORDER BY job_id, is_completed, step
            ) ojs ON ojs.job_id=oj.id
            LEFT JOIN info_station ist ON ojs.station_id=ist.id
        ) as tmp
        ON vv.id = tmp.vehicle_id
        WHERE vv.status IN (1, 2, 3)
    """

    @classmethod
    def read_env(cls, filename):
        with open(filename, 'r') as fd:
            line = fd.readline()
            while line:
                key_value = line.split('=')
                if key_value[0] == 'DATABASE_URL':
                    cls.DB_URL = key_value[1][:-1]
                if key_value[0] == 'ALIYUN_MOBILE_PUSH_APP_KEY':
                    cls.ALIYUN_MOBILE_PUSH_APP_KEY = key_value[1][:-1]
                if key_value[0] == 'ALIYUN_MOBILE_PUSH_APP_SECRET':
                    cls.ALIYUN_MOBILE_PUSH_APP_SECRET = key_value[1][:-1]
                if key_value[0] == 'ALIYUN_ACCESS_KEY_ID':
                    cls.ALIYUN_ACCESS_KEY_ID = key_value[1][:-1]
                if key_value[0] == 'ALIYUN_ACCESS_KEY_SECRET':
                    cls.ALIYUN_ACCESS_KEY_SECRET = key_value[1][:-1]
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
            print('ALIYUN_MOBILE_PUSH_APP_KEY', Config.ALIYUN_MOBILE_PUSH_APP_KEY)
            print('ALIYUN_MOBILE_PUSH_APP_SECRET', Config.ALIYUN_MOBILE_PUSH_APP_SECRET)
            print('ALIYUN_ACCESS_KEY_ID', Config.ALIYUN_ACCESS_KEY_ID)
            print('ALIYUN_ACCESS_KEY_SECRET', Config.ALIYUN_ACCESS_KEY_SECRET)
            print('G7_MQTT_HOST', Config.HOST)
            print('G7_MQTT_PORT', Config.PORT)
            print('G7_MQTT_POSITION_TOPIC', Config.TOPIC)
            print('G7_MQTT_POSITION_CLIENT_ID', Config.CLIENT_ID)
            print('G7_MQTT_POSITION_ACCESS_ID', Config.USERNAME)
            print('G7_MQTT_POSITION_SECRET', Config.PASSWORD)
            print('G7_MQTT_QOS', Config.QOS)

        if Config.LOG_FILEPATH:
            with open(Config.LOG_FILEPATH, 'a') as f:
                now_time = datetime.datetime.now()
                time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f'{time_fmt} [Settings] DATABASE_URL: {Config.DB_URL}\n')
                f.write(f'{time_fmt} [Settings] ALIYUN_MOBILE_PUSH_APP_KEY: {Config.ALIYUN_MOBILE_PUSH_APP_KEY}\n')
                f.write(f'{time_fmt} [Settings] ALIYUN_MOBILE_PUSH_APP_SECRET: {Config.ALIYUN_MOBILE_PUSH_APP_SECRET}\n')
                f.write(f'{time_fmt} [Settings] ALIYUN_ACCESS_KEY_ID: {Config.ALIYUN_ACCESS_KEY_ID}\n')
                f.write(f'{time_fmt} [Settings] ALIYUN_ACCESS_KEY_SECRET: {Config.ALIYUN_ACCESS_KEY_SECRET}\n')
                f.write(f'{time_fmt} [Settings] G7_MQTT_HOST: {Config.HOST}\n')
                f.write(f'{time_fmt} [Settings] G7_MQTT_PORT: {Config.PORT}\n')
                f.write(f'{time_fmt} [Settings] G7_MQTT_POSITION_TOPIC: {Config.TOPIC}\n')
                f.write(f'{time_fmt} [Settings] G7_MQTT_POSITION_CLIENT_ID: {Config.CLIENT_ID}\n')
                f.write(f'{time_fmt} [Settings] G7_MQTT_POSITION_ACCESS_ID: {Config.USERNAME}\n')
                f.write(f'{time_fmt} [Settings] G7_MQTT_POSITION_SECRET: {Config.PASSWORD}\n')
                f.write(f'{time_fmt} [Settings] G7_MQTT_QOS: {Config.QOS}\n')

    @classmethod
    def load_data_from_db(cls):
        is_blackdots_updated = r.get('blackdot') == b'updated'
        is_vehicles_updated = r.get('vehicle') == b'updated'
        updated_jobs = r.smembers('jobs')
        if not is_blackdots_updated and not is_vehicles_updated and not updated_jobs:
            return

        try:
            connection = psycopg2.connect(cls.DB_URL)
            cursor = connection.cursor()
            if is_blackdots_updated:
                cls.blackdots = []
                if Config.DEBUG:
                    print('[Load Data]: Loading blackdots...')

                if Config.LOG_FILEPATH:
                    with open(Config.LOG_FILEPATH, 'a') as f:
                        now_time = datetime.datetime.now()
                        time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f'{time_fmt} [Load Data]: Loading blackdots...\n')

                cursor.execute("""
                    SELECT id, latitude, longitude, radius
                    FROM info_station
                    WHERE station_type=5
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

                if Config.LOG_FILEPATH:
                    with open(Config.LOG_FILEPATH, 'a') as f:
                        now_time = datetime.datetime.now()
                        time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
                        for blackdot in cls.blackdots:
                            f.write(
                                f"{time_fmt} [Blackdot]: "
                                f"station_id: {blackdot['station_id']} "
                                f"latitude: {blackdot['latitude']} "
                                f"longitude: {blackdot['longitude']} "
                                f"radius: {blackdot['radius']}\n")

                r.set('blackdot', 'read')

            if is_vehicles_updated or updated_jobs:
                if Config.DEBUG:
                    print('[Load Data]: Loading updated vehicles...')

                if Config.LOG_FILEPATH:
                    with open(Config.LOG_FILEPATH, 'a') as f:
                        now_time = datetime.datetime.now()
                        time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")

                        f.write(
                            f"{time_fmt} "
                            f'[Load Data]: Loading updated vehicles...\n')

                current_updated_jobs = []
                for updated_job in updated_jobs:
                    current_updated_jobs.append(
                        updated_job.decode('utf-8')
                    )
                current_updated_job_ids = ', '.join(current_updated_jobs)

                if Config.LOG_FILEPATH:
                    with open(Config.LOG_FILEPATH, 'a') as f:
                        now_time = datetime.datetime.now()
                        time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
                        f.write(
                            f"{time_fmt} "
                            f'[Load Data]: Loading updated jobs: {current_updated_job_ids}...\n')

                if current_updated_job_ids:
                    query_str = Config.VEHICLES_JOBS_QUERY.format(
                        current_updated_job_ids
                    )
                    cursor.execute(query_str)
                    results = cursor.fetchall()
                    for row in results:
                        plate_num = row[0]
                        if plate_num not in cls.vehicles:
                            cls.vehicles[plate_num] = {
                                'blackdotposition': cls.VEHICLE_OUT_AREA,
                                'stationposition': cls.VEHICLE_OUT_AREA,
                                'is_same_station': row[1],
                                'job_id': row[3],
                            }
                        cls.vehicles[plate_num]['progress'] = row[2]
                        cls.vehicles[plate_num]['step'] = row[4]
                        cls.vehicles[plate_num]['station_id'] = row[5]
                        cls.vehicles[plate_num]['longitude'] = row[6]
                        cls.vehicles[plate_num]['latitude'] = row[7]
                        cls.vehicles[plate_num]['radius'] = row[8]

                    if Config.DEBUG:
                        print('[Load Data]: ', cls.vehicles)

                    if Config.LOG_FILEPATH:
                        with open(Config.LOG_FILEPATH, 'a') as f:
                            now_time = datetime.datetime.now()
                            time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
                            for plate_num, data in cls.vehicles.items():
                                f.write(
                                    f"{time_fmt} [Load Data]: "
                                    f"{plate_num}: "
                                    f"blackdotposition: {data['blackdotposition']} "
                                    f"stationposition: {data['stationposition']} "
                                    f"is_same_station: {data['is_same_station']} "
                                    f"progress: {data['progress']} "
                                    f"job_id: {data['job_id']} "
                                    f"step: {data['step']} "
                                    f"station_id: {data['station_id']} "
                                    f"longitude: {data['longitude']} "
                                    f"latitude: {data['latitude']} "
                                    f"radius: {data['radius']}\n")

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

                if Config.LOG_FILEPATH:
                    with open(Config.LOG_FILEPATH, 'a') as f:
                        now_time = datetime.datetime.now()
                        time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f'{time_fmt} [Load Data]: Database connection closed.\n')


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

    if Config.LOG_FILEPATH:
        with open(Config.LOG_FILEPATH, 'a') as f:
            now_time = datetime.datetime.now()
            time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f'{time_fmt} [G7]: Connected to MQTT Server\n')

    client.subscribe(userdata['topic'], userdata['qos'])


def _on_message(client, userdata, message):
    if Config.DEBUG:
        print('[G7]: Received message')

    response = json.loads(message.payload.decode('utf-8'))
    vehicles = response.get('data', None)

    if Config.DEBUG:
        print('[G7]: ', vehicles)

    if Config.LOG_FILEPATH:
        with open(Config.LOG_FILEPATH, 'a') as f:
            now_time = datetime.datetime.now()
            time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{time_fmt} [G7]: Received message: {message.payload.decode('utf-8')}\n")

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
            'monitor',
            {
                'type': 'notify_monitor',
                'notification_type': 'position',
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

        current_vehicle = Config.vehicles[plate_num]

        vehicle_pos = (vehicle['lat'], vehicle['lng'])
        if Config.DEBUG:
            print('[GeoPy]: Current {} Position - ({}, {})'.format(
                plate_num, vehicle['lat'], vehicle['lng']
            ))

        if Config.LOG_FILEPATH:
            with open(Config.LOG_FILEPATH, 'a') as f:
                now_time = datetime.datetime.now()
                time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(
                    f"{time_fmt} [GeoPy]: Current {plate_num} Position - ({vehicle['lat']}, {vehicle['lng']})\n"
                )

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

            if Config.LOG_FILEPATH:
                with open(Config.LOG_FILEPATH, 'a') as f:
                    now_time = datetime.datetime.now()
                    time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"{time_fmt} [GeoPy]: Current {plate_num} "
                            f"Position - ({vehicle['lat']}, {vehicle['lng']})\n")

            if delta_distance < blackdot['radius'] and current_vehicle['blackdotposition'] == Config.VEHICLE_OUT_AREA:
                current_vehicle['blackdotposition'] = Config.VEHICLE_IN_AREA
                enter_exit_event = Config.ENTER_BLACK_DOT_EVENT
                if Config.DEBUG:
                    print('[GeoPy]: {} enter into ({}, {})'.format(
                        plate_num, blackdot['latitude'], blackdot['longitude']
                    ))

                if Config.LOG_FILEPATH:
                    with open(Config.LOG_FILEPATH, 'a') as f:
                        now_time = datetime.datetime.now()
                        time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"{time_fmt} [GeoPy]: {plate_num} "
                                f"enter into ({blackdot['latitude']}, {blackdot['longitude']})\n")

            if delta_distance > blackdot['radius'] and current_vehicle['blackdotposition'] == Config.VEHICLE_IN_AREA:
                current_vehicle['blackdotposition'] = Config.VEHICLE_OUT_AREA
                enter_exit_event = Config.EXIT_BLACK_DOT_EVENT
                if Config.DEBUG:
                    print('[G7]: {} exit from ({}, {})'.format(
                        plate_num, blackdot['latitude'], blackdot['longitude']
                    ))

                if Config.LOG_FILEPATH:
                    with open(Config.LOG_FILEPATH, 'a') as f:
                        now_time = datetime.datetime.now()
                        time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"{time_fmt} [GeoPy]: {plate_num} "
                                f"exit from ({blackdot['latitude']}, {blackdot['longitude']})\n")

            if enter_exit_event:
                try:
                    connection = psycopg2.connect(Config.DB_URL)
                    cursor = connection.cursor()
                    cursor.execute(
                        Config.CHANNEL_NAME_QUERY.format(plate_num)
                    )
                    results = cursor.fetchall()
                    if len(results) == 0:
                        if Config.DEBUG:
                            print('[Error]: Vehicle and user not bind')

                        if Config.LOG_FILEPATH:
                            with open(Config.LOG_FILEPATH, 'a') as f:
                                now_time = datetime.datetime.now()
                                time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
                                f.write(f"{time_fmt} [Error]: vehicle and user not bind\n")
                        continue

                    # load black dot message
                    cursor.execute("""
                    SELECT notification_message
                    FROM info_station WHERE id={}
                    """.format(blackdot['station_id']))
                    notification_message = cursor.fetchone()[0]
                    message = {
                        'notification': notification_message
                    }

                    for result in results:
                        worker_id = result[0]
                        channel_name = result[1]
                        device_token = result[2]

                        cursor.execute("""
                        INSERT INTO notification_notification
                            (msg_type, message, user_id, is_read, is_deleted, sent_on)
                        VALUES ('{}', '{}', '{}', False, False, now()) RETURNING sent_on;
                        """.format(
                            enter_exit_event, json.dumps(message), worker_id
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
                            title = 'In Blackdot' if Config.ENTER_STATION_EVENT else 'Out Black dot'
                            body = 'In Blackdot' if Config.ENTER_STATION_EVENT else 'Out Black dot'
                            Config.aliyun_request.set_Title(title)
                            Config.aliyun_request.set_Body(body)
                            Config.aliyun_request.set_TargetValue(device_token)
                            Config.aliyun_client.do_action(Config.aliyun_request)

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

                        if Config.LOG_FILEPATH:
                            with open(Config.LOG_FILEPATH, 'a') as f:
                                now_time = datetime.datetime.now()
                                time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
                                f.write("[Enter & Exit]: Database connection closed.\n")

        # check if the vehicle enter or exit next station
        if current_vehicle['progress'] is None:
            return

        next_station_pos = (
            current_vehicle['latitude'],
            current_vehicle['longitude']
        )
        next_station_radius = current_vehicle['radius']
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
                current_vehicle['latitude'],
                current_vehicle['longitude'],
                delta_distance
            ))

        if Config.LOG_FILEPATH:
            with open(Config.LOG_FILEPATH, 'a') as f:
                now_time = datetime.datetime.now()
                time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[GeoPy]: Distance with ({current_vehicle['latitude']}, {current_vehicle['longitude']})"
                        f" is {delta_distance}\n")

        if delta_distance < next_station_radius and \
           current_vehicle['stationposition'] == Config.VEHICLE_OUT_AREA:
            current_vehicle['stationposition'] = Config.VEHICLE_IN_AREA
            enter_exit_event = Config.ENTER_STATION_EVENT
            if Config.DEBUG:
                print('[GeoPy]: {} enter into ({}, {})'.format(
                    plate_num, current_vehicle['latitude'],
                    current_vehicle['longitude']
                ))

            if Config.LOG_FILEPATH:
                with open(Config.LOG_FILEPATH, 'a') as f:
                    now_time = datetime.datetime.now()
                    time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"[GeoPy]: {plate_num} enter into "
                            f"({current_vehicle['latitude']}, {current_vehicle['longitude']})\n")

        if delta_distance > next_station_radius and \
           current_vehicle['stationposition'] == Config.VEHICLE_IN_AREA:
            current_vehicle['stationposition'] = Config.VEHICLE_OUT_AREA
            enter_exit_event = Config.EXIT_STATION_EVENT
            if Config.DEBUG:
                print('[G7]: {} exit from ({}, {})'.format(
                    plate_num, current_vehicle['latitude'],
                    current_vehicle['longitude']
                ))

            if Config.LOG_FILEPATH:
                with open(Config.LOG_FILEPATH, 'a') as f:
                    now_time = datetime.datetime.now()
                    time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"[GeoPy]: {plate_num} exit from "
                            f"({current_vehicle['latitude']}, {current_vehicle['longitude']})\n")

        if enter_exit_event:
            try:
                connection = psycopg2.connect(Config.DB_URL)
                cursor = connection.cursor()

                # Get the current job progress
                cursor.execute("""
                SELECT progress FROM order_job WHERE id={}
                """.format(current_vehicle['job_id']))
                current_progress = cursor.fetchone()[0]
                step = current_vehicle['step']
                job_id = current_vehicle['job_id']
                station_id = current_vehicle['station_id']

                quality_station_exit = step == 0 and current_vehicle['is_same_station']
                if enter_exit_event == Config.ENTER_STATION_EVENT:
                    expected_progress = step * 4 + 3
                elif enter_exit_event == Config.EXIT_STATION_EVENT:
                    expected_progress = step * 4 + 6
                    if quality_station_exit:
                        expected_progress += 4

                if expected_progress != current_progress:
                    if Config.DEBUG:
                        print("Driver didn't update the progress")

                    if Config.LOG_FILEPATH:
                        with open(Config.LOG_FILEPATH, 'a') as f:
                            now_time = datetime.datetime.now()
                            time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
                            f.write(f"{time_fmt} Driver didn't update the progress\n")

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
                        current_vehicle['progress'] = expected_progress
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
                            current_vehicle['is_same_station'] = None
                            current_vehicle['progress'] = None
                            current_vehicle['job_id'] = None
                            current_vehicle['step'] = None
                            current_vehicle['longitude'] = None
                            current_vehicle['latitude'] = None
                            current_vehicle['radius'] = None
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
                            current_vehicle['progress'] = expected_progress
                            current_vehicle['step'] = next_step
                            current_vehicle['station_id'] = station_info[0]
                            current_vehicle['longitude'] = station_info[1]
                            current_vehicle['latitude'] = station_info[2]
                            current_vehicle['radius'] = station_info[3]

                        connection.commit()

                cursor.execute(
                    Config.CHANNEL_NAME_QUERY.format(plate_num)
                )
                results = cursor.fetchall()
                if len(results) == 0:
                    if Config.DEBUG:
                        print('[Error]: Vehicle and user not bind')

                    if Config.LOG_FILEPATH:
                        with open(Config.LOG_FILEPATH, 'a') as f:
                            now_time = datetime.datetime.now()
                            time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
                            f.write(f"{time_fmt} [Error]: vehicle and user not bind\n")
                    continue

                # Get Station address
                cursor.execute("""
                SELECT address
                FROM info_station WHERE id={}
                """.format(station_id))

                notification_message = cursor.fetchone()[0]
                message = {
                    'notification': notification_message
                }

                for result in results:
                    worker_id = result[0]
                    channel_name = result[1]
                    device_token = result[2]

                    cursor.execute("""
                    INSERT INTO notification_notification
                        (msg_type, message, user_id, is_read, is_deleted, sent_on)
                    VALUES ('{}', '{}', '{}', False, False, now()) RETURNING sent_on;
                    """.format(
                        enter_exit_event, json.dumps(message), worker_id
                    ))
                    connection.commit()

                    if channel_name:
                        sent_on = cursor.fetchone()[0]
                        data = {
                            'msg_type': enter_exit_event,
                            'message': message,
                            'is_read': False,
                            'sent_on': sent_on.strftime('%Y-%m-%d %H:%M')
                        }
                        async_to_sync(channel_layer.send)(
                            channel_name,
                            {
                                'type': 'notify',
                                'data': data
                            }
                        )

                    if device_token:
                        title = 'In Station' if Config.ENTER_STATION_EVENT else 'Out Station'
                        body = 'In Station' if Config.ENTER_STATION_EVENT else 'Out Station'
                        Config.aliyun_request.set_Title(title)
                        Config.aliyun_request.set_Body(body)
                        Config.aliyun_request.set_TargetValue(device_token)
                        Config.aliyun_client.do_action(Config.aliyun_request)

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

                    if Config.LOG_FILEPATH:
                        with open(Config.LOG_FILEPATH, 'a') as f:
                            now_time = datetime.datetime.now()
                            time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
                            f.write(f"{time_fmt} [Enter & Exit]: Database connection closed.\n")


def _on_disconnect(client, userdata, rc):
    if Config.DEBUG:
        print('[G7]: Disconnected')

    if Config.LOG_FILEPATH:
        with open(Config.LOG_FILEPATH, 'a') as f:
            now_time = datetime.datetime.now()
            time_fmt = now_time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{time_fmt} [G7]: Disconnected\n")


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
        '-l', '--log', help='Specify log file path',
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
    Config.LOG_FILEPATH = args.log
    Config.TEST_MODE = args.test
    Config.read_env(args.settings)
    Config.load_data_from_db()

    Config.aliyun_client = client.AcsClient(
        Config.ALIYUN_ACCESS_KEY_ID,
        Config.ALIYUN_ACCESS_KEY_SECRET,
        'cn-hangzhou'
    )
    Config.aliyun_request = PushRequest.PushRequest()
    Config.aliyun_request.set_AppKey(Config.ALIYUN_MOBILE_PUSH_APP_KEY)
    Config.aliyun_request.set_Target('ALL')
    Config.aliyun_request.set_DeviceType('ANDROID')
    Config.aliyun_request.set_PushType('NOTICE')

    asgi_client = ASGIMQTTClient(
        Config.HOST, Config.PORT, Config.CLIENT_ID, Config.USERNAME,
        Config.PASSWORD, Config.TOPIC, Config.QOS, channel_layer
    )
    asgi_client.run()
