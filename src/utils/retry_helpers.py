# src/utils/retry_helpers.py
import asyncio
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, RetryCallState
from src.scraper.jira_client import RateLimitError
import aiohttp

# Wait strategy: exponential backoff (1s, 2s, 4s, ...) up to attempts
def before_sleep(retry_state: RetryCallState):
    last = retry_state.outcome
    # optional: log here
    # print("Retrying after error:", retry_state.outcome.exception())

retry_on = (aiohttp.ClientError, RateLimitError, asyncio.TimeoutError)

def retry_decorator():
    return retry(
        retry=retry_if_exception_type(retry_on),
        wait=wait_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(8),
        reraise=True,
        before_sleep=before_sleep
    )
