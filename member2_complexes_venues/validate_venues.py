"""Validate the complexes and venues data from raw JSON through to SQLite.

Read-only: this script never modifies any file or table.
Run after create_venue_tables.py.
"""

import json
import sqlite3
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

RAW_FILE = DATA_DIR / "complexes_venues_raw.json"
COMPLEXES_FILE = DATA_DIR / "complexes.csv"
VENUES_FILE = DATA_DIR / "venues.csv"
DB_FILE = DATA_DIR / "tennis_venues.db"


def check(condition, message):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {message}")
    return bool(condition)


def has_text(value):
    """True when the value is a non-blank string or number."""
    return value is not None and str(value).strip() != ""


def main():
    print("=" * 55)
    print("TENNIS COMPLEXES AND VENUES - DATA QUALITY REPORT")
    print("=" * 55)

    errors = []

    # 1. Check that all required files exist.
    for file_path in [RAW_FILE, COMPLEXES_FILE, VENUES_FILE, DB_FILE]:
        if not check(file_path.is_file(), f"File exists: {file_path.name}"):
            errors.append(f"Missing file: {file_path.name}")

    if errors:
        print("\nValidation stopped because required files are missing.")
        sys.exit(1)

    # 2. Load the raw JSON and count what SHOULD be saved.
    # This is computed independently of process_complexes_venues.py.
    try:
        with RAW_FILE.open("r", encoding="utf-8") as file:
            raw_data = json.load(file)

        raw_complexes = raw_data.get("complexes")

        if not isinstance(raw_complexes, list):
            raise ValueError("'complexes' must be a JSON list.")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"[FAIL] Raw JSON validation: {exc}")
        sys.exit(1)

    raw_venue_count = 0
    valid_complex_ids = set()
    valid_venue_ids = set()

    for item in raw_complexes:
        if not isinstance(item, dict):
            continue

        venues = item.get("venues") or []
        raw_venue_count += len(venues) if isinstance(venues, list) else 0

        if not (has_text(item.get("id")) and has_text(item.get("name"))):
            continue

        valid_complex_ids.add(str(item["id"]).strip())

        for venue in venues if isinstance(venues, list) else []:
            if (
                isinstance(venue, dict)
                and has_text(venue.get("id"))
                and has_text(venue.get("name"))
            ):
                valid_venue_ids.add(str(venue["id"]).strip())

    check(True, f"Raw JSON loaded: {len(raw_complexes)} complexes, "
                f"{raw_venue_count} venues")

    # 3. Load CSV files.
    try:
        complexes = pd.read_csv(COMPLEXES_FILE, dtype=str)
        venues = pd.read_csv(VENUES_FILE, dtype=str)
        check(True, "Both CSV files loaded successfully")
    except Exception as exc:
        print(f"[FAIL] CSV loading: {exc}")
        sys.exit(1)

    # 4. Check required columns.
    complex_columns = {"complex_id", "complex_name"}
    venue_columns = {
        "venue_id",
        "venue_name",
        "city_name",
        "country_name",
        "country_code",
        "timezone",
        "complex_id",
    }

    if not check(
        complex_columns.issubset(complexes.columns),
        "Complexes CSV has all required columns",
    ):
        errors.append("Missing required complex columns")

    if not check(
        venue_columns.issubset(venues.columns),
        "Venues CSV has all required columns",
    ):
        errors.append("Missing required venue columns")

    if errors:
        print("\nCannot continue: required columns are missing.")
        sys.exit(1)

    # 5. Check row counts against the raw JSON.
    check(
        len(complexes) == len(valid_complex_ids),
        f"Complex count matches valid raw complexes "
        f"({len(complexes)}/{len(valid_complex_ids)})",
    ) or errors.append("Complex count differs from raw JSON")

    check(
        len(venues) == len(valid_venue_ids),
        f"Venue count matches valid raw venues "
        f"({len(venues)}/{len(valid_venue_ids)})",
    ) or errors.append("Venue count differs from raw JSON")

    skipped = raw_venue_count - len(venues)
    print(f"       Raw venues not saved (duplicates or rejected): {skipped}")

    # 6. Check duplicate IDs.
    duplicate_complexes = complexes["complex_id"].duplicated().sum()
    duplicate_venues = venues["venue_id"].duplicated().sum()

    check(
        duplicate_complexes == 0,
        f"No duplicate complex IDs ({duplicate_complexes})",
    ) or errors.append("Duplicate complex IDs found")

    check(
        duplicate_venues == 0,
        f"No duplicate venue IDs ({duplicate_venues})",
    ) or errors.append("Duplicate venue IDs found")

    # 7. Check required fields for missing or blank values.
    for column in ["complex_id", "complex_name"]:
        missing = (
            complexes[column].isna() | complexes[column].str.strip().eq("")
        ).sum()
        check(
            missing == 0,
            f"Complexes.{column}: {missing} missing or blank",
        ) or errors.append(f"Missing complex field: {column}")

    for column in sorted(venue_columns):
        missing = (
            venues[column].isna() | venues[column].str.strip().eq("")
        ).sum()
        check(
            missing == 0,
            f"Venues.{column}: {missing} missing or blank",
        ) or errors.append(f"Missing venue field: {column}")

    # 8. Check country_code length (CHAR(3)).
    bad_codes = (venues["country_code"].str.len() != 3).sum()
    check(
        bad_codes == 0,
        f"country_code is exactly 3 characters ({bad_codes} invalid)",
    ) or errors.append("Invalid country_code length found")

    # 9. Check venue -> complex references.
    unknown_complexes = set(venues["complex_id"].dropna()) - set(
        complexes["complex_id"]
    )
    check(
        len(unknown_complexes) == 0,
        f"Every venue links to a known complex ({len(unknown_complexes)} unknown)",
    ) or errors.append("Venues reference unknown complexes")

    # 10. Show how many placeholder values were used.
    print("\nPlaceholder values used (for the data-quality table):")
    for column, placeholder in [
        ("city_name", "Unknown"),
        ("country_name", "Unknown"),
        ("timezone", "Unknown"),
        ("country_code", "UNK"),
    ]:
        count = (venues[column] == placeholder).sum()
        print(f"  {column} = '{placeholder}': {count}")

    # 11. Quick exploratory summary.
    print("\nExploratory summary:")
    print("  Complexes:", len(complexes))
    print("  Venues:", len(venues))
    print("  Countries:", venues["country_name"].nunique())
    print("  Timezones:", venues["timezone"].nunique())

    complexes_with_venues = venues["complex_id"].nunique()
    print("  Complexes with no venues:", len(complexes) - complexes_with_venues)

    print("\nTop 5 countries by venue count:")
    print(venues["country_name"].value_counts().head(5).to_string())

    # 12. Check database counts and foreign keys.
    try:
        with sqlite3.connect(DB_FILE) as connection:
            complex_count = connection.execute(
                "SELECT COUNT(*) FROM Complexes"
            ).fetchone()[0]

            venue_count = connection.execute(
                "SELECT COUNT(*) FROM Venues"
            ).fetchone()[0]

            violations = connection.execute(
                "PRAGMA foreign_key_check"
            ).fetchall()

            check(
                complex_count == len(complexes),
                f"Database complex count matches CSV ({complex_count})",
            ) or errors.append("Database complex count mismatch")

            check(
                venue_count == len(venues),
                f"Database venue count matches CSV ({venue_count})",
            ) or errors.append("Database venue count mismatch")

            check(
                len(violations) == 0,
                f"Database foreign key violations: {len(violations)}",
            ) or errors.append("Database foreign key violations found")

    except sqlite3.Error as exc:
        print(f"[FAIL] Database validation: {exc}")
        errors.append(f"Database error: {exc}")

    # 13. Final report.
    print("\n" + "=" * 55)

    if errors:
        print(f"VALIDATION FAILED: {len(errors)} issue(s) found.")
        for error in errors:
            print("-", error)
        sys.exit(1)

    print("VALIDATION PASSED: All checks completed successfully.")
    print("No files were modified.")
    print("=" * 55)


if __name__ == "__main__":
    main()
