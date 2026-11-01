-- Canadian Labour Market Analytics | Group 3
-- Portable MySQL 8 schema. Structure only: no source data is inserted.
-- Intended for a NEW/EMPTY database. Review existing tables before running.
CREATE DATABASE IF NOT EXISTS canadian_labour_market CHARACTER SET utf8mb4;
USE canadian_labour_market;

CREATE TABLE IF NOT EXISTS dim_date (
  DateKey INT NOT NULL,
  ReferenceMonth DATE NOT NULL,
  `Year` SMALLINT NOT NULL,
  MonthNumber TINYINT NOT NULL,
  YearMonth CHAR(7) NOT NULL,
  PRIMARY KEY (DateKey),
  UNIQUE KEY uq_dim_date_reference_month (ReferenceMonth)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS dim_province (
  ProvinceKey INT NOT NULL,
  ProvinceCode VARCHAR(10) NOT NULL,
  ProvinceName VARCHAR(100) NOT NULL,
  PRIMARY KEY (ProvinceKey),
  UNIQUE KEY uq_dim_province_code (ProvinceCode)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS dim_industry (
  IndustryKey INT NOT NULL,
  NAICSCode VARCHAR(100) NULL,
  IndustryLabel VARCHAR(255) NOT NULL,
  IsAggregate TINYINT NOT NULL,
  IsAnalyticalIndustry TINYINT NOT NULL,
  PRIMARY KEY (IndustryKey),
  UNIQUE KEY uq_dim_industry_label (IndustryLabel)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS fact_employment (
  EmploymentID INT NOT NULL,
  DateKey INT NOT NULL,
  ProvinceKey INT NOT NULL,
  IndustryKey INT NOT NULL,
  EmploymentValueThousands DECIMAL(14,2) NULL,
  StatusFlag VARCHAR(10) NULL,
  SeriesCode VARCHAR(50) NULL,
  PRIMARY KEY (EmploymentID),
  UNIQUE KEY uq_fact_month_province_industry (DateKey, ProvinceKey, IndustryKey),
  CONSTRAINT fk_fact_date FOREIGN KEY (DateKey) REFERENCES dim_date(DateKey),
  CONSTRAINT fk_fact_province FOREIGN KEY (ProvinceKey) REFERENCES dim_province(ProvinceKey),
  CONSTRAINT fk_fact_industry FOREIGN KEY (IndustryKey) REFERENCES dim_industry(IndustryKey)
) ENGINE=InnoDB;

-- Analytical reporting view: exclude source aggregate categories and the
-- combined Wholesale and retail trade category to avoid double-counting.
CREATE OR REPLACE VIEW vw_employment_analytical AS
SELECT
  f.EmploymentID,
  d.DateKey, d.ReferenceMonth, d.`Year`, d.MonthNumber, d.YearMonth,
  p.ProvinceKey, p.ProvinceCode, p.ProvinceName,
  i.IndustryKey, i.NAICSCode, i.IndustryLabel,
  f.EmploymentValueThousands, f.StatusFlag, f.SeriesCode
FROM fact_employment AS f
JOIN dim_date AS d ON f.DateKey = d.DateKey
JOIN dim_province AS p ON f.ProvinceKey = p.ProvinceKey
JOIN dim_industry AS i ON f.IndustryKey = i.IndustryKey
WHERE i.IsAnalyticalIndustry = 1
  AND i.IndustryLabel NOT LIKE 'Wholesale and retail trade%';
