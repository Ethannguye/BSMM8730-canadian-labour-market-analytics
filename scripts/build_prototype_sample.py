#!/usr/bin/env python3
"""Build a small, relational prototype dataset from Statistics Canada product 14100355.

Uses only the Python standard library. The outputs are intended for MySQL loading
and Power BI connection testing; they are not the final analytical dataset.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import zipfile
from pathlib import Path


PROVINCES = {
    "Ontario": "ON",
    "Alberta": "AB",
    "British Columbia": "BC",
}

# Four non-overlapping industry examples for the prototype. Matching uses the
# NAICS code in square brackets, so minor label wording changes do not break it.
INDUSTRY_CODES = ("23", "31-33", "54", "62")
REFERENCE_MONTHS = ("2019-01", "2020-02", "2020-04", "2025-12")


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input-zip", type=Path, help="14100355-eng.zip")
    source.add_argument("--input-csv", type=Path, help="Extracted 14100355.csv")
    parser.add_argument("--articles-dir", type=Path, help="Scraper run directory")
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def locate_csv_in_zip(path: Path):
    archive = zipfile.ZipFile(path)
    candidates = [n for n in archive.namelist() if n.lower().endswith(".csv")]
    data = [n for n in candidates if "metadata" not in n.lower()]
    if not data:
        archive.close()
        raise RuntimeError("No data CSV was found in the ZIP archive.")
    return archive, archive.open(data[0], "r")


def source_rows(args: argparse.Namespace):
    if args.input_zip:
        archive, raw = locate_csv_in_zip(args.input_zip)
        import io
        text = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
        try:
            yield from csv.DictReader(text)
        finally:
            text.close()
            archive.close()
    else:
        with args.input_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            yield from csv.DictReader(handle)


def industry_code(label: str) -> str:
    matches = re.findall(r"\[([^\]]+)\]", label or "")
    return matches[-1].strip() if matches else ""


def number_or_blank(value: str):
    value = (value or "").strip()
    if value == "":
        return ""
    return value


def write_csv(path: Path, fields: list[str], rows: list[dict]):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build_employment(args: argparse.Namespace, out: Path):
    selected = []
    labels_by_code: dict[str, str] = {}
    required = {
        "REF_DATE", "GEO", "North American Industry Classification System (NAICS)",
        "Statistics", "Data type", "VALUE", "STATUS", "VECTOR"
    }
    seen_header = False

    for row in source_rows(args):
        if not seen_header:
            missing = required - set(row)
            if missing:
                raise RuntimeError(f"Source CSV is missing required columns: {sorted(missing)}")
            seen_header = True
        month = (row.get("REF_DATE") or "")[:7]
        province = (row.get("GEO") or "").strip()
        label = (row.get("North American Industry Classification System (NAICS)") or "").strip()
        code = industry_code(label)
        if month not in REFERENCE_MONTHS or province not in PROVINCES or code not in INDUSTRY_CODES:
            continue
        if (row.get("Statistics") or "").strip() != "Estimate":
            continue
        if (row.get("Data type") or "").strip() != "Seasonally adjusted":
            continue
        labels_by_code.setdefault(code, label)
        selected.append({
            "ReferenceMonth": month,
            "ProvinceName": province,
            "NAICSCode": code,
            "EmploymentValueThousands": number_or_blank(row.get("VALUE", "")),
            "StatusFlag": (row.get("STATUS") or "").strip(),
            "SeriesCode": (row.get("VECTOR") or "").strip(),
        })

    missing_codes = set(INDUSTRY_CODES) - set(labels_by_code)
    if missing_codes:
        raise RuntimeError(
            "These prototype NAICS codes were not found after filtering: "
            + ", ".join(sorted(missing_codes))
        )

    dim_date = [
        {"DateKey": int(m.replace("-", "")), "ReferenceMonth": f"{m}-01", "Year": int(m[:4]),
         "MonthNumber": int(m[5:7]), "YearMonth": m}
        for m in REFERENCE_MONTHS
    ]
    province_keys = {name: i + 1 for i, name in enumerate(PROVINCES)}
    dim_province = [
        {"ProvinceKey": province_keys[name], "ProvinceCode": code, "ProvinceName": name}
        for name, code in PROVINCES.items()
    ]
    industry_keys = {code: i + 1 for i, code in enumerate(INDUSTRY_CODES)}
    dim_industry = [
        {"IndustryKey": industry_keys[code], "NAICSCode": code,
         "IndustryLabel": labels_by_code[code], "IsPrototypeSelection": 1}
        for code in INDUSTRY_CODES
    ]

    facts = []
    unique = set()
    for item in sorted(selected, key=lambda x: (x["ReferenceMonth"], x["ProvinceName"], x["NAICSCode"])):
        key = (int(item["ReferenceMonth"].replace("-", "")), province_keys[item["ProvinceName"]],
               industry_keys[item["NAICSCode"]])
        if key in unique:
            raise RuntimeError(f"Duplicate month-province-industry grain found: {key}")
        unique.add(key)
        facts.append({
            "EmploymentID": len(facts) + 1,
            "DateKey": key[0], "ProvinceKey": key[1], "IndustryKey": key[2],
            "EmploymentValueThousands": item["EmploymentValueThousands"],
            "StatusFlag": item["StatusFlag"], "SeriesCode": item["SeriesCode"],
        })

    expected = len(REFERENCE_MONTHS) * len(PROVINCES) * len(INDUSTRY_CODES)
    if len(facts) != expected:
        print(f"WARNING: expected {expected} fact rows but produced {len(facts)}. ", end="", file=sys.stderr)
        print("Suppressed or unavailable combinations may explain the difference; inspect the output.", file=sys.stderr)

    write_csv(out / "dim_date.csv", list(dim_date[0]), dim_date)
    write_csv(out / "dim_province.csv", list(dim_province[0]), dim_province)
    write_csv(out / "dim_industry.csv", list(dim_industry[0]), dim_industry)
    write_csv(out / "fact_employment.csv", [
        "EmploymentID", "DateKey", "ProvinceKey", "IndustryKey",
        "EmploymentValueThousands", "StatusFlag", "SeriesCode"
    ], facts)
    return len(facts)


def build_articles(args: argparse.Namespace, out: Path):
    fields = ["ArticleID", "Title", "PublicationDate", "ReferenceMonth", "BodyText",
              "SourceURL", "RetrievedAtUTC", "ReviewStatus"]
    if not args.articles_dir:
        write_csv(out / "article.csv", fields, [])
        return 0
    index_path = args.articles_dir / "articles_index.json"
    records = json.loads(index_path.read_text(encoding="utf-8"))
    review_exists = (args.articles_dir / "article_review.md").exists()
    articles = []
    for i, item in enumerate(records, 1):
        text_path = args.articles_dir / item["text_file"]
        articles.append({
            "ArticleID": i,
            "Title": item.get("title", ""),
            "PublicationDate": item.get("publication_date", ""),
            "ReferenceMonth": item.get("reference_month", ""),
            "BodyText": text_path.read_text(encoding="utf-8"),
            "SourceURL": item.get("source_url", ""),
            "RetrievedAtUTC": item.get("retrieved_at_utc", ""),
            "ReviewStatus": "Reviewed sample" if review_exists else item.get("review_status", "Pending manual review"),
        })
    write_csv(out / "article.csv", fields, articles)
    return len(articles)


def write_dictionary(out: Path):
    rows = [
        ["dim_date", "DateKey", "INT", "PK", "Month key in YYYYMM format"],
        ["dim_date", "ReferenceMonth", "DATE", "UNIQUE", "First day of the reference month"],
        ["dim_province", "ProvinceKey", "INT", "PK", "Surrogate province key"],
        ["dim_province", "ProvinceCode", "CHAR(2)", "UNIQUE", "Canadian postal abbreviation"],
        ["dim_industry", "IndustryKey", "INT", "PK", "Surrogate industry key"],
        ["dim_industry", "NAICSCode", "VARCHAR(20)", "", "Source classification code"],
        ["fact_employment", "EmploymentID", "BIGINT", "PK", "Prototype row identifier"],
        ["fact_employment", "DateKey", "INT", "FK", "References dim_date"],
        ["fact_employment", "ProvinceKey", "INT", "FK", "References dim_province"],
        ["fact_employment", "IndustryKey", "INT", "FK", "References dim_industry"],
        ["fact_employment", "EmploymentValueThousands", "DECIMAL(12,1)", "NULL allowed", "Estimated employed persons, thousands"],
        ["fact_employment", "StatusFlag", "VARCHAR(10)", "", "Statistics Canada status flag"],
        ["article", "ArticleID", "INT", "PK", "Article record identifier"],
        ["article", "ReferenceMonth", "CHAR(7)", "", "Month discussed by the article"],
        ["article", "BodyText", "LONGTEXT", "", "Scraped narrative text"],
    ]
    with (out / "data_dictionary.csv").open("w", encoding="utf-8", newline="") as h:
        w = csv.writer(h); w.writerow(["Table", "Column", "MySQLType", "Constraint", "Meaning"]); w.writerows(rows)


def main():
    args = arguments()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    facts = build_employment(args, out)
    articles = build_articles(args, out)
    write_dictionary(out)
    (out / "VALIDATION_SUMMARY.txt").write_text(
        "Prototype sample created successfully.\n"
        f"Employment fact rows: {facts}\nArticle rows: {articles}\n"
        "Expected employment grain: one row per reference month, province and industry.\n"
        "This sample is for schema, load and connection testing; it is not the final analysis dataset.\n",
        encoding="utf-8",
    )
    print(f"Created prototype files in: {out}")
    print(f"Employment rows: {facts}; article rows: {articles}")


if __name__ == "__main__":
    main()
