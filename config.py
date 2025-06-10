"""
Configuration classes for Twitter scraper.

Contains all configuration-related classes and enums.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


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
class RateLimitConfig:
    """Configuration for rate limiting behavior."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 300.0  # 5 minutes max
    backoff_multiplier: float = 2.0
    jitter: bool = True
    respect_reset_time: bool = True


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