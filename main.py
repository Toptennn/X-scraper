"""
Twitter/X Data Scraper

A professional, enterprise-grade Twitter scraping tool using twikit library.
Supports fetching user timelines and searching tweets with advanced filtering options.

Author: GitHub Copilot
Version: 2.0.0
"""

import asyncio
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Callable
import time
import random

import pandas as pd
from twikit import Client
from twikit.errors import TooManyRequests, Unauthorized, BadRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting behavior."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 300.0  # 5 minutes max
    backoff_multiplier: float = 2.0
    jitter: bool = True
    respect_reset_time: bool = True


class RateLimitHandler:
    """Advanced rate limit handling with exponential backoff and jitter."""
    
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self.request_times = []
        self.last_rate_limit_reset = None
    
    async def execute_with_rate_limit(self, func: Callable, *args, **kwargs):
        """Execute a function with advanced rate limit handling."""
        retries = 0
        
        while retries <= self.config.max_retries:
            try:
                # Add pre-emptive delay if we've been rate limited recently
                await self._preemptive_delay()
                
                result = await func(*args, **kwargs)
                
                # Track successful request
                self._track_request()
                
                return result
                
            except TooManyRequests as e:
                retries += 1
                
                if retries > self.config.max_retries:
                    logger.error(f"Max retries ({self.config.max_retries}) exceeded for rate limiting")
                    raise
                
                wait_time = await self._calculate_wait_time(e, retries)
                logger.warning(f"Rate limited. Waiting {wait_time:.2f} seconds (attempt {retries}/{self.config.max_retries})")
                
                await asyncio.sleep(wait_time)
                
            except (Unauthorized, BadRequest) as e:
                logger.error(f"Non-recoverable error: {e}")
                raise
                
            except Exception as e:
                retries += 1
                if retries > self.config.max_retries:
                    logger.error(f"Max retries exceeded for error: {e}")
                    raise
                
                wait_time = self._exponential_backoff(retries)
                logger.warning(f"Unexpected error: {e}. Retrying in {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
        
        raise Exception(f"Failed after {self.config.max_retries} retries")
    
    async def _calculate_wait_time(self, exception: TooManyRequests, retry_count: int) -> float:
        """Calculate optimal wait time based on rate limit information."""
        wait_time = self.config.base_delay
        
        # Use rate limit reset time if available and configured
        if self.config.respect_reset_time and hasattr(exception, 'rate_limit_reset'):
            try:
                reset_time = datetime.fromtimestamp(exception.rate_limit_reset)
                time_until_reset = (reset_time - datetime.now()).total_seconds()
                
                if time_until_reset > 0:
                    wait_time = min(time_until_reset + 5, self.config.max_delay)  # Add 5s buffer
                    self.last_rate_limit_reset = reset_time
                    logger.info(f"Using rate limit reset time: {reset_time}")
            except (ValueError, TypeError, AttributeError) as e:
                logger.warning(f"Could not parse rate limit reset time: {e}")
        
        # Fall back to exponential backoff if reset time not available
        if wait_time == self.config.base_delay:
            wait_time = self._exponential_backoff(retry_count)
        
        return wait_time
    
    def _exponential_backoff(self, retry_count: int) -> float:
        """Calculate exponential backoff with jitter."""
        delay = self.config.base_delay * (self.config.backoff_multiplier ** (retry_count - 1))
        delay = min(delay, self.config.max_delay)
        
        # Add jitter to avoid thundering herd
        if self.config.jitter:
            jitter = delay * 0.1 * random.random()  # Up to 10% jitter
            delay += jitter
        
        return delay
    
    async def _preemptive_delay(self):
        """Add delay if we've been making requests too frequently."""
        current_time = time.time()
        
        # Remove old request times (older than 15 minutes)
        cutoff_time = current_time - 900  # 15 minutes
        self.request_times = [t for t in self.request_times if t > cutoff_time]
        
        # If we have more than 100 requests in the last 15 minutes, add delay
        if len(self.request_times) > 100:
            delay = min(5.0, len(self.request_times) * 0.1)
            logger.info(f"Preemptive rate limiting: waiting {delay:.2f} seconds")
            await asyncio.sleep(delay)
    
    def _track_request(self):
        """Track successful request timing."""
        self.request_times.append(time.time())


class SearchType(Enum):
    """Enumeration for tweet search types."""
    TOP = "Top"
    LATEST = "Latest"


class SearchMode(Enum):
    """Enumeration for search modes."""
    DATE_RANGE = "date_range"
    POPULAR = "popular"
    LATEST = "latest"


@dataclass
class TwitterCredentials:
    """Twitter authentication credentials."""
    auth_id: str
    password: str
    cookies_file: str = 'cookies.json'


@dataclass
class SearchParameters:
    """Parameters for tweet search operations."""
    query: str
    count: int = 100
    mode: SearchMode = SearchMode.POPULAR
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
    def __post_init__(self):
        """Validate search parameters."""
        if self.mode == SearchMode.DATE_RANGE and (not self.start_date or not self.end_date):
            raise ValueError("Date range search requires both start_date and end_date")


@dataclass
class TwitterConfig:
    """Configuration class for Twitter scraping operations."""
    credentials: TwitterCredentials
    screen_name: str = 'Jingggxd'
    output_dir: str = 'output'
    search_params: SearchParameters = field(default_factory=lambda: SearchParameters('#Python'))
    
    @classmethod
    def create_default(cls) -> 'TwitterConfig':
        """Create default configuration."""
        credentials = TwitterCredentials(
            auth_id='USERNAME',
            password='***REMOVED***'
        )
        return cls(credentials=credentials)


class TweetDataExtractor:
    """Utility class for extracting and processing tweet data."""
    
    @staticmethod
    def extract_tweet_data(tweets: List) -> List[Dict[str, Any]]:
        """Extract relevant data from tweet objects."""
        tweet_data = []
        for tweet in tweets:
            try:
                data = {
                    'created_at': tweet.created_at,
                    'username': tweet.user.screen_name,
                    'user_id': tweet.user.id,
                    'tweet_id': tweet.id,
                    'text': TweetDataExtractor._clean_text(tweet.text),
                    'retweet_count': getattr(tweet, 'retweet_count', 0),
                    'favorite_count': getattr(tweet, 'favorite_count', 0),
                    'reply_count': getattr(tweet, 'reply_count', 0),
                    'lang': getattr(tweet, 'lang', 'unknown'),
                    'url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
                }
                tweet_data.append(data)
            except Exception as e:
                logger.warning(f"Failed to extract data from tweet: {e}")
                continue
        
        return tweet_data
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean tweet text for CSV export."""
        if not text:
            return ""
        return text.replace('\n', ' ').replace('\r', ' ').strip()


class FileManager:
    """Handles file operations and data export."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self._ensure_output_directory()
    
    def _ensure_output_directory(self) -> None:
        """Create output directory if it doesn't exist."""
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_filename(self, prefix: str, suffix: str = "") -> str:
        """Generate timestamped filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = f"_{suffix}" if suffix else ""
        return f"{prefix}{suffix}_{timestamp}.csv"
    
    async def export_to_csv(self, tweets: List, filename: str = None, 
                           prefix: str = "tweets") -> Optional[str]:
        """Export tweets to CSV file."""
        if not tweets:
            logger.warning("No tweets to export")
            return None
        
        try:
            tweet_data = TweetDataExtractor.extract_tweet_data(tweets)
            
            if not filename:
                filename = self.generate_filename(prefix)
            
            filepath = self.output_dir / filename
            
            df = pd.DataFrame(tweet_data)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            logger.info(f"Exported {len(tweet_data)} tweets to: {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Failed to export tweets to CSV: {e}")
            raise


class QueryBuilder:
    """Builds search queries based on parameters."""
    
    @staticmethod
    def build_search_query(params: SearchParameters) -> str:
        """Build search query based on search parameters."""
        query = params.query
        
        if params.mode == SearchMode.DATE_RANGE:
            if params.start_date:
                query += f" since:{params.start_date}"
            if params.end_date:
                query += f" until:{params.end_date}"
        
        return query
    
    @staticmethod
    def get_search_type(params: SearchParameters) -> SearchType:
        """Get search type based on search mode."""
        if params.mode == SearchMode.LATEST:
            return SearchType.LATEST
        else:  # Both DATE_RANGE and POPULAR use TOP
            return SearchType.TOP


class TwitterScraper:
    """Professional Twitter scraper with comprehensive functionality."""
    
    def __init__(self, config: TwitterConfig, rate_limit_config: RateLimitConfig = None):
        self.config = config
        self.client = Client('en-US')
        self.file_manager = FileManager(config.output_dir)
        self.query_builder = QueryBuilder()
        self.rate_limiter = RateLimitHandler(rate_limit_config)
    
    async def authenticate(self) -> None:
        """Authenticate with Twitter using provided credentials."""
        try:
            await self.client.login(
                auth_info_1=self.config.credentials.auth_id,
                password=self.config.credentials.password,
                cookies_file=self.config.credentials.cookies_file
            )
            logger.info("Successfully authenticated with Twitter")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    async def get_user_by_screen_name(self, screen_name: str):
        """Get user object by screen name."""
        try:
            user = await self.client.get_user_by_screen_name(screen_name)
            logger.info(f"Retrieved user: {user.screen_name} (ID: {user.id})")
            return user
        except Exception as e:
            logger.error(f"Failed to get user {screen_name}: {e}")
            raise
    
    async def fetch_user_timeline(self, user_id: str, count: int = 100) -> List:
        """Fetch tweets from user's timeline with pagination support."""
        all_tweets = []
        cursor = None
        
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
                logger.info(f"Fetched {len(tweets)} tweets (Total: {len(all_tweets)})")
                
                cursor = self._get_next_cursor(tweets, batch_size)
                if not cursor:
                    break

                delay = random.uniform(1.5, 3.5)
                logger.info(f"Sleeping for {delay:.2f} seconds to mimic human behavior.")
                await asyncio.sleep(delay)
                
            
            logger.info(f"Total timeline tweets fetched: {len(all_tweets)}")
            return all_tweets[:count]
            
        except Exception as e:
            logger.error(f"Failed to fetch timeline tweets: {e}")
            if all_tweets:
                logger.info(f"Returning {len(all_tweets)} tweets collected before error")
                return all_tweets
            raise
    
    async def search_tweets(self, search_params: SearchParameters) -> List:
        """Search tweets based on provided parameters."""
        search_query = self.query_builder.build_search_query(search_params)
        search_type = self.query_builder.get_search_type(search_params)
        
        logger.info(f"Search query: {search_query}")
        logger.info(f"Search type: {search_type.value}")
        logger.info(f"Search mode: {search_params.mode.value}")
        
        all_tweets = []
        cursor = None
        
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
                logger.info(f"Found {len(results)} tweets (Total: {len(all_tweets)})")
                
                cursor = self._get_next_cursor(results, batch_size)
                if not cursor:
                    break

                delay = random.uniform(1.5, 3.5)
                logger.info(f"Sleeping for {delay:.2f} seconds to mimic human behavior.")
                await asyncio.sleep(delay) 
            
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
    
    async def _fetch_search_batch(self, query: str, search_type: SearchType, 
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


class TwitterScraperUI:
    """User interface and display utilities for Twitter scraper."""
    
    @staticmethod
    def print_tweets_summary(tweets: List, title: str) -> None:
        """Print a summary of tweets to console."""
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")
        
        if not tweets:
            print("No tweets found.")
            return
        
        for i, tweet in enumerate(tweets[:5], 1):
            print(f"{i}. [{tweet.created_at}] @{tweet.user.screen_name}")
            print(f"   {tweet.text[:100]}{'...' if len(tweet.text) > 100 else ''}")
            print(f"   ❤️{getattr(tweet, 'favorite_count', 0)} "
                  f"🔄{getattr(tweet, 'retweet_count', 0)} "
                  f"💬{getattr(tweet, 'reply_count', 0)}")
            print()
        
        if len(tweets) > 5:
            print(f"... and {len(tweets) - 5} more tweets")
    
    @staticmethod
    def print_completion_summary(config: TwitterConfig, timeline_file: str, 
                               search_files: List[str]) -> None:
        """Print completion summary."""
        print(f"\n{'='*60}")
        print("EXPORT COMPLETED")
        print(f"{'='*60}")
        print(f"\n✅ Scraping completed successfully!")
        print(f"📁 Files saved in: {config.output_dir}/")
        
        if timeline_file:
            print(f"📊 Timeline tweets: {Path(timeline_file).name}")
        
        for search_file in search_files:
            if search_file:
                print(f"🔍 Search tweets: {Path(search_file).name}")


async def main():
    """Main execution function demonstrating all search modes."""
    config = TwitterConfig.create_default()
    scraper = TwitterScraper(config)
    ui = TwitterScraperUI()
    
    try:
        # Authenticate
        await scraper.authenticate()
        
        # Get user information
        user = await scraper.get_user_by_screen_name(config.screen_name)
        
        # Fetch timeline tweets
        logger.info("Fetching user timeline...")
        timeline_tweets = await scraper.fetch_user_timeline(user.id, count=20)
        ui.print_tweets_summary(timeline_tweets, f"Timeline: @{config.screen_name}")
        
        # Search examples for all three modes
        search_results = []
        
        # 1. Search by date range (uses 'Top')
        date_range_params = SearchParameters(
            query="#Python",
            count=50,
            mode=SearchMode.DATE_RANGE,
            start_date="2024-01-01",
            end_date="2024-01-02"
        )
        logger.info("Searching tweets by date range...")
        date_range_tweets = await scraper.search_tweets(date_range_params)
        ui.print_tweets_summary(date_range_tweets, "Date Range Search: #Python (2024)")
        search_results.append(('date_range_Python', date_range_tweets))
        
        # 2. Search for popular tweets (uses 'Top')
        popular_params = SearchParameters(
            query="#AI",
            count=50,
            mode=SearchMode.POPULAR
        )
        logger.info("Searching popular tweets...")
        popular_tweets = await scraper.search_tweets(popular_params)
        ui.print_tweets_summary(popular_tweets, "Popular Search: #AI")
        search_results.append(('popular_AI', popular_tweets))
        
        # 3. Search for latest tweets (uses 'Latest')
        latest_params = SearchParameters(
            query="#MachineLearning",
            count=1000,
            mode=SearchMode.LATEST
        )
        logger.info("Searching latest tweets...")
        latest_tweets = await scraper.search_tweets(latest_params)
        ui.print_tweets_summary(latest_tweets, "Latest Search: #MachineLearning")
        search_results.append(('latest_MachineLearning', latest_tweets))
        
        # Export to CSV
        print(f"\n{'='*60}")
        print("EXPORTING DATA")
        print(f"{'='*60}")
        
        timeline_file = await scraper.export_to_csv(
            timeline_tweets, 
            prefix=f"timeline_{config.screen_name}"
        )
        
        search_files = []
        for prefix, tweets in search_results:
            search_file = await scraper.export_to_csv(tweets, prefix=prefix)
            search_files.append(search_file)
        
        ui.print_completion_summary(config, timeline_file, search_files)
            
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    exit(exit_code)