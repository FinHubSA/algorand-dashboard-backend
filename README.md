# Check if postgresql is running
sudo netstat -plunt |grep postgres

# Start postgresql server
sudo service postgresql start \
sudo /etc/init.d/postgresql restart \

# Use your python virtual environment
source venv/bin/activate

# Start backend server
python3 manage.py runserver

# Process transactions in dashboard_analytics/data folder
Copy transactions to be processed from cbdc_dict_all.py to cbdc_dict.py. \
Copy all if required; it might take a bit of time to load all. \
## Start celery worker
Run celery worker command: celery -A algorand_dashboard worker -l info \
Wait for task to be successful.

