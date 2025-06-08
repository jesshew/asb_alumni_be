from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from fastapi import UploadFile

class CsvUploadBase(BaseModel):
    """Base model for CSV upload data."""
    csv_upload_file_name: str = Field(..., max_length=255)
    csv_upload_file_url: str = Field(..., max_length=512)
    csv_upload_description: Optional[str] = None

class CsvUploadCreate(BaseModel):
    """Model for creating new CSV upload records."""
    file: UploadFile
    description: Optional[str] = None

class CsvUploadUpdate(BaseModel):
    """Model for updating CSV upload records."""
    csv_upload_file_name: Optional[str] = Field(None, max_length=255)
    csv_upload_file_url: Optional[str] = Field(None, max_length=512)
    csv_upload_description: Optional[str] = None

class CsvUploadResponse(CsvUploadBase):
    """Model for CSV upload response data."""
    csv_upload_id: int
    csv_upload_uploaded_at: datetime

    class Config:
        from_attributes = True

class CsvUploadListResponse(BaseModel):
    """Model for paginated CSV upload list response."""
    csv_uploads: list[CsvUploadResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int 