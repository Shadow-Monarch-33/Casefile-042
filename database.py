"""Local SQLite connection shared by the CASEFILE application and setup script."""

import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "casefile.db"


def get_connection(use_database=True):
    """Open the local case database. Legacy argument retained for compatibility."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row  # Supports both row[0] and row["name"]
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


if __name__ == "__main__":
    try:
        connection = get_connection()
        print(f"Successfully connected to SQLite: {DATABASE_PATH}")
        connection.close()
    except sqlite3.Error as error:
        print(f"Connection failed: {error}")
