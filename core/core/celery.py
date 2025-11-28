from os import environ
from celery import Celery
from celery.schedules import crontab

environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")

app.conf.update(
    broker_connection_retry_on_startup=True,
)


app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
