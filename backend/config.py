"""
Configuration classes and enums for the X/Twitter scraper.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from pathlib import Path


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SearchType(Enum):
    """Which tab to hit when searching tweets."""
    TOP = "Top"
    LATEST = "Latest"


class SearchMode(Enum):
    """High-level search modes exposed to the user."""
    DATE_RANGE = "date_range"
    POPULAR    = "popular"
    LATEST     = "latest"


# ---------------------------------------------------------------------------
# Low-level configs
# ---------------------------------------------------------------------------

@dataclass
class RateLimitConfig:
    """Back-off strategy when the scraper is rate-limited."""
    max_retries: int   = 3
    base_delay: float  = 1.0
    max_delay: float   = 300.0          # ≤ 5 min
    backoff_multiplier: float = 2.0
    jitter: bool       = True
    respect_reset_time: bool = True


@dataclass
class TwitterCredentials:
    """Login / cookie information."""
    auth_id: str
    password: str
    # Path to this user’s cookie file; None ➜ login each time
    cookies_file: Optional[str] = None


# ---------------------------------------------------------------------------
# User-facing params
# ---------------------------------------------------------------------------

@dataclass
class SearchParameters:
    """Parameters for a single tweet search."""
    query: str
    count: int                    = 100
    mode: SearchMode              = SearchMode.POPULAR
    start_date: Optional[str]     = None
    end_date: Optional[str]       = None

    def __post_init__(self):
        if self.mode is SearchMode.DATE_RANGE and (not self.start_date or not self.end_date):
            raise ValueError("Date-range search requires both start_date and end_date.")


# ---------------------------------------------------------------------------
# Top-level config that gets passed around
# ---------------------------------------------------------------------------

@dataclass
class TwitterConfig:
    credentials: TwitterCredentials
    output_dir: str                       = "output"
    search_params: Optional[SearchParameters] = None

    @classmethod
    def create_default(cls) -> "TwitterConfig":
        """Blank config stub – fill in credentials later."""
        return cls(
            credentials=TwitterCredentials(auth_id="", password="", cookies_file=None)
        )


# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

# Central place for every module to know where cookie files live
COOKIES_DIR = Path("cookies")
COOKIES_DIR.mkdir(exist_ok=True)
