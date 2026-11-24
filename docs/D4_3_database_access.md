# D.4.3 | Database access

**Existing database:** The team's validation was performed on a locally populated MySQL 8 database named `canadian_labour_market`. No externally reachable host or grader account has been verified. A copy of the PBIX and the full CSVs are available from the [project portal](../README.md). The current access decision is tracked in [GitHub issue #3](https://github.com/Ethannguye/BSMM8730-canadian-labour-market-analytics/issues/3).

## Connect to an already populated instance

1. Open MySQL Workbench and choose an existing connection, or create a **Standard TCP/IP** connection. Use the hostname, port and read-only username supplied by the database owner. For a remote instance, follow the owner's TLS or campus network settings.
2. Choose **Test Connection** and enter the password privately. `localhost` refers only to a server on the computer running Workbench; it is not the address of another team member's computer.
3. Run these read-only checks. Expected results for the group's documented full load are **17,640**, **9** and **14,280** respectively.

```sql
USE canadian_labour_market;
SELECT COUNT(*) AS fact_rows,
       SUM(EmploymentValueThousands IS NULL) AS missing_measurements
FROM fact_employment;
SELECT COUNT(*) AS analytical_rows FROM vw_employment_analytical;
```

## Recreate a local copy if shared access is unavailable

Use an **empty, dedicated MySQL 8 instance/schema**. Skip this section on an existing team database. From the repository root with Python 3.9+ and the MySQL command-line client, run the following in a terminal. Replace `YOUR_LOCAL_USER` with your local account that can create the project schema, tables, views and routines. The client prompts for the password; run each step only if the previous one succeeded.

```bash
mysql -u YOUR_LOCAL_USER -p < sql/01_schema.sql
python3 scripts/emit_mysql_seed.py > employment_seed.sql
mysql -u YOUR_LOCAL_USER -p < employment_seed.sql
mysql -u YOUR_LOCAL_USER -p < sql/03_article_links_FIXED.sql
mysql -u YOUR_LOCAL_USER -p < sql/02_validation.sql
```

The Python step generates a temporary SQL file from the [full CSVs](../data/prepared/full/), loading dimensions first and keeping blank employment values as SQL NULL. Do not use the client's `--force` option or commit the generated file. The article script loads the reviewed article records and their tags separately; article joins must not multiply employment facts. [Documented MySQL results](../sql/README.md) cover the team's original local load.
