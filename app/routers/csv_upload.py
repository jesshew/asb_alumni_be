from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional
from app.models.csv_upload import (
    CsvUploadCreate, 
    CsvUploadUpdate, 
    CsvUploadResponse, 
    CsvUploadListResponse
)
from app.services.csv_upload_service import CsvUploadService
import logging

logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(prefix="/csv-uploads", tags=["CSV Uploads"])

@router.post("/", response_model=CsvUploadResponse, status_code=status.HTTP_201_CREATED)
async def create_csv_upload(csv_data: CsvUploadCreate):
    """Create a new CSV upload record."""
    try:
        return CsvUploadService.create_csv_upload(csv_data)
    except Exception as e:
        logger.error(f"Error creating CSV upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create CSV upload record"
        )

@router.get("/", response_model=CsvUploadListResponse)
async def get_csv_upload_list(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    search: Optional[str] = Query(None, description="Search in file name and description")
):
    """Get paginated list of CSV uploads with optional filters."""
    try:
        result = CsvUploadService.get_csv_upload_list(
            page=page,
            page_size=page_size,
            search=search
        )
        return CsvUploadListResponse(**result)
    except Exception as e:
        logger.error(f"Error fetching CSV upload list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch CSV upload list"
        )

@router.get("/recent", response_model=list[CsvUploadResponse])
async def get_recent_csv_uploads(
    limit: int = Query(10, ge=1, le=50, description="Number of recent records to fetch")
):
    """Get the most recent CSV upload records."""
    try:
        return CsvUploadService.get_recent_csv_uploads(limit)
    except Exception as e:
        logger.error(f"Error fetching recent CSV uploads: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch recent CSV uploads"
        )

@router.get("/{csv_upload_id}", response_model=CsvUploadResponse)
async def get_csv_upload_by_id(csv_upload_id: int):
    """Get CSV upload by ID."""
    try:
        csv_upload = CsvUploadService.get_csv_upload_by_id(csv_upload_id)
        if not csv_upload:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CSV upload not found"
            )
        return csv_upload
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching CSV upload {csv_upload_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch CSV upload"
        )

@router.put("/{csv_upload_id}", response_model=CsvUploadResponse)
async def update_csv_upload(csv_upload_id: int, csv_data: CsvUploadUpdate):
    """Update a CSV upload record."""
    try:
        csv_upload = CsvUploadService.update_csv_upload(csv_upload_id, csv_data)
        if not csv_upload:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CSV upload not found"
            )
        return csv_upload
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating CSV upload {csv_upload_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update CSV upload"
        )

@router.delete("/{csv_upload_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_csv_upload(csv_upload_id: int):
    """Delete a CSV upload record."""
    try:
        success = CsvUploadService.delete_csv_upload(csv_upload_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CSV upload not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting CSV upload {csv_upload_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete CSV upload"
        ) 