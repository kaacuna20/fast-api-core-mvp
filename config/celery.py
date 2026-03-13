from celery import Celery
from config.settings import Settings


celery_app = Celery(
    f'celery_{Settings.APP_API_NAME.lower().replace(" ", "_")}',
    broker=Settings.CELERY_BROKER_URL,
    backend=Settings.CELERY_RESULT_BACKEND
)


celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

