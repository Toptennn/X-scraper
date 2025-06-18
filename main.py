#!/usr/bin/env python3
"""
Twitter/X Data Scraper

A professional, enterprise-grade Twitter scraping tool using twikit library.
Supports fetching user timelines and searching tweets with advanced filtering options.

Author: GitHub Copilot
Version: 2.0.0
"""

import asyncio
import logging
from pathlib import Path

from config import TwitterConfig, SearchParameters, SearchMode
from scraper import TwitterScraper
from ui_utils import TwitterScraperUI

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


async def main():
    """Main execution function demonstrating all search modes."""
    config = TwitterConfig.create_default()
    screen_name = input("Enter the Twitter screen name to scrape: ").strip()
    scraper = TwitterScraper(config)
    ui = TwitterScraperUI()
    
    try:
        # Authenticate
        await scraper.authenticate()
        
        # Get user information
        user = await scraper.get_user_by_screen_name(screen_name)
        
        # Fetch timeline tweets
        logger.info("Fetching user timeline...")
        timeline_tweets = await scraper.fetch_user_timeline(user.id, count=20)
        ui.print_tweets_summary(timeline_tweets, f"Timeline: @{screen_name}")
        
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
            prefix=f"timeline_{screen_name}"
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