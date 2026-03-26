# eaupourtous/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eaupourtous.settings')

app = Celery('eaupourtous')

# Le namespace='CELERY' force Celery à lire les variables commençant par CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()