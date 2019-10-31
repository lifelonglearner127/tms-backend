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