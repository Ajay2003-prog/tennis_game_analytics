
import json
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
INPUT_FILE = DATA_DIR / "competitions_raw.json"

CATEGORIES_FILE = DATA_DIR / "categories.csv"
COMPETITIONS_FILE = DATA_DIR / "competitions.csv"


def main():
    if not INPUT_FILE.exists():
        sys.exit(
            f"ERROR: {INPUT_FILE} not found. "
            "Run fetch_competitions.py first."
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    raw_competitions = data.get("competitions", [])

    if not isinstance(raw_competitions, list):
        sys.exit("ERROR: Invalid competitions data in the JSON file.")

    category_rows = []
    competition_rows = []
    missing_category_count = 0

    for item in raw_competitions:
        if not isinstance(item, dict):
            continue

        category = item.get("category") or {}

        category_id = category.get("id")
        category_name = category.get("name")

        if category_id and category_name:
            category_rows.append({
                "category_id": str(category_id),
                "category_name": str(category_name),
            })
        else:
            missing_category_count += 1

        competition_id = item.get("id")
        competition_name = item.get("name")

        if not competition_id or not competition_name:
            continue

        competition_rows.append({
            "competition_id": str(competition_id),
            "competition_name": str(competition_name),
            "parent_id": item.get("parent_id"),
            "type": item.get("type") or "unknown",
            "gender": item.get("gender") or "unknown",
            "category_id": str(category_id) if category_id else None,
        })

    # Build category table and remove duplicate category IDs.
    categories_df = pd.DataFrame(
        category_rows,
        columns=["category_id", "category_name"],
    )

    if not categories_df.empty:
        categories_df = categories_df.drop_duplicates(
            subset=["category_id"],
            keep="first",
        )

    # Build competition table and remove duplicate competition IDs.
    competitions_df = pd.DataFrame(
        competition_rows,
        columns=[
            "competition_id",
            "competition_name",
            "parent_id",
            "type",
            "gender",
            "category_id",
        ],
    )

    if not competitions_df.empty:
        competitions_df["parent_id"] = competitions_df[
            "parent_id"
        ].apply(lambda value: str(value) if pd.notna(value) else None)

        competitions_df = competitions_df.drop_duplicates(
            subset=["competition_id"],
            keep="first",
        )

    # Save CSV files.
    categories_df.to_csv(CATEGORIES_FILE, index=False, encoding="utf-8")
    competitions_df.to_csv(
        COMPETITIONS_FILE,
        index=False,
        encoding="utf-8",
    )

    print("SUCCESS: Competition data processed.")
    print("Raw competitions received:", len(raw_competitions))
    print("Unique categories:", len(categories_df))
    print("Unique competitions:", len(competitions_df))
    print("Competitions without category details:", missing_category_count)
    print("Categories CSV:", CATEGORIES_FILE)
    print("Competitions CSV:", COMPETITIONS_FILE)

    print("\nCompetition data preview:")
    print(competitions_df.head().to_string(index=False))


if __name__ == "__main__":
    main()
