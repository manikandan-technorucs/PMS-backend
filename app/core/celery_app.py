from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "pms_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Configure retry behavior defaults globally if needed
    task_acks_late=True,
    task_reject_on_worker_lost=True
)

# Optional: Ensure our imports get picked up by the worker
celery_app.autodiscover_tasks(["app.services"])
