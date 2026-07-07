"""Database for air quality measurement storage and retrieval."""

import sqlite3
from datetime import datetime


class Database:
    """Handles all database operations for air quality measurements."""

    def __init__(self, db_name="measurements.db"):
        """Initialize database connection and create table if it doesn't exist."""
        self.db_name = db_name
        self._create_table()

    def _create_table(self):
        """Create measurements table if it does not already exist."""
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    co2 REAL NOT NULL,
                    tvoc REAL NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)

    def insert(self, co2, tvoc):
        """Insert a new measurement with the current timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = (
            "INSERT INTO measurements (co2, tvoc, timestamp) "
            "VALUES (?, ?, ?)"
        )
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(query, (co2, tvoc, timestamp))

    def get_all(self):
        """Retrieve all measurements ordered by timestamp ascending."""
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM measurements ORDER BY timestamp ASC"
            )
            return cursor.fetchall()

    def get_latest(self):
        """Retrieve the most recent measurement."""
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM measurements ORDER BY timestamp DESC LIMIT 1"
            )
            return cursor.fetchone()

    def get_page(self, page=1, per_page=20):
        """Retrieve a paginated set of measurements and the total count of pages"""
        offset = (page - 1) * per_page
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM measurements "
                "ORDER BY timestamp ASC LIMIT ? OFFSET ?",
                (per_page, offset)
            )
            rows = cursor.fetchall()
            total = conn.execute(
                "SELECT COUNT(*) FROM measurements"
            ).fetchone()[0]
        return rows, total

    def get_min_max(self):
        """Retrieve min and max CO2/TVOC values with their timestamps."""
        query = """
            SELECT
                (SELECT co2 FROM measurements
                    ORDER BY co2 ASC LIMIT 1) AS min_co2,
                (SELECT timestamp FROM measurements
                    ORDER BY co2 ASC LIMIT 1) AS min_co2_timestamp,
                (SELECT co2 FROM measurements
                    ORDER BY co2 DESC LIMIT 1) AS max_co2,
                (SELECT timestamp FROM measurements
                    ORDER BY co2 DESC LIMIT 1) AS max_co2_timestamp,
                (SELECT tvoc FROM measurements
                    ORDER BY tvoc ASC LIMIT 1) AS min_tvoc,
                (SELECT timestamp FROM measurements
                    ORDER BY tvoc ASC LIMIT 1) AS min_tvoc_timestamp,
                (SELECT tvoc FROM measurements
                    ORDER BY tvoc DESC LIMIT 1) AS max_tvoc,
                (SELECT timestamp FROM measurements
                    ORDER BY tvoc DESC LIMIT 1) AS max_tvoc_timestamp
        """
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute(query).fetchone()