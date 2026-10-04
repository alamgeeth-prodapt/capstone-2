import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "pii_mapping.db"

class PIIRepository:

    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def create_table(self):
        connection = self._connect()

        connection.execute("""
            CREATE TABLE IF NOT EXISTS pii_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT NOT NULL UNIQUE,
                pii_type TEXT NOT NULL,
                original_value TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT
            )
        """)

        connection.commit()
        connection.close()

    def save_mapping(
        self,
        token: str,
        pii_type: str,
        original_value: str,
    ):
        connection = self._connect()

        connection.execute(
            """
            INSERT INTO pii_mappings (
                token,
                pii_type,
                original_value,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                token,
                pii_type,
                original_value,
                datetime.utcnow().isoformat(),
            ),
        )

        connection.commit()
        connection.close()

    def get_original_value(self, token: str):
        connection = self._connect()

        cursor = connection.execute(
            """
            SELECT original_value
            FROM pii_mappings
            WHERE token = ?
            """,
            (token,),
        )

        row = cursor.fetchone()

        connection.close()

        if row is None:
            return None

        return row[0]

    def get_token(
        self,
        pii_type: str,
        original_value: str,
    ):
        connection = self._connect()

        cursor = connection.execute(
            """
            SELECT token
            FROM pii_mappings
            WHERE pii_type = ?
              AND original_value = ?
            """,
            (
                pii_type,
                original_value,
            ),
        )

        row = cursor.fetchone()

        connection.close()

        if row is None:
            return None

        return row[0]

    def get_all_mappings(self):

        connection = self._connect()

        cursor = connection.execute(
            """
            SELECT token, original_value
            FROM pii_mappings
            """
        )

        rows = cursor.fetchall()

        connection.close()

        return rows