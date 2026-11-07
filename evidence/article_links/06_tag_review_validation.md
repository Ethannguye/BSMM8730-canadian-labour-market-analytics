# T03–T06 — Source-level review of article tags

**Review date:** 2026-11-07  
**Input:** [Original article tags](../../data/prepared/article_tags_review.csv)  
**Output:** [Reviewed tags with row-level status and notes](../../data/prepared/article_tags_review_checked.csv)  
**Method:** AI-assisted source check against the three official Statistics Canada *Labour Force Survey* releases. Original SQL and source CSV were left unchanged.

## Review results

| Article | Province tags | Industry tags | Total |
|---|---:|---:|---:|
| February 2020 (released March 6, 2020) | 8 | 6 | 14 |
| April 2020 (released May 8, 2020) | 1 | 9 | 10 |
| December 2025 (released January 9, 2026) | 4 | 5 | 9 |
| **Total** | **13** | **20** | **33** |

**Outcome:** 28 `VERIFIED` and 5 `VERIFIED_WITH_CONTEXT`; no unsupported article-topic tag was identified. Here, “verified” confirms that the article discusses the tagged province/industry, not that it supplies a numeric employment estimate for the category.

## Context notes (row numbers exclude CSV header)

| Row | Article | Tag | Reason for a note |
|---:|---|---|---|
| 8 | February 2020 | Newfoundland and Labrador (NL) | The quoted evidence concerns **hours worked** after severe weather; it should not be described as a change in the number employed. |
| 21 | April 2020 | Transportation and warehousing (48–49) | This passage discusses staff retention **by firm size**, not a numerical transportation-industry employment change. |
| 22 | April 2020 | Public administration (91) | This passage qualitatively compares sectors retaining employment; it does not give a monthly change figure. |
| 23 | April 2020 | Professional, scientific and technical services (54) | This passage qualitatively compares retained employment rather than giving a numeric change for the sector. |
| 24 | April 2020 | Other services (81) | The evidence concerns job-security concerns and **reduced hours**, not an employment headcount change. |

All five are still relevant **topic tags**. A province tag and an industry tag on the same article also do **not**, by themselves, prove that the article reports that specific province–industry combination.

## Original Statistics Canada sources

1. [Labour Force Survey, February 2020](https://www150.statcan.gc.ca/n1/daily-quotidien/200306/dq200306a-eng.htm).
2. [Labour Force Survey, April 2020](https://www150.statcan.gc.ca/n1/daily-quotidien/200508/dq200508a-eng.htm).
3. [Labour Force Survey, December 2025](https://www150.statcan.gc.ca/n1/daily-quotidien/260109/dq260109a-eng.htm).

## What this does and does not prove

The existing [article-link evidence](README.md) documents the local SQL checks: 3 articles; 13 province links; 20 industry links; a Quebec/Construction lookup; and one sample employment query without fact-row multiplication. This additional review checks **passage relevance** for all 33 tags. It does not re-run the database, independently validate every official employment number, establish that every province–industry claim is supported, or test Power BI refresh.

**Scope completed:** Source-level topic-tag review for the project's three manually selected articles. Optional human sign-off, broader article coverage, and end-to-end integration remain separate project activities.
