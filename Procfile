release: python manage.py migrate
release: python manage.py loaddata fixtures/model_fixtures.json
web: gunicorn algorand_dashboard.wsgi
worker: celery -A algorand_dashboard worker -B