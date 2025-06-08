from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import date, datetime
from enum import Enum

class DataState(str, Enum):
    """Enumeration for alumni data state."""
    INCOMPLETE = "incomplete"
    MISSING = "missing"
    COMPLETE = "complete"

class AlumniBase(BaseModel):
    """Base model for alumni data."""
    alumni_first_name: Optional[str] = Field(None, max_length=100)
    alumni_preferred_name: Optional[str] = Field(None, max_length=100)
    alumni_last_name: Optional[str] = Field(None, max_length=100)
    alumni_gender: Optional[str] = Field(None, max_length=20)
    alumni_graduation_year: Optional[int] = Field(None, ge=1900, le=2100)
    alumni_intake: Optional[str] = Field(None, max_length=100)
    alumni_program: Optional[str] = Field(None, max_length=255)
    alumni_graduation_awards: Optional[str] = Field(None, max_length=255)
    alumni_birthdate: Optional[date] = None
    alumni_linkedin_url: Optional[str] = Field(None, max_length=255)
    alumni_citizenship_primary: Optional[str] = Field(None, max_length=100)
    alumni_region_primary: Optional[str] = Field(None, max_length=100)
    alumni_citizenship_secondary: Optional[str] = Field(None, max_length=100)
    alumni_phone_number: Optional[str] = Field(None, max_length=50)
    alumni_organizations_pre_asb: Optional[str] = None
    alumni_city: Optional[str] = Field(None, max_length=100)
    alumni_country: Optional[str] = Field(None, max_length=100)
    alumni_current_job_title: Optional[str] = Field(None, max_length=255)
    alumni_current_job_city: Optional[str] = Field(None, max_length=100)
    alumni_current_job_country: Optional[str] = Field(None, max_length=100)
    alumni_current_company_name: Optional[str] = Field(None, max_length=255)
    alumni_current_start_date: Optional[date] = None
    alumni_additional_notes: Optional[str] = None
    alumni_is_in_startup_ecosystem: Optional[bool] = False
    alumni_startup_description: Optional[str] = None
    alumni_is_latest: Optional[bool] = True
    alumni_source: Optional[str] = Field(None, max_length=50)
    alumni_tags: Optional[Dict[str, Any]] = None
    alumni_raw_data: Optional[Dict[str, Any]] = None
    alumni_data_state: Optional[DataState] = None

class AlumniCreate(AlumniBase):
    """Model for creating new alumni records."""
    pass

class AlumniUpdate(AlumniBase):
    """Model for updating alumni records."""
    pass

class AlumniResponse(AlumniBase):
    """Model for alumni response data."""
    alumni_id: int
    alumni_created_at: datetime
    alumni_updated_at: datetime

    class Config:
        from_attributes = True

class AlumniListResponse(BaseModel):
    """Model for paginated alumni list response."""
    alumni: list[AlumniResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int 