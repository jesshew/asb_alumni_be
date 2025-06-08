#!/usr/bin/env python3
"""
Startup script for ASB Alumni Management System FastAPI server.
This script provides a convenient way to start the server with proper configuration.
"""

import uvicorn
import os
from app.config import PROJECT_NAME

def main():
    """Start the FastAPI server."""
    print(f"Starting {PROJECT_NAME}...")
    print("=" * 50)
    
    # Server configuration
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 3001))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info")
    
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Reload: {reload}")
    print(f"Log Level: {log_level}")
    print("=" * 50)
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"Health Check: http://{host}:{port}/api/v1/health")
    print("=" * 50)
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True
    )

if __name__ == "__main__":
    main() 