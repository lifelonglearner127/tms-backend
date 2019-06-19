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
export DJANGO_SETTINGS_MODULE=config.settings.local
python manage.py migrate
python manage.py runserver
```


## Deployment
### Deploying to Heroku
```
heroku create tms-backend
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
git push heroku master
```


### Deploying to Alibaba Cloud
1. In order to deploy django app to Alibaba Cloud, we need to intall Prerequisites.
 - Python & Pip & Virtualenv
```
sudo apt-get install python-pip
sudo pip install virtualenv
```
> Important! Please double check python version before installing Prerequisites. This part can be skipped if these prerequisites are already installed.
 
 - Nginx
```
sudo apt-get install nginx
```
> Important! This part can be skipped if these prerequisites are already installed.
 
 - [Install Postgresql](https://www.postgresql.org/download/)
```
sudo su postgres
psql
CREATE DATABASE tms;
CREATE USER dev WITH PASSWORD 'admin123';
GRANT ALL PRIVILEGES ON DATABASE "tms" to dev;
```
> Important! This part can be skipped if these prerequisites are already installed.

2. Clone and setup db
```
mkdir ~/.virtualenvs && cd ~/.virtualenvs
virtualenv tms-backend
source tms-backend/bin/activate
cd ~ && mkdir Projects && cd Projects && git clone https://github.com/lifelonglearner127/tms-backend.git
cd tms-backend && pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=config.settings.staging_alibaba
cp .env.example .env
python manage.py collectstatic
python manage.py migrate
python manage.py createsuperuser
```

3. Configure wsgi & nginx
```
cp tms_backend /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/tms_backend /etc/nginx/sites-enabled/tms_backend
uwsgi uwsgi.ini
systemctl restart nginx
```

