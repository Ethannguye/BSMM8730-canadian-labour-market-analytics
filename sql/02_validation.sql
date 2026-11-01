-- Run after loading source CSVs; read-only checks.
USE canadian_labour_market;
SELECT COUNT(*) AS fact_rows,
       COUNT(EmploymentValueThousands) AS numeric_values,
       SUM(EmploymentValueThousands IS NULL) AS null_values
FROM fact_employment;
SELECT COUNT(*) AS unmatched_keys
FROM fact_employment AS f
LEFT JOIN dim_date AS d ON f.DateKey=d.DateKey
LEFT JOIN dim_province AS p ON f.ProvinceKey=p.ProvinceKey
LEFT JOIN dim_industry AS i ON f.IndustryKey=i.IndustryKey
WHERE d.DateKey IS NULL OR p.ProvinceKey IS NULL OR i.IndustryKey IS NULL;
SELECT DateKey, ProvinceKey, IndustryKey, COUNT(*) AS count_at_grain
FROM fact_employment
GROUP BY DateKey, ProvinceKey, IndustryKey
HAVING COUNT(*) > 1;
SELECT COUNT(*) AS missing_combinations
FROM dim_date AS d CROSS JOIN dim_province AS p CROSS JOIN dim_industry AS i
LEFT JOIN fact_employment AS f
  ON f.DateKey=d.DateKey AND f.ProvinceKey=p.ProvinceKey AND f.IndustryKey=i.IndustryKey
WHERE f.EmploymentID IS NULL;
SELECT COUNT(*) AS analytical_rows,
       COUNT(DISTINCT IndustryKey) AS analytical_industries,
       SUM(EmploymentValueThousands IS NULL) AS null_values
FROM vw_employment_analytical;
SELECT COUNT(*) AS mismatched_view_rows
FROM vw_employment_analytical AS v
LEFT JOIN fact_employment AS f ON v.EmploymentID=f.EmploymentID
WHERE f.EmploymentID IS NULL OR NOT (
 v.DateKey <=> f.DateKey AND v.ProvinceKey <=> f.ProvinceKey
 AND v.IndustryKey <=> f.IndustryKey
 AND v.EmploymentValueThousands <=> f.EmploymentValueThousands
 AND v.StatusFlag <=> f.StatusFlag AND v.SeriesCode <=> f.SeriesCode
);
