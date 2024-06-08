from celery import Celery
from kombu import Queue

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config["broker_url"],
        backend=app.config["result_backend"],
        include=["tasks"],
    )
    celery.conf.update(app.config)

    if app.config["DEBUG"]:
        celery_log_level = "DEBUG"
    else:
        celery_log_level = "INFO"

    celery.conf.update(
        worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
        worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
        worker_log_color=False,
        worker_redirect_stdouts_level=celery_log_level,
        worker_redirect_stdouts=True,
        task_queues=(Queue("default", routing_key="task.#"),),
    )

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
