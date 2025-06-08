from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ScrapeHistoryBase(BaseModel):
    """Base model for scrape history data."""
    scrape_history_started_at: datetime
    scrape_history_ended_at: Optional[datetime] = None
    scrape_history_status: Optional[str] = Field(None, max_length=50)
    scrape_history_mode: Optional[str] = None
    scrape_history_input_file: Optional[str] = Field(None, max_length=255)
    scrape_history_summary: Optional[str] = None
    scrape_history_record_count: Optional[int] = None
    scrape_history_error_log: Optional[str] = None

class ScrapeHistoryCreate(ScrapeHistoryBase):
    """Model for creating new scrape history records."""
    pass

class ScrapeHistoryUpdate(BaseModel):
    """Model for updating scrape history records."""
    scrape_history_ended_at: Optional[datetime] = None
    scrape_history_status: Optional[str] = Field(None, max_length=50)
    scrape_history_mode: Optional[str] = None
    scrape_history_input_file: Optional[str] = Field(None, max_length=255)
    scrape_history_summary: Optional[str] = None
    scrape_history_record_count: Optional[int] = None
    scrape_history_error_log: Optional[str] = None

class ScrapeHistoryResponse(ScrapeHistoryBase):
    """Model for scrape history response data."""
    scrape_history_id: int

    class Config:
        from_attributes = True

class ScrapeHistoryListResponse(BaseModel):
    """Model for paginated scrape history list response."""
    scrape_histories: list[ScrapeHistoryResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int 