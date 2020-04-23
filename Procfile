web: gunicorn app.wsgi --log-file -
worker: celery worker --app=app.celery.app