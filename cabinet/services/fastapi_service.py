import requests
import logging
from django.conf import settings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class FastAPIService:
    def __init__(self):
        self.base_url = settings.FASTAPI_SERVICE_URL.rstrip("/")
        self.session = self._create_session()

    def _create_session(self):
        session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def get_user_stats(self, user_id: int) -> dict:
        """
        ЧИСТО: только запрос → только данные
        """
        url = f"{self.base_url}/user/users/{user_id}/status"

        logger.info(f"Request FastAPI stats for user {user_id}")

        response = self.session.get(url, timeout=5)
        response.raise_for_status()

        payload = response.json()

        if payload.get("error"):
            raise RuntimeError(payload.get("error_msg", "FastAPI error"))

        return payload["data"]
