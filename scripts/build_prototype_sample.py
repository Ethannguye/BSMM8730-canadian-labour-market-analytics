#!/usr/bin/env python3
"""Prepare prototype or full project data from Statistics Canada product 14100355.

Uses only the Python standard library. Prototype mode supports schema and connection
testing; full mode prepares the January 2019–December 2025 analytical scope.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import zipfile
from pathlib import Path


PROTOTYPE_PROVINCES = {
    "Ontario": "ON",
    "Alberta": "AB",
    "British Columbia": "BC",
}

ALL_PROVINCES = {
    "Newfoundland and Labrador": "NL",
    "Prince Edward Island": "PE",
    "Nova Scotia": "NS",
    "New Brunswick": "NB",
    "Quebec": "QC",
    "Ontario": "ON",
    "Manitoba": "MB",
    "Saskatchewan": "SK",
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
    parser.add_argument("--metadata-json", type=Path, help="Statistics Canada WDS JSON metadata")
    parser.add_argument("--mode", choices=("prototype", "full"), default="prototype")
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


def full_months():
    return tuple(f"{year}-{month:02d}" for year in range(2019, 2026) for month in range(1, 13))


def aggregate_industry(label: str) -> int:
    name = (label or "").casefold()
    aggregate_terms = ("all industries", "total employed", "goods-producing sector", "services-producing sector")
    return int(any(term in name for term in aggregate_terms))


def write_csv(path: Path, fields: list[str], rows: list[dict]):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build_employment(args: argparse.Namespace, out: Path):
    provinces = PROTOTYPE_PROVINCES if args.mode == "prototype" else ALL_PROVINCES
    months = REFERENCE_MONTHS if args.mode == "prototype" else full_months()
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
        if month not in months or province not in provinces:
            continue
        if args.mode == "prototype" and code not in INDUSTRY_CODES:
            continue
        if (row.get("Statistics") or "").strip() != "Estimate":
            continue
        if (row.get("Data type") or "").strip() != "Seasonally adjusted":
            continue
        # Product 14100355 is already an employment table. Do not use exact-text
        # UOM/SCALAR_FACTOR filters here because Statistics Canada exports can use
        # localized or revised labels even when the series itself is unchanged.
        labels_by_code.setdefault(code, label)
        selected.append({
            "ReferenceMonth": month,
            "ProvinceName": province,
            "NAICSCode": code,
            "IndustryLabel": label,
            "EmploymentValueThousands": number_or_blank(row.get("VALUE", "")),
            "StatusFlag": (row.get("STATUS") or "").strip(),
            "SeriesCode": (row.get("VECTOR") or "").strip(),
        })

    missing_codes = set(INDUSTRY_CODES) - set(labels_by_code) if args.mode == "prototype" else set()
    if missing_codes:
        raise RuntimeError(
            "These prototype NAICS codes were not found after filtering: "
            + ", ".join(sorted(missing_codes))
        )

    dim_date = [
        {"DateKey": int(m.replace("-", "")), "ReferenceMonth": f"{m}-01", "Year": int(m[:4]),
         "MonthNumber": int(m[5:7]), "YearMonth": m}
        for m in months
    ]
    province_keys = {name: i + 1 for i, name in enumerate(provinces)}
    dim_province = [
        {"ProvinceKey": province_keys[name], "ProvinceCode": code, "ProvinceName": name}
        for name, code in provinces.items()
    ]
    if args.mode == "prototype":
        industry_items = [(code, labels_by_code[code]) for code in INDUSTRY_CODES]
    else:
        # Key by complete source label because aggregate codes can use special notation.
        industry_items = sorted(((industry_code(label), label) for label in {x["IndustryLabel"] for x in selected}), key=lambda x: x[1])
    if not industry_items:
        raise RuntimeError(
            "No employment rows remained after filtering. Check REF_DATE, GEO, "
            "Statistics and Data type values in the source CSV."
        )
    industry_keys = {label: i + 1 for i, (_, label) in enumerate(industry_items)}
    dim_industry = [{
        "IndustryKey": industry_keys[label], "NAICSCode": code,
        "IndustryLabel": label, "IsAggregate": aggregate_industry(label),
        "IsAnalyticalIndustry": 1 - aggregate_industry(label),
    } for code, label in industry_items]

    facts = []
    unique = set()
    for item in sorted(selected, key=lambda x: (x["ReferenceMonth"], x["ProvinceName"], x["NAICSCode"])):
        key = (int(item["ReferenceMonth"].replace("-", "")), province_keys[item["ProvinceName"]],
               industry_keys[item["IndustryLabel"]])
        if key in unique:
            raise RuntimeError(f"Duplicate month-province-industry grain found: {key}")
        unique.add(key)
        facts.append({
            "EmploymentID": len(facts) + 1,
            "DateKey": key[0], "ProvinceKey": key[1], "IndustryKey": key[2],
            "EmploymentValueThousands": item["EmploymentValueThousands"],
            "StatusFlag": item["StatusFlag"], "SeriesCode": item["SeriesCode"],
        })

    expected = len(months) * len(provinces) * len(industry_items)
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
    return {
        "fact_rows": len(facts), "expected_fact_rows": expected,
        "months": len(dim_date), "provinces": len(dim_province),
        "industries": len(dim_industry),
        "analytical_industries": sum(x["IsAnalyticalIndustry"] for x in dim_industry),
        "blank_values": sum(1 for x in facts if x["EmploymentValueThousands"] == ""),
    }


def build_articles(args: argparse.Namespace, out: Path):
    fields = ["ArticleID", "Title", "PublicationDate", "DateKey", "ReferenceMonth", "BodyText",
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
            "DateKey": (item.get("reference_month", "") or "").replace("-", ""),
            "ReferenceMonth": item.get("reference_month", ""),
            "BodyText": text_path.read_text(encoding="utf-8"),
            "SourceURL": item.get("source_url", ""),
            "RetrievedAtUTC": item.get("retrieved_at_utc", ""),
            "ReviewStatus": "Reviewed sample" if review_exists else item.get("review_status", "Pending manual review"),
        })
    write_csv(out / "article.csv", fields, articles)
    return len(articles)


def flatten_json(value, path="$", rows=None):
    rows = [] if rows is None else rows
    if isinstance(value, dict):
        for key, item in value.items():
            flatten_json(item, f"{path}.{key}", rows)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            flatten_json(item, f"{path}[{index}]", rows)
    else:
        rows.append({"MetadataID": len(rows) + 1, "JsonPath": path,
                     "ValueText": "" if value is None else str(value),
                     "ValueType": type(value).__name__})
    return rows


def build_metadata(args: argparse.Namespace, out: Path):
    fields = ["MetadataID", "JsonPath", "ValueText", "ValueType"]
    if not args.metadata_json:
        write_csv(out / "source_metadata.csv", fields, [])
        return 0
    payload = json.loads(args.metadata_json.read_text(encoding="utf-8-sig"))
    rows = flatten_json(payload)
    write_csv(out / "source_metadata.csv", fields, rows)
    return len(rows)


def write_dictionary(out: Path):
    rows = [
        ["dim_date", "DateKey", "INT", "PK", "Month key in YYYYMM format"],
        ["dim_date", "ReferenceMonth", "DATE", "UNIQUE", "First day of the reference month"],
        ["dim_province", "ProvinceKey", "INT", "PK", "Surrogate province key"],
        ["dim_province", "ProvinceCode", "CHAR(2)", "UNIQUE", "Canadian postal abbreviation"],
        ["dim_industry", "IndustryKey", "INT", "PK", "Surrogate industry key"],
        ["dim_industry", "NAICSCode", "VARCHAR(30)", "", "Source classification code"],
        ["dim_industry", "IsAggregate", "TINYINT", "", "1 for total/sector aggregate rows"],
        ["dim_industry", "IsAnalyticalIndustry", "TINYINT", "", "Use 1 for non-overlapping analytical views"],
        ["fact_employment", "EmploymentID", "BIGINT", "PK", "Prototype row identifier"],
        ["fact_employment", "DateKey", "INT", "FK", "References dim_date"],
        ["fact_employment", "ProvinceKey", "INT", "FK", "References dim_province"],
        ["fact_employment", "IndustryKey", "INT", "FK", "References dim_industry"],
        ["fact_employment", "EmploymentValueThousands", "DECIMAL(12,1)", "NULL allowed", "Estimated employed persons, thousands"],
        ["fact_employment", "StatusFlag", "VARCHAR(10)", "", "Statistics Canada status flag"],
        ["article", "ArticleID", "INT", "PK", "Article record identifier"],
        ["article", "ReferenceMonth", "CHAR(7)", "", "Month discussed by the article"],
        ["article", "BodyText", "LONGTEXT", "", "Scraped narrative text"],
        ["source_metadata", "JsonPath", "VARCHAR(1000)", "", "Path from normalized WDS JSON"],
        ["source_metadata", "ValueText", "LONGTEXT", "", "Metadata scalar value"],
    ]
    with (out / "data_dictionary.csv").open("w", encoding="utf-8", newline="") as h:
        w = csv.writer(h); w.writerow(["Table", "Column", "MySQLType", "Constraint", "Meaning"]); w.writerows(rows)


def main():
    args = arguments()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    metrics = build_employment(args, out)
    articles = build_articles(args, out)
    metadata = build_metadata(args, out)
    write_dictionary(out)
    row_count_matches = metrics["fact_rows"] == metrics["expected_fact_rows"]
    validation_status = "PASS" if row_count_matches else "WARNING - inspect missing combinations"
    completion_message = (
        "Prototype sample created successfully.\n"
        if args.mode == "prototype"
        else (
            "Full 2019-2025 project dataset created successfully.\n"
            if row_count_matches
            else "Full 2019-2025 project output created with a validation warning.\n"
        )
    )
    scope_note = (
        "This sample is for schema, load and connection testing; it is not the final analysis dataset.\n"
        if args.mode == "prototype"
        else (
            "This output covers the configured full employment scope and is ready for MySQL loading.\n"
            if row_count_matches
            else "Do not hand off this output until the missing month-province-industry combinations are explained.\n"
        )
    )
    (out / "VALIDATION_SUMMARY.txt").write_text(
        completion_message
        + f"Mode: {args.mode}\n"
        f"Validation status: {validation_status}\n"
        f"Employment fact rows: {metrics['fact_rows']}\n"
        f"Expected fact rows: {metrics['expected_fact_rows']}\n"
        f"Reference months: {metrics['months']}\nProvinces: {metrics['provinces']}\n"
        f"Source industry labels: {metrics['industries']}\n"
        f"Analytical industry labels: {metrics['analytical_industries']}\n"
        f"Blank employment values preserved: {metrics['blank_values']}\n"
        f"Article rows: {articles}\nMetadata scalar rows: {metadata}\n"
        "Expected employment grain: one row per reference month, province and industry.\n"
        + scope_note,
        encoding="utf-8",
    )
    print(f"Created {args.mode} files in: {out}")
    print(f"Employment rows: {metrics['fact_rows']}; article rows: {articles}; metadata rows: {metadata}")


if __name__ == "__main__":
    main()
