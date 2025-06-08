import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Generator
import os

#TODO: Since now we are merging both page and engage , we have to pull the project type in order to load the correct project
def get_db_connection():
    """Establishes and returns a new database connection."""
    db_params = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT')
    }
    conn = psycopg2.connect(**db_params)
    return conn

def get_db_cursor():
    """Establishes and returns a new database cursor."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    return cur

def test_connection():
    """Test database connection and return status."""
    try:
        cur = get_db_cursor()
        cur.execute("select * from alumni limit 1")
        result = cur.fetchone()
        # print(result)
        return {"status": "connected", "test_query": result}
    except Exception as e:
        return {"status": "error", "message": str(e)} 