from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional
from app.models.scrape_history import (
    ScrapeHistoryCreate, 
    ScrapeHistoryUpdate, 
    ScrapeHistoryResponse, 
    ScrapeHistoryListResponse
)
from app.services.scrape_history_service import ScrapeHistoryService
import logging

logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(prefix="/scrape-history", tags=["Scrape History"])

@router.post("/", response_model=ScrapeHistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_scrape_history(scrape_data: ScrapeHistoryCreate):
    """Create a new scrape history record."""
    try:
        return ScrapeHistoryService.create_scrape_history(scrape_data)
    except Exception as e:
        logger.error(f"Error creating scrape history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create scrape history record"
        )

@router.get("/", response_model=ScrapeHistoryListResponse)
async def get_scrape_history_list(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    mode: Optional[str] = Query(None, description="Filter by mode")
):
    """Get paginated list of scrape history with optional filters."""
    try:
        result = ScrapeHistoryService.get_scrape_history_list(
            page=page,
            page_size=page_size,
            status=status_filter,
            mode=mode
        )
        return ScrapeHistoryListResponse(**result)
    except Exception as e:
        logger.error(f"Error fetching scrape history list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch scrape history list"
        )

@router.get("/latest", response_model=list[ScrapeHistoryResponse])
async def get_latest_scrape_histories(
    limit: int = Query(10, ge=1, le=50, description="Number of latest records to fetch")
):
    """Get the latest scrape history records."""
    try:
        return ScrapeHistoryService.get_latest_scrape_histories(limit)
    except Exception as e:
        logger.error(f"Error fetching latest scrape histories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch latest scrape histories"
        )

@router.get("/{scrape_history_id}", response_model=ScrapeHistoryResponse)
async def get_scrape_history_by_id(scrape_history_id: int):
    """Get scrape history by ID."""
    try:
        scrape_history = ScrapeHistoryService.get_scrape_history_by_id(scrape_history_id)
        if not scrape_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scrape history not found"
            )
        return scrape_history
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching scrape history {scrape_history_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch scrape history"
        )

@router.put("/{scrape_history_id}", response_model=ScrapeHistoryResponse)
async def update_scrape_history(scrape_history_id: int, scrape_data: ScrapeHistoryUpdate):
    """Update a scrape history record."""
    try:
        scrape_history = ScrapeHistoryService.update_scrape_history(scrape_history_id, scrape_data)
        if not scrape_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scrape history not found"
            )
        return scrape_history
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating scrape history {scrape_history_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update scrape history"
        )

@router.delete("/{scrape_history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scrape_history(scrape_history_id: int):
    """Delete a scrape history record."""
    try:
        success = ScrapeHistoryService.delete_scrape_history(scrape_history_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scrape history not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting scrape history {scrape_history_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete scrape history"
        ) 