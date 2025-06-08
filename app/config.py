import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration constants
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
USE_POSTGRES = os.getenv('USE_POSTGRES', 'True').lower() == 'true'

# Database connection parameters
DB_PARAMS = {
    'dbname': DB_NAME,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'host': DB_HOST,
    'port': DB_PORT
}

# API configuration constants
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"
PROJECT_NAME = "ASB Alumni Management System"
PROJECT_DESCRIPTION = "FastAPI server for managing ASB alumni data with CRUD operations" 