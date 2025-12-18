import os
from celery import Celery

BROKER = os.getenv("CELERY_BROKER_URL", None)
BACKEND = os.getenv("CELERY_RESULT_BACKEND", None)

if BROKER:
    celery = Celery(
        "linkmomentum",
        broker=BROKER,
        backend=BACKEND or BROKER,
        include=["app.tasks"]
    )

    # basic recommended config
    celery.conf.update(
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        timezone='UTC',
        enable_utc=True,
    )
else:
    celery = None
