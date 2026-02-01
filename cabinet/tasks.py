# tasks.py
import logging
from celery import shared_task
from django.core.cache import cache
from .services.fastapi_service import FastAPIService

logger = logging.getLogger(__name__)

CACHE_TTL = 300  # 5 минут


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={"max_retries": 5},
)
def update_user_stats_cache(self, user_id: str):
    """
    Асинхронно получает данные из FastAPI и кладёт в cache
    """
    logger.info(f"Start async stats update for user {user_id}")

    service = FastAPIService()
    data = service.get_user_stats(user_id)

    cache_key = f"user:stats:{user_id}"
    cache.set(cache_key, data, timeout=CACHE_TTL)

    logger.info(f"Stats cached for user {user_id}")
    return True
