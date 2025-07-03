import logging
from pathlib import Path
from typing import Dict, Optional
import os

from upstash_redis import Redis

ROOT = Path(__file__).resolve().parents[1].parent
COOKIES_DIR = ROOT / "cookies"
COOKIES_DIR.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)

class RedisCookieManager:
    """Manage cookie files stored locally and in Upstash Redis."""

    def __init__(self) -> None:
        url = os.getenv("UPSTASH_REDIS_URL", "")
        token = os.getenv("UPSTASH_REDIS_TOKEN", "")
        if url and token:
            self.redis: Optional[Redis] = Redis(url=url, token=token)
        else:
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
        path = self.get_cookie_path(auth_id)
        if path.exists():
            try:
                self.cache[self._key(auth_id)] = path.read_text()
            except Exception as exc:  # pragma: no cover - log only
                logger.warning("failed reading %s: %s", path, exc)
            return path
        if not self.redis:
            return path
        try:
            data = self.redis.get(self._key(auth_id))
        except Exception as exc:  # pragma: no cover - log only
            logger.warning("redis get failed: %s", exc)
            return path
        if data:
            try:
                path.write_text(str(data))
                self.cache[self._key(auth_id)] = str(data)
            except Exception as exc:  # pragma: no cover - log only
                logger.warning("failed writing %s: %s", path, exc)
        return path

    def save_cookie(self, auth_id: str) -> None:
        if not self.redis:
            return
        path = self.get_cookie_path(auth_id)
        if not path.exists():
            return
        try:
            content = path.read_text()
        except Exception as exc:  # pragma: no cover - log only
            logger.warning("failed reading %s: %s", path, exc)
            return
        key = self._key(auth_id)
        if self.cache.get(key) == content:
            return
        try:
            self.redis.set(key, content)
            self.cache[key] = content
        except Exception as exc:  # pragma: no cover - log only
            logger.warning("redis set failed: %s", exc)
