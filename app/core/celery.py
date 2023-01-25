from django_redis import get_redis_connection
import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


def tearDown(self):
    get_redis_connection("default").flushall()
    print('Cache Flushed!!')
