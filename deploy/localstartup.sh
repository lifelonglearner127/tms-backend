#!/bin/bash
cd /home/dev/Projects/tms-backend
/home/dev/.virtualenvs/tms-backend-venv/bin/celery worker -A config -D &
/home/dev/.virtualenvs/tms-backend-venv/bin/python mqtt/asgimqtt.py --settings .env config.asgi:channel_layer &
/home/dev/.virtualenvs/tms-backend-venv/bin/python mqtt/stop_event.py --settings .env config.asgi:channel_layer &
/home/dev/.virtualenvs/tms-backend-venv/bin/python mqtt/idle_event.py --settings .env config.asgi:channel_layer &
/home/dev/.virtualenvs/tms-backend-venv/bin/python mqtt/ems_event.py --settings .env config.asgi:channel_layer &
