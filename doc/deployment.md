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

 - [Install RabbitMQ]
 ```
 sudo apt-get install rabbitmq-server
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
- Configure Nginx
```
cp deploy/tms_backend.conf /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/tms_backend /etc/nginx/sites-enabled/tms_backend
systemctl restart nginx
```
- configure redis as docker
```
docker run -dit --restart unless-stopped -p 6379:6379 -d redis:2.8
```

- Configure Various serivices
```
cp deploy/tms_backend.ini /etc/uwsgi/sites/
cp deploy/*.service /lib/systemd/system/
```
- Restart Services
```
systemctl daemon-reload
systemctl restart tms_celery.service
systemctl restart tms_celery_beat.service
systemctl restart tms_daphne.service
systemctl restart tms_uwsgi.service
systemctl restart tms_g7_position.service
systemctl restart tms_g7_stop_event.service
systemctl restart tms_g7_ems_event.service
systemctl restart tms_g7_idle_event.service

systemctl status tms_celery.service
systemctl status tms_celery_beat.service
systemctl status tms_daphne.service
systemctl status tms_uwsgi.service
systemctl status tms_g7_position.service
systemctl status tms_g7_stop_event.service
systemctl status tms_g7_ems_event.service
systemctl status tms_g7_idle_event.service
```

5. Explanation
Django Channels is used for providing socket. Although ASGI server - daphne is able to handle websocket and http requests, I use WSGI server for http requests and ASGI server for handling only web sockets.
Check the `deploy` folder
 - Debugging Enter & Exit Area
```
python mqtt/asgimqtt.py --settings .env --debug config.asgi:channel_layer
```