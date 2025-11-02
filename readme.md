🧩 Overview

This project implements a data scraping and transformation pipeline that extracts public issue data from Apache’s Jira instance and converts it into a structured JSONL corpus suitable for training Large Language Models (LLMs).

The system is designed to be fault-tolerant, resumable, and efficient, handling real-world issues such as network timeouts, rate limits, and malformed data gracefully.

🎯 Objective

The scraper:

Fetches issues, comments, and metadata from three Apache Jira projects (HADOOP, SPARK, KAFKA).

Handles network errors, retries, and timeouts using exponential backoff.

Converts unstructured HTML issue descriptions into clean plain text.

Produces a JSONL dataset suitable for downstream machine learning / NLP tasks.

Supports resume functionality with checkpointing to recover from interruptions.

⚙️ Setup & Environment Configuration


1️⃣ Prerequisites

Python 3.10+

Internet connection (to access Apache Jira)

Optional: Git & GitHub CLI for repository management

2️⃣ Installation

Clone or download the project and install dependencies:

git clone https://github.com/<your-username>/web-scraper-jira.git
cd web-scraper-jira

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

3️⃣ Dependencies

Main libraries used:

Library	Purpose
aiohttp	Asynchronous HTTP requests
tenacity	Retry with exponential backoff
ujson	Fast JSON serialization
beautifulsoup4	HTML-to-text conversion
dateutil	Date parsing and normalization
tqdm	Progress tracking

🚀 Usage


Run the scraper

Example command:

python run_scrape.py --projects HADOOP SPARK KAFKA --max-results 50 --concurrency 5

Arguments
Argument	Description	Default
--projects	List of Apache Jira project keys	Required
--max-results	Results per page (Jira pagination)	50
--concurrency	Number of simultaneous API calls	5
--output-dir	Output directory for JSONL files	output
--checkpoint-file	Path to checkpoint JSON	checkpoint.json
Output

Each project will produce a JSONL file:

output/
 ├─ HADOOP.jsonl
 ├─ SPARK.jsonl
 └─ KAFKA.jsonl


Each line represents a single Jira issue in JSON format.

📁 Example Output (Sample)
{
  "id": "HADOOP-19",
  "project": "HADOOP",
  "title": "Datanode corruption",
  "status": "Closed",
  "priority": "Critical",
  "assignee": "Doug Cutting",
  "reporter": "Rod Taylor",
  "labels": [],
  "created_at": "2005-10-07T11:46:42+00:00",
  "updated_at": "2009-07-08T16:41:48+00:00",
  "description": "Our admins accidentally started a second Nutch datanode ...",
  "comments": [],
  "url": "https://issues.apache.org/jira/browse/HADOOP-19",
  "derived": {
    "summary": "Our admins accidentally started a second Nutch datanode ...",
    "classification_labels": ["bug"],
    "qna_pairs": [
      {
        "q": "What is the issue reported?",
        "a": "Our admins accidentally started a second Nutch datanode pointing to the same directories..."
      }
    ]
  }
}


🔹 Design Reasoning

Asynchronous I/O (aiohttp) — allows concurrent HTTP requests with controlled concurrency using asyncio.Semaphore.

Retry/backoff (tenacity) — ensures reliability against transient network and 429/5xx errors.

Checkpointing — prevents data loss during long runs or interruptions.

Streaming JSONL output — avoids memory overload; each issue is written immediately.

Modular structure — separate folders for scraper, transform, and utils for clarity and reusability.

⚠️ Edge Cases Handled

Edge Case	How It’s Handled
HTTP 429 (Rate Limit)	Raises RateLimitError and retries after Retry-After header or exponential delay
5xx Server Errors	Retries with exponential backoff up to 8 times
Timeouts / Connection Errors	Automatically retried by tenacity
Malformed or empty data	Skipped safely with fallback defaults; saved in bad_records/ for review
Interrupted execution	Resumes via checkpoint.json with last_startAt
Large HTML fields	Sanitized using BeautifulSoup (html.parser)
Missing optional fields	Uses None or empty lists instead of crashing
File access errors (Windows)	Retries replacing checkpoint file to handle OS locks
⚙️ Optimization Decisions
Optimization	Description
Async concurrency	Fetch multiple Jira pages simultaneously, limited by a semaphore
Retry + backoff	Exponential retry avoids server overload and ensures success on transient errors
Streaming writes	Writes JSONL lines incrementally (no full dataset in memory)
Checkpointing	Saves progress after each page, allowing resume without data loss
Heuristic derived fields	Generates summaries, classification labels, and QnA pairs automatically for LLM readiness
Bad record isolation	Logs invalid or malformed issues into separate directory for debugging
🧪 Testing

Run all tests:

pytest -q


Tests include:

test_transform.py → Validates HTML-to-text conversion and record transformation.

test_checkpoint.py → Ensures save/load consistency.

test_fetcher.py → Mocks HTTP responses for pagination and retry validation.

🔐 Reliability and Recovery

If the scraper stops midway (e.g., network failure, power loss), simply rerun:

python run_scrape.py --projects HADOOP SPARK KAFKA


It will automatically resume from the last saved checkpoint.

Each project maintains independent progress markers.

🚀 Potential Future Improvements

Area	Possible Enhancement

Derived fields	Integrate an LLM or summarizer for higher-quality summaries & QnA generation
Storage	Write directly to SQLite / Parquet for easier downstream analysis
Parallel pipelines	Use multiprocessing + async for very large-scale crawling
Rate limit awareness	Adaptive throttling based on Jira response times
Error analytics	Aggregate and visualize error types from logs
Dockerization	Package into a Docker container for reproducible runs
CI/CD Integration	Automate testing using GitHub Actions


📚 Example Run Summary

Metric	Value (Sample Run – Hadoop)
Total Issues Fetched	500+
Total Retries	4
Skipped (Malformed)	2
Total Runtime	~2 minutes
Output Size	2.4 MB
👨‍💻 Author

Samrath
Bachelor of Technology (CSE), Bennett University
📧 e22cseu0738@bennett.edu.in
