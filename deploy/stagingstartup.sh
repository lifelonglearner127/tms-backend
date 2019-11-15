#!/bin/bash
cd /root/Projects/tms-backend
/root/.virtualenvs/tms-backend/bin/uwsgi /etc/uwsgi/sites/tms_backend.ini &
/root/.virtualenvs/tms-backend/bin/daphne --bind 0.0.0.0 --port 9000 --verbosity 0 config.asgi:application &
/root/.virtualenvs/tms-backend/bin/celery worker -A config -D &
/root/.virtualenvs/tms-backend/bin/python mqtt/asgimqtt.py --settings .env config.asgi:channel_layer &
/root/.virtualenvs/tms-backend/bin/python mqtt/stop_event.py --settings .env config.asgi:channel_layer &
/root/.virtualenvs/tms-backend/bin/python mqtt/idle_event.py --settings .env config.asgi:channel_layer &
/root/.virtualenvs/tms-backend/bin/python mqtt/ems_event.py --settings .env config.asgi:channel_layer &