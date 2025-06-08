from fastapi import APIRouter, HTTPException, status
from app.database import test_connection
from app.config import PROJECT_NAME, API_VERSION
import logging

logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": PROJECT_NAME,
        "version": API_VERSION
    }

@router.get("/database")
async def database_health_check():
    """Check database connection health."""
    try:
        db_status = test_connection()
        if db_status["status"] == "connected":
            return {
                "status": "healthy",
                "database": "connected",
                "details": db_status
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "status": "unhealthy",
                    "database": "disconnected",
                    "details": db_status
                }
            )
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "database": "error",
                "error": str(e)
            }
        )

@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check including all components."""
    try:
        # Check database
        db_status = test_connection()
        
        health_data = {
            "status": "healthy",
            "service": PROJECT_NAME,
            "version": API_VERSION,
            "components": {
                "database": {
                    "status": "healthy" if db_status["status"] == "connected" else "unhealthy",
                    "details": db_status
                }
            }
        }
        
        # If any component is unhealthy, mark overall status as unhealthy
        if db_status["status"] != "connected":
            health_data["status"] = "unhealthy"
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=health_data
            )
        
        return health_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "service": PROJECT_NAME,
                "version": API_VERSION,
                "error": str(e)
            }
        ) 