import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Generator
import logging
from app.config import DB_PARAMS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Establishes and returns a new database connection.
    Returns a connection with RealDictCursor for dictionary-like row access.
    """
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        logger.info("Database connection established successfully")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise

@contextmanager
def get_db_cursor() -> Generator[psycopg2.extras.RealDictCursor, None, None]:
    """
    Context manager for database operations.
    Automatically handles connection and cursor lifecycle.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        yield cursor
        conn.commit()
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database operation failed: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def test_connection():
    """Test database connection and return status."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return {"status": "connected", "test_query": result[0]}
    except Exception as e:
        return {"status": "error", "message": str(e)} 