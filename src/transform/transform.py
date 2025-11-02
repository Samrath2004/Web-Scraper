# src/transform/transform.py
import ujson
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
from typing import Dict, Any, List

def html_to_text(html: str) -> str:
    if not html:
        return ""
    return BeautifulSoup(html, "html.parser").get_text(separator="\n").strip()

def convert_issue_raw_to_record(raw_issue: Dict[str, Any]) -> Dict[str, Any]:
    fields = raw_issue.get("fields", {})
    key = raw_issue.get("key")
    description_html = fields.get("description") or fields.get("renderedFields", {}).get("description")
    description = html_to_text(description_html)
    comments_list = []
    comments = fields.get("comment", {}).get("comments") or fields.get("renderedFields", {}).get("comment", {}).get("comments") or []
    for c in comments:
        body_html = c.get("body") or c.get("renderedBody")
        comments_list.append({
            "author": (c.get("author") or {}).get("displayName"),
            "created": c.get("created"),
            "body": html_to_text(body_html)
        })

    def parse_time(t):
        if not t:
            return None
        try:
            return dateparser.parse(t).isoformat()
        except Exception:
            return t

    record = {
        "id": key,
        "project": (raw_issue.get("key") or "").split("-")[0] if raw_issue.get("key") else None,
        "title": fields.get("summary"),
        "status": (fields.get("status") or {}).get("name"),
        "priority": (fields.get("priority") or {}).get("name"),
        "assignee": (fields.get("assignee") or {}).get("displayName") if fields.get("assignee") else None,
        "reporter": (fields.get("reporter") or {}).get("displayName") if fields.get("reporter") else None,
        "labels": fields.get("labels") or [],
        "created_at": parse_time(fields.get("created")),
        "updated_at": parse_time(fields.get("updated")),
        "description": description,
        "comments": comments_list,
        "url": f"https://issues.apache.org/jira/browse/{key}"
    }

    # derived simple summary: first 200 chars or first sentence
    if description:
        first_sentence = description.splitlines()[0].split('. ')[0]
        record["derived"] = {
            "summary": first_sentence[:300],
            "classification_labels": [],  # placeholder heuristics can be added
            "qna_pairs": []
        }
    else:
        record["derived"] = {"summary": "", "classification_labels": [], "qna_pairs": []}

    return record

def write_jsonl_line(fh, obj: Dict[str, Any]):
    fh.write(ujson.dumps(obj, ensure_ascii=False) + "\n")
