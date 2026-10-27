
import json
import sqlite3
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

RAW_FILE = DATA_DIR / "competitions_raw.json"
CATEGORIES_FILE = DATA_DIR / "categories.csv"
COMPETITIONS_FILE = DATA_DIR / "competitions.csv"
DB_FILE = DATA_DIR / "tennis_competitions.db"


def check(condition, message):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {message}")
    return bool(condition)


def main():
    print("=" * 55)
    print("TENNIS COMPETITIONS - DATA QUALITY REPORT")
    print("=" * 55)

    errors = []

    # 1. Check that all required files exist.
    required_files = [
        RAW_FILE,
        CATEGORIES_FILE,
        COMPETITIONS_FILE,
        DB_FILE,
    ]

    for file_path in required_files:
        if not check(file_path.is_file(), f"File exists: {file_path.name}"):
            errors.append(f"Missing file: {file_path.name}")

    if errors:
        print("\nValidation stopped because required files are missing.")
        sys.exit(1)

    # 2. Load and validate the raw JSON.
    try:
        with RAW_FILE.open("r", encoding="utf-8") as file:
            raw_data = json.load(file)

        raw_competitions = raw_data.get("competitions")

        if not isinstance(raw_competitions, list):
            raise ValueError("'competitions' must be a JSON list.")

        raw_count = len(raw_competitions)
        check(True, f"Raw JSON loaded: {raw_count} competitions")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"[FAIL] Raw JSON validation: {exc}")
        sys.exit(1)

    # 3. Load CSV files.
    try:
        categories = pd.read_csv(CATEGORIES_FILE, dtype=str)
        competitions = pd.read_csv(COMPETITIONS_FILE, dtype=str)
        check(True, "Both CSV files loaded successfully")
    except Exception as exc:
        print(f"[FAIL] CSV loading: {exc}")
        sys.exit(1)

    # 4. Check required columns.
    category_columns = {"category_id", "category_name"}
    competition_columns = {
        "competition_id",
        "competition_name",
        "parent_id",
        "type",
        "gender",
        "category_id",
    }

    if not check(
        category_columns.issubset(categories.columns),
        "Categories CSV has all required columns",
    ):
        errors.append("Missing required category columns")

    if not check(
        competition_columns.issubset(competitions.columns),
        "Competitions CSV has all required columns",
    ):
        errors.append("Missing required competition columns")

    if errors:
        print("\nCannot continue: required columns are missing.")
        sys.exit(1)

    # 5. Check row counts.
    check(
        len(competitions) == raw_count,
        f"Competition count matches raw JSON ({len(competitions)}/{raw_count})",
    ) or errors.append("Raw JSON and competition CSV counts differ")

    # 6. Check duplicate IDs.
    duplicate_category_ids = categories["category_id"].duplicated().sum()
    duplicate_competition_ids = competitions[
        "competition_id"
    ].duplicated().sum()

    check(
        duplicate_category_ids == 0,
        f"No duplicate category IDs ({duplicate_category_ids})",
    ) or errors.append("Duplicate category IDs found")

    check(
        duplicate_competition_ids == 0,
        f"No duplicate competition IDs ({duplicate_competition_ids})",
    ) or errors.append("Duplicate competition IDs found")

    # 7. Check required fields for missing or blank values.
    required_category_fields = ["category_id", "category_name"]
    required_competition_fields = [
        "competition_id",
        "competition_name",
        "type",
        "gender",
        "category_id",
    ]

    for column in required_category_fields:
        missing = (
            categories[column].isna()
            | categories[column].str.strip().eq("")
        ).sum()

        check(
            missing == 0,
            f"Categories.{column}: {missing} missing or blank",
        ) or errors.append(f"Missing category field: {column}")

    for column in required_competition_fields:
        missing = (
            competitions[column].isna()
            | competitions[column].str.strip().eq("")
        ).sum()

        check(
            missing == 0,
            f"Competitions.{column}: {missing} missing or blank",
        ) or errors.append(f"Missing competition field: {column}")

    # 8. Check category references in the CSV.
    category_ids = set(categories["category_id"].dropna())
    linked_category_ids = set(competitions["category_id"].dropna())

    unknown_categories = linked_category_ids - category_ids

    check(
        len(unknown_categories) == 0,
        f"CSV category references valid ({len(unknown_categories)} unknown)",
    ) or errors.append("Unknown category references found in CSV")

    # 9. Check competition types.
    print("\nCompetition type distribution:")
    print(competitions["type"].value_counts(dropna=False).to_string())

    # 10. Check database counts and foreign keys.
    try:
        with sqlite3.connect(DB_FILE) as connection:
            category_count = connection.execute(
                "SELECT COUNT(*) FROM Categories"
            ).fetchone()[0]

            competition_count = connection.execute(
                "SELECT COUNT(*) FROM Competitions"
            ).fetchone()[0]

            violations = connection.execute(
                "PRAGMA foreign_key_check"
            ).fetchall()

            check(
                category_count == len(categories),
                f"Database category count matches CSV ({category_count})",
            ) or errors.append("Database category count mismatch")

            check(
                competition_count == len(competitions),
                f"Database competition count matches CSV ({competition_count})",
            ) or errors.append("Database competition count mismatch")

            check(
                len(violations) == 0,
                f"Database foreign key violations: {len(violations)}",
            ) or errors.append("Database foreign key violations found")

    except sqlite3.Error as exc:
        print(f"[FAIL] Database validation: {exc}")
        errors.append(f"Database error: {exc}")

    # 11. Final report.
    print("\n" + "=" * 55)

    if errors:
        print(f"VALIDATION FAILED: {len(errors)} issue(s) found.")
        for error in errors:
            print("-", error)
        sys.exit(1)
    else:
        print("VALIDATION PASSED: All checks completed successfully.")
        print("No files were modified.")
        print("=" * 55)


if __name__ == "__main__":
    main()
