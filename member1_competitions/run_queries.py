
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "data" / "tennis_competitions.db"
SQL_FILE = BASE_DIR / "member1_queries.sql"

def main():
    if not SQL_FILE.is_file():
        print(f"ERROR: SQL file not found: {SQL_FILE}")
        return

    sql_text = SQL_FILE.read_text(encoding="utf-8")
    queries = [
        part.strip()
        for part in sql_text.split(";")
        if part.strip() and any(line.strip().upper().startswith("SELECT")
        for line in part.splitlines())
    ]

    if len(queries) != 7:
        print(f"ERROR: Expected 7 queries, found {len(queries)}.")
        print("Check that member1_queries.sql contains all seven SELECT statements.")
        return

    try:
        with sqlite3.connect(DB_FILE) as connection:
            print("=" * 55)
            print("MEMBER 1 - SQL QUERY TEST REPORT")
            print("=" * 55)

            for number, query in enumerate(queries, start=1):
                cursor = connection.execute(query)
                rows = cursor.fetchall()
                columns = [item[0] for item in cursor.description or []]

                print(f"\nQuery {number}: PASS")
                print(f"Rows returned: {len(rows)}")
                print("Columns:", ", ".join(columns))

                for row in rows[:3]:
                    print(" ", row)

                if len(rows) > 3:
                    print(f"  ... and {len(rows) - 3} more rows")

            print("\n" + "=" * 55)
            print("All 7 SQL queries executed successfully.")
            print("=" * 55)

    except sqlite3.Error as error:
        print(f"\nSQL ERROR: {error}")

if __name__ == "__main__":
    main()
