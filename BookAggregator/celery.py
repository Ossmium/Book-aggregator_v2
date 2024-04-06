import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BookAggregator.settings')
app = Celery('BookAggregator', broker_connection_retry=False,
             broker_connection_retry_on_startup=True, )
app.config_from_object('django.conf:settings')
broker_connection_retry = False

app.autodiscover_tasks()

app.autodiscover_tasks()
app.conf.beat_schedule = {
    'send-report-every-sunday': {
        'task': 'book_aggregator.tasks.get_new_books',
        'schedule': crontab(hour=7, minute=30, day_of_week='sunday'),
    },
}
