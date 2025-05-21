from flask import Flask
from redis import Redis
from celery import Celery, Task


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def init_redis(app: Flask) -> Redis:
    redis_client = Redis(
        host=app.config.get("REDIS_HOST", "redis"),
        port=app.config.get("REDIS_PORT", 6379),
    )
    return redis_client
