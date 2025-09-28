"""
SQLAlchemy models for Email Campaign App.

Defines database models for Campaign and EmailSend entities with proper
relationships, indexes, and constraints.
"""

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer, 
    String, Text, Index, event, func
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CampaignStatus(PyEnum):
    """Campaign status enumeration."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EmailStatus(PyEnum):
    """Email send status enumeration."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"
    SKIPPED = "skipped"


class Campaign(Base):
    """
    Campaign model for email campaigns.
    
    Represents an email campaign with associated metadata,
    Google Sheets source, and email content.
    """
    
    __tablename__ = "campaigns"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Campaign basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Email content
    subject = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)
    
    # Google Sheets integration
    google_sheet_id = Column(String(100), nullable=False, index=True)
    google_sheet_range = Column(String(50), default="A:Z")
    
    # Campaign status and metadata
    status = Column(
        Enum(CampaignStatus), 
        default=CampaignStatus.DRAFT, 
        nullable=False,
        index=True
    )
    
    # Email statistics
    total_recipients = Column(Integer, default=0)
    emails_sent = Column(Integer, default=0)
    emails_failed = Column(Integer, default=0)
    emails_pending = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False,
        index=True
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Configuration
    send_immediately = Column(Boolean, default=True)
    use_delay = Column(Boolean, default=False)
    delay_min_minutes = Column(Integer, default=4)
    delay_max_minutes = Column(Integer, default=7)
    
    # Business hours configuration
    respect_business_hours = Column(Boolean, default=False)
    business_hours_start = Column(Integer, default=7)  # 7 AM (24-hour format)
    business_hours_end = Column(Integer, default=17)   # 5 PM (24-hour format)
    business_days_only = Column(Boolean, default=True)  # Monday-Friday only
    timezone = Column(String(50), default="UTC")  # Timezone for business hours
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    error_count = Column(Integer, default=0)
    
    # Relationships
    email_sends = relationship(
        "EmailSend", 
        back_populates="campaign",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Campaign(id={self.id}, name='{self.name}', status='{self.status.value}')>"
    
    def get_success_rate(self):
        """Calculate campaign success rate as percentage."""
        total = getattr(self, 'total_recipients', 0) or 0
        sent = getattr(self, 'emails_sent', 0) or 0
        if total == 0:
            return 0.0
        return (sent / total) * 100
    
    def get_failure_rate(self):
        """Calculate campaign failure rate as percentage."""
        total = getattr(self, 'total_recipients', 0) or 0
        failed = getattr(self, 'emails_failed', 0) or 0
        if total == 0:
            return 0.0
        return (failed / total) * 100
    
    def is_active(self):
        """Check if campaign is currently active (sending)."""
        active_statuses = [CampaignStatus.SCHEDULED, CampaignStatus.SENDING]
        return self.status in active_statuses
    
    def is_completed(self):
        """Check if campaign is completed (success or failure)."""
        completed_statuses = [
            CampaignStatus.COMPLETED, 
            CampaignStatus.FAILED, 
            CampaignStatus.CANCELLED
        ]
        return self.status in completed_statuses
    
    def update_statistics(self, session):
        """Update campaign statistics based on email sends."""
        # Count emails by status
        total_count = session.query(EmailSend).filter(EmailSend.campaign_id == self.id).count()
        sent_count = session.query(EmailSend).filter(
            EmailSend.campaign_id == self.id,
            EmailSend.status == EmailStatus.SENT
        ).count()
        failed_count = session.query(EmailSend).filter(
            EmailSend.campaign_id == self.id,
            EmailSend.status == EmailStatus.FAILED
        ).count()
        pending_count = session.query(EmailSend).filter(
            EmailSend.campaign_id == self.id,
            EmailSend.status == EmailStatus.PENDING
        ).count()
        
        # Update statistics
        self.total_recipients = total_count
        self.emails_sent = sent_count
        self.emails_failed = failed_count
        self.emails_pending = pending_count


class EmailTemplate(Base):
    """
    EmailTemplate model for reusable email templates.
    
    Stores template email content that can be reused across campaigns.
    """
    
    __tablename__ = "email_templates"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Template information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Email content (same as Campaign fields for easy reuse)
    subject = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)
    
    # Template metadata
    variables = Column(Text, nullable=True)  # Comma-separated list of variables
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False,
        index=True
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    def __repr__(self):
        return f"<EmailTemplate(id={self.id}, name='{self.name}')>"
    
    def get_variables_list(self):
        """Get template variables as a list."""
        variables_str = getattr(self, 'variables', None)
        if not variables_str:
            return []
        return [var.strip() for var in variables_str.split(',') if var.strip()]


class EmailSend(Base):
    """
    EmailSend model for individual email send records.
    
    Tracks each individual email sent as part of a campaign,
    including recipient information and send status.
    """
    
    __tablename__ = "email_sends"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to campaign
    campaign_id = Column(
        Integer, 
        ForeignKey("campaigns.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    # Recipient information
    recipient_email = Column(String(255), nullable=False, index=True)
    recipient_name = Column(String(255), nullable=True)
    
    # Email content (personalized)
    personalized_subject = Column(String(500), nullable=False)
    personalized_message = Column(Text, nullable=False)
    
    # Send status and tracking
    status = Column(
        Enum(EmailStatus), 
        default=EmailStatus.PENDING, 
        nullable=False,
        index=True
    )
    
    # Send attempts and timing
    send_attempts = Column(Integer, default=0)
    max_send_attempts = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False,
        index=True
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    smtp_response = Column(Text, nullable=True)
    
    # Google Sheets tracking
    sheet_row_number = Column(Integer, nullable=True)
    marked_as_sent_in_sheet = Column(Boolean, default=False)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="email_sends")
    
    def __repr__(self):
        return f"<EmailSend(id={self.id}, email='{self.recipient_email}', status='{self.status.value}')>"
    
    def can_retry(self):
        """Check if email send can be retried."""
        return (
            self.status == EmailStatus.FAILED and 
            self.send_attempts < self.max_send_attempts
        )
    
    def mark_as_sent(self, smtp_response=None):
        """Mark email as successfully sent."""
        self.status = EmailStatus.SENT
        self.sent_at = datetime.utcnow()
        if smtp_response:
            self.smtp_response = smtp_response
    
    def mark_as_failed(self, error_message, smtp_response=None):
        """Mark email as failed."""
        self.status = EmailStatus.FAILED
        self.error_message = error_message
        if smtp_response:
            self.smtp_response = smtp_response
        self.send_attempts += 1
    
    def mark_as_skipped(self, reason):
        """Mark email as skipped."""
        self.status = EmailStatus.SKIPPED
        self.error_message = f"Skipped: {reason}"


# SQLAlchemy event listeners for automatic timestamp updates
@event.listens_for(Campaign, 'before_update')
def campaign_before_update(mapper, connection, target):
    """Update campaign updated_at timestamp before update."""
    target.updated_at = datetime.utcnow()


@event.listens_for(EmailSend, 'before_update')
def email_send_before_update(mapper, connection, target):
    """Update email_send updated_at timestamp before update."""
    target.updated_at = datetime.utcnow()