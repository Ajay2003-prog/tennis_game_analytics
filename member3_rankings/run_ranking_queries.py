"""Run the SELECT statements in member3_queries.sql against the ranking DB."""

import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "data" / "tennis_rankings.db"
SQL_FILE = BASE_DIR / "member3_queries.sql"


def main() -> int:
    sql_text = SQL_FILE.read_text(encoding="utf-8")
    statements = [part.strip() for part in sql_text.split(";") if part.strip()]
    with sqlite3.connect(DB_FILE) as connection:
        for number, statement in enumerate(statements, start=1):
            cursor = connection.execute(statement)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description or []]
            print(f"\nQUERY {number}: {len(rows)} rows")
            if columns:
                print(" | ".join(columns))
                for row in rows[:10]:
                    print(" | ".join("" if value is None else str(value) for value in row))
                if len(rows) > 10:
                    print(f"... ({len(rows) - 10} more rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
