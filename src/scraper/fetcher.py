# src/scraper/fetcher.py
import os
import asyncio
import aiohttp
from typing import List
from src.scraper.jira_client import JiraClient, RateLimitError
from src.scraper.checkpoint import load_checkpoint, save_checkpoint
from src.transform.transform import convert_issue_raw_to_record, write_jsonl_line
from src.utils.retry_helpers import retry_decorator

async def fetch_project(project_key: str, client: JiraClient, max_results: int, output_dir: str, checkpoint: dict, checkpoint_file: str):
    jql = f'project = {project_key} ORDER BY created ASC'
    start_at = checkpoint.get(project_key, {}).get("last_startAt", 0)
    done = checkpoint.get(project_key, {}).get("completed", False)
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{project_key}.jsonl")
    fh = open(out_path, "a", encoding="utf-8")
    try:
        while True:
            # use decorated call which retries on errors
            @retry_decorator()
            async def get_page():
                return await client.search_issues(jql=jql, start_at=start_at, max_results=max_results)
            try:
                page = await get_page()
            except RateLimitError as e:
                # Will be retried by decorator; should not get here, but in case:
                ra = e.retry_after or 60
                await asyncio.sleep(ra)
                continue

            issues = page.get("issues", [])
            total = page.get("total", 0)
            if not issues:
                # nothing in this page; finish
                checkpoint.setdefault(project_key, {})["completed"] = True
                checkpoint[project_key]["last_startAt"] = start_at
                save_checkpoint(checkpoint_file, checkpoint)
                break

            for issue in issues:
                record = convert_issue_raw_to_record(issue)
                write_jsonl_line(fh, record)

            start_at += max_results
            checkpoint.setdefault(project_key, {})["last_startAt"] = start_at
            checkpoint.setdefault(project_key, {})["completed"] = (start_at >= total)
            save_checkpoint(checkpoint_file, checkpoint)
            if checkpoint[project_key]["completed"]:
                break
    finally:
        fh.close()

async def run_for_projects(projects: List[str], max_results: int = 50, concurrency: int = 5, output_dir: str = "output", checkpoint_file: str = "checkpoint.json"):
    checkpoint = load_checkpoint(checkpoint_file)
    timeout = aiohttp.ClientTimeout(total=120)
    sem = asyncio.Semaphore(concurrency)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        client = JiraClient(session=session, semaphore=sem)
        tasks = []
        for p in projects:
            tasks.append(fetch_project(p, client, max_results, output_dir, checkpoint, checkpoint_file))
        # run them sequentially or concurrently depending on concurrency; for safety run sequentially to avoid burst
        # But we will run them concurrently with gather to speed up (safe because semaphore limits)
        await asyncio.gather(*tasks)
