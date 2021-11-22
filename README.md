# Algorand Blockchain Analysis Dashboard - Backend

This project exposes an API for the algorand-dashboard-frontend project.

## Requirements

- This is a django project, thus requires a python installation and the pip package manager.

### Python

- #### Installation on Ubuntu

  You can install python and pip easily with apt install following online tutorials or run the following commands:

      $ sudo apt install python3-pip
      $ python3 --version

- #### Setup the environment
  
  Create and activate a virtual environment
      
      $ sudo apt install python3.8-venv
      $ python3 -m venv venv
      $ source venv/bin/activate
  
  Install packages defined in requirements.txt using pip
  
      $ sudo pip install -r requirements.txt

### Postgresql

- #### Installation on Ubuntu

  $ sudo apt install postgresql postgresql-contrib
  
  Create a db called algodashboard
  
  $ sudo -u postgres psql
  postgres=# create database algorand_dashboard;
  postgres=# create user algorand_admin with encrypted password '123456';
  postgres=# grant all privileges on database algorand_dashboard to algorand_admin;
  
- #### Run postgresql
  
  Start the server
  
  $ sudo service postgresql start
  $ sudo /etc/init.d/postgresql restart
  
  Check if postgresql is running
  
  $ sudo netstat -plunt |grep postgres

### Redis server

- #### Installation ubuntu

  $ sudo apt install redis-server

## Configure app

- Create a local_settings.py file in the folder algorand_dashboard.
- Copy the file local_settings_copy.py into the local_settings.py file.

## Start backend server

python3 manage.py runserver

# Load initial data for AccountType and InstrumentType models
python3 manage.py loaddata fixtures/model_fixtures.json

# Reset tables ** BE CAREFUL **
python3 manage.py flush

# Process transactions in dashboard_analytics/data folder
Copy transactions to be processed from cbdc_dict_all.py to cbdc_dict.py. \
Copy all if required; it might take a bit of time to load all. \

## Start celery worker
Run celery worker command: celery -A algorand_dashboard worker -l info \
Wait for task to be successful.

