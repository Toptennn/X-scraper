"""
User interface and display utilities for Twitter scraper.

Provides methods for displaying tweets and completion summaries.
"""

from pathlib import Path
from typing import List

from config import TwitterConfig


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