# Automatic Reporting Pipeline

**Automated accounts receivable reporting from raw order and payment CSVs — no spreadsheets, no manual matching.**

---

## Problem Statement

The client currently calculates outstanding balances manually. 

Reconciling outstanding client balances requires:
- Manually download and open files
- Match and normalize client names
- Compute totals
- Produce a summary

The current workflow of the company is a tedious, error-prone process repeated every reporting cycle. This pipeline replaces that manual workflow entirely.

---

## Solution Overview

The pipeline ingests two CSV files (orders and payments), validates their schemas, transforms and normalises the data, aggregates totals per client, merges them into a single receivables view, and writes a timestamped summary CSV to an output directory. Processed input files are automatically archived and a log file containing the last 7 days of information is saved.

Everything is containerised and requires a single command to run.

---

## Key Features

- Automatic discovery of input files — no hardcoded filenames required
- Schema validation with clear error messages on missing columns
- Client name normalization (case-insensitive matching across both files)
- Automatic computation of `outstanding_balance = total_purchased − total_paid`
- Timestamped output files to preserve a full audit trail
- Automatic archival of processed inputs after a successful run
- Structured logging to both console and a rotating log file
- Docker-first design — runs identically on any machine

---

## High-Level Workflow

```
input_files/
  orders_<date>.csv   ┐
  payments_<date>.csv ┘  
↓
Validate 
↓
Transform
↓
Aggregate
↓
Merge
↓
Write CSV
↓
Archive inputs

```
---
## Project Structure

```
.
├── config.yaml              
├── docker-compose.yml       
├── Dockerfile               
├── requirements.txt         
├── src/
│   ├── main.py              
│   ├── ingestion.py         
│   ├── validation.py        
│   ├── transform.py         
│   ├── aggregation.py       
│   ├── report.py            
│   └── utils.py             
├── input_files/             
├── output/                  
├── archive/                 
└── logs/                    
```

---

## Requirements

- **Docker** and **Docker Compose** 

---

## Installation & Setup

```bash
git clone <repo-url>
cd <repo-directory>
```

Or download the project as a .zip file

```bash
docker compose up --build
```

Builds and runs the pipeline

```bash
docker compose up
```

Runs the already built container

The pipeline will exit automatically after processing. If no CSV files are present in the input directory, it logs a warning and stops without error.

---

## Typical Day-to-Day Workflow

1. Export your orders CSV and payments CSV from your source system.
2. Place both files in the `input_files/` directory and make sure the are named `orders_<date>.cvs` and `payments_<date>.csv`

The repository comes with sample files in the folder named `archive/`, move those files to `input_files/` or generate similar files

3. Run `docker compose up --build` or `docker compose up` if you already built the tool.
4. Collect the output report from `output/receivables_summary_<timestamp>.csv`.
5. Confirm that both input files have been moved to `archive/`.

---

## Configuration

All directory paths are defined in `config.yaml`:

```yaml
input_dir: /data/input       # Where the pipeline looks for CSVs
output_dir: /data/output     # Where the report is written
archive_dir: /data/archive   # Where processed inputs are moved
log_dir: /data/logs          # Where pipeline.log is written
```

These paths are container-internal. The `docker-compose.yml` maps them to local host directories:

| Container path   | Host directory    |
|------------------|-------------------|
| `/data/input`    | `./input_files`   |
| `/data/output`   | `./output`        |
| `/data/archive`  | `./archive`       |
| `/data/logs`     | `./logs`          |

To change a path, update both `config.yaml` and the corresponding volume entry in `docker-compose.yml`.

---

## Input Data Expectations

The pipeline identifies files by name — the filename must contain the word `orders` or `payments`.

**Orders file** — required columns:

The pipeline identifies the required columns from the client's expected input files:

| Column       | Type    | Description                        |
|--------------|---------|------------------------------------|
| `order_id`   | integer | Unique order identifier            |
| `date`       | string  | Order date (parseable by pandas)   |
| `client_name`| string  | Client name                        |
| `product`    | string  | Product name                       |
| `quantity`   | integer | Units ordered                      |
| `unit_price` | float   | Price per unit                     |

**Payments file** — required columns:

| Column           | Type    | Description                          |
|------------------|---------|--------------------------------------|
| `payment_id`     | integer | Unique payment identifier            |
| `date`           | string  | Payment date (parseable by pandas)   |
| `client`         | string  | Client name                          |
| `payment_amount` | float   | Amount paid                          |

Column names are trimmed and lowercased automatically. `client_name` in the orders file is aliased to `client` for matching purposes. Client strings are title-cased and stripped of whitespace before any join.

---

## Output Description

Each successful run produces one file in `output/`:

```
receivables_summary_YYYYMMDD_HHMMSS.csv
```

| Column                | Description                                     |
|-----------------------|-------------------------------------------------|
| `client`              | Normalised client name                          |
| `total_purchased`     | Sum of all order totals (`quantity × unit_price`) |
| `total_paid`          | Sum of all payments received                    |
| `outstanding_balance` | `total_purchased − total_paid`                  |

Clients with no payment on record receive `total_paid = 0` and a full outstanding balance. The timestamp in the filename ensures that repeated runs never overwrite previous reports.

---

## Logging and Traceability

Logs are written to `logs/pipeline.log` and echoed to the console. The log captures:

- Pipeline start and file discovery results
- Which orders and payments files were identified
- The full path of the report that was generated
- Any warnings or errors encountered

Log files rotate daily and are retained for 7 days. Each log line includes a timestamp, severity level, module name, function name, and line number.

---

## Error Handling Behavior

| Situation                                  | Behaviour                                      |
|--------------------------------------------|------------------------------------------------|
| Input directory does not exist             | Logs an error and stops                        |
| No CSV files in the input directory        | Logs a warning and stops                       |
| Orders or payments file not identifiable   | Raises `FileNotFoundError` and stops           |
| Required columns missing from a file       | Raises `ValueError` with missing column names  |
| Any other unexpected exception             | Logged; pipeline stops without corrupting outputs |

The pipeline does **not** perform partial writes — if an error occurs before `write_report`, no output file is created and no input files are archived.

---

## Data Archival Behavior

After a report is successfully written, both the orders file and the payments file are moved (not copied) from the input directory to the archive directory using `shutil.move`. This prevents the same files from being reprocessed on the next run and keeps the input directory clean.

---

## Extensibility / Customisation Options

- **Add new input formats:** Extend `ingestion.py` to support Excel or other delimited files alongside CSV.
- **Add new validations:** Extend `validation.py` to check data types, date ranges, or value constraints.
- **Change aggregation logic:** Edit `aggregation.py` to group by additional dimensions (e.g., product or date range).
- **Add new output formats:** Edit `report.py` to write Excel, JSON, or push results to a database.
- **Add email delivery:** Call a notification function from `main.py` after `write_report`.
- **Schedule recurring runs:** Wrap `docker compose up` in a cron job or task scheduler.

---

## Technical Architecture Overview

| Module           | Responsibility                                                                 |
|------------------|--------------------------------------------------------------------------------|
| `main.py`        | Orchestrates the pipeline; loads config; calls each module in sequence         |
| `ingestion.py`   | Scans a directory and returns a list of CSV `Path` objects                     |
| `utils.py`       | Sets up logging; identifies which file is orders vs. payments by name          |
| `validation.py`  | Asserts required columns are present; raises `ValueError` if not               |
| `transform.py`   | Strips/lowercases columns, aliases `client_name` → `client`, computes `order_total`, normalises dates and client strings |
| `aggregation.py` | Groups orders and payments by client; merges them with a left join             |
| `report.py`      | Creates the output directory if needed; writes the DataFrame to a timestamped CSV |

Data flows strictly in one direction: ingest → validate → transform → aggregate → report → archive.

---

## Development Notes

- The project uses `loguru` in place of the standard `logging` module. The default logger is removed in `setup_logging` to prevent duplicate output.
- `shutil.move` is used for archival, meaning the archive and input directories must be on the same filesystem (which they are by default in the Docker setup).
- Column aliases are defined as a dictionary in `transform.py` (`COLUMN_ALIASES`). Adding a new alias there is sufficient — no other module needs to change.
- All date parsing is delegated to `pandas.to_datetime` with `errors="raise"`, so malformed dates will surface as exceptions rather than silent NaTs.

To add unit tests, create a `tests/` directory and import the individual modules directly (they have no side effects at import time).

This tool is designed to make an otherwise tedious job, automatic and less prone to errors. However, malformation in the input files may generate errors in the pipeline that require human intervation (for example: corrupted files or invalid time formats; mismatched client names like "The Pub" and "Pub" will register as two different entities; invalid or different column names may have to be renamed manually; etc)

---
## Limitations / Assumptions

- Exactly one orders file and one payments file are expected per run. Multiple files of either type are not supported.
- Files are identified by the presence of `"orders"` or `"payments"` anywhere in the filename.
- The pipeline performs a **left join** on client name — clients who have placed orders but made no payments are included with `total_paid = 0`. Clients who have made payments but placed no orders are excluded from the report.
- All monetary values are treated as floats; no currency conversion or multi-currency logic is applied.
- Date columns are parsed but not used in aggregation; the report covers all dates present in the input files.

---

## Future Improvements

- Support multiple input file pairs per run (e.g., files for different date ranges or regions)
- Add a configurable date-range filter to scope the report to a specific period
- Write output to Excel format with formatting (column widths, totals row, conditional formatting for overdue balances)
- Add a configurable alerting threshold to flag clients whose outstanding balance exceeds a set amount
- Expose a `--dry-run` flag that validates and previews results without writing or archiving
- Add a `tests/` suite with sample fixture CSVs covering edge cases (empty files, missing columns, mismatched client names)
- Check for similar client names
