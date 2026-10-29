# Canadian Labour Market Analytics

**Industry Growth and Provincial Employment Trends, 2019–2025**

BSMM.8730 — Data Acquisition and Management  
University of Windsor | Fall 2026 | Group 3
## Team Members

- Nguyen Van Sa
- Raviranjan Rajput
- Mujeeb Ahmed Sayed

## Project Overview

This project examines employment growth, decline, and recovery
across Canada's ten provinces and major industries between
January 2019 and December 2025.

The central research question is:

> Which industries are growing in which Canadian provinces,
> and where has employment strengthened or recovered over time?

The project will combine public employment data, metadata,
and labour-market commentary to develop an interactive
Power BI report supported by a MySQL database.

The report is intended for students, job seekers, career advisors,
employers, researchers, educational institutions, and other readers
interested in Canadian labour-market trends.

Employment growth will not be interpreted as a direct measure
of current job vacancies or an individual's employment prospects.

## Project Scope

- Study period: January 2019 to December 2025.
- Geography: Ten Canadian provinces.
- Frequency: Monthly.
- Industry coverage: Selected classifications available in the source.
- Numerical series: Seasonally adjusted employment estimates.
- Employment unit: Thousands of persons.
- Recovery baseline: February 2020.

Territories, city-level analysis, individual job advertisements,
salary analysis, and employment forecasting are outside the scope.

## Planned Data Sources

| Format | Source | Purpose |
|---|---|---|
| CSV — structured | Statistics Canada Table 14-10-0355-01 | Monthly employment estimates by province and industry |
| JSON — semi-structured | Statistics Canada Web Data Service, product 14100355 | Geography and industry metadata |
| Text — unstructured | Selected Labour Force Survey releases from The Daily | Narrative context for employment trends |

The full CSV will be filtered to the study period, ten provinces,
employment estimates, and seasonally adjusted series.

Article publication dates will be stored separately from the
reference months discussed in the articles.

Source URLs, retrieval dates, and preparation steps will be
recorded to support reproducibility.

### Source Links

- [Statistics Canada employment table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410035501)
- [Statistics Canada Web Data Service guide](https://www.statcan.gc.ca/en/developers/wds/user-guide)

The URLs of individual articles will be recorded when selected
for scraping.

## Planned Workflow

1. Acquire the employment CSV and JSON metadata.
2. Scrape selected Labour Force Survey article text.
3. Clean and transform the inputs using Python and Power Query.
4. Map geography and industry labels and review article tags.
5. Create and populate the final MySQL schema.
6. Validate values, relationships, missing data, and duplicate records.
7. Import validated tables into Power BI.
8. Develop DAX measures and interactive report pages.
9. Document findings, limitations, and testing evidence.

Article records will be stored separately from employment facts
so that multiple articles cannot duplicate employment totals.

## Tools and Their Roles

| Tool | Planned role |
|---|---|
| Python | Data acquisition, JSON parsing, web scraping, and database loading |
| Power Query in Excel | Data cleaning and transformation |
| MySQL | Storage of prepared tables and enforcement of relationships |
| Power BI Desktop and DAX | Analytical calculations and interactive reporting |
| GitHub | Version control, collaboration, and development evidence |

## Planned Analytical Features

- Employment levels for a selected reference month.
- Absolute and percentage month-over-month changes.
- Absolute and percentage year-over-year changes.
- A trailing 12-month employment average.
- Recovery measures relative to February 2020.
- An industry-by-province comparison matrix.
- Monthly trend charts and industry drill-through.
- A toggle between employment levels and year-over-year growth.
- Relevant article excerpts and source links.

Missing or suppressed estimates will remain unavailable rather
than being replaced with zero. Employment levels will not be
calculated by summing estimates across different months.

## Repository Structure

| Location | Intended contents |
|---|---|
| [docs](docs/) | Proposal, requirements, design documents, and reports |
| [data](data/) | Source information, metadata, and sample datasets |
| [scripts](scripts/) | Acquisition, scraping, preparation, and loading scripts |
| [sql](sql/) | Database schema and validation queries |
| [powerbi](powerbi/) | Power BI report files and DAX documentation |
| [evidence](evidence/) | Screenshots, validation results, and demonstration evidence |

## Current Repository Status

The initial repository structure and folder README files have
been created.

Project documents, implementation files, and validation evidence
will be added as the team develops and reviews each component.

The features listed above describe the planned solution.
Completed functionality will be documented with supporting
files and test results.

## Getting Started

Start with the project documentation in the `docs` folder as it
becomes available. Review the source information in `data` before
working on acquisition or preparation.

Detailed setup instructions, tested software versions, dependencies,
and execution commands will be added alongside the implementation.

The planned environment uses Python, Excel with Power Query,
MySQL, and Power BI Desktop. Power BI report authoring will use
a Windows environment.

## Team Collaboration and Version Control

Each team member will use their own GitHub account to contribute
work and maintain a traceable development history.

Commits should describe a meaningful change, for example:

- `Add employment data source documentation`
- `Implement JSON metadata retrieval`
- `Create employment fact and dimension tables`
- `Add year-over-year employment measures`
- `Document database validation results`

Branches and pull requests will support review when members
work on shared components.

Each contribution should be linked to the relevant task,
file, commit, or pull request. Completion claims must match
the implementation and evidence available in the repository.


## Data Attribution

Statistics Canada is the source of the employment data,
metadata, and selected Labour Force Survey commentary.

The team will retain source attribution and document any
differences between historical article figures and the
retrieved employment estimates.


---

## Environment Setup and GitHub Contribution Guide

This guide explains how team members can install Python and Git,
download a local copy of the shared repository, and upload their work.

### 1. Install Python

Download a supported Python 3 version from:
[Python Downloads](https://www.python.org/downloads/).

The team will document the exact tested Python version and package
dependencies when the implementation is available.

#### macOS

Download the macOS installer, open the `.pkg` file, and follow
the installation instructions.

Open Terminal and verify the installation:

```bash
python3 --version
python3 -m pip --version
```

#### Windows

Install the Python install manager from the official Python website
and follow its setup instructions.

Open a new PowerShell window and verify the installation:

```powershell
py --version
py -m pip --version
```

A Python version number should appear. If the command is not found,
restart the terminal and check the installation instructions for
your operating system.

### 2. Create or Sign In to a GitHub Account

Go to [GitHub](https://github.com/) and create an account,
or sign in to your existing account.

Each team member must use their own account and accept the
repository owner's collaborator invitation.

GitHub can be used through a web browser. Installing GitHub Desktop
is optional.

### 3. Install Git

Git records changes on your computer and synchronizes them
with the shared GitHub repository.

#### macOS

First, check whether Git is already installed:

```bash
git --version
```

If Git is unavailable, install Apple's Command Line Tools:

```bash
xcode-select --install
```

Complete the installation, reopen Terminal, and check again:

```bash
git --version
```

#### Windows

Download and install Git from:
[Git for Windows](https://git-scm.com/install/windows).

After installation, open Git Bash and run:

```bash
git --version
```

The Git commands in the following sections can be run in
Terminal on macOS or Git Bash on Windows.

### 4. Clone the Shared Repository

Cloning creates a local copy of the existing repository.

1. Open the group's repository on GitHub.
2. Click the green **Code** button.
3. Select **HTTPS** and copy the repository URL.
4. Open Terminal or Git Bash in the location where you want
   to store the project.

Replace `REPOSITORY_HTTPS_URL` in the following command with
the URL you copied:

```bash
git clone REPOSITORY_HTTPS_URL canadian-labour-market-analytics
cd canadian-labour-market-analytics
```

This creates a local folder named `canadian-labour-market-analytics`.

The team will collaborate in the existing shared repository.
A separate repository or fork is not required for this workflow.

#### Authentication

Private repositories require authentication to clone.
Pushing changes also requires authentication and write access.

If Git asks for an HTTPS username and password, enter your GitHub
username and use a personal access token authorized for the
repository instead of your GitHub account password.

Follow the official
[GitHub authentication guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github)
if authentication has not been configured.

Keep access tokens out of files, screenshots, and repository URLs.

### 5. Configure Your Commit Identity

Run these commands inside the cloned project folder.
Replace the example values with your own details:

```bash
git config user.name "Your Full Name"
git config user.email "your-verified-github-email@example.com"
```

Use an email associated with your GitHub account, or your GitHub
no-reply email from **Settings → Emails**, so commits can be linked
to your account.

Check the configuration:

```bash
git config user.name
git config user.email
```

These settings identify your commits in this repository.
They do not sign you in to GitHub.

### 6. Start a New Task

Before making changes, check the current state:

```bash
git status
```

If you have unfinished changes, save and commit them on their
current task branch before switching branches.

With a clean working directory, update `main` and create a task branch:

```bash
git switch main
git pull --ff-only origin main
git switch -c docs/add-project-proposal
```

Use a descriptive, unique branch name for each new task.

Examples include:

- `docs/update-design`
- `scripts/add-metadata-retrieval`
- `sql/create-employment-schema`

### 7. Add Your File and Commit the Change

Copy or save your work into the appropriate local folder:

| File type | Folder |
|---|---|
| Proposal, requirements, or design documents | `docs/` |
| Data source information or sample data | `data/` |
| Python scripts | `scripts/` |
| SQL scripts | `sql/` |
| Power BI files and DAX documentation | `powerbi/` |
| Screenshots and validation results | `evidence/` |

For example, save a proposal document as `docs/proposal.pdf`.

Check the changes:

```bash
git status
```

Stage the file you intend to include:

```bash
git add "docs/proposal.pdf"
```

Replace the example path with the actual path of your file.

Review the staged files, then create the commit:

```bash
git diff --cached --stat
git commit -m "Add project proposal document"
```

A commit saves a version locally. It does not upload the file
to GitHub until you push.

### 8. Push Your Branch to GitHub

For the example branch created above, run:

```bash
git push -u origin docs/add-project-proposal
```

Replace the branch name if you used a different one.

After the first successful push, additional commits on the
same branch can be uploaded with:

```bash
git push
```

Open the repository on GitHub and select your branch to confirm
that the uploaded files appear.

### 9. Create and Review a Pull Request

A pull request lets the team review changes before adding them
to the shared `main` branch.

1. Open the repository on GitHub.
2. Click **Compare & pull request**, or open **Pull requests**
   and select **New pull request**.
3. Set the base branch to `main` and compare it with your task branch.
4. Describe what changed and any checks you performed.
5. Ask another team member to review the changes.
6. Merge the pull request after review and resolution of any issues.

After the merge, update your local copy:

```bash
git switch main
git pull --ff-only origin main
```

### 10. Maintain Contribution Evidence

Commit meaningful changes as work progresses.

Examples:

```text
Add CSV source information and retrieval notes
Implement Labour Force Survey article scraping
Create province and industry dimension tables
Fix duplicate employment records
Document MySQL validation results
```

For the midterm report, retain links to relevant commits and
pull requests, together with a short explanation of each
member's contribution.

If an existing document is uploaded for the first time,
describe it as an initial import. The commit date records
when that version entered GitHub.

### Troubleshooting

| Message or issue | What to check |
|---|---|
| `git: command not found` | Install Git and reopen the terminal |
| `not a git repository` | Use `cd` to enter the cloned project folder |
| `nothing to commit` | Save your changes and check `git status` |
| `pathspec ... did not match any files` | Check the file path, filename, and capitalization |
| `Repository not found` | Check the URL, account, and collaborator access |
| Authentication failed | Check your Git authentication and token permissions |
| Push rejected | Check whether the remote branch changed or has restrictions; coordinate with the team before retrying |

Do not use a force push to bypass a rejected push.

For large datasets or Power BI files, check GitHub's file limits
before uploading. Store source download instructions when files
are managed outside the repository.

### Official Documentation

- [Python on macOS](https://docs.python.org/3/using/mac.html)
- [Python on Windows](https://docs.python.org/3/using/windows.html)
- [Install Git on macOS](https://git-scm.com/install/mac)
- [Set up Git](https://docs.github.com/en/get-started/git-basics/set-up-git)
- [Clone a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)
