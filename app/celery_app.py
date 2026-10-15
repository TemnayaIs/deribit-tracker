from celery import Celery

from app.config import Settings


def make_celery(settings: Settings) -> Celery:
    app = Celery("deribit_tracker", broker=settings.redis_url, include=["app.tasks"])
    app.conf.update(
        timezone="UTC",
        enable_utc=True,
        task_ignore_result=True,
        broker_connection_retry_on_startup=True,
        beat_schedule={
            "collect-prices": {
                "task": "prices.collect",
                "schedule": float(settings.fetch_interval_seconds),
            },
        },
    )
    return app


celery_app = make_celery(Settings())
