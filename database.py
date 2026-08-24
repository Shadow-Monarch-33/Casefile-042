import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Create and return a connection to the MySQL server."""
    return mysql.connector.connect(
        host = os.getenv("DB_HOST"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        database="casefile"
    )

if __name__ == "__main__":
    try:
        connection = get_connection()

        if connection.is_connected():
            print("Successfully connected to MySQL!")

        connection.close()

    except mysql.connector.Error as error:
        print(f"Connection failed: {error}")