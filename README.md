# tms-backend
Vehicle Management System
- [Development](#development)
- [Deployment](#deployment)
  - [Deploy to Heroku](#deploy-to-heroku)
  - [Deploy to Alibaba](#deploy-to-alibaba)
- [About Project](#about-project)
  - [asgimqtt.py](#asgimqtt.py)

## Development
### Prequisites
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

### Clone and installing project into local
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
### Deploy to Heroku
```
heroku create tms-backend
heroku config:set DJANGO_SETTINGS_MODULE='config.settings.staging_heroku'
git push heroku master
```


### Deploy to Alibaba Cloud
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

3. Configure wsgi & asgi & nginx
```
cp deploy/tms_backend.conf /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/tms_backend /etc/nginx/sites-enabled/tms_backend
systemctl restart nginx

cp deploy/daphne.service /lib/systemd/system/
cp deploy/uwsgi.service /lib/systemd/system/
cp deploy/tms_backend.ini /etc/uwsgi/sites/
cp deploy/g7.service /lib/systemd/system/
docker run -dit --restart unless-stopped -p 6379:6379 -d redis:2.8
```

5. Explanation
Django Channels is used for providing socket. Although ASGI server - daphne is able to handle websocket and http requests, I use WSGI server for http requests and ASGI server for handling only web sockets.
Check the `deploy` folder


## About Project
### asgimqtt.py
asgimqtt.py is a MQTT interface from ASGI. It connects to G7 MQTT Server and receives real-time vehicle positioning data published by G7.

- `Functionalities`:
  - Send vehicle positioning data to Django Channel Layres
  - Monitor the entry enter & exit by calculating longitude and latitude between vehicle and stations
  - At first, I tried to query station position data from db when mqtt client receive poition data. But G7 server publish the data every seconds(of course, it can be adjusted on our side). Querying db every second was redundant and useless. So in order to improve the performance, I load station position data into our variables at the first beginning of the process startup or when the station data are updated.
 
- `Why I don't use Redis?`
  - This is because redis is `key-value` in-memory database, (de)serializing the station data might be time-consuming. When we have large data, (de)serializing might be longer than db query time.

> `TODO`: Try to import arguments from .env file
