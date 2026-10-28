"""Flatten the raw complexes JSON into complexes.csv and venues.csv.

Venues are nested inside each complex in the API response, so every venue
row carries the complex_id of the complex it came from.

Cleaning rules (also write these in the README):
- A complex or venue without an id or name is rejected and logged.
- Missing city, country or timezone is filled with "Unknown".
- A missing or invalid country_code (not exactly 3 letters) becomes "UNK".
- Duplicate IDs are removed (first one kept) and counted.
Every rejected row is written to data/rejected_rows.csv with a reason.
"""

import json
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
INPUT_FILE = DATA_DIR / "complexes_venues_raw.json"

COMPLEXES_FILE = DATA_DIR / "complexes.csv"
VENUES_FILE = DATA_DIR / "venues.csv"
REJECTED_FILE = DATA_DIR / "rejected_rows.csv"

COMPLEX_COLUMNS = ["complex_id", "complex_name"]
VENUE_COLUMNS = [
    "venue_id",
    "venue_name",
    "city_name",
    "country_name",
    "country_code",
    "timezone",
    "complex_id",
]


def clean_text(value):
    """Return a stripped string, or None when the value is empty."""
    if value is None:
        return None

    text = str(value).strip()
    return text if text else None


def main():
    if not INPUT_FILE.exists():
        sys.exit(
            f"ERROR: {INPUT_FILE} not found. "
            "Run fetch_complexes_venues.py first."
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    raw_complexes = data.get("complexes", [])

    if not isinstance(raw_complexes, list):
        sys.exit("ERROR: Invalid complexes data in the JSON file.")

    complex_rows = []
    venue_rows = []
    rejected_rows = []
    raw_venue_count = 0

    # How many missing values were filled, per column.
    filled = {
        "city_name": 0,
        "country_name": 0,
        "timezone": 0,
        "country_code": 0,
    }

    for item in raw_complexes:
        if not isinstance(item, dict):
            continue

        complex_id = clean_text(item.get("id"))
        complex_name = clean_text(item.get("name"))
        raw_venues = item.get("venues") or []

        if isinstance(raw_venues, list):
            raw_venue_count += len(raw_venues)

        if not complex_id or not complex_name:
            rejected_rows.append({
                "table": "complexes",
                "id": complex_id,
                "reason": "missing complex id or name",
            })
            # Venues of a rejected complex cannot be linked, so log them.
            if isinstance(raw_venues, list):
                for venue in raw_venues:
                    rejected_rows.append({
                        "table": "venues",
                        "id": clean_text(
                            venue.get("id") if isinstance(venue, dict) else None
                        ),
                        "reason": "parent complex was rejected",
                    })
            continue

        complex_rows.append({
            "complex_id": complex_id,
            "complex_name": complex_name,
        })

        if not isinstance(raw_venues, list):
            continue

        for venue in raw_venues:
            if not isinstance(venue, dict):
                continue

            venue_id = clean_text(venue.get("id"))
            venue_name = clean_text(venue.get("name"))

            if not venue_id or not venue_name:
                rejected_rows.append({
                    "table": "venues",
                    "id": venue_id,
                    "reason": "missing venue id or name",
                })
                continue

            city_name = clean_text(venue.get("city_name"))
            country_name = clean_text(venue.get("country_name"))
            timezone = clean_text(venue.get("timezone"))
            country_code = clean_text(venue.get("country_code"))

            if city_name is None:
                city_name = "Unknown"
                filled["city_name"] += 1

            if country_name is None:
                country_name = "Unknown"
                filled["country_name"] += 1

            if timezone is None:
                timezone = "Unknown"
                filled["timezone"] += 1

            if country_code is None or len(country_code) != 3:
                country_code = "UNK"
                filled["country_code"] += 1
            else:
                country_code = country_code.upper()

            venue_rows.append({
                "venue_id": venue_id,
                "venue_name": venue_name,
                "city_name": city_name,
                "country_name": country_name,
                "country_code": country_code,
                "timezone": timezone,
                "complex_id": complex_id,
            })

    complexes_df = pd.DataFrame(complex_rows, columns=COMPLEX_COLUMNS)
    venues_df = pd.DataFrame(venue_rows, columns=VENUE_COLUMNS)

    complexes_before = len(complexes_df)
    venues_before = len(venues_df)

    complexes_df = complexes_df.drop_duplicates(
        subset=["complex_id"],
        keep="first",
    )
    venues_df = venues_df.drop_duplicates(
        subset=["venue_id"],
        keep="first",
    )

    duplicate_complexes = complexes_before - len(complexes_df)
    duplicate_venues = venues_before - len(venues_df)

    # Save CSV files.
    complexes_df.to_csv(COMPLEXES_FILE, index=False, encoding="utf-8")
    venues_df.to_csv(VENUES_FILE, index=False, encoding="utf-8")

    if rejected_rows:
        pd.DataFrame(rejected_rows).to_csv(
            REJECTED_FILE,
            index=False,
            encoding="utf-8",
        )
    elif REJECTED_FILE.exists():
        REJECTED_FILE.unlink()

    print("SUCCESS: Complexes and venues processed.")
    print("Raw complexes received:", len(raw_complexes))
    print("Raw venues received:", raw_venue_count)
    print("Unique complexes saved:", len(complexes_df))
    print("Unique venues saved:", len(venues_df))
    print("Duplicate complexes removed:", duplicate_complexes)
    print("Duplicate venues removed:", duplicate_venues)
    print("Rejected rows (see rejected_rows.csv):", len(rejected_rows))

    print("\nMissing values filled:")
    for column, count in filled.items():
        print(f"  {column}: {count}")

    print("Complexes CSV:", COMPLEXES_FILE)
    print("Venues CSV:", VENUES_FILE)

    print("\nVenue data preview:")
    print(venues_df.head().to_string(index=False))


if __name__ == "__main__":
    main()
