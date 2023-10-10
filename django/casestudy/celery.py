"""
Celery initialization file.
"""
from __future__ import absolute_import, unicode_literals

import logging

from casestudy import settings
from celery import Celery
from kombu import Exchange, Queue

CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
)

CELERYD_HIJACK_ROOT_LOGGER = False

LOG_LEVEL = logging.INFO
LOG_FORMAT = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

app = Celery('casestudy')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(settings.INSTALLED_APPS)
