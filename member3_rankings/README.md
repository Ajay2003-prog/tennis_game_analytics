# Member 3 — Doubles Rankings

This directory contains the SportRadar doubles competitor rankings pipeline.
It is separate from the Member 1 competition work and Member 2 complexes and
venues work.

## Data source

The fetch script calls:

`https://api.sportradar.com/tennis/trial/v3/en/double_competitors_rankings.json`

The API key is read from the repository-root `.env` file. The `.env` file is
ignored by Git and must never be committed. The scripts do not print the key.

The downloaded response was inspected before processing. It contains the
top-level fields `generated_at` and `rankings`. The observed response contains
2 ranking groups with 500 competitor rankings in each group.

## Files and outputs

- `fetch_doubles_rankings.py`: downloads the raw JSON response.
- `process_rankings.py`: creates normalized CSV files.
- `create_ranking_tables.py`: builds the SQLite database.
- `analyze_rankings.py`: creates summary and top-10 CSVs.
- `member3_queries.sql`: ranking analysis queries.
- `run_ranking_queries.py`: executes the SQL queries.
- `validate_rankings.py`: checks missing values, duplicates, data ranges, and foreign keys.
- `data/doubles_rankings_raw.json`: untouched API response.
- `data/ranking_snapshots.csv`: one row per ranking group/snapshot.
- `data/competitors.csv`: unique competitors.
- `data/doubles_rankings.csv`: competitor rank records linked to snapshots.
- `data/tennis_rankings.db`: SQLite database with three relational tables.
- `data/ranking_analysis_summary.csv`: snapshot-level summaries.
- `data/top_10_doubles_rankings.csv`: top 10 rows from each snapshot.
- `validation_report.md`: validation results.
- `api_connectivity_troubleshooting.md`: earlier network troubleshooting notes.

## Database schema

`RankingSnapshots` stores ranking metadata and the API generation time.
`Competitors` stores one row per competitor ID. `DoublesRankings` stores the
rank, movement, points, and competitions played for each competitor in each
snapshot. Its composite primary key is `(ranking_snapshot_id, competitor_id)`.

Foreign keys connect `DoublesRankings` to both parent tables, and the scripts
enable SQLite foreign-key enforcement.

## Commands

Run these commands from this directory using the project Python environment:

```text
python fetch_doubles_rankings.py
python process_rankings.py
python create_ranking_tables.py
python analyze_rankings.py
python run_ranking_queries.py
python validate_rankings.py
```

The normal order is fetch, process, create the database, analyze, query, and
validate. Re-running the processing and database scripts rebuilds their
outputs from the current raw response.

## Limitations

This pipeline contains doubles rankings only. It does not invent match
results, singles rankings, or competitor statistics not present in the API
response. API access depends on the SportRadar subscription, VPN/network
connectivity, and rate limits.
