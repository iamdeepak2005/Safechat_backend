from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager


from celery import Celery


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


celery_app = None


def make_celery(app=None):
    global celery_app
    if celery_app is None:
        app = app or __import__('app').app
        celery_app = Celery(app.import_name,
                             broker=app.config['CELERY_BROKER_URL'],
                             backend=app.config['CELERY_RESULT_BACKEND'])
        celery_app.conf.update(app.config)
# ensure tasks run with app context
        TaskBase = celery_app.Task
        class ContextTask(TaskBase):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)
        celery_app.Task = ContextTask
    return celery_app