"""Validate processed ranking CSVs and the SQLite relationships."""

import csv
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORT_FILE = BASE_DIR / "validation_report.md"


def read_csv(name: str) -> list[dict]:
    with (DATA_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def missing_count(rows: list[dict], fields: list[str]) -> int:
    return sum(1 for row in rows for field in fields if not str(row.get(field, "")).strip())


def main() -> int:
    snapshots = read_csv("ranking_snapshots.csv")
    competitors = read_csv("competitors.csv")
    rankings = read_csv("doubles_rankings.csv")
    snapshot_ids = [row["ranking_snapshot_id"] for row in snapshots]
    competitor_ids = [row["competitor_id"] for row in competitors]
    ranking_keys = [
        (row["ranking_snapshot_id"], row["competitor_id"]) for row in rankings
    ]

    with sqlite3.connect(DATA_DIR / "tennis_rankings.db") as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        fk_violations = connection.execute("PRAGMA foreign_key_check").fetchall()
        orphan_snapshots = connection.execute(
            """SELECT COUNT(*) FROM DoublesRankings AS r
               LEFT JOIN RankingSnapshots AS s
                 ON s.ranking_snapshot_id = r.ranking_snapshot_id
               WHERE s.ranking_snapshot_id IS NULL"""
        ).fetchone()[0]
        orphan_competitors = connection.execute(
            """SELECT COUNT(*) FROM DoublesRankings AS r
               LEFT JOIN Competitors AS c ON c.competitor_id = r.competitor_id
               WHERE c.competitor_id IS NULL"""
        ).fetchone()[0]
        invalid_ranks = connection.execute(
            "SELECT COUNT(*) FROM DoublesRankings WHERE rank < 1"
        ).fetchone()[0]
        negative_points = connection.execute(
            "SELECT COUNT(*) FROM DoublesRankings WHERE points < 0"
        ).fetchone()[0]

    checks = [
        ("snapshot_rows", len(snapshots)),
        ("competitor_rows", len(competitors)),
        ("ranking_rows", len(rankings)),
        ("snapshot_missing_required_values", missing_count(snapshots, ["ranking_snapshot_id", "ranking_name", "gender"])),
        ("competitor_missing_required_values", missing_count(competitors, ["competitor_id", "competitor_name"])),
        ("ranking_missing_required_values", missing_count(rankings, ["ranking_snapshot_id", "competitor_id", "rank"])),
        ("duplicate_snapshot_ids", len(snapshot_ids) - len(set(snapshot_ids))),
        ("duplicate_competitor_ids", len(competitor_ids) - len(set(competitor_ids))),
        ("duplicate_ranking_keys", len(ranking_keys) - len(set(ranking_keys))),
        ("foreign_key_violations", len(fk_violations)),
        ("orphan_snapshot_references", orphan_snapshots),
        ("orphan_competitor_references", orphan_competitors),
        ("invalid_rank_values", invalid_ranks),
        ("negative_points", negative_points),
    ]
    passed = all(value == 0 for name, value in checks if name not in {"snapshot_rows", "competitor_rows", "ranking_rows"})
    lines = [
        "# Doubles Rankings Validation Report",
        "",
        f"Overall result: {'PASS' if passed else 'FAIL'}",
        "",
        "| Check | Value |",
        "|---|---:|",
    ]
    lines.extend(f"| {name} | {value} |" for name, value in checks)
    lines.extend(
        [
            "",
            "Repeated competitor IDs across ranking snapshots are valid relationships;"
            " duplicate ranking keys are treated as invalid duplicate records.",
        ]
    )
    REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("SUCCESS: Ranking validation completed.")
    for name, value in checks:
        print(f"{name}: {value}")
    print(f"Report: {REPORT_FILE}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
