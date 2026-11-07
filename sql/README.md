 MySQL Database Design and Validation

Canadian Labour Market Analytics — Group 3

**Course:** BSMM.8730 — Data Acquisition and Management  
**Institution:** University of Windsor  
**Project Period:** January 2019 – December 2025  
**Contributor:** Raviranjan Rajput  
**Database:** `canadian_labour_market`  
**Database System:** MySQL 8.0

---

1. Overview

This module implements the relational database and SQL validation layer for the Canadian Labour Market Analytics project.

The project investigates employment patterns across Canadian provinces and industry sectors, addressing two primary questions:

- Which industries are experiencing employment growth across Canadian provinces?
- Which industries and provinces have recovered their employment levels compared with the pre-pandemic period?

The database uses prepared Statistics Canada Labour Force Survey employment data and supports downstream analysis and visualization in Power BI.

2. Database Architecture

<img width="1448" height="1086" alt="image" src="https://github.com/user-attachments/assets/6b4c5f4e-8be6-4ca9-ae0f-46f35591b76b" />






The database follows a **star schema**, consisting of one central fact table connected to three dimension tables.

| Table | Description | Records |
|---|---|---:|
| `dim_date` | Monthly reference periods | 84 |
| `dim_province` | Canadian provincial classifications | 10 |
| `dim_industry` | NAICS-based industry categories | 21 |
| `fact_employment` | Monthly industry employment observations | 17,640 |

2.1 Fact Table — fact_employment

Primary key:`EmploymentID`

| Column | Description |
|---|---|
| `EmploymentID` | Unique employment record identifier |
| `DateKey` | Reference to the Date dimension |
| `ProvinceKey` | Reference to the Province dimension |
| `IndustryKey` | Reference to the Industry dimension |
| `EmploymentValueThousands` | Employment measurement in thousands of persons |
| `StatusFlag` | Source data availability/status indicator |
| `SeriesCode` | Statistics Canada source series identifier |

Granularity: One employment observation per month, province and industry.

The database design uses foreign-key relationships and a uniqueness constraint on the combination of DateKey, ProvinceKey and IndustryKey.

 2.2 Date Dimension — dim_date

Contains `DateKey`, `ReferenceMonth`, `Year`, `MonthNumber` and `YearMonth`.

Supports monthly, annual, year-over-year and time-series employment analysis.

 2.3 Province Dimension — dim_province

Contains `ProvinceKey`, `ProvinceCode` and `ProvinceName`.

Supports employment comparisons across the ten Canadian provinces.

2.4 Industry Dimension — dim_industry

Contains `IndustryKey`, `NAICSCode`, `IndustryLabel`, `IsAggregate` and `IsAnalyticalIndustry`.

The classification flags distinguish aggregate industry categories from those selected for detailed analysis.

3. Entity Relationships

The database is designed with three one-to-many relationships.

| Parent Table | Child Table | Relationship Key |
|---|---|---|
| `dim_date` | `fact_employment` | DateKey |
| `dim_province` | `fact_employment` | ProvinceKey |
| `dim_industry` | `fact_employment` | IndustryKey |

Each employment record references a valid month, province and industry.

This structure reduces redundancy, maintains referential integrity and supports analytical queries.
 4. Analytical SQL View

View Name:`vw_employment_analytical`

The analytical view combines employment records with their corresponding dates, provinces and industry labels using INNER JOIN operations.

It applies industry filters to exclude broad aggregates and overlapping categories.

For example, the combined Wholesale and Retail Trade category is excluded because its component industries are already represented separately.

 Analytical View Summary

| Metric | Value |
|---|---:|
| Total analytical records | 14,280 |
| Detailed industry categories | 17 |
| Provinces | 10 |
| Reference months | 84 |
| Missing employment observations | 9 |

The view is intended to provide a consistent source for province-level and industry-level analysis in Power BI.

 5. Data Loading and Preparation

The database was populated using prepared CSV files from the project's data pipeline.

Data location: `data/prepared/full/`

The loading process included:

1. Creating dimension and fact tables.
2. Importing Date, Province and Industry records.
3. Importing monthly employment observations.
4. Identifying nine observations initially skipped because of missing employment values.
5. Restoring those observations with their original identifiers and NULL employment values.
6. Validating record completeness and referential integrity.
7. Creating the filtered analytical view.

Missing employment measurements were preserved as NULL instead of being converted to zero.

6. SQL Data Validation

SQL validation was performed locally using MySQL Workbench.

| Validation Test | Result | Status |
|---|---:|---|
| Total fact records | 17,640 | PASS |
| Reference months | 84 | PASS |
| Provinces | 10 | PASS |
| Source industry categories | 21 | PASS |
| Missing employment values | 9 NULL | PASS |
| Negative employment values | 0 | PASS |
| Invalid foreign-key references | 0 | PASS |
| Duplicate month–province–industry combinations | 0 | PASS |
| Missing expected combinations | 0 | PASS |
| Analytical view records | 14,280 | PASS |
| Row-level view mismatches | 0 | PASS |

Employment Reconciliation

An additional reconciliation was performed for Ontario in January 2019.

| Measurement | Employment (thousands) |
|---|---:|
| Official employment total | 7,322.6 |
| Sum of analytical industry employment | 7,322.6 |

The totals match after rounding, providing a successful sample reconciliation between the detailed analytical categories and the reported overall employment value.

This reconciliation is a sample check and does not establish that all province-month totals have been independently reconciled.

 7. SQL Files

| File | Purpose |
|---|---|
| `01_schema.sql` | Defines the relational schema and analytical view |
| `02_validation.sql` | Contains database completeness and integrity validation queries |

The SQL scripts are included for reproducibility and further testing. Validation results reported above were obtained from the locally populated MySQL database; the committed scripts should also be tested independently against a fresh database.
 8. Integration With Power BI

The validated analytical view supports theThis folder will contain database schema, loading, and validation SQL scripts.
