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
    
    Installation command
    
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

    Installation command

      $ sudo apt install redis-server

### Data migration

- #### Run data migration 

    Preload constant data

      $ python manage.py migrate
      $ python manage.py loaddata fixtures/model_fixtures.json
    
    To reset the data if needed ** WARNING: THIS DELETES ALL DATA **
    
      $ python3 manage.py flush
      
- #### Simulated data

    Simulated data is in the file dashboard_analytics/data/cbcd_dict.py.
    It is an array of transactions and can be extended by following the same structure.
    A celery worker can be initiated to run the transaction processing task with the below command
    NB this is run after after starting the server (which queues the task on redis)
    
      $ celery -A algorand_dashboard worker -l info
      
## Configure app

- Create a local_settings.py file in the folder algorand_dashboard.
- Copy the file local_settings_copy.py into the local_settings.py file.

## Start backend server

      $ python3 manage.py runserver

