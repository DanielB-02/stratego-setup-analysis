import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import List, Tuple, Optional
from src.database.append_conditions_params import build_conditions_and_params
import logging
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'sqlite_database.db')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        if conn:
            conn.rollback()
        raise DatabaseError(f"Database operation failed: {e}")
    finally:
        if conn:
            conn.close()


class StrategoDatabase:
    """Database operations for Stratego game analysis."""

    def __init__(self):
        self.db_path = DATABASE_PATH

    def get_all_setup_positions(self) -> List[Tuple]:
        """Retrieve all setup positions from the database."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM GameSetups")
            return cursor.fetchall()

    def get_pieces_at_position(self, row: int, col: int) -> List[Tuple[str]]:
        """Get all pieces at a specific position across all setups."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT piece FROM GameSetups WHERE row = ? AND col = ?", (row, col))
            return cursor.fetchall()

    def get_pieces_at_position_for_opponent(self, opponent: str, row: int, col: int) -> List[Tuple[str]]:
        """Get pieces at a specific position for games against a specific opponent."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           SELECT s.piece
                           FROM GameSetups s
                                    INNER JOIN GameRecords r ON s.setup_id = r.setup_id
                           WHERE r.opponent_name = ?
                             AND s.row = ?
                             AND s.col = ?
                           """, (opponent, row, col))
            return cursor.fetchall()

    def determine_new_setup_id_from_game_setups(self) -> int:
        """Determine the next available setup ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(setup_id) FROM GameSetups")
            result = cursor.fetchone()
            return result[0] + 1 if result and result[0] is not None else 1

    def select_opponent_id_and_name(self, opponent: str) -> Optional[Tuple]:
        """Get opponent ID and name from the database."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT opponent_id, opponent_name FROM Opponents WHERE opponent_name = ?", (opponent,))
            return cursor.fetchone()

    def select_everything_from_staging_setup(self, setup_id: int) -> List[Tuple]:
        """Get all data from temporary setup table for a specific setup ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM TempSetup WHERE setup_id = ?", (setup_id,))
            return cursor.fetchall()

    def select_pieces_from_staging_setup(self, setup_id: int) -> List[str]:
        """Get pieces from temporary setup table for a specific setup ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT piece FROM TempSetup WHERE setup_id = ?", (setup_id,))
            return [row[0] for row in cursor.fetchall()]

    def delete_from_temp_setup(self) -> None:
        """Clear all data from temporary setup table."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM TempSetup")
            conn.commit()

    def check_duplicate_setup(self) -> Optional[int]:
        """Check if the current temporary setup matches an existing setup."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           SELECT gs.setup_id
                           FROM GameSetups gs
                                    JOIN TempSetup ts ON gs.row = ts.row AND gs.col = ts.col AND gs.piece = ts.piece
                           GROUP BY gs.setup_id
                           HAVING COUNT(*) = 40
                           """)
            result = cursor.fetchone()
            return result[0] if result else None

    def get_setup_id_with_game_record_filters(self, **kwargs) -> List[Tuple[str]]:
        """Return all setups that satisfy the filters that are applied."""

        conditions, params = build_conditions_and_params(kwargs)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
                SELECT setup_id
                FROM GameRecords
                WHERE {where_clause}
                ORDER BY setup_id DESC
            """

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [result[0] for result in cursor.fetchall()]

    def get_setups_with_setup_ids(self, setup_ids: List[int]):
        """Get all setups that have specified ids. Complementary method to get_setup_id_with_game_record_filters."""
        results = []
        for setup_id in setup_ids:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                                   SELECT row, col, piece
                                   FROM GameSetups 
                                   WHERE setup_id = ?
                                   """,(setup_id,))
                result = cursor.fetchall()
                results.append(result)
        return results


db = StrategoDatabase()

"""Legacy function wrappers for backward compatibility."""


def get_all_setup_positions() -> List[Tuple]:
    return db.get_all_setup_positions()


def get_pieces_at_position(row: int, col: int) -> List[Tuple[str]]:
    return db.get_pieces_at_position(row, col)


def get_pieces_at_position_for_opponent(opponent: str, row: int, col: int) -> List[Tuple[str]]:
    return db.get_pieces_at_position_for_opponent(opponent, row, col)


def determine_new_setup_id_from_game_setups() -> int:
    return db.determine_new_setup_id_from_game_setups()


def select_opponent_id_and_name(opponent: str) -> Optional[Tuple]:
    return db.select_opponent_id_and_name(opponent)


def select_everything_from_staging_setup(setup_id: int) -> List[Tuple]:
    return db.select_everything_from_staging_setup(setup_id)


def select_pieces_from_staging_setup(setup_id: int) -> List[str]:
    return db.select_pieces_from_staging_setup(setup_id)


def delete_from_temp_setup() -> None:
    return db.delete_from_temp_setup()


def check_duplicate_setup() -> Optional[int]:
    return db.check_duplicate_setup()


def get_setup_id_with_game_record_filters(**kwargs):
    return db.get_setup_id_with_game_record_filters(**kwargs)


def get_setups_with_setup_ids(setup_ids: List[int]) -> Optional[List[int]]:
    return db.get_setups_with_setup_ids(setup_ids)

