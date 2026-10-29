#!/usr/bin/env python3
"""Scrape three selected StatCan releases. Python 3.9+; standard library only.

Run from the project folder: python3 scripts/scrape_lfs_articles.py
This is a pilot sample, not a complete monthly article collection.
"""
import argparse
import csv
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

SOURCES = [
    ("2020-02", "February 2020", "2020-03-06",
     "https://www150.statcan.gc.ca/n1/daily-quotidien/200306/dq200306a-eng.htm"),
    ("2020-04", "April 2020", "2020-05-08",
     "https://www150.statcan.gc.ca/n1/daily-quotidien/200508/dq200508a-eng.htm"),
    ("2025-12", "December 2025", "2026-01-09",
     "https://www150.statcan.gc.ca/n1/daily-quotidien/260109/dq260109a-eng.htm"),
]


class ArticleParser(HTMLParser):
    """Extract narrative headings/paragraphs from main; retain original HTML too."""
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"}
    SKIP = {"script", "style", "nav", "header", "footer", "aside", "table",
            "figure", "form", "button"}
    BLOCKS = {"h1", "h2", "h3", "h4", "p"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.excluded = []
        self.meta = {}
        self.blocks = []
        self.active = None
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "meta":
            self.meta[attributes.get("name", "").lower()] = attributes.get("content", "")
        if tag == "br" and self.active:
            self.parts.append(" ")
        if tag in self.VOID:
            return
        self.stack.append(tag)
        classes = set(attributes.get("class", "").split())
        self.excluded.append(
            tag in self.SKIP or bool(classes & {"indicator-box", "sdg", "release_nav"})
            or attributes.get("id") in {"archived", "archived-bnr"})
        if tag in self.BLOCKS and "main" in self.stack and not any(self.excluded):
            self.active = tag
            self.parts = []

    def handle_data(self, value):
        if self.active and not any(self.excluded):
            self.parts.append(value)

    def handle_endtag(self, tag):
        if self.active == tag:
            value = re.sub(r"\s+", " ", "".join(self.parts)).strip()
            if value:
                self.blocks.append((tag, value))
            self.active = None
            self.parts = []
        if tag in self.stack:
            index = len(self.stack) - 1 - self.stack[::-1].index(tag)
            del self.stack[index:]
            del self.excluded[index:]


def extract_article(html, expected_month, expected_date):
    parser = ArticleParser()
    parser.feed(html)
    expected_title = "Labour Force Survey, " + expected_month
    titles = [text for tag, text in parser.blocks if tag == "h1"]
    if expected_title not in titles:
        raise ValueError("Expected article title not found; review downloaded HTML and selectors.")
    publication_date = parser.meta.get("dcterms.issued", "")[:10]
    if publication_date != expected_date:
        raise ValueError("Publication date missing or different from the source manifest.")
    lines = []
    started = False
    stop_headings = ("note to readers", "selected tables", "contact information", "related information")
    for tag, text in parser.blocks:
        if tag == "h1" and text == expected_title:
            started = True
            continue
        if not started:
            continue
        if tag in {"h2", "h3", "h4"} and text.lower().strip(" :") in stop_headings:
            break
        if text.startswith("Released:"):
            continue
        if text in {"View the most recent version.", "This page has been archived on the Web.", "Archived"}:
            continue
        lines.append(text)
    body = "\n\n".join(lines).strip()
    if len(body) < 1000 or "employment" not in body.lower():
        raise ValueError("Too little article text extracted; manual investigation required.")
    return expected_title, publication_date, body


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path,
                        default=Path(__file__).resolve().parents[1] / "data" / "raw" / "articles")
    args = parser.parse_args()
    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%S_%fZ")
    out = args.output_root / run_id
    out.mkdir(parents=True, exist_ok=False)
    records, log = [], []
    for number, (ref_month, month_label, expected_date, url) in enumerate(SOURCES):
        if number:
            time.sleep(2)
        article_id = "lfs_" + ref_month.replace("-", "_")
        event = {"article_id": article_id, "source_url": url,
                 "reference_month": ref_month, "status": "error"}
        try:
            req = Request(url, headers={"User-Agent": "CanadianLabourMarketStudentProject/1.0"})
            with urlopen(req, timeout=40) as response:
                raw = response.read()
                final_url = response.geturl()
                encoding = response.headers.get_content_charset() or "utf-8"
                event["http_status"] = response.status
            retrieved_at = datetime.now(timezone.utc).isoformat()
            html_name, text_name = article_id + ".html", article_id + ".txt"
            (out / html_name).write_bytes(raw)
            title, publication_date, body = extract_article(
                raw.decode(encoding), month_label, expected_date)
            (out / text_name).write_text(body + "\n", encoding="utf-8")
            record = {
                "article_id": article_id, "title": title,
                "reference_month": ref_month, "publication_date": publication_date,
                "source_url": url, "final_url": final_url,
                "retrieved_at_utc": retrieved_at,
                "html_file": html_name, "text_file": text_name,
                "text_characters": len(body),
                "html_sha256": hashlib.sha256(raw).hexdigest(),
                "review_status": "Pending manual review",
            }
            records.append(record)
            event.update(status="extracted", retrieved_at_utc=retrieved_at,
                         text_characters=len(body))
            print("OK:", article_id, "-", len(body), "characters")
        except Exception as exc:
            event["error"] = str(exc)
            print("ERROR:", article_id, "-", exc, file=sys.stderr)
        event["logged_at_utc"] = datetime.now(timezone.utc).isoformat()
        log.append(event)
    (out / "articles_index.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = ["article_id", "title", "reference_month", "publication_date", "source_url",
              "final_url", "retrieved_at_utc", "html_file", "text_file", "text_characters",
              "html_sha256", "review_status"]
    with (out / "articles_index.csv").open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    (out / "scrape_log.json").write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
    notes = (
        "# Scraped Labour Force Survey releases\n\n"
        "Source: Statistics Canada, The Daily. Source URLs and retrieval timestamps "
        "are recorded in articles_index.csv and articles_index.json.\n\n"
        "Three deliberately selected releases form a pilot sample. They do not provide "
        "complete monthly text coverage for 2019-2025.\n\n"
        "Original HTML is preserved. TXT files contain narrative headings and paragraphs. "
        "Navigation, tables and figures are excluded. Extraction stops at source-note/related "
        "sections when identified. The HTML retains material omitted from the text.\n\n"
        "Compare each TXT with its source before changing review_status. Keep the historical "
        "publication date separate from the reference month. Archived release figures may "
        "differ from revised CSV estimates; use the CSV for analytical calculations and the "
        "articles for context. Province and industry tags require review during preparation.\n\n"
        "Statistics Canada Open Licence: https://www.statcan.gc.ca/en/terms-conditions/open-licence\n"
        "Source content retains its original terms and attribution; it is not relicensed under "
        "the project's code licence.\n\n"
        "Successfully extracted: " + str(len(records)) + "/3. See scrape_log.json for failures.\n"
    )
    (out / "README.md").write_text(notes, encoding="utf-8")
    print("\nSaved to:", out)
    print("Extracted:", str(len(records)) + "/3. Manual review is still required.")
    return 0 if len(records) == len(SOURCES) else 1


if __name__ == "__main__":
    sys.exit(main())
