# T03-B: Scrape selected Labour Force Survey releases

This starter contains a Python script for the Canadian Labour Market Analytics project.
It downloads three official Statistics Canada HTML releases and extracts their narrative
text automatically. Python 3.9 or later is required. No third-party packages are required.

## Run on macOS

1. Extract the ZIP. Open the extracted folder containing this README and `scripts/`.
2. Open Terminal and run `python3 --version`. If Python is missing, install a supported
   Python 3 from https://www.python.org/downloads/macos/ and reopen Terminal.
3. Type `cd ` (include the space), drag the extracted folder from Finder into Terminal,
   and press Return. This avoids typing a long path manually.
4. Run:

```bash
python3 scripts/scrape_lfs_articles.py
```

Each run creates a new folder under `data/raw/articles/run_<UTC timestamp>/`.
Keep that run folder intact. Existing runs and the T02/T03-A files are not overwritten.

## Sample selection

| Reference month | Publication date | Reason for inclusion |
| --- | --- | --- |
| 2020-02 | 2020-03-06 | Context around the project's February 2020 baseline |
| 2020-04 | 2020-05-08 | Early pandemic employment disruption |
| 2025-12 | 2026-01-09 | Context at the end of the study period |

These three selected releases demonstrate the scraping workflow. They are not a
representative sample or a complete monthly collection. The article about December
2025 is in scope by reference month even though it was published in January 2026.

## Outputs and review

- Three `.html` files: original downloaded pages for traceability.
- Three `.txt` files: extracted headings and narrative paragraphs.
- `articles_index.csv` and `articles_index.json`: titles, reference months, publication
  dates, URLs, UTC retrieval timestamps, file references, hashes, and review status.
- `scrape_log.json`: success/error record for every requested source.
- `README.md`: source attribution and extraction limitations for that run.

The CSV index does not contain the long article bodies. Read the TXT files via their
`text_file` paths when loading article text into MySQL. Do not copy long text through
Excel cells, which can truncate it.

Before marking the pilot complete, confirm `Extracted: 3/3` and compare each TXT with
the original page. Verify the title, publication date, reference month, and substantive
paragraphs, including an industry/province passage when present. Record your review
and any omissions in a separate review note. The initial review status is deliberately
`Pending manual review` even when automatic checks pass.

The scraper selects main-content paragraphs/headings and excludes tables, figures,
navigation, and supplementary sections when identified. It does not perform tagging
or load MySQL. Those are later preparation/loading tasks. A website layout change may
require updating the parser; title/date/minimum-text checks flag obvious failures.

Archived articles reflect information available when published. Their numbers may
differ from a later revised CSV. Use the employment CSV as the calculation source and
the articles for context. Keep article-to-province/industry links separate from the
employment fact table to avoid multiplying employment records.

## Add to the existing GitHub repository

Upload `scripts/scrape_lfs_articles.py` to the existing `scripts/` folder and this guide
to `docs/` or include its relevant instructions in `scripts/README.md`.

Upload the complete output run folder under `data/raw/articles/`, keeping filenames
and relative paths intact. If using the GitHub website, create the destination folder
with a README first, then use Add file > Upload files for its contents. Do not upload
this starter as a second nested project repository. Keep the existing T02/T03-A files.

Suggested commits:

- `Add scraper for selected Labour Force Survey releases`
- `Add scraped article sample and source metadata`

Add a screenshot of a successful local run to `evidence/`. This is your execution
evidence; testing performed by someone else does not establish your local completion.
Review and understand the code, and disclose assistance as required by course rules.

## Troubleshooting

- `command not found: python3`: install Python 3 and reopen Terminal.
- `can't open file`: check that Terminal is in the extracted folder containing `scripts/`.
- Certificate verification error after installing Python from python.org: run the
  `Install Certificates.command` supplied in that Python installation's Applications
  folder, then retry. Keep HTTPS certificate verification enabled.
- HTTP error or timeout: read `scrape_log.json`, check the original page in a browser,
  and retry later if the service is temporarily unavailable.
- `Extracted: 0/3`, `1/3`, or `2/3`: do not mark the complete pilot as finished. Preserve
  the log and investigate the failed source(s).

## Sources

- https://www150.statcan.gc.ca/n1/daily-quotidien/200306/dq200306a-eng.htm
- https://www150.statcan.gc.ca/n1/daily-quotidien/200508/dq200508a-eng.htm
- https://www150.statcan.gc.ca/n1/daily-quotidien/260109/dq260109a-eng.htm
- https://www.statcan.gc.ca/en/terms-conditions/open-licence

Statistics Canada source content remains subject to its own terms and attribution.
The project's MIT code licence does not relicense the downloaded articles.
