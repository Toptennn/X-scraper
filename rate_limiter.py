import asyncio
import logging
import time
import random
from datetime import datetime
from typing import Callable

from twikit.errors import TooManyRequests, Unauthorized, BadRequest
from config import RateLimitConfig

logger = logging.getLogger(__name__)


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
            if retry_count >= 2:
                long_pause = random.uniform(20, 60)
                wait_time += long_pause
                logger.warning(f"Adding long pause {long_pause:.2f} sec due to repeated rate limits.")
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
            delay = min(5.0, len(self.request_times) * 0.2)
            logger.info(f"Preemptive rate limiting: waiting {delay:.2f} seconds")
            await asyncio.sleep(delay)
    
    def _track_request(self):
        """Track successful request timing."""
        self.request_times.append(time.time())