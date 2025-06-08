import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

# Database configuration constants
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
USE_POSTGRES = os.getenv("USE_POSTGRES", "True").lower() == "true"

# Database connection parameters
DB_PARAMS = {
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": DB_PORT,
}

# API configuration constants
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"
PROJECT_NAME = "ASB Alumni Management System"
PROJECT_DESCRIPTION = "FastAPI server for managing ASB alumni data with CRUD operations"


class Settings(BaseModel):
    # Database settings
    db_name: str = DB_NAME
    db_user: str = DB_USER
    db_password: str = DB_PASSWORD
    db_host: str = DB_HOST
    db_port: int = int(DB_PORT)

    # Supabase settings
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    supabase_bucket_name: str = os.getenv("SUPABASE_BUCKET_NAME", "csv")


settings = Settings()
