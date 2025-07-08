import os
import logging
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv

try:
    from upstash_redis import Redis
except Exception:  # pragma: no cover - optional dependency
    Redis = None  # type: ignore

from config import COOKIES_DIR

logger = logging.getLogger(__name__)

load_dotenv()

class RedisCookieManager:
    """Manage cookie files with optional Upstash Redis storage."""

    def __init__(self) -> None:
        url   = os.getenv("UPSTASH_REDIS_URL")
        token = os.getenv("UPSTASH_REDIS_TOKEN")

        if url and token and Redis:
            self.redis = Redis(url=url, token=token)
        else:
            logger.warning(
                "UPSTASH_REDIS_URL or UPSTASH_REDIS_TOKEN environment variables not found. "
                "Cookie persistence will be disabled."
            )
            self.redis = None
            
        self.cache: Dict[str, str] = {}

    def _safe_id(self, auth_id: str) -> str:
        safe = "".join(c for c in auth_id if c.isalnum() or c in ("_", "-"))
        return safe.lower() or "anonymous"

    def _key(self, auth_id: str) -> str:
        return f"cookie:{self._safe_id(auth_id)}.json"

    def get_cookie_path(self, auth_id: str) -> Path:
        return COOKIES_DIR / f"{self._safe_id(auth_id)}.json"

    def load_cookie(self, auth_id: str) -> Path:
        """Ensure cookie file exists locally, fetching from Redis if needed."""
        path = self.get_cookie_path(auth_id)
        if path.exists():
            try:
                content = path.read_text()
                self.cache[self._key(auth_id)] = content
            except Exception as e:  # pragma: no cover - logging only
                logger.warning(f"Failed reading cookie file {path}: {e}")
            return path

        if not self.redis:
            return path

        try:
            data = self.redis.get(self._key(auth_id))
        except Exception as e:
            logger.warning(f"Redis get failed: {e}")
            return path

        if data:
            try:
                path.write_text(str(data))
                self.cache[self._key(auth_id)] = str(data)
            except Exception as e:
                logger.warning(f"Failed writing cookie file {path}: {e}")
        return path

    def save_cookie(self, auth_id: str) -> None:
        """Upload cookie file to Redis if changed."""
        if not self.redis:
            return

        path = self.get_cookie_path(auth_id)
        if not path.exists():
            return

        try:
            content = path.read_text()
        except Exception as e:
            logger.warning(f"Failed reading cookie file {path}: {e}")
            return

        key = self._key(auth_id)
        if self.cache.get(key) == content:
            return

        try:
            self.redis.set(key, content)
            self.cache[key] = content
        except Exception as e:
            logger.warning(f"Redis set failed: {e}")
