1. copy .env.example -> .env and fill values
 2. docker-compose up -d (postgres + redis + minio)
3. python -m venv venv && source venv/bin/activate
4. pip install -r requirements.txt
5. flask db init && flask db migrate && flask db upgrade
6. start: flask run OR python run.py
7. celery worker: celery -A tasks.celery_app worker --loglevel=info
8. celery beat (periodic expiry): celery -A tasks.celery_app beat --loglevel=info
