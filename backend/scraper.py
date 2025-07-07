import asyncio
import logging
import random
from typing import List, Optional, Callable

from twikit import Client

from config import TwitterConfig, RateLimitConfig, SearchParameters
from rate_limiter import RateLimitHandler
from data_utils import FileManager
from query_builder import QueryBuilder
from cookie_manager import RedisCookieManager

logger = logging.getLogger(__name__)


class TwitterScraper:
    """Professional Twitter scraper with comprehensive functionality."""
    
    def __init__(self, config: TwitterConfig, rate_limit_config: RateLimitConfig = None,
                 cookie_manager: RedisCookieManager | None = None):
        self.config = config
        self.cookie_manager = cookie_manager or RedisCookieManager()

        # Ensure cookie path exists locally (may fetch from Redis)
        cookie_path = self.cookie_manager.load_cookie(self.config.credentials.auth_id)
        self.config.credentials.cookies_file = str(cookie_path)

        self.client = Client('en-US')
        self.file_manager = FileManager(config.output_dir)
        self.query_builder = QueryBuilder()
        self.rate_limiter = RateLimitHandler(
            rate_limit_config,
            reauth_callback=self.authenticate,)
    
    async def authenticate(self) -> None:
        """Authenticate with Twitter using provided credentials."""
        try:
            await self.rate_limiter.execute_with_rate_limit(
                self.client.login,
                auth_info_1=self.config.credentials.auth_id,
                password=self.config.credentials.password,
                cookies_file=self.config.credentials.cookies_file,
            )
            logger.info("Successfully authenticated with Twitter")

            # Persist updated cookies to Redis
            self.cookie_manager.save_cookie(self.config.credentials.auth_id)
            
            await self._human_delay(long=False)
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise

    async def _human_delay(self, long: bool = False) -> None:
        """
        Delay แบบสมจริง
        • long=True  → พักใหญ่ (expovariate λ≈1/40  →  mean≈40 s, cap 120 s)
        • long=False → พักสั้น (log-normal μ=0.8, σ=0.6  →  ~1-10 s)
        นอกจากนี้ทุก ๆ 3-5 batch จะ inject “typing-pause” 0.2-1 s
        """
        if long:
            delay = min(random.expovariate(1/40), 120)
        else:
            delay = min(random.lognormvariate(0.8, 0.6), 10)
        await asyncio.sleep(delay)

        # ⌨️  typing-pause  (25-33 % chance)
        if random.randint(0, 2) == 0:
            await asyncio.sleep(random.uniform(0.2, 1.0))
    
    async def get_user_by_screen_name(self, screen_name: str):
        """Get user object by screen name."""
        try:
            user = await self.client.get_user_by_screen_name(screen_name)
            logger.info(f"Retrieved user: {user.screen_name} (ID: {user.id})")
            return user
        except Exception as e:
            logger.error(f"Failed to get user {screen_name}: {e}")
            raise
    
    async def fetch_user_timeline(self, user_id: str, count: int = 100, 
                                 progress_callback: Optional[Callable] = None) -> List:
        """Fetch tweets from user's timeline with pagination support."""
        all_tweets = []
        cursor = None
        batch_num = 0
        
        try:
            while len(all_tweets) < count:
                remaining = count - len(all_tweets)
                batch_size = min(20, remaining)
                
                tweets = await self.rate_limiter.execute_with_rate_limit(
                    self._fetch_timeline_batch, user_id, batch_size, cursor
                )
                
                if not tweets:
                    logger.info("No more tweets available")
                    break
                
                all_tweets.extend(tweets)
                progress = len(all_tweets) / count
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(progress, len(all_tweets), count, tweets)
                
                logger.info(f"Fetched {len(tweets)} tweets (Total: {len(all_tweets)})")
                
                cursor = self._get_next_cursor(tweets, batch_size)
                if not cursor:
                    break

                batch_num += 1
                await self._human_delay(long=(batch_num % 10 == 0))
                
            
            logger.info(f"Total timeline tweets fetched: {len(all_tweets)}")
            return all_tweets[:count]
            
        except Exception as e:
            logger.error(f"Failed to fetch timeline tweets: {e}")
            if all_tweets:
                logger.info(f"Returning {len(all_tweets)} tweets collected before error")
                return all_tweets
            raise
    
    async def search_tweets(self, search_params: SearchParameters, 
                           progress_callback: Optional[Callable] = None) -> List:
        """Search tweets based on provided parameters."""
        search_query = self.query_builder.build_search_query(search_params)
        search_type = self.query_builder.get_search_type(search_params)
        
        logger.info(f"Search query: {search_query}")
        logger.info(f"Search type: {search_type.value}")
        logger.info(f"Search mode: {search_params.mode.value}")
        
        all_tweets = []
        cursor = None
        batch_num = 0
        
        try:
            while len(all_tweets) < search_params.count:
                remaining = search_params.count - len(all_tweets)
                batch_size = min(20, remaining)
                
                results = await self.rate_limiter.execute_with_rate_limit(
                    self._fetch_search_batch, search_query, search_type, batch_size, cursor
                )
                
                if not results:
                    logger.info("No more search results available")
                    break
                
                all_tweets.extend(results)
                progress = len(all_tweets) / search_params.count
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(progress, len(all_tweets), search_params.count, results)
                
                logger.info(f"Found {len(results)} tweets (Total: {len(all_tweets)})")
                
                cursor = self._get_next_cursor(results, batch_size)
                if not cursor:
                    break

                batch_num += 1
                await self._human_delay(long=(batch_num % 10 == 0))
            
            logger.info(f"Total search tweets found: {len(all_tweets)} for query: {search_query}")
            return all_tweets[:search_params.count]
            
        except Exception as e:
            logger.error(f"Failed to search tweets for '{search_query}': {e}")
            if all_tweets:
                logger.info(f"Returning {len(all_tweets)} tweets collected before error")
                return all_tweets
            raise
    
    async def _fetch_timeline_batch(self, user_id: str, count: int, cursor: str = None):
        """Fetch a batch of timeline tweets."""
        if cursor:
            return await self.client.get_user_tweets(
                user_id, 'Tweets', count=count, cursor=cursor
            )
        else:
            return await self.client.get_user_tweets(
                user_id, 'Tweets', count=count
            )
    
    async def _fetch_search_batch(self, query: str, search_type, 
                                count: int, cursor: str = None):
        """Fetch a batch of search results."""
        if cursor:
            return await self.client.search_tweet(
                query, search_type.value, count=count, cursor=cursor
            )
        else:
            return await self.client.search_tweet(
                query, search_type.value, count=count
            )
    
    def _get_next_cursor(self, tweets: List, batch_size: int) -> Optional[str]:
        """Extract cursor for pagination."""
        if hasattr(tweets, 'next_cursor') and tweets.next_cursor:
            return tweets.next_cursor
        elif len(tweets) < batch_size:
            return None
        else:
            return getattr(tweets[-1], 'cursor', None)
    
    async def export_to_csv(self, tweets: List, filename: str = None, 
                           prefix: str = "tweets") -> Optional[str]:
        """Export tweets to CSV file."""
        return await self.file_manager.export_to_csv(tweets, filename, prefix)