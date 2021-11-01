# Check if postgresql is running
sudo netstat -plunt |grep postgres

# Start postgresql server
sudo service postgresql start
sudo /etc/init.d/postgresql restart

# Use your python virtual environment
source venv/bin/activate

# Start backend server
python3 manage.py runserver

# Start celery worker
celery -A algorand_dashboard worker -l info

