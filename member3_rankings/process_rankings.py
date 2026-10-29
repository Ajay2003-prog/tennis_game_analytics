"""Convert the observed SportRadar rankings JSON into relational CSV files."""

import csv
import json
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_FILE = DATA_DIR / "doubles_rankings_raw.json"
SNAPSHOTS_FILE = DATA_DIR / "ranking_snapshots.csv"
COMPETITORS_FILE = DATA_DIR / "competitors.csv"
RANKINGS_FILE = DATA_DIR / "doubles_rankings.csv"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    if not RAW_FILE.is_file():
        print(f"ERROR: Raw response not found: {RAW_FILE}")
        return 1

    payload = json.loads(RAW_FILE.read_text(encoding="utf-8"))
    rankings = payload.get("rankings")
    if not isinstance(rankings, list) or not rankings:
        print("ERROR: Raw response has no non-empty rankings list.")
        return 1

    snapshots: list[dict] = []
    competitors_by_id: dict[str, dict] = {}
    ranking_rows: list[dict] = []
    snapshot_ids: set[str] = set()

    for group in rankings:
        required_group = {"type_id", "name", "year", "week", "gender", "competitor_rankings"}
        missing_group = required_group - group.keys()
        if missing_group:
            raise ValueError(f"Ranking group is missing fields: {sorted(missing_group)}")

        snapshot_id = f"{group['type_id']}_{group['year']}_{group['week']}_{group['gender']}"
        if snapshot_id in snapshot_ids:
            raise ValueError(f"Duplicate ranking snapshot identity: {snapshot_id}")
        snapshot_ids.add(snapshot_id)
        snapshots.append(
            {
                "ranking_snapshot_id": snapshot_id,
                "ranking_type_id": group["type_id"],
                "ranking_name": group["name"],
                "year": group["year"],
                "week": group["week"],
                "gender": group["gender"],
                "generated_at": payload.get("generated_at"),
            }
        )

        for item in group["competitor_rankings"]:
            required_item = {"rank", "movement", "points", "competitions_played", "competitor"}
            missing_item = required_item - item.keys()
            if missing_item:
                raise ValueError(f"Ranking record is missing fields: {sorted(missing_item)}")
            competitor = item["competitor"]
            # The live response contains all five documented competitor
            # fields, but country_code is absent/empty for some records.
            # Keep the field and preserve those observations as blank CSV/NULL.
            required_competitor = {"id", "name"}
            missing_competitor = required_competitor - competitor.keys()
            if missing_competitor:
                raise ValueError(
                    f"Competitor is missing fields: {sorted(missing_competitor)}"
                )

            competitor_id = str(competitor["id"])
            clean_competitor = {
                "competitor_id": competitor_id,
                "competitor_name": competitor.get("name"),
                "abbreviation": competitor.get("abbreviation"),
                "country": competitor.get("country"),
                "country_code": competitor.get("country_code"),
            }
            previous = competitors_by_id.get(competitor_id)
            if previous and previous != clean_competitor:
                raise ValueError(f"Competitor details conflict for ID: {competitor_id}")
            competitors_by_id[competitor_id] = clean_competitor

            ranking_rows.append(
                {
                    "ranking_snapshot_id": snapshot_id,
                    "competitor_id": competitor_id,
                    "rank": item.get("rank"),
                    "movement": item.get("movement"),
                    "points": item.get("points"),
                    "competitions_played": item.get("competitions_played"),
                }
            )

    write_csv(
        SNAPSHOTS_FILE,
        [
            "ranking_snapshot_id",
            "ranking_type_id",
            "ranking_name",
            "year",
            "week",
            "gender",
            "generated_at",
        ],
        snapshots,
    )
    write_csv(
        COMPETITORS_FILE,
        ["competitor_id", "competitor_name", "abbreviation", "country", "country_code"],
        list(competitors_by_id.values()),
    )
    write_csv(
        RANKINGS_FILE,
        [
            "ranking_snapshot_id",
            "competitor_id",
            "rank",
            "movement",
            "points",
            "competitions_played",
        ],
        ranking_rows,
    )

    print("SUCCESS: Ranking CSVs created from the observed JSON structure.")
    print(f"Snapshots: {len(snapshots)}")
    print(f"Unique competitors: {len(competitors_by_id)}")
    print(f"Ranking records: {len(ranking_rows)}")
    for path in (SNAPSHOTS_FILE, COMPETITORS_FILE, RANKINGS_FILE):
        print(f"Saved: {path}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {type(error).__name__}: {error}")
        sys.exit(1)
