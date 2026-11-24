"""Write the four prepared employment tables as MySQL INSERTs for an empty schema.

Run from any directory: python3 scripts/emit_mysql_seed.py > employment_seed.sql
The script reads the versioned full CSVs; it never connects to a database.
"""
import csv
import re
import sys
from itertools import islice
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "prepared" / "full"
# Use a fixed table order and explicit columns: foreign keys require dimensions first.
TABLES = {
    "dim_date": "DateKey ReferenceMonth Year MonthNumber YearMonth",
    "dim_province": "ProvinceKey ProvinceCode ProvinceName",
    "dim_industry": "IndustryKey NAICSCode IndustryLabel IsAggregate IsAnalyticalIndustry",
    "fact_employment": "EmploymentID DateKey ProvinceKey IndustryKey EmploymentValueThousands StatusFlag SeriesCode",
}
NUMBERS = set("DateKey Year MonthNumber ProvinceKey IndustryKey IsAggregate IsAnalyticalIndustry EmploymentID EmploymentValueThousands".split())
NULLABLE = {"NAICSCode", "EmploymentValueThousands", "StatusFlag", "SeriesCode"}


def literal(column, value):
    if value == "" and column in NULLABLE:
        # An unpublished measurement has no numeric value; treating it as zero
        # would create a false employment collapse in trend and recovery charts.
        return "NULL"
    if column in NUMBERS:
        if not re.fullmatch(r"-?[0-9]+(?:\.[0-9]+)?", value):
            raise ValueError(f"Invalid numeric {column}: {value!r}")
        return value
    # UTF-8 hex literals preserve accents and quotes without relying on a
    # particular MySQL backslash-escaping mode or the client's character set.
    return "CONVERT(X'" + value.encode("utf-8").hex() + "' USING utf8mb4)"


def emit(data=DATA, out=None):
    if out is None:
        out = sys.stdout
    print("USE canadian_labour_market;\nSTART TRANSACTION;", file=out)
    for table, names in TABLES.items():
        names = names.split()
        with (data / (table + ".csv")).open(encoding="utf-8-sig", newline="") as file:
            rows = csv.DictReader(file)
            if rows.fieldnames != names:
                raise ValueError(f"{table}: unexpected CSV header {rows.fieldnames}")
            columns = ", ".join(f"`{key}`" for key in names)
            # Batch inserts to keep statement sizes small. No REPLACE, IGNORE
            # or DELETE: a conflicting primary key must fail visibly.
            while batch := list(islice(rows, 200)):
                values = ["(" + ", ".join(literal(k, row[k]) for k in names) + ")" for row in batch]
                print(f"INSERT INTO `{table}` ({columns}) VALUES\n" + ",\n".join(values) + ";", file=out)
    print("COMMIT;", file=out)


if __name__ == "__main__":
    emit()
