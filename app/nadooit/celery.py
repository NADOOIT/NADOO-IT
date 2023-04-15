from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nadooit.settings")

app = Celery("nadooit")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.broker_url = os.environ["CELERY_BROKER_URL"]
app.conf.result_backend = os.environ["CELERY_BROKER_URL"]
