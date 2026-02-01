import requests
import logging
from django.conf import settings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.settings import FASTAPI_SERVICE_URL

logger = logging.getLogger(__name__)


class FastAPIService:
    def __init__(self):
        self.base_url = FASTAPI_SERVICE_URL.rstrip("/")
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

    def get_user_stats(self, user_id: str) -> dict:
        """
        ЧИСТО: только запрос → только данные
        """
        url = f"{self.base_url}/user/users/{user_id}/status"

        logger.info(f"Request FastAPI stats for user {user_id}")
        logger.info(f"Request FastAPI url {url}")

        response = self.session.get(url, timeout=5)
        response.raise_for_status()

        payload = response.json()

        if payload.get("error"):
            raise RuntimeError(payload.get("error_msg", "FastAPI error"))

        return payload["data"]

    def add_user(self, user_id: str, referrer_id: str) -> dict:
        """
        отправка данных о новом пользователе
        """
        url = f"{self.base_url}/user/users/"

        payload = {
            "user_id": user_id,
            "referrer_id": referrer_id
        }

        logger.info(f"Request FastAPI add new user {user_id} with referrer {referrer_id}")
        logger.info(f"Request FastAPI url {url} | payload: {payload}")

        response = self.session.post(url, json=payload, timeout=5)
        response.raise_for_status()

        data = response.json()

        if data.get("error"):
            raise RuntimeError(data.get("error_msg", "FastAPI error"))

        return data["data"]

