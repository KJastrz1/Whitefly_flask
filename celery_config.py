from celery import Celery
import logging

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['result_backend'],
        include=['tasks']
    )
    celery.conf.update(app.config)

    if app.config['DEBUG']:
        celery_log_level = logging.DEBUG
    else:
        celery_log_level = logging.INFO

    celery_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
    logging.basicConfig(level=celery_log_level, format=celery_log_format)

    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
