import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import pandas as pd

logger = logging.getLogger(__name__)


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