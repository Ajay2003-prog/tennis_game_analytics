"""Create and populate the Member 3 doubles rankings SQLite database."""

import csv
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_FILE = DATA_DIR / "tennis_rankings.db"


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def nullable(value: str | None):
    return None if value in (None, "") else value


def main() -> int:
    snapshots = read_csv(DATA_DIR / "ranking_snapshots.csv")
    competitors = read_csv(DATA_DIR / "competitors.csv")
    rankings = read_csv(DATA_DIR / "doubles_rankings.csv")

    with sqlite3.connect(DB_FILE) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            """
            DROP TABLE IF EXISTS DoublesRankings;
            DROP TABLE IF EXISTS Competitors;
            DROP TABLE IF EXISTS RankingSnapshots;

            CREATE TABLE RankingSnapshots (
                ranking_snapshot_id VARCHAR(100) PRIMARY KEY,
                ranking_type_id INTEGER NOT NULL,
                ranking_name VARCHAR(100) NOT NULL,
                year INTEGER NOT NULL,
                week INTEGER NOT NULL,
                gender VARCHAR(20) NOT NULL,
                generated_at VARCHAR(50)
            );

            CREATE TABLE Competitors (
                competitor_id VARCHAR(100) PRIMARY KEY,
                competitor_name VARCHAR(200) NOT NULL,
                abbreviation VARCHAR(20),
                country VARCHAR(100),
                country_code CHAR(3)
            );

            CREATE TABLE DoublesRankings (
                ranking_snapshot_id VARCHAR(100) NOT NULL,
                competitor_id VARCHAR(100) NOT NULL,
                rank INTEGER NOT NULL,
                movement INTEGER,
                points INTEGER,
                competitions_played INTEGER,
                PRIMARY KEY (ranking_snapshot_id, competitor_id),
                FOREIGN KEY (ranking_snapshot_id)
                    REFERENCES RankingSnapshots(ranking_snapshot_id),
                FOREIGN KEY (competitor_id)
                    REFERENCES Competitors(competitor_id)
            );

            CREATE INDEX idx_doubles_rankings_rank
                ON DoublesRankings(rank);
            CREATE INDEX idx_doubles_rankings_competitor
                ON DoublesRankings(competitor_id);
            """
        )

        connection.executemany(
            """INSERT INTO RankingSnapshots VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    row["ranking_snapshot_id"],
                    int(row["ranking_type_id"]),
                    row["ranking_name"],
                    int(row["year"]),
                    int(row["week"]),
                    row["gender"],
                    nullable(row["generated_at"]),
                )
                for row in snapshots
            ],
        )
        connection.executemany(
            """INSERT INTO Competitors VALUES (?, ?, ?, ?, ?)""",
            [
                (
                    row["competitor_id"],
                    row["competitor_name"],
                    nullable(row["abbreviation"]),
                    nullable(row["country"]),
                    nullable(row["country_code"]),
                )
                for row in competitors
            ],
        )
        connection.executemany(
            """INSERT INTO DoublesRankings VALUES (?, ?, ?, ?, ?, ?)""",
            [
                (
                    row["ranking_snapshot_id"],
                    row["competitor_id"],
                    int(row["rank"]),
                    int(row["movement"]) if row["movement"] else None,
                    int(row["points"]) if row["points"] else None,
                    int(row["competitions_played"])
                    if row["competitions_played"]
                    else None,
                )
                for row in rankings
            ],
        )

        violations = connection.execute("PRAGMA foreign_key_check").fetchall()
        counts = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ("RankingSnapshots", "Competitors", "DoublesRankings")
        }
        print("SUCCESS: SQLite ranking database created and verified.")
        print(f"Database: {DB_FILE}")
        for table, count in counts.items():
            print(f"{table}: {count}")
        print(f"Foreign key violations: {len(violations)}")
        if violations:
            raise RuntimeError(f"Foreign key violations found: {violations[:3]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
