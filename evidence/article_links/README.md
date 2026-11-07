# T03–T06: Reviewed Article Tags and MySQL Links

## Scope
This evidence set demonstrates the integration of three manually reviewed Statistics Canada Labour Force Survey articles with the Canadian labour-market MySQL database. Article-level province and industry tags support retrieval of relevant commentary by reference month, province, or industry. A province tag and an industry tag on the same article **do not** by themselves establish that the article reports a specific province–industry claim.

## Reproducible files
- [SQL loader and validation queries](../../sql/03_article_links_FIXED.sql) — creates the `article`, `article_province`, and `article_industry` tables; loads reviewed articles; and produces nine result grids. Requires the existing `canadian_labour_market` database and its dimension/fact tables. Run the entire script in a new MySQL Workbench session.
- [Article tags review CSV](../../data/prepared/article_tags_review.csv) — article IDs, reference months, province/industry tags, source codes, supporting excerpts and source URLs. Tags should be assessed against the cited passages.

## Workbench evidence
| File | Check and observed result |
| --- | --- |
| [01_article_counts.png](01_article_counts.png) | 3 selected articles; 13 article–province links; 20 article–industry links |
| [02_quebec_lookup.png](02_quebec_lookup.png) | Quebec, February 2020: *Labour Force Survey, February 2020*, published 2020-03-06 |
| [03_construction_lookup.png](03_construction_lookup.png) | Construction (NAICS 23), April 2020: *Labour Force Survey, April 2020* |
| [04_employment_validation.png](04_employment_validation.png) | A Quebec manufacturing (NAICS 31-33), February 2020 test retains one employment row and 503.00 thousand people when a related article is found using `EXISTS` |
| [05_fact_employment.png](05_fact_employment.png) | `fact_employment` contains 17,640 rows after the article load |

## Interpretation and limits
The screenshots demonstrate the listed local Workbench checks, **not** automated validation of all tags or all province–industry combinations. The `EXISTS` query in grid 4 avoids multiplying the sample fact row. The script checks tag-key mappings against the dimensions, but passage-level tagging accuracy should also be manually reviewed. This article integration is separate from Power BI model refresh/visual verification, which is a subsequent project task.

## How to demonstrate
1. Open `sql/03_article_links_FIXED.sql` and run it against a database already populated with the project's employment schema, dimensions, and fact rows.
2. Show result grids 1–4 to demonstrate counts, article retrieval, and the one-row employment test.
3. Show grids 5–8 to inspect human-readable article metadata, tags and excerpts; show grid 9 for the employment fact row count.
4. Cross-check tag labels with `data/prepared/article_tags_review.csv` and the cited source passages.

Prepared for BSMM.8730, Group 3 — article tagging and database-link evidence (November 7, 2026).
