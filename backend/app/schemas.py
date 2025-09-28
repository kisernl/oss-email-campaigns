"""
Pydantic schemas for Email Campaign App.

Defines request/response models for API validation and serialization.
"""

from datetime import datetime
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, validator
from pydantic.config import ConfigDict


class CampaignStatusEnum(str, Enum):
    """Campaign status enumeration for API."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EmailStatusEnum(str, Enum):
    """Email send status enumeration for API."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"
    SKIPPED = "skipped"


# Base schemas
class CampaignBase(BaseModel):
    """Base schema for Campaign."""
    name: str = Field(..., min_length=1, max_length=255, description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    subject: str = Field(..., min_length=1, max_length=500, description="Email subject")
    message: str = Field(..., min_length=1, description="Email message content")
    google_sheet_id: str = Field(..., min_length=10, max_length=100, description="Google Sheets ID")
    google_sheet_range: str = Field(default="A:Z", max_length=50, description="Sheet range")
    send_immediately: bool = Field(default=True, description="Send campaign immediately")
    use_delay: bool = Field(default=False, description="Use random delay between emails")
    delay_min_minutes: int = Field(default=4, ge=1, le=60, description="Minimum delay in minutes")
    delay_max_minutes: int = Field(default=7, ge=1, le=60, description="Maximum delay in minutes")
    
    # Business hours configuration
    respect_business_hours: bool = Field(default=False, description="Only send emails during business hours")
    business_hours_start: int = Field(default=7, ge=0, le=23, description="Business hours start (24-hour format)")
    business_hours_end: int = Field(default=17, ge=1, le=24, description="Business hours end (24-hour format)")
    business_days_only: bool = Field(default=True, description="Only send on Monday-Friday")
    timezone: str = Field(default="UTC", description="Timezone for business hours")
    
    @validator('delay_max_minutes')
    def validate_delay_range(cls, v, values):
        """Validate that max delay is greater than min delay."""
        if 'delay_min_minutes' in values and v < values['delay_min_minutes']:
            raise ValueError('delay_max_minutes must be greater than or equal to delay_min_minutes')
        return v
    
    @validator('business_hours_end')
    def validate_business_hours(cls, v, values):
        """Validate that business hours end is after start."""
        if 'business_hours_start' in values and v <= values['business_hours_start']:
            raise ValueError('business_hours_end must be greater than business_hours_start')
        return v
    
    @validator('google_sheet_id')
    def validate_google_sheet_id(cls, v):
        """Validate Google Sheets ID format."""
        if not v or len(v) < 10:
            raise ValueError('Google Sheets ID must be at least 10 characters')
        # Basic format validation (Google Sheets IDs are typically 44 characters)
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Invalid Google Sheets ID format')
        return v
    
    @validator('message')
    def validate_message(cls, v):
        """Validate email message content."""
        if not v.strip():
            raise ValueError('Email message cannot be empty')
        return v.strip()


class CampaignCreate(CampaignBase):
    """Schema for creating a new campaign."""
    pass


class CampaignUpdate(BaseModel):
    """Schema for updating an existing campaign."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    subject: Optional[str] = Field(None, min_length=1, max_length=500)
    message: Optional[str] = Field(None, min_length=1)
    google_sheet_id: Optional[str] = Field(None, min_length=10, max_length=100)
    google_sheet_range: Optional[str] = Field(None, max_length=50)
    send_immediately: Optional[bool] = None
    use_delay: Optional[bool] = None
    delay_min_minutes: Optional[int] = Field(None, ge=1, le=60)
    delay_max_minutes: Optional[int] = Field(None, ge=1, le=60)
    
    # Business hours configuration
    respect_business_hours: Optional[bool] = None
    business_hours_start: Optional[int] = Field(None, ge=0, le=23)
    business_hours_end: Optional[int] = Field(None, ge=1, le=24)
    business_days_only: Optional[bool] = None
    timezone: Optional[str] = None
    
    status: Optional[CampaignStatusEnum] = None


class CampaignResponse(CampaignBase):
    """Schema for campaign response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: CampaignStatusEnum
    total_recipients: int
    emails_sent: int
    emails_failed: int
    emails_pending: int
    created_at: datetime
    updated_at: datetime
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    error_count: int
    
    # Computed fields
    success_rate: Optional[float] = None
    failure_rate: Optional[float] = None
    is_active: Optional[bool] = None
    is_completed: Optional[bool] = None


class CampaignSummary(BaseModel):
    """Schema for campaign summary (list view)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    status: CampaignStatusEnum
    total_recipients: int
    emails_sent: int
    emails_failed: int
    success_rate: float
    created_at: datetime
    completed_at: Optional[datetime] = None


# Email Send schemas
class EmailSendBase(BaseModel):
    """Base schema for EmailSend."""
    recipient_email: EmailStr = Field(..., description="Recipient email address")
    recipient_name: Optional[str] = Field(None, max_length=255, description="Recipient name")
    personalized_subject: str = Field(..., max_length=500, description="Personalized email subject")
    personalized_message: str = Field(..., description="Personalized email message")


class EmailSendCreate(EmailSendBase):
    """Schema for creating a new email send record."""
    campaign_id: int = Field(..., description="Campaign ID")
    sheet_row_number: Optional[int] = Field(None, description="Row number in Google Sheet")


class EmailSendUpdate(BaseModel):
    """Schema for updating an email send record."""
    status: Optional[EmailStatusEnum] = None
    error_message: Optional[str] = None
    smtp_response: Optional[str] = None
    marked_as_sent_in_sheet: Optional[bool] = None


class EmailSendResponse(EmailSendBase):
    """Schema for email send response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    campaign_id: int
    status: EmailStatusEnum
    send_attempts: int
    max_send_attempts: int
    created_at: datetime
    updated_at: datetime
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    smtp_response: Optional[str] = None
    sheet_row_number: Optional[int] = None
    marked_as_sent_in_sheet: bool


# Google Sheets schemas
class GoogleSheetPreview(BaseModel):
    """Schema for Google Sheets preview."""
    sheet_id: str
    sheet_name: Optional[str] = None
    total_rows: int
    email_column: Optional[str] = None
    name_column: Optional[str] = None
    headers: List[str]
    sample_data: List[List[str]]
    valid_emails: int
    invalid_emails: int
    duplicate_emails: int


class GoogleSheetEmailRow(BaseModel):
    """Schema for a single email row from Google Sheets."""
    row_number: int
    email: EmailStr
    name: Optional[str] = None
    additional_data: Optional[dict] = None


# API Response schemas
class HealthCheck(BaseModel):
    """Schema for health check response."""
    status: str
    timestamp: datetime
    version: str
    database: dict
    environment: str


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime


class SuccessResponse(BaseModel):
    """Schema for success responses."""
    message: str
    data: Optional[dict] = None
    timestamp: datetime


# Campaign Statistics
class CampaignStats(BaseModel):
    """Schema for campaign statistics."""
    total_campaigns: int
    active_campaigns: int
    completed_campaigns: int
    failed_campaigns: int
    total_emails_sent: int
    total_recipients: int
    overall_success_rate: float
    recent_campaigns: List[CampaignSummary]


# Pagination schemas
class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=50, ge=1, le=200, description="Page size")
    sort_by: Optional[str] = Field(default="created_at", description="Sort field")
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")


class PaginatedResponse(BaseModel):
    """Schema for paginated responses."""
    items: List[BaseModel]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool


# Campaign filtering
class CampaignFilter(BaseModel):
    """Schema for campaign filtering."""
    status: Optional[CampaignStatusEnum] = None
    google_sheet_id: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    name_contains: Optional[str] = None


# ============================================================================
# EMAIL TEMPLATE TYPES
# ============================================================================

class EmailTemplateBase(BaseModel):
    """Base schema for EmailTemplate."""
    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    subject: str = Field(..., min_length=1, max_length=500, description="Email subject template")
    message: str = Field(..., min_length=1, description="Email message template")
    variables: Optional[str] = Field(None, description="Comma-separated list of template variables")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate template name."""
        if not v.strip():
            raise ValueError('Template name cannot be empty')
        return v.strip()
    
    @validator('subject')
    def validate_subject(cls, v):
        """Validate template subject."""
        if not v.strip():
            raise ValueError('Template subject cannot be empty')
        return v.strip()
    
    @validator('message')
    def validate_message(cls, v):
        """Validate template message."""
        if not v.strip():
            raise ValueError('Template message cannot be empty')
        return v.strip()


class EmailTemplateCreate(EmailTemplateBase):
    """Schema for creating a new email template."""
    pass


class EmailTemplateUpdate(BaseModel):
    """Schema for updating an existing email template."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    subject: Optional[str] = Field(None, min_length=1, max_length=500)
    message: Optional[str] = Field(None, min_length=1)
    variables: Optional[str] = None


class EmailTemplateResponse(EmailTemplateBase):
    """Schema for email template response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime
    
    # Computed field
    variables_list: Optional[List[str]] = None


class EmailTemplateSummary(BaseModel):
    """Schema for email template summary (list view)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    variables_count: Optional[int] = None