import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection(use_database=True):
    """Return a MySQL connection."""
    config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    if use_database:
        config["database"] = "casefile"

    return mysql.connector.connect(**config)


if __name__ == "__main__":
    try:
        connection = get_connection()
        print("Successfully connected to MySQL!")
        connection.close()
    except mysql.connector.Error as error:
        print(f"Connection failed: {error}")
