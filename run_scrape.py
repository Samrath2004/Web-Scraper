# run_scrape.py
import asyncio
import argparse
from src.scraper.fetcher import run_for_projects

def main():
    parser = argparse.ArgumentParser(description="Scrape Apache Jira projects to JSONL.")
    parser.add_argument("--projects", nargs="+", required=True, help="Project keys, e.g. HADOOP SPARK KAFKA")
    parser.add_argument("--max-results", type=int, default=50, help="page size per request (maxResults)")
    parser.add_argument("--concurrency", type=int, default=5, help="concurrent HTTP requests")
    parser.add_argument("--output-dir", default="output", help="where to store JSONL files")
    parser.add_argument("--checkpoint-file", default="checkpoint.json", help="checkpoint path")
    args = parser.parse_args()
    asyncio.run(run_for_projects(
        projects=args.projects,
        max_results=args.max_results,
        concurrency=args.concurrency,
        output_dir=args.output_dir,
        checkpoint_file=args.checkpoint_file
    ))

if __name__ == "__main__":
    main()
