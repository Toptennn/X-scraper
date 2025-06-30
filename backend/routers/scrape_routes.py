import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, auth
from ..database import get_db
from ..auth import get_current_user

from config import TwitterCredentials, TwitterConfig, SearchParameters, SearchMode
from scraper import TwitterScraper
from data_utils import TweetDataExtractor

router = APIRouter(prefix="/scrape", tags=["scrape"])


@router.post("/tweets", response_model=schemas.ScrapeResponse)
async def scrape_tweets(request: schemas.ScrapeRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    credentials = TwitterCredentials(
        auth_id=request.x_auth_id,
        password=request.x_password,
        cookies_file=f"cookies/{request.x_auth_id}.json"
    )
    config = TwitterConfig(credentials=credentials)
    scraper = TwitterScraper(config)

    try:
        await scraper.authenticate()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if request.mode == "timeline":
        if not request.screen_name:
            raise HTTPException(status_code=400, detail="screen_name required")
        tweets = await scraper.fetch_user_timeline(request.screen_name, count=request.count)
    else:
        if not request.query:
            raise HTTPException(status_code=400, detail="query required")
        mode_map = {
            "date_range": SearchMode.DATE_RANGE,
            "popular": SearchMode.POPULAR,
            "latest": SearchMode.LATEST,
        }
        search_params = SearchParameters(
            query=request.query,
            count=request.count,
            mode=mode_map[request.mode],
            start_date=request.start_date,
            end_date=request.end_date,
        )
        tweets = await scraper.search_tweets(search_params)

    data = TweetDataExtractor.extract_tweet_data(tweets)
    return {"tweets": data}
