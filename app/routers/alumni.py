from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional
from app.models.alumni import (
    AlumniCreate, 
    AlumniUpdate, 
    AlumniResponse, 
    AlumniListResponse
)
from app.services.alumni_service import AlumniService
import logging

logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(prefix="/alumni", tags=["Alumni"])

@router.post("/", response_model=AlumniResponse, status_code=status.HTTP_201_CREATED)
async def create_alumni(alumni_data: AlumniCreate):
    """Create a new alumni record."""
    try:
        return AlumniService.create_alumni(alumni_data)
    except Exception as e:
        logger.error(f"Error creating alumni: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create alumni record"
        )

@router.get("/", response_model=AlumniListResponse)
async def get_alumni_list(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    is_latest: Optional[bool] = Query(None, description="Filter by latest records"),
    graduation_year: Optional[int] = Query(None, description="Filter by graduation year"),
    program: Optional[str] = Query(None, description="Filter by program"),
    search: Optional[str] = Query(None, description="Search in names and company")
):
    """Get paginated list of alumni with optional filters."""
    try:
        result = AlumniService.get_alumni_list(
            page=page,
            page_size=page_size,
            is_latest=is_latest,
            graduation_year=graduation_year,
            program=program,
            search=search
        )
        return AlumniListResponse(**result)
    except Exception as e:
        logger.error(f"Error fetching alumni list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch alumni list"
        )

@router.get("/{alumni_id}", response_model=AlumniResponse)
async def get_alumni_by_id(alumni_id: int):
    """Get alumni by ID."""
    try:
        alumni = AlumniService.get_alumni_by_id(alumni_id)
        if not alumni:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alumni not found"
            )
        return alumni
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching alumni {alumni_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch alumni"
        )

@router.put("/{alumni_id}", response_model=AlumniResponse)
async def update_alumni(alumni_id: int, alumni_data: AlumniUpdate):
    """Update an alumni record."""
    try:
        alumni = AlumniService.update_alumni(alumni_id, alumni_data)
        if not alumni:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alumni not found"
            )
        return alumni
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating alumni {alumni_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update alumni"
        )

@router.delete("/{alumni_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alumni(alumni_id: int):
    """Delete an alumni record."""
    try:
        success = AlumniService.delete_alumni(alumni_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alumni not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting alumni {alumni_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete alumni"
        )

@router.get("/linkedin/{linkedin_url:path}", response_model=AlumniResponse)
async def get_alumni_by_linkedin_url(linkedin_url: str):
    """Get alumni by LinkedIn URL."""
    try:
        alumni = AlumniService.get_alumni_by_linkedin_url(linkedin_url)
        if not alumni:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alumni not found"
            )
        return alumni
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching alumni by LinkedIn URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch alumni"
        ) 