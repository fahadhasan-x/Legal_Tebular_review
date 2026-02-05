"""
Celery Application Configuration
Async task processing for document parsing and extraction
"""
from celery import Celery
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Create Celery app
celery_app = Celery(
    "legal_review_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"]  # Import tasks module
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.EXTRACTION_TIMEOUT,
    task_soft_time_limit=settings.EXTRACTION_TIMEOUT - 30,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    broker_connection_retry_on_startup=True,
)

logger.info("celery_app_configured", broker=settings.CELERY_BROKER_URL)
