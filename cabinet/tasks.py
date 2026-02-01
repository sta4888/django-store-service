from celery import shared_task
import logging
from .services.fastapi_service import FastAPIService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def update_user_stats_cache(self, user_id):
    """
    Асинхронное обновление кэша пользователя
    """
    try:
        service = FastAPIService()
        stats = service.get_user_stats(user_id, force_refresh=True)

        if stats is None:
            # Если данные не получены, пробуем еще раз
            raise self.retry(countdown=self.default_retry_delay)

        logger.info(f"Async cache update completed for user {user_id}")
        return {"user_id": user_id, "success": True}

    except Exception as exc:
        logger.error(f"Async update failed for user {user_id}: {exc}")
        try:
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        except self.MaxRetriesExceededError:
            logger.critical(f"Max retries exceeded for user {user_id}")
            return {"user_id": user_id, "success": False, "error": str(exc)}


import httpx
from celery import shared_task
from django.core.cache import cache

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 10})
def sync_user_stats(user_id: int):
    url = f"http://localhost:8001/user/users/{user_id}/status"

    r = httpx.get(url, timeout=5)
    r.raise_for_status()

    data = r.json()["data"]

    cache.set(
        f"user:stats:{user_id}",
        data,
        timeout=300  # 5 минут
    )


CACHE_TTL = 300
@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={"max_retries": 5},
)
def update_user_stats_cache(user_id: int):
    service = FastAPIService()

    data = service.get_user_stats(user_id)

    cache_key = f"user:stats:{user_id}"
    cache.set(cache_key, data, timeout=CACHE_TTL)

    logger.info(f"User stats cached for user {user_id}")
    return True