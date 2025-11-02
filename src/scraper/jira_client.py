# src/scraper/jira_client.py
import aiohttp
import asyncio

JIRA_SEARCH = "https://issues.apache.org/jira/rest/api/2/search"
JIRA_ISSUE = "https://issues.apache.org/jira/rest/api/2/issue/{issue_key}"
DEFAULT_HEADERS = {"Accept": "application/json"}

class RateLimitError(Exception):
    def __init__(self, retry_after=None):
        self.retry_after = retry_after
        super().__init__("Rate limited")

class JiraClient:
    def __init__(self, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore):
        self.session = session
        self.sem = semaphore

    async def get(self, url, params=None):
        async with self.sem:
            async with self.session.get(url, params=params, headers=DEFAULT_HEADERS, timeout=60) as resp:
                if resp.status == 429:
                    ra = resp.headers.get("Retry-After")
                    raise RateLimitError(int(ra) if ra else None)
                resp.raise_for_status()
                return await resp.json()

    async def search_issues(self, jql: str, start_at: int = 0, max_results: int = 50, expand: str = "renderedFields,comments"):
        params = {"jql": jql, "startAt": start_at, "maxResults": max_results, "expand": expand}
        return await self.get(JIRA_SEARCH, params=params)

    async def fetch_issue(self, issue_key: str, expand: str = "renderedFields,comments"):
        url = JIRA_ISSUE.format(issue_key=issue_key)
        params = {"expand": expand}
        return await self.get(url, params=params)
