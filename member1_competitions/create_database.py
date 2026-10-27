
import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

DB_FILE = DATA_DIR / "tennis_competitions.db"
CATEGORIES_FILE = DATA_DIR / "categories.csv"
COMPETITIONS_FILE = DATA_DIR / "competitions.csv"


def main():
    # Validate input files.
    if not CATEGORIES_FILE.exists():
        raise FileNotFoundError(
            f"Categories file not found: {CATEGORIES_FILE}"
        )

    if not COMPETITIONS_FILE.exists():
        raise FileNotFoundError(
            f"Competitions file not found: {COMPETITIONS_FILE}"
        )

    # Load CSV data as strings to preserve IDs.
    categories = pd.read_csv(CATEGORIES_FILE, dtype=str)
    competitions = pd.read_csv(COMPETITIONS_FILE, dtype=str)

    # Convert pandas missing values to Python None / SQL NULL.
    categories = categories.astype(object).where(
        pd.notna(categories), None
    )
    competitions = competitions.astype(object).where(
        pd.notna(competitions), None
    )

    required_category_columns = {"category_id", "category_name"}
    required_competition_columns = {
        "competition_id",
        "competition_name",
        "parent_id",
        "type",
        "gender",
        "category_id",
    }

    if not required_category_columns.issubset(categories.columns):
        raise ValueError("Categories CSV has missing required columns.")

    if not required_competition_columns.issubset(competitions.columns):
        raise ValueError("Competitions CSV has missing required columns.")

    with sqlite3.connect(DB_FILE) as connection:
        # Enable foreign key enforcement for subsequent operations.
        connection.execute("PRAGMA foreign_keys = ON")

        # Recreate tables for a clean, repeatable database build.
        connection.execute("DROP TABLE IF EXISTS Competitions")
        connection.execute("DROP TABLE IF EXISTS Categories")

        connection.execute("""
            CREATE TABLE Categories (
                category_id VARCHAR(50) PRIMARY KEY,
                category_name VARCHAR(100) NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE Competitions (
                competition_id VARCHAR(50) PRIMARY KEY,
                competition_name VARCHAR(100) NOT NULL,
                parent_id VARCHAR(50),
                type VARCHAR(20) NOT NULL,
                gender VARCHAR(10) NOT NULL,
                category_id VARCHAR(50),
                FOREIGN KEY (category_id)
                    REFERENCES Categories(category_id),
                FOREIGN KEY (parent_id)
                    REFERENCES Competitions(competition_id)
            )
        """)

        # Insert categories first because Competitions references them.
        categories.to_sql(
            "Categories",
            connection,
            if_exists="append",
            index=False,
        )

        # Insert competitions with foreign key checks temporarily disabled.
        # Some parent competitions are absent from the API response.
        connection.execute("PRAGMA foreign_keys = OFF")

        competitions.to_sql(
            "Competitions",
            connection,
            if_exists="append",
            index=False,
        )

        # Count parent references that cannot be resolved.
        missing_parent_count = connection.execute("""
            SELECT COUNT(*)
            FROM Competitions AS child
            WHERE child.parent_id IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1
                  FROM Competitions AS parent
                  WHERE parent.competition_id = child.parent_id
              )
        """).fetchone()[0]

        # Clear only parent IDs that do not exist in the downloaded data.
        connection.execute("""
            UPDATE Competitions
            SET parent_id = NULL
            WHERE parent_id IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1
                  FROM Competitions AS parent
                  WHERE parent.competition_id = Competitions.parent_id
              )
        """)

        # Re-enable enforcement after cleaning the data.
        connection.execute("PRAGMA foreign_keys = ON")

        # Verify row counts and integrity.
        category_count = connection.execute(
            "SELECT COUNT(*) FROM Categories"
        ).fetchone()[0]

        competition_count = connection.execute(
            "SELECT COUNT(*) FROM Competitions"
        ).fetchone()[0]

        violations = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        print("SUCCESS: SQLite database created and verified.")
        print(f"Database: {DB_FILE}")
        print(f"Categories inserted: {category_count}")
        print(f"Competitions inserted: {competition_count}")
        print(f"Missing parent references cleaned: {missing_parent_count}")
        print(f"Foreign key violations: {len(violations)}")

        print("\nTables:")
        tables = connection.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """).fetchall()

        for table in tables:
            print("-", table[0])

        print("\nCompetition preview:")
        preview = pd.read_sql_query("""
            SELECT
                c.competition_id,
                c.competition_name,
                c.parent_id,
                c.type,
                c.gender,
                cat.category_name
            FROM Competitions AS c
            LEFT JOIN Categories AS cat
                ON c.category_id = cat.category_id
            LIMIT 5
        """, connection)

        print(preview.to_string(index=False))

        if violations:
            print("\nWARNING: Foreign key violations remain.")
            for violation in violations[:10]:
                print(violation)
        else:
            print("\nDatabase integrity check passed.")


if __name__ == "__main__":
    main()
