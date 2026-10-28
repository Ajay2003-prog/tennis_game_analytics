"""Create the Complexes and Venues tables in SQLite and load the CSV data.

Run after process_complexes_venues.py. The script drops and recreates both
tables, so it can be re-run safely to rebuild the database.
"""

import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

DB_FILE = DATA_DIR / "tennis_venues.db"
COMPLEXES_FILE = DATA_DIR / "complexes.csv"
VENUES_FILE = DATA_DIR / "venues.csv"


def main():
    # Validate input files.
    if not COMPLEXES_FILE.exists():
        raise FileNotFoundError(
            f"Complexes file not found: {COMPLEXES_FILE}"
        )

    if not VENUES_FILE.exists():
        raise FileNotFoundError(
            f"Venues file not found: {VENUES_FILE}"
        )

    # Load CSV data as strings to preserve IDs.
    complexes = pd.read_csv(COMPLEXES_FILE, dtype=str)
    venues = pd.read_csv(VENUES_FILE, dtype=str)

    # Convert pandas missing values to Python None / SQL NULL.
    complexes = complexes.astype(object).where(pd.notna(complexes), None)
    venues = venues.astype(object).where(pd.notna(venues), None)

    required_complex_columns = {"complex_id", "complex_name"}
    required_venue_columns = {
        "venue_id",
        "venue_name",
        "city_name",
        "country_name",
        "country_code",
        "timezone",
        "complex_id",
    }

    if not required_complex_columns.issubset(complexes.columns):
        raise ValueError("Complexes CSV has missing required columns.")

    if not required_venue_columns.issubset(venues.columns):
        raise ValueError("Venues CSV has missing required columns.")

    with sqlite3.connect(DB_FILE) as connection:
        # Enable foreign key enforcement.
        connection.execute("PRAGMA foreign_keys = ON")

        # Recreate tables for a clean, repeatable database build.
        connection.execute("DROP TABLE IF EXISTS Venues")
        connection.execute("DROP TABLE IF EXISTS Complexes")

        connection.execute("""
            CREATE TABLE Complexes (
                complex_id VARCHAR(50) PRIMARY KEY,
                complex_name VARCHAR(100) NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE Venues (
                venue_id VARCHAR(50) PRIMARY KEY,
                venue_name VARCHAR(100) NOT NULL,
                city_name VARCHAR(100) NOT NULL,
                country_name VARCHAR(100) NOT NULL,
                country_code CHAR(3) NOT NULL,
                timezone VARCHAR(100) NOT NULL,
                complex_id VARCHAR(50),
                FOREIGN KEY (complex_id)
                    REFERENCES Complexes(complex_id)
            )
        """)

        # Indexes on the columns used for joins and filters.
        connection.execute(
            "CREATE INDEX idx_venues_complex ON Venues(complex_id)"
        )
        connection.execute(
            "CREATE INDEX idx_venues_country ON Venues(country_name)"
        )

        # Insert complexes first because Venues references them.
        complexes.to_sql(
            "Complexes",
            connection,
            if_exists="append",
            index=False,
        )

        venues.to_sql(
            "Venues",
            connection,
            if_exists="append",
            index=False,
        )

        # Verify row counts and integrity.
        complex_count = connection.execute(
            "SELECT COUNT(*) FROM Complexes"
        ).fetchone()[0]

        venue_count = connection.execute(
            "SELECT COUNT(*) FROM Venues"
        ).fetchone()[0]

        violations = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        print("SUCCESS: SQLite database created and verified.")
        print(f"Database: {DB_FILE}")
        print(f"Complexes inserted: {complex_count}")
        print(f"Venues inserted: {venue_count}")
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

        print("\nVenue preview:")
        preview = pd.read_sql_query("""
            SELECT
                v.venue_id,
                v.venue_name,
                v.city_name,
                v.country_name,
                c.complex_name
            FROM Venues AS v
            LEFT JOIN Complexes AS c
                ON v.complex_id = c.complex_id
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
