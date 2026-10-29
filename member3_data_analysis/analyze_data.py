"""Read-only analysis of the existing SportRadar tennis CSV datasets.

This script reads the datasets from the existing team folders. It does not
copy, move, or modify those source files. Numerical summary tables are saved
under member3_data_analysis/outputs/.
"""

from pathlib import Path

import pandas as pd


ANALYSIS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = ANALYSIS_DIR.parent / "tennis_game_analytics-main"
OUTPUT_DIR = ANALYSIS_DIR / "outputs"

DATA_PATHS = {
    "competitions": PROJECT_DIR / "member1_competitions" / "data" / "competitions.csv",
    "categories": PROJECT_DIR / "member1_competitions" / "data" / "categories.csv",
    "complexes": PROJECT_DIR / "member2_complexes_venues" / "data" / "complexes.csv",
    "venues": PROJECT_DIR / "member2_complexes_venues" / "data" / "venues.csv",
}

PRIMARY_ID_COLUMNS = {
    "competitions": "competition_id",
    "categories": "category_id",
    "complexes": "complex_id",
    "venues": "venue_id",
}


def print_heading(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def load_datasets() -> dict[str, pd.DataFrame]:
    """Load the four source CSV files without changing them."""
    missing_files = [str(path) for path in DATA_PATHS.values() if not path.exists()]
    if missing_files:
        raise FileNotFoundError("Missing source file(s):\n" + "\n".join(missing_files))

    return {name: pd.read_csv(path) for name, path in DATA_PATHS.items()}


def dataset_quality_summary(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Summarize row counts, missing values, and primary-key quality."""
    rows: list[dict[str, object]] = []

    for name, frame in datasets.items():
        primary_id = PRIMARY_ID_COLUMNS[name]
        id_values = frame[primary_id].dropna()
        missing_values = int(frame.isna().sum().sum())
        rows.append(
            {
                "dataset": name,
                "rows": len(frame),
                "columns": len(frame.columns),
                "missing_value_cells": missing_values,
                "primary_id_column": primary_id,
                "primary_id_missing": int(frame[primary_id].isna().sum()),
                "primary_id_unique_values": int(id_values.nunique()),
                "primary_id_duplicate_rows_after_first": int(id_values.duplicated().sum()),
                "duplicate_entire_rows": int(frame.duplicated().sum()),
            }
        )

    return pd.DataFrame(rows)


def foreign_key_summary(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Show relationship-column repetition without calling it duplicate records."""
    relationship_columns = {
        "competitions.parent_id": (datasets["competitions"], "parent_id"),
        "competitions.category_id": (datasets["competitions"], "category_id"),
        "venues.complex_id": (datasets["venues"], "complex_id"),
    }
    rows: list[dict[str, object]] = []

    for label, (frame, column) in relationship_columns.items():
        values = frame[column].dropna()
        rows.append(
            {
                "relationship_column": label,
                "missing_values": int(frame[column].isna().sum()),
                "non_null_rows": len(values),
                "unique_values": int(values.nunique()),
                "repeated_foreign_key_rows": int(values.duplicated().sum()),
                "interpretation": "Repeated values are expected for a foreign key.",
            }
        )

    return pd.DataFrame(rows)


def competition_summaries(
    competitions: pd.DataFrame, categories: pd.DataFrame
) -> dict[str, pd.DataFrame]:
    """Calculate competition distributions requested for Member 3."""
    with_category_names = competitions.merge(
        categories[["category_id", "category_name"]],
        on="category_id",
        how="left",
        validate="many_to_one",
    )

    by_type = (
        competitions.groupby("type", dropna=False)
        .size()
        .reset_index(name="competition_count")
        .sort_values("competition_count", ascending=False)
    )
    by_gender = (
        competitions.groupby("gender", dropna=False)
        .size()
        .reset_index(name="competition_count")
        .sort_values("competition_count", ascending=False)
    )
    by_category = (
        with_category_names.groupby(["category_id", "category_name"], dropna=False)
        .size()
        .reset_index(name="competition_count")
        .sort_values("competition_count", ascending=False)
    )

    return {
        "competition_counts_by_type": by_type,
        "competition_counts_by_gender": by_gender,
        "competition_counts_by_category": by_category,
    }


def venue_summaries(venues: pd.DataFrame, complexes: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Calculate venue counts by country and by complex."""
    by_country = (
        venues.groupby(["country_name", "country_code"], dropna=False)
        .size()
        .reset_index(name="venue_count")
        .sort_values("venue_count", ascending=False)
    )

    with_complex_names = venues.merge(
        complexes[["complex_id", "complex_name"]],
        on="complex_id",
        how="left",
        validate="many_to_one",
    )
    by_complex = (
        with_complex_names.groupby(["complex_id", "complex_name"], dropna=False)
        .size()
        .reset_index(name="venue_count")
        .sort_values("venue_count", ascending=False)
    )

    return {
        "venue_counts_by_country": by_country,
        "venues_per_complex": by_complex,
    }


def print_table(title: str, table: pd.DataFrame, display_rows: int | None = None) -> None:
    """Print a summary table, optionally limiting terminal rows."""
    print_heading(title)
    if display_rows is not None and len(table) > display_rows:
        print(table.head(display_rows).to_string(index=False))
        print(f"... showing the first {display_rows} rows; the complete table is saved to CSV.")
    else:
        print(table.to_string(index=False))


def save_table(table: pd.DataFrame, filename: str) -> None:
    """Save one generated summary table inside the Member 3 folder."""
    table.to_csv(OUTPUT_DIR / filename, index=False)


def main() -> None:
    """Run the complete numerical analysis."""
    datasets = load_datasets()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    quality = dataset_quality_summary(datasets)
    foreign_keys = foreign_key_summary(datasets)
    competition_tables = competition_summaries(
        datasets["competitions"], datasets["categories"]
    )
    venue_tables = venue_summaries(datasets["venues"], datasets["complexes"])

    print_heading("DATASET QUALITY SUMMARY")
    print(quality.to_string(index=False))
    print_table("FOREIGN-KEY RELATIONSHIP SUMMARY", foreign_keys)
    print_table("COMPETITION COUNTS BY TYPE", competition_tables["competition_counts_by_type"])
    print_table(
        "COMPETITION COUNTS BY GENDER", competition_tables["competition_counts_by_gender"]
    )
    print_table(
        "COMPETITION COUNTS BY CATEGORY",
        competition_tables["competition_counts_by_category"],
    )
    print_table("VENUE COUNTS BY COUNTRY", venue_tables["venue_counts_by_country"], 20)
    print_table("VENUES PER COMPLEX", venue_tables["venues_per_complex"], 20)

    save_table(quality, "dataset_quality_summary.csv")
    save_table(foreign_keys, "foreign_key_summary.csv")
    for name, table in competition_tables.items():
        save_table(table, f"{name}.csv")
    for name, table in venue_tables.items():
        save_table(table, f"{name}.csv")

    print_heading("OUTPUTS SAVED")
    for output_path in sorted(OUTPUT_DIR.glob("*.csv")):
        print(output_path)
    print("\nRanking and match-result datasets are not available in the current project files.")


if __name__ == "__main__":
    main()
