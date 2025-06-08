from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from fastapi import UploadFile

class CsvUploadBase(BaseModel):
    """Base model for CSV upload."""
    description: Optional[str] = None

class CsvUploadCreate(CsvUploadBase):
    """Model for creating a new CSV upload."""
    file: UploadFile

class CsvUploadUpdate(CsvUploadBase):
    """Model for updating an existing CSV upload."""
    pass

class CsvUploadResponse(CsvUploadBase):
    """Model for CSV upload response."""
    csv_upload_id: int
    csv_upload_file_name: str
    csv_upload_file_url: str
    csv_upload_uploaded_at: datetime

    class Config:
        from_attributes = True

class CsvUploadListResponse(BaseModel):
    """Model for paginated CSV upload list response."""
    csv_uploads: List[CsvUploadResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
