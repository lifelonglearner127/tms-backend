# tms-backend
Vehicle Management System

## Prequisites
 - Postgresql
 - Python3.6
 - virtualenv

### Install & Configure Postgresql
Please refer to this [link](https://www.postgresql.org/download/) to install Postgresql

Configure postgresql:
```
sudo su postgres
psql
CREATE DATABASE database_name;
CREATE USER my_username WITH PASSWORD 'my_password';
GRANT ALL PRIVILEGES ON DATABASE "database_name" to my_username;
```

## Clone and installing project into local
```
git clone git@github.com:lifelonglearner127/tms-backend.git
cd tms-backend
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Configure Environment Variables
```
cd tms-backend
cp .env.example .env
```

Running Locally
```
export DJANGO_READ_DOT_ENV_FILE=True
export DJANGO_SETTINGS_MODULE=config.settings.local
python manage.py migrate
python manage.py runserver
```

Running on Heroku
```
heroku config:set G7_HTTP_HOST=''
heroku config:set G7_HTTP_BASEURL=''
heroku config:set G7_HTTP_VEHICLE_BASIC_ACCESS_ID=''
heroku config:set G7_HTTP_VEHICLE_BASIC_SECRET=''
heroku config:set G7_HTTP_VEHICLE_DATA_ACCESS_ID=''
heroku config:set G7_HTTP_VEHICLE_DATA_SECRET=''

heroku config:set G7_MQTT_HOST=''
heroku config:set G7_MQTT_POSITION_TOPIC=''
heroku config:set G7_MQTT_POSITION_CLIENT_ID=''
heroku config:set G7_MQTT_POSITION_ACCESS_ID=''
heroku config:set G7_MQTT_POSITION_SECRET=''
```