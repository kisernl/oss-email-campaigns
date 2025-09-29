"""
FastAPI main application for Email Campaign App.

Provides REST API endpoints for campaign management, Google Sheets integration,
and email sending functionality.
"""

import os
import traceback
import random
import time
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, Field
import uvicorn

# Local imports
from app.database import get_db, create_tables, db_manager, SessionLocal
from app.models import Campaign, EmailSend, EmailTemplate, CampaignStatus, EmailStatus
from app.schemas import (
    CampaignCreate, CampaignUpdate, CampaignResponse, CampaignSummary,
    EmailSendResponse, HealthCheck, ErrorResponse, SuccessResponse,
    PaginationParams, PaginatedResponse,
    EmailTemplateCreate, EmailTemplateUpdate, EmailTemplateResponse, EmailTemplateSummary
)
from app.services.google_sheets import (
    GoogleSheetsService, GoogleSheetsError, GoogleSheetsAuthError,
    GoogleSheetsAccessError, GoogleSheetsValidationError
)
from app.services.email_service import (
    EmailService, EmailServiceError, EmailConnectionError,
    EmailAuthenticationError, create_email_service
)

# Initialize FastAPI app
app = FastAPI(
    title="Email Campaign API",
    description="REST API for managing email campaigns with Google Sheets integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
origins = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",  # Alternative localhost
    "http://localhost:3001",  # Alternative port
    "http://127.0.0.1:3001",  # Alternative port
]

# Add environment-based CORS origins
env_origins = os.getenv("CORS_ORIGINS", "").split(",")
if env_origins and env_origins[0]:  # Check if not empty
    origins.extend([origin.strip() for origin in env_origins])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global services (initialized on startup)
google_sheets_service: Optional[GoogleSheetsService] = None
email_service: Optional[EmailService] = None


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services and database on startup."""
    global google_sheets_service, email_service
    
    try:
        # Create database tables
        create_tables()
        print("📊 Database tables created/verified")
        
        # Initialize Google Sheets service
        google_sheets_service = GoogleSheetsService()
        print("📋 Google Sheets service initialized")
        
        # Initialize Email service
        email_service = create_email_service()
        print("📧 Email service initialized")
        
        print("🚀 Email Campaign API started successfully")
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        traceback.print_exc()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("👋 Email Campaign API shutting down")


# Custom exception handlers
@app.exception_handler(GoogleSheetsError)
async def google_sheets_exception_handler(request, exc: GoogleSheetsError):
    """Handle Google Sheets service errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    
    if isinstance(exc, GoogleSheetsAuthError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, GoogleSheetsAccessError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, GoogleSheetsValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": "Google Sheets Error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(EmailServiceError)
async def email_service_exception_handler(request, exc: EmailServiceError):
    """Handle Email service errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    
    if isinstance(exc, EmailConnectionError):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif isinstance(exc, EmailAuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": "Email Service Error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request, exc: SQLAlchemyError):
    """Handle database errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database Error",
            "detail": "An error occurred while accessing the database",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Utility functions
def get_google_sheets_service() -> GoogleSheetsService:
    """Get Google Sheets service instance."""
    if google_sheets_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Sheets service not available"
        )
    return google_sheets_service


def get_email_service() -> EmailService:
    """Get Email service instance."""
    if email_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email service not available"
        )
    return email_service


# Pydantic models for request/response
class GoogleSheetPreviewRequest(BaseModel):
    """Request model for Google Sheet preview."""
    sheet_id: str = Field(..., min_length=10, description="Google Sheets ID")
    sheet_range: str = Field(default="A:Z", description="Sheet range to preview")
    max_rows: int = Field(default=10, ge=1, le=100, description="Maximum rows to preview")


class GoogleSheetPreviewResponse(BaseModel):
    """Response model for Google Sheet preview."""
    sheet_id: str
    sheet_name: Optional[str]
    total_rows: int
    headers: List[str]
    email_column: Optional[str]
    name_column: Optional[str]
    valid_emails: int
    invalid_emails: int
    duplicate_emails: int
    sample_data: List[List[str]]


class CampaignSendRequest(BaseModel):
    """Request model for sending a campaign."""
    send_immediately: bool = Field(default=True, description="Send campaign immediately")
    test_mode: bool = Field(default=False, description="Send in test mode (mock)")


# Background task functions
def send_single_email_task(email_send_id: int, db_session=None) -> dict:
    """
    Send a single email as part of a campaign. Used by Cloud Tasks.
    
    Args:
        email_send_id: ID of the EmailSend record to process
        db_session: Optional database session (will create one if not provided)
        
    Returns:
        Dictionary with result status and details
    """
    from app.services.email_service import EmailAddress, EmailMessage
    
    # Get database session
    if db_session is None:
        db = db_manager.get_session()
        should_close_db = True
    else:
        db = db_session
        should_close_db = False
    
    try:
        # Get email send record
        email_send = db.query(EmailSend).filter(EmailSend.id == email_send_id).first()
        if not email_send:
            return {'status': 'error', 'message': 'EmailSend record not found'}
        
        # Skip if already sent or failed too many times
        if email_send.status != EmailStatus.PENDING:
            return {'status': 'skipped', 'message': f'Email status is {email_send.status.value}'}
        
        # Get campaign details
        campaign = db.query(Campaign).filter(Campaign.id == email_send.campaign_id).first()
        if not campaign:
            return {'status': 'error', 'message': 'Campaign not found'}
        
        # Check if campaign is still active
        if campaign.status == CampaignStatus.CANCELLED:
            email_send.status = EmailStatus.SKIPPED
            email_send.error_message = "Campaign was cancelled"
            db.commit()
            return {'status': 'skipped', 'message': 'Campaign was cancelled'}
        
        print(f"📧 Sending email to {email_send.recipient_email} for campaign: {campaign.name}")
        
        # Check if services are available
        if not email_service:
            raise Exception("Email service not initialized")
        if not google_sheets_service:
            raise Exception("Google Sheets service not initialized")
        
        try:
            # Create email address objects
            to_address = EmailAddress(
                email=email_send.recipient_email, 
                name=email_send.recipient_name
            )
            from_address = EmailAddress(
                email=email_service.default_from_email,
                name=email_service.default_from_name
            )
            
            # Create email message
            email_message = EmailMessage(
                to=to_address,
                subject=email_send.personalized_subject,
                body=email_send.personalized_message,
                from_email=from_address
            )
            
            # Send email
            result = email_service.send_email(email_message)
            
            if result.success:
                # Mark as sent
                email_send.status = EmailStatus.SENT
                email_send.sent_at = datetime.utcnow()
                email_send.smtp_response = result.smtp_response
                
                print(f"✅ Successfully sent email to {email_send.recipient_email}")
                
                # Mark as sent in Google Sheets (if row number available)
                if email_send.sheet_row_number:
                    try:
                        # Create a minimal email row object for the sheet update
                        from app.services.google_sheets import EmailRow
                        email_row = EmailRow(
                            row_number=email_send.sheet_row_number,
                            email=email_send.recipient_email,
                            name=email_send.recipient_name,
                            is_valid=True
                        )
                        
                        google_sheets_service.mark_emails_as_sent(
                            campaign.google_sheet_id,
                            [email_row],
                            status_column='sent'
                        )
                        email_send.marked_as_sent_in_sheet = True
                        print(f"✅ Marked as sent in Google Sheets")
                    except Exception as sheet_error:
                        print(f"⚠️  Could not mark email as sent in sheet: {sheet_error}")
                
                # Update send attempts and commit
                email_send.send_attempts += 1
                db.commit()
                
                return {
                    'status': 'success', 
                    'message': f'Email sent to {email_send.recipient_email}',
                    'smtp_response': result.smtp_response
                }
                
            else:
                # Mark as failed
                email_send.status = EmailStatus.FAILED
                email_send.error_message = result.error_message
                email_send.send_attempts += 1
                db.commit()
                
                print(f"❌ Failed to send email to {email_send.recipient_email}: {result.error_message}")
                
                return {
                    'status': 'failed',
                    'message': f'Email failed: {result.error_message}',
                    'smtp_response': result.smtp_response
                }
                
        except Exception as email_error:
            email_send.status = EmailStatus.FAILED
            email_send.error_message = str(email_error)
            email_send.send_attempts += 1
            db.commit()
            
            error_msg = f"Error sending email to {email_send.recipient_email}: {email_error}"
            print(f"❌ {error_msg}")
            
            return {'status': 'error', 'message': error_msg}
            
    except Exception as e:
        error_msg = f"Unexpected error processing email_send_id {email_send_id}: {e}"
        print(f"❌ {error_msg}")
        return {'status': 'error', 'message': error_msg}
        
    finally:
        if should_close_db:
            db.close()





def start_campaign_with_cloud_tasks(campaign_id: int) -> dict:
    """
    Start campaign using Cloud Tasks for scalable email processing.
    
    Creates individual Cloud Tasks for each email instead of processing
    them in a long-running process. This enables resilient email sending
    that survives Cloud Run instance restarts.
    
    Args:
        campaign_id: ID of the campaign to start
        
    Returns:
        Dictionary with status and details
    """
    db = db_manager.get_session()
    
    try:
        # Get campaign details
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return {'status': 'error', 'message': 'Campaign not found'}
        
        print(f"🚀 Starting campaign with Cloud Tasks: {campaign.name} (ID: {campaign_id})")
        
        # Update campaign status to sending
        campaign.status = CampaignStatus.SENDING
        campaign.started_at = datetime.utcnow()
        db.commit()
        
        # Get email list from Google Sheets
        if not google_sheets_service:
            raise Exception("Google Sheets service not initialized")
        
        try:
            email_data = google_sheets_service.read_email_addresses(
                campaign.google_sheet_id,
                campaign.google_sheet_range
            )
            print(f"📋 Retrieved {len(email_data)} emails from Google Sheets")
        except Exception as e:
            print(f"❌ Error retrieving emails from Google Sheets: {e}")
            campaign.status = CampaignStatus.FAILED
            campaign.error_message = f"Google Sheets error: {str(e)}"
            campaign.completed_at = datetime.utcnow()
            db.commit()
            return {'status': 'error', 'message': f'Google Sheets error: {str(e)}'}
        
        # Update total recipients count
        campaign.total_recipients = len(email_data)
        db.commit()
        
        # Create EmailSend records for all emails
        email_send_ids = []
        valid_email_count = 0
        
        for email_row in email_data:
            if not email_row.email.strip() or not email_row.is_valid:
                print(f"⚠️  Skipping invalid email at row {email_row.row_number}: {email_row.validation_error or 'invalid email'}")
                continue
            
            valid_email_count += 1
            
            recipient_email = email_row.email.strip()
            recipient_name = email_row.name.strip() if email_row.name else None
            
            # Personalize subject and message
            personalized_subject = campaign.subject
            personalized_message = campaign.message
            
            # Replace template variables
            template_vars = {
                'name': recipient_name or recipient_email.split('@')[0],
                'email': recipient_email,
                **(email_row.additional_data or {})
            }
            
            for var_name, var_value in template_vars.items():
                personalized_subject = personalized_subject.replace(f"{{{{{var_name}}}}}", str(var_value))
                personalized_message = personalized_message.replace(f"{{{{{var_name}}}}}", str(var_value))
            
            # Create email send record
            email_send = EmailSend(
                campaign_id=campaign_id,
                recipient_email=recipient_email,
                recipient_name=recipient_name,
                personalized_subject=personalized_subject,
                personalized_message=personalized_message,
                sheet_row_number=email_row.row_number,
                status=EmailStatus.PENDING
            )
            db.add(email_send)
            db.flush()  # Get the ID without committing
            email_send_ids.append(email_send.id)
        
        db.commit()
        print(f"📝 Created {valid_email_count} EmailSend records")
        
        # Create Cloud Tasks for each email with staggered delays
        try:
            from app.services.task_service import get_tasks_service
            tasks_service = get_tasks_service()
            
            created_tasks = tasks_service.create_campaign_tasks(
                email_send_ids=email_send_ids,
                delay_min_minutes=campaign.delay_min_minutes or 4,
                delay_max_minutes=campaign.delay_max_minutes or 7
            )
            
            print(f"✅ Created {len(created_tasks)} Cloud Tasks for campaign {campaign_id}")
            
            # Update campaign statistics
            campaign.update_statistics(db)
            db.commit()
            
            return {
                'status': 'success',
                'message': f'Campaign started with {len(created_tasks)} email tasks',
                'tasks_created': len(created_tasks),
                'emails_scheduled': valid_email_count
            }
            
        except Exception as task_error:
            print(f"❌ Error creating Cloud Tasks: {task_error}")
            
            # Mark campaign as failed
            campaign.status = CampaignStatus.FAILED
            campaign.error_message = f"Task creation error: {str(task_error)}"
            campaign.completed_at = datetime.utcnow()
            db.commit()
            
            return {
                'status': 'error',
                'message': f'Error creating email tasks: {str(task_error)}'
            }
        
    except Exception as e:
        print(f"❌ Unexpected error starting campaign: {e}")
        
        try:
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if campaign:
                campaign.status = CampaignStatus.FAILED
                campaign.error_message = str(e)
                campaign.completed_at = datetime.utcnow()
                db.commit()
        except Exception as update_error:
            print(f"❌ Could not update campaign status after error: {update_error}")
        
        return {'status': 'error', 'message': str(e)}
        
    finally:
        db.close()


# Root endpoint
@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Email Campaign API",
        "version": "1.0.0",
        "description": "REST API for managing email campaigns with Google Sheets integration",
        "docs": "/docs",
        "health": "/api/health",
        "timestamp": datetime.utcnow().isoformat()
    }


# Health check endpoints
@app.get("/api/health", response_model=HealthCheck)
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check for all services."""
    try:
        # Database health
        db_health = db_manager.health_check()
        
        # Google Sheets health
        sheets_health = {"status": "healthy", "connection": True}
        try:
            sheets_service = get_google_sheets_service()
            # Test with a minimal operation
            sheets_service.validate_sheet_id("test_validation_12345")
        except Exception as e:
            sheets_health = {"status": "unhealthy", "connection": False, "error": str(e)}
        
        # Email service health
        email_health = get_email_service().health_check()
        
        # Overall status
        all_healthy = (
            db_health["status"] == "healthy" and
            sheets_health["status"] == "healthy" and
            email_health["status"] == "healthy"
        )
        
        return HealthCheck(
            status="healthy" if all_healthy else "unhealthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            database=db_health,
            environment=os.getenv("ENVIRONMENT", "development")
        )
        
    except Exception as e:
        return HealthCheck(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            database={"status": "unhealthy", "error": str(e)},
            environment=os.getenv("ENVIRONMENT", "development")
        )


@app.get("/api/health/database")
async def database_health():
    """Database-specific health check."""
    try:
        health = db_manager.health_check()
        status_code = status.HTTP_200_OK if health["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
        return JSONResponse(status_code=status_code, content=health)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.get("/api/health/email")
async def email_health():
    """Email service health check."""
    try:
        email_svc = get_email_service()
        health = email_svc.health_check()
        status_code = status.HTTP_200_OK if health["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
        return JSONResponse(status_code=status_code, content=health)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)}
        )


# Google Sheets endpoints
@app.get("/api/sheets/{sheet_id}/preview", response_model=GoogleSheetPreviewResponse)
async def preview_google_sheet(
    sheet_id: str,
    sheet_range: str = Query(default="A:Z", description="Sheet range to preview"),
    max_rows: int = Query(default=10, ge=1, le=100, description="Maximum rows to preview"),
    sheets_service: GoogleSheetsService = Depends(get_google_sheets_service)
):
    """Preview a Google Sheet to validate data and show statistics."""
    try:
        # Get sheet preview data
        preview_data = sheets_service.get_preview_data(
            sheet_id=sheet_id,
            sheet_range=sheet_range,
            max_rows=max_rows
        )
        
        return GoogleSheetPreviewResponse(**preview_data)
        
    except GoogleSheetsError:
        raise  # Will be handled by custom exception handler
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error previewing sheet: {str(e)}"
        )


@app.post("/api/sheets/{sheet_id}/validate")
async def validate_google_sheet(
    sheet_id: str,
    sheets_service: GoogleSheetsService = Depends(get_google_sheets_service)
):
    """Validate Google Sheet access and format."""
    try:
        # Validate sheet ID format
        if not sheets_service.validate_sheet_id(sheet_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google Sheets ID format"
            )
        
        # Test sheet access
        can_access = sheets_service.test_sheet_access(sheet_id)
        
        if not can_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access Google Sheet. Check sharing permissions."
            )
        
        # Get sheet information
        sheet_info = sheets_service.get_sheet_info(sheet_id)
        
        return SuccessResponse(
            message="Google Sheet validation successful",
            data={
                "sheet_id": sheet_id,
                "sheet_name": sheet_info.sheet_name,
                "total_rows": sheet_info.total_rows,
                "valid_emails": sheet_info.valid_emails,
                "invalid_emails": sheet_info.invalid_emails,
                "email_column": sheet_info.email_column,
                "name_column": sheet_info.name_column
            },
            timestamp=datetime.utcnow()
        )
        
    except GoogleSheetsError:
        raise  # Will be handled by custom exception handler
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error validating sheet: {str(e)}"
        )


# Campaign CRUD endpoints
@app.post("/api/campaigns/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_db),
    sheets_service: GoogleSheetsService = Depends(get_google_sheets_service)
):
    """Create a new email campaign."""
    try:
        # Validate Google Sheet access
        if not sheets_service.test_sheet_access(campaign.google_sheet_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot access the specified Google Sheet"
            )
        
        # Get sheet info to populate recipient count
        sheet_info = sheets_service.get_sheet_info(campaign.google_sheet_id, campaign.google_sheet_range)
        
        # Create campaign in database
        db_campaign = Campaign(
            name=campaign.name,
            description=campaign.description,
            subject=campaign.subject,
            message=campaign.message,
            google_sheet_id=campaign.google_sheet_id,
            google_sheet_range=campaign.google_sheet_range,
            send_immediately=campaign.send_immediately,
            use_delay=campaign.use_delay,
            delay_min_minutes=campaign.delay_min_minutes,
            delay_max_minutes=campaign.delay_max_minutes,
            total_recipients=sheet_info.valid_emails,
            emails_pending=sheet_info.valid_emails
        )
        
        db.add(db_campaign)
        db.commit()
        db.refresh(db_campaign)
        
        # Convert to response model
        response_data = db_campaign.__dict__.copy()
        response_data.update({
            'success_rate': db_campaign.get_success_rate(),
            'failure_rate': db_campaign.get_failure_rate(),
            'is_active': db_campaign.is_active(),
            'is_completed': db_campaign.is_completed()
        })
        
        return CampaignResponse(**response_data)
        
    except GoogleSheetsError:
        raise  # Will be handled by custom exception handler
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error creating campaign"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error creating campaign: {str(e)}"
        )


@app.get("/api/campaigns/", response_model=List[CampaignSummary])
async def list_campaigns(
    skip: int = Query(default=0, ge=0, description="Number of campaigns to skip"),
    limit: int = Query(default=50, ge=1, le=200, description="Number of campaigns to return"),
    status_filter: Optional[str] = Query(default=None, description="Filter by campaign status"),
    db: Session = Depends(get_db)
):
    """List all campaigns with optional filtering and pagination."""
    try:
        query = db.query(Campaign)
        
        # Apply status filter if provided
        if status_filter:
            try:
                status_enum = CampaignStatus(status_filter.lower())
                query = query.filter(Campaign.status == status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status filter: {status_filter}"
                )
        
        # Apply pagination
        campaigns = query.order_by(Campaign.created_at.desc()).offset(skip).limit(limit).all()
        
        # Convert to summary format
        summaries = []
        for campaign in campaigns:
            # Create summary data dictionary with computed fields
            summary_data = {
                'id': campaign.id,
                'name': campaign.name,
                'status': campaign.status,
                'total_recipients': campaign.total_recipients,
                'emails_sent': campaign.emails_sent,
                'emails_failed': campaign.emails_failed,
                'success_rate': campaign.get_success_rate(),
                'created_at': campaign.created_at,
                'completed_at': campaign.completed_at
            }
            summary = CampaignSummary(**summary_data)
            summaries.append(summary)
        
        return summaries
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing campaigns: {str(e)}"
        )


@app.get("/api/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Get a specific campaign by ID."""
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Convert to response model with computed fields
        response_data = campaign.__dict__.copy()
        response_data.update({
            'success_rate': campaign.get_success_rate(),
            'failure_rate': campaign.get_failure_rate(),
            'is_active': campaign.is_active(),
            'is_completed': campaign.is_completed()
        })
        
        return CampaignResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving campaign: {str(e)}"
        )


@app.put("/api/campaigns/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_update: CampaignUpdate,
    db: Session = Depends(get_db),
    sheets_service: GoogleSheetsService = Depends(get_google_sheets_service)
):
    """Update an existing campaign."""
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Check if campaign can be updated
        if campaign.status in [CampaignStatus.SENDING, CampaignStatus.COMPLETED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update campaign that is sending or completed"
            )
        
        # Validate Google Sheet if changed
        if campaign_update.google_sheet_id and campaign_update.google_sheet_id != campaign.google_sheet_id:
            if not sheets_service.test_sheet_access(campaign_update.google_sheet_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot access the specified Google Sheet"
                )
        
        # Update fields
        update_data = campaign_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(campaign, field, value)
        
        db.commit()
        db.refresh(campaign)
        
        # Convert to response model
        response_data = campaign.__dict__.copy()
        response_data.update({
            'success_rate': campaign.get_success_rate(),
            'failure_rate': campaign.get_failure_rate(),
            'is_active': campaign.is_active(),
            'is_completed': campaign.is_completed()
        })
        
        return CampaignResponse(**response_data)
        
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error updating campaign"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error updating campaign: {str(e)}"
        )


@app.delete("/api/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Delete a campaign."""
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Check if campaign can be deleted
        if campaign.status == CampaignStatus.SENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete campaign that is currently sending"
            )
        
        db.delete(campaign)
        db.commit()
        
        return SuccessResponse(
            message="Campaign deleted successfully",
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error deleting campaign"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error deleting campaign: {str(e)}"
        )


@app.post("/api/campaigns/{campaign_id}/send")
async def send_campaign(
    campaign_id: int,
    send_request: CampaignSendRequest = CampaignSendRequest(),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Send a campaign (placeholder for background task)."""
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Check if campaign can be sent
        if campaign.status not in [CampaignStatus.DRAFT, CampaignStatus.SCHEDULED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campaign cannot be sent in current status"
            )
        
        # Update campaign status
        campaign.status = CampaignStatus.SCHEDULED if not send_request.send_immediately else CampaignStatus.SENDING
        campaign.started_at = datetime.utcnow() if send_request.send_immediately else None
        
        db.commit()
        
        # Use Cloud Tasks for all campaign processing (immediate and scheduled)
        result = start_campaign_with_cloud_tasks(campaign_id)
        if result['status'] == 'error':
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error starting campaign: {result['message']}"
            )
        
        return SuccessResponse(
            message=f"Campaign {'scheduled' if not send_request.send_immediately else 'started'} successfully",
            data={
                "campaign_id": campaign_id,
                "status": campaign.status.value,
                "test_mode": send_request.test_mode,
                "send_immediately": send_request.send_immediately
            },
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error updating campaign status"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error sending campaign: {str(e)}"
        )


@app.post("/api/campaigns/{campaign_id}/stop")
async def stop_campaign(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Stop a currently sending campaign."""
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Check if campaign can be stopped
        if campaign.status not in [CampaignStatus.SENDING, CampaignStatus.SCHEDULED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Campaign is not currently sending (status: {campaign.status.value})"
            )
        
        # Update campaign status to cancelled
        campaign.status = CampaignStatus.CANCELLED
        campaign.completed_at = datetime.utcnow()
        
        db.commit()
        
        return SuccessResponse(
            message=f"Campaign '{campaign.name}' stopped successfully",
            data={
                "campaign_id": campaign_id,
                "status": campaign.status.value,
                "stopped_at": campaign.completed_at.isoformat()
            },
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error stopping campaign"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error stopping campaign: {str(e)}"
        )


@app.get("/api/campaigns/{campaign_id}/emails", response_model=List[EmailSendResponse])
async def get_campaign_emails(
    campaign_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    status_filter: Optional[str] = Query(default=None),
    db: Session = Depends(get_db)
):
    """Get email sends for a specific campaign."""
    try:
        # Verify campaign exists
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Query email sends
        query = db.query(EmailSend).filter(EmailSend.campaign_id == campaign_id)
        
        # Apply status filter if provided
        if status_filter:
            try:
                status_enum = EmailStatus(status_filter.lower())
                query = query.filter(EmailSend.status == status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status filter: {status_filter}"
                )
        
        # Apply pagination
        email_sends = query.order_by(EmailSend.created_at.desc()).offset(skip).limit(limit).all()
        
        return [EmailSendResponse.model_validate(email_send) for email_send in email_sends]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving campaign emails: {str(e)}"
        )


# Email Template CRUD endpoints
@app.get("/api/templates/", response_model=List[EmailTemplateSummary])
async def list_templates(
    skip: int = Query(default=0, ge=0, description="Number of templates to skip"),
    limit: int = Query(default=50, ge=1, le=200, description="Number of templates to return"),
    db: Session = Depends(get_db)
):
    """List all email templates with pagination."""
    try:
        query = db.query(EmailTemplate)
        templates = query.order_by(EmailTemplate.created_at.desc()).offset(skip).limit(limit).all()
        
        # Convert to summary format
        summaries = []
        for template in templates:
            summary_data = {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'created_at': template.created_at,
                'variables_count': len(template.get_variables_list()) if template.variables else 0
            }
            summaries.append(EmailTemplateSummary(**summary_data))
        
        return summaries
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing templates: {str(e)}"
        )


@app.post("/api/templates/", response_model=EmailTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template: EmailTemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new email template."""
    try:
        # Create template in database
        db_template = EmailTemplate(
            name=template.name,
            description=template.description,
            subject=template.subject,
            message=template.message,
            variables=template.variables
        )
        
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        
        # Convert to response model
        response_data = db_template.__dict__.copy()
        response_data['variables_list'] = db_template.get_variables_list()
        
        return EmailTemplateResponse(**response_data)
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error creating template"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error creating template: {str(e)}"
        )


@app.get("/api/templates/{template_id}", response_model=EmailTemplateResponse)
async def get_template(template_id: int, db: Session = Depends(get_db)):
    """Get a specific email template by ID."""
    try:
        template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Convert to response model
        response_data = template.__dict__.copy()
        response_data['variables_list'] = template.get_variables_list()
        
        return EmailTemplateResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving template: {str(e)}"
        )


@app.put("/api/templates/{template_id}", response_model=EmailTemplateResponse)
async def update_template(
    template_id: int,
    template_update: EmailTemplateUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing email template."""
    try:
        template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Update fields
        update_data = template_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(template, field, value)
        
        template.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(template)
        
        # Convert to response model
        response_data = template.__dict__.copy()
        response_data['variables_list'] = template.get_variables_list()
        
        return EmailTemplateResponse(**response_data)
        
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error updating template"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error updating template: {str(e)}"
        )


@app.delete("/api/templates/{template_id}")
async def delete_template(template_id: int, db: Session = Depends(get_db)):
    """Delete an email template."""
    try:
        template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        db.delete(template)
        db.commit()
        
        return SuccessResponse(
            message="Template deleted successfully",
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error deleting template"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error deleting template: {str(e)}"
        )


# ============================================================================
# CLOUD TASKS ENDPOINTS
# ============================================================================

@app.post("/api/tasks/send-email")
async def handle_send_email_task(request: Request):
    """
    Handle individual email sending task from Cloud Tasks.
    
    This endpoint is called by Google Cloud Tasks to send individual emails
    as part of a campaign, enabling resilient and scalable email processing.
    """
    try:
        # Parse the request payload
        payload = await request.json()
        email_send_id = payload.get('email_send_id')
        
        if not email_send_id:
            return {
                "status": "error", 
                "message": "Missing email_send_id in payload"
            }
        
        # Send the email using our helper function
        result = send_single_email_task(email_send_id)
        
        # Update campaign statistics after processing email
        if result['status'] in ['success', 'failed']:
            try:
                db = db_manager.get_session()
                
                # Get the email record to find campaign
                email_send = db.query(EmailSend).filter(EmailSend.id == email_send_id).first()
                if email_send:
                    campaign = db.query(Campaign).filter(Campaign.id == email_send.campaign_id).first()
                    if campaign:
                        # Update campaign statistics
                        campaign.update_statistics(db)
                        
                        # Check if campaign is complete
                        if campaign.emails_pending == 0:
                            campaign.status = CampaignStatus.COMPLETED
                            campaign.completed_at = datetime.utcnow()
                            print(f"🎉 Campaign {campaign.id} ({campaign.name}) completed!")
                        
                        db.commit()
                        print(f"📊 Updated statistics for campaign {campaign.id}")
                
                db.close()
                
            except Exception as stats_error:
                print(f"⚠️ Error updating campaign statistics: {stats_error}")
        
        return result
        
    except json.JSONDecodeError:
        return {
            "status": "error", 
            "message": "Invalid JSON payload"
        }
    except Exception as e:
        error_msg = f"Error processing email task: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "status": "error", 
            "message": error_msg
        }


@app.get("/api/tasks/health")
async def tasks_health_check():
    """Health check endpoint for Cloud Tasks queue."""
    try:
        from app.services.task_service import get_tasks_service
        
        tasks_service = get_tasks_service()
        queue_info = tasks_service.get_queue_info()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "queue_info": queue_info
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# Development server entry point
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", os.getenv("API_PORT", "8000"))),  # Check PORT first, then API_PORT
        reload=os.getenv("API_RELOAD", "false").lower() == "true",   # Default to false for production
        log_level="info"
    )