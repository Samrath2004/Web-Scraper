# 🧩 Apache Jira Web Scraper

## 🧠 Overview

This project implements a **data scraping and transformation pipeline** that extracts public issue data from **Apache’s Jira instance** and converts it into a **structured JSONL corpus** suitable for training **Large Language Models (LLMs)**.

The system is designed to be **fault-tolerant, resumable, and efficient**, handling real-world issues such as network timeouts, rate limits, and malformed data gracefully.

---

## 🎯 Objective

The scraper:

- Fetches issues, comments, and metadata from three Apache Jira projects (`HADOOP`, `SPARK`, `KAFKA`).
- Handles network errors, retries, and timeouts using **exponential backoff**.
- Converts unstructured HTML issue descriptions into **clean plain text**.
- Produces a **JSONL dataset** suitable for downstream ML / NLP tasks.
- Supports **resume functionality** with checkpointing to recover from interruptions.

---

## ⚙️ Setup & Environment Configuration

### 1️⃣ Prerequisites

- Python **3.10+**
- Internet connection (to access Apache Jira)
- *(Optional)* Git & GitHub CLI for repository management

---

### 2️⃣ Installation

Clone or download the project and install dependencies:

```bash
git clone https://github.com/Samrath2004/Web-Scraper.git
cd web-scraper-jira

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

---

### 3️⃣ Dependencies

**Main libraries used:**

| Library | Purpose |
|----------|----------|
| `aiohttp` | Asynchronous HTTP requests |
| `tenacity` | Retry with exponential backoff |
| `ujson` | Fast JSON serialization |
| `beautifulsoup4` | HTML-to-text conversion |
| `dateutil` | Date parsing and normalization |
| `tqdm` | Progress tracking |

---

## 🚀 Usage

### Run the scraper

Example command:

```bash
python run_scrape.py --projects HADOOP SPARK KAFKA --max-results 50 --concurrency 5
```

---

### Arguments

| Argument | Description | Default |
|-----------|--------------|----------|
| `--projects` | List of Apache Jira project keys | Required |
| `--max-results` | Results per page (Jira pagination) | `50` |
| `--concurrency` | Number of simultaneous API calls | `5` |
| `--output-dir` | Output directory for JSONL files | `output` |
| `--checkpoint-file` | Path to checkpoint JSON | `checkpoint.json` |

---

### Output

Each project will produce a JSONL file:

```
output/
 ├─ HADOOP.jsonl
 ├─ SPARK.jsonl
 └─ KAFKA.jsonl
```

Each line represents a single Jira issue in JSON format.

---

## 📁 Example Output (Sample)

```json
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
```

---

## 🔹 Design Reasoning

- **Asynchronous I/O (`aiohttp`)** → enables concurrent HTTP requests using `asyncio.Semaphore`.
- **Retry/backoff (`tenacity`)** → ensures reliability against transient network errors and rate limits.
- **Checkpointing** → prevents data loss during long runs or unexpected interruptions.
- **Streaming JSONL output** → writes each record immediately, avoiding memory overload.
- **Modular structure** → clear separation between `scraper`, `transform`, and `utils` modules.

---

## ⚠️ Edge Cases Handled

| Edge Case | How It’s Handled |
|------------|------------------|
| **HTTP 429 (Rate Limit)** | Raises `RateLimitError`, retries after `Retry-After` header or exponential delay |
| **5xx Server Errors** | Retries with exponential backoff up to 8 times |
| **Timeouts / Connection Errors** | Automatically retried via `tenacity` |
| **Malformed or empty data** | Skipped safely; invalid issues stored in `bad_records/` |
| **Interrupted execution** | Resumes via `checkpoint.json` with `last_startAt` |
| **Large HTML fields** | Sanitized with `BeautifulSoup(html.parser)` |
| **Missing optional fields** | Defaults to `None` or `[]` instead of crashing |
| **File access errors (Windows)** | Retries checkpoint replacement to handle OS locks |

---

## ⚙️ Optimization Decisions

| Optimization | Description |
|---------------|-------------|
| **Async concurrency** | Fetch multiple Jira pages simultaneously, limited by a semaphore |
| **Retry + backoff** | Exponential retry avoids overload and improves reliability |
| **Streaming writes** | Writes JSONL lines incrementally (no large memory use) |
| **Checkpointing** | Saves progress after each page for safe resumption |
| **Heuristic derived fields** | Generates summaries, classification labels, and QnA pairs automatically |
| **Bad record isolation** | Logs invalid or malformed issues separately for debugging |

---

## 🧪 Testing

Run all tests:

```bash
pytest -q
```

**Included tests:**

- `test_transform.py` → validates HTML-to-text conversion and record transformation  
- `test_checkpoint.py` → ensures checkpoint save/load consistency  
- `test_fetcher.py` → mocks HTTP responses for pagination and retry validation  

---

## 🔐 Reliability and Recovery

If the scraper stops midway (e.g., network failure, power loss), simply rerun:

```bash
python run_scrape.py --projects HADOOP SPARK KAFKA
```

It will **automatically resume** from the last saved checkpoint.  
Each project maintains independent progress markers.

---

## 🚀 Potential Future Improvements

| Area | Possible Enhancement |
|-------|-----------------------|
| **Derived fields** | Integrate an LLM or summarizer for richer summaries & QnA |
| **Storage** | Write directly to SQLite / Parquet for efficient analytics |
| **Parallel pipelines** | Use multiprocessing + async for large-scale crawls |
| **Rate limit awareness** | Adaptive throttling based on API latency |
| **Error analytics** | Aggregate and visualize failure types |
| **Dockerization** | Package for reproducible runs |
| **CI/CD Integration** | Add GitHub Actions to automate testing and linting |

---

## 📚 Example Run Summary

| Metric | Value (Sample Run – Hadoop) |
|--------|------------------------------|
| **Total Issues Fetched** | 500+ |
| **Total Retries** | 4 |
| **Skipped (Malformed)** | 2 |
| **Total Runtime** | ~2 minutes |
| **Output Size** | 2.4 MB |

---

## 👨‍💻 Author

**Samrath**  
Bachelor of Technology (CSE), Bennett University  
📧 **e22cseu0738@bennett.edu.in**

---
