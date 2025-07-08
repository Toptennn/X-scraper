from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware


from config import TwitterConfig, TwitterCredentials, SearchParameters, SearchMode
from scraper import TwitterScraper
from cookie_manager import RedisCookieManager
from data_utils import TweetDataExtractor

app = FastAPI(title="X Scraper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


async def create_scraper(auth_id: str, password: str) -> TwitterScraper:
    """Initialize scraper with credentials and authenticate."""
    cookie_manager = RedisCookieManager()
    cookie_path = cookie_manager.load_cookie(auth_id)
    credentials = TwitterCredentials(
        auth_id=auth_id,
        password=password,
        cookies_file=str(cookie_path)
    )
    config = TwitterConfig(credentials=credentials, output_dir="output")
    scraper = TwitterScraper(config, cookie_manager=cookie_manager)
    await scraper.authenticate()
    return scraper


class TimelineRequest(BaseModel):
    auth_id: str
    password: str
    screen_name: str
    count: int = 50


class SearchRequest(BaseModel):
    auth_id: str
    password: str
    query: str
    count: int = 50
    mode: SearchMode = SearchMode.POPULAR
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@app.post("/timeline")
async def scrape_timeline(req: TimelineRequest):
    """Fetch tweets from a user's timeline."""
    scraper = await create_scraper(req.auth_id, req.password)
    user = await scraper.get_user_by_screen_name(req.screen_name)
    tweets = await scraper.fetch_user_timeline(user.id, count=req.count)
    return TweetDataExtractor.extract_tweet_data(tweets)


@app.post("/search")
async def search_tweets(req: SearchRequest):
    """Search tweets based on query parameters."""
    scraper = await create_scraper(req.auth_id, req.password)
    params = SearchParameters(
        query=req.query,
        count=req.count,
        mode=req.mode,
        start_date=req.start_date,
        end_date=req.end_date,
    )
    tweets = await scraper.search_tweets(params)
    return TweetDataExtractor.extract_tweet_data(tweets)
