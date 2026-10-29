"""Create useful ranking summary tables from the processed CSV files."""

import csv
from collections import defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def read_csv(name: str) -> list[dict]:
    with (DATA_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, fields: list[str], rows: list[dict]) -> None:
    with (DATA_DIR / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    snapshots = read_csv("ranking_snapshots.csv")
    rankings = read_csv("doubles_rankings.csv")
    by_snapshot = defaultdict(list)
    for row in rankings:
        by_snapshot[row["ranking_snapshot_id"]].append(row)

    summaries = []
    top_rows = []
    snapshot_by_id = {row["ranking_snapshot_id"]: row for row in snapshots}
    for snapshot_id, rows in by_snapshot.items():
        ordered = sorted(rows, key=lambda row: int(row["rank"]))
        snapshot = snapshot_by_id[snapshot_id]
        summaries.append(
            {
                "ranking_snapshot_id": snapshot_id,
                "ranking_name": snapshot["ranking_name"],
                "gender": snapshot["gender"],
                "year": snapshot["year"],
                "week": snapshot["week"],
                "ranking_record_count": len(rows),
                "unique_competitor_count": len({row["competitor_id"] for row in rows}),
                "top_rank_points": ordered[0]["points"],
            }
        )
        for row in ordered[:10]:
            top_rows.append({"ranking_name": snapshot["ranking_name"], **row})

    summary_fields = [
        "ranking_snapshot_id",
        "ranking_name",
        "gender",
        "year",
        "week",
        "ranking_record_count",
        "unique_competitor_count",
        "top_rank_points",
    ]
    top_fields = [
        "ranking_name",
        "ranking_snapshot_id",
        "competitor_id",
        "rank",
        "movement",
        "points",
        "competitions_played",
    ]
    write_csv("ranking_analysis_summary.csv", summary_fields, summaries)
    write_csv("top_10_doubles_rankings.csv", top_fields, top_rows)
    print("SUCCESS: Ranking analysis summaries created.")
    print(f"Snapshot summaries: {len(summaries)}")
    print(f"Top-10 rows: {len(top_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
