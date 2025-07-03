import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable

from .redis_cookie_manager import RedisCookieManager

from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from config import TwitterCredentials, TwitterConfig, SearchParameters, SearchMode
from scraper import TwitterScraper

@dataclass
class TaskState:
    progress: float = 0.0
    collected: int = 0
    total: int = 0
    result: Optional[List[Dict[str, Any]]] = None
    done: bool = False


TASKS: Dict[str, TaskState] = {}


def _progress_cb(task_id: str) -> Callable[[float, int, int, Any], None]:
    def inner(progress: float, current: int, total: int, _batch: Any = None) -> None:
        state = TASKS.get(task_id)
        if state:
            state.progress = progress
            state.collected = current
            state.total = total
    return inner

def start_scrape_task(params: Dict[str, Any]) -> str:
    task_id = uuid.uuid4().hex
    state = TaskState(total=params.get("count", 50))
    TASKS[task_id] = state
    asyncio.create_task(_run_task(task_id, params))
    return task_id


async def _run_task(task_id: str, params: Dict[str, Any]) -> None:
    try:
        cookie_manager = RedisCookieManager()
        creds = TwitterCredentials(
            auth_id=params["auth"],
            password=params["password"],
            cookies_file=str(cookie_manager.load_cookie(params["auth"]))
        )
        config = TwitterConfig(credentials=creds)
        scraper = TwitterScraper(config, cookie_manager=cookie_manager)
        await scraper.authenticate()
        cb = _progress_cb(task_id)
        mode = params["mode"]
        if mode == "timeline":
            user = await scraper.get_user_by_screen_name(params["screen_name"])
            tweets = await scraper.fetch_user_timeline(
                user.id,
                count=params.get("count", 50),
                progress_callback=cb,
            )
        else:
            search_params = SearchParameters(
                query=params["query"],
                count=params.get("count", 50),
                mode=SearchMode[params["mode"].upper()],
                start_date=params.get("start_date"),
                end_date=params.get("end_date"),
            )
            tweets = await scraper.search_tweets(search_params, progress_callback=cb)
        from data_utils import TweetDataExtractor
        TASKS[task_id].result = TweetDataExtractor.extract_tweet_data(tweets)
        cookie_manager.save_cookie(params["auth"])
    except Exception as exc:  # pragma: no cover - log only
        TASKS[task_id].result = {"error": str(exc)}
    finally:
        TASKS[task_id].done = True
        TASKS[task_id].progress = 1.0
