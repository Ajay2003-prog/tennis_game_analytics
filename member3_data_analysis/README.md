# Member 3: Data Analysis and Visualizations

This folder contains the data analysis and visualization work for the project
**Game Analytics: Unlocking Tennis Data with SportRadar API**.

The code reads the existing Member 1 and Member 2 CSV files in place. It does
not copy, move, overwrite, or delete those source datasets.

## Folder structure

```text
member3_data_analysis/
├── README.md
├── analyze_data.py
├── create_charts.py
└── outputs/
    ├── dataset_quality_summary.csv
    ├── foreign_key_summary.csv
    ├── competition_counts_by_type.csv
    ├── competition_counts_by_gender.csv
    ├── competition_counts_by_category.csv
    ├── venue_counts_by_country.csv
    ├── venues_per_complex.csv
    ├── findings_and_recommendations.md
    └── charts/
        ├── competition_counts_by_type.png
        ├── competition_counts_by_gender.png
        ├── top_10_competition_categories.png
        ├── top_10_countries_by_venue_count.png
        └── top_10_complexes_by_venue_count.png
```

The source CSV files remain in their original locations:

- `tennis_game_analytics-main/member1_competitions/data/`
- `tennis_game_analytics-main/member2_complexes_venues/data/`

## Dependencies

- Python 3.14 or a compatible Python 3 version
- pandas
- Matplotlib

The validated interpreter in this workspace is:

```text
C:/Users/mudde/AppData/Local/Programs/Python/Python314/python.exe
```

## How to run the analysis

From the outer project folder, run:

```powershell
& "C:/Users/mudde/AppData/Local/Programs/Python/Python314/python.exe" ".\member3_data_analysis\analyze_data.py"
```

This reads `competitions.csv`, `categories.csv`, `complexes.csv`, and
`venues.csv`. It prints dataset quality statistics and summary tables, then
regenerates the summary CSV files inside `outputs/`.

## How to create the charts

After running the analysis script, run:

```powershell
& "C:/Users/mudde/AppData/Local/Programs/Python/Python314/python.exe" ".\member3_data_analysis\create_charts.py"
```

This reads only the summary CSV files in `outputs/` and saves five PNG charts
inside `outputs/charts/`.

## Generated outputs

The analysis outputs include:

- Dataset quality and primary-ID checks
- Foreign-key relationship checks
- Competition counts by type, gender, and category
- Venue counts by country
- Venue counts per complex
- Evidence-based findings and dashboard recommendations

The charts show competition type, competition gender, the top ten categories,
the top ten countries by venue count, and the top ten complexes by venue count.

## Current limitations

The available datasets contain competition, category, complex, and venue
information only. Competitor rankings, player details, match results, scores,
wins, losses, and match-level performance fields are not currently available.
Those features require additional SportRadar API data or exported datasets.

The current findings are descriptive and should not be interpreted as global
claims about tennis popularity or player performance. Repeated foreign keys are
relationship values, not duplicate records. Missing `parent_id` values are
reported rather than silently removed.

Dashboard integration and ZIP packaging are intentionally not included in this
step.
