"""
Email service for Email Campaign App.

Provides functionality to send emails via SMTP (SpaceMail) with personalization,
connection testing, and comprehensive error handling.
"""

import os
import re
import smtplib
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, parseaddr
import asyncio
import aiosmtplib
from email_validator import validate_email, EmailNotValidError
from jinja2 import Template
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class EmailAddress:
    """Represents an email address with optional name."""
    email: str
    name: Optional[str] = None
    
    def __str__(self) -> str:
        if self.name:
            return formataddr((self.name, self.email))
        return self.email
    
    @classmethod
    def from_string(cls, email_string: str) -> 'EmailAddress':
        """Create EmailAddress from string like 'Name <email@domain.com>' or 'email@domain.com'."""
        name, email = parseaddr(email_string)
        return cls(email=email, name=name if name else None)


@dataclass
class EmailMessage:
    """Represents an email message."""
    to: EmailAddress
    subject: str
    body: str
    from_email: Optional[EmailAddress] = None
    reply_to: Optional[EmailAddress] = None
    additional_headers: Optional[Dict[str, str]] = None


@dataclass
class EmailResult:
    """Represents the result of sending an email."""
    success: bool
    recipient: str
    message_id: Optional[str] = None
    smtp_response: Optional[str] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    sent_at: Optional[datetime] = None
    retry_count: int = 0


class EmailServiceError(Exception):
    """Base exception for email service operations."""
    pass


class EmailConnectionError(EmailServiceError):
    """SMTP connection error."""
    pass


class EmailAuthenticationError(EmailServiceError):
    """SMTP authentication error."""
    pass


class EmailSendError(EmailServiceError):
    """Email sending error."""
    pass


class EmailValidationError(EmailServiceError):
    """Email validation error."""
    pass


class EmailService:
    """
    Email service class for sending emails via SMTP.
    
    Supports both SpaceMail and generic SMTP servers with connection testing,
    email personalization, and comprehensive error handling.
    """
    
    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        use_tls: Optional[bool] = None,
        use_ssl: Optional[bool] = None,
        default_from_email: Optional[str] = None,
        default_from_name: Optional[str] = None,
        mock_mode: Optional[bool] = None
    ):
        """
        Initialize email service.
        
        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            smtp_username: SMTP username
            smtp_password: SMTP password
            use_tls: Whether to use TLS
            use_ssl: Whether to use SSL
            default_from_email: Default sender email
            default_from_name: Default sender name
            mock_mode: Whether to mock email sending (for testing)
        """
        # SMTP Configuration
        self.smtp_host = smtp_host or os.getenv('SMTP_HOST', 'smtp.spacemail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = smtp_username or os.getenv('SMTP_USERNAME', '')
        self.smtp_password = smtp_password or os.getenv('SMTP_PASSWORD', '')
        self.use_tls = use_tls if use_tls is not None else os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
        self.use_ssl = use_ssl if use_ssl is not None else os.getenv('SMTP_USE_SSL', 'false').lower() == 'true'
        
        # Default sender configuration
        self.default_from_email = default_from_email or os.getenv('DEFAULT_FROM_EMAIL', '')
        self.default_from_name = default_from_name or os.getenv('DEFAULT_FROM_NAME', '')
        
        # Email settings
        self.mock_mode = mock_mode if mock_mode is not None else os.getenv('MOCK_EMAIL_SENDING', 'false').lower() == 'true'
        self.rate_limit = int(os.getenv('EMAIL_RATE_LIMIT', '60'))  # emails per minute
        self.max_retry_attempts = int(os.getenv('EMAIL_RETRY_ATTEMPTS', '3'))
        self.retry_delay = int(os.getenv('EMAIL_RETRY_DELAY_SECONDS', '300'))  # 5 minutes
        
        # Connection pool for async operations
        self._connection_pool = None
        
        # Validate configuration
        self._validate_configuration()
    
    def _validate_configuration(self):
        """Validate email service configuration."""
        if not self.smtp_host:
            raise EmailServiceError("SMTP host is required")
        
        if not self.smtp_username and not self.mock_mode:
            raise EmailServiceError("SMTP username is required")
        
        if not self.smtp_password and not self.mock_mode:
            raise EmailServiceError("SMTP password is required")
        
        if not self.default_from_email and not self.mock_mode:
            raise EmailServiceError("Default from email is required")
        
        # Validate default from email format
        if self.default_from_email:
            try:
                validate_email(self.default_from_email)
            except EmailNotValidError as e:
                raise EmailValidationError(f"Invalid default from email: {e}")
    
    def test_connection(self) -> bool:
        """
        Test SMTP connection.
        
        Returns:
            True if connection successful, False otherwise
            
        Raises:
            EmailConnectionError: If connection fails
            EmailAuthenticationError: If authentication fails
        """
        if self.mock_mode:
            return True
        
        try:
            # Create SMTP connection
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=30)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)
                if self.use_tls:
                    server.starttls()
            
            # Test authentication
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            
            # Test connection
            server.noop()
            server.quit()
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            raise EmailAuthenticationError(f"SMTP authentication failed: {e}")
        except smtplib.SMTPConnectError as e:
            raise EmailConnectionError(f"SMTP connection failed: {e}")
        except smtplib.SMTPServerDisconnected as e:
            raise EmailConnectionError(f"SMTP server disconnected: {e}")
        except smtplib.SMTPException as e:
            raise EmailConnectionError(f"SMTP error: {e}")
        except Exception as e:
            raise EmailConnectionError(f"Unexpected connection error: {e}")
    
    def validate_email_address(self, email: str) -> bool:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False
    
    def personalize_message(self, template: str, recipient_name: Optional[str] = None, **kwargs) -> str:
        """
        Personalize email message with recipient information.
        
        Args:
            template: Email template with placeholders
            recipient_name: Recipient's name
            **kwargs: Additional template variables
            
        Returns:
            Personalized message
        """
        try:
            # Create template context
            context = {
                'name': recipient_name or 'there',
                'first_name': recipient_name.split()[0] if recipient_name else 'there',
                **kwargs
            }
            
            # Use Jinja2 for advanced templating
            jinja_template = Template(template)
            personalized = jinja_template.render(**context)
            
            # Fallback to simple string formatting for basic placeholders
            if '{{' not in template and '{' in template:
                try:
                    personalized = template.format(**context)
                except KeyError:
                    # If some keys are missing, use partial formatting
                    for key, value in context.items():
                        placeholder = '{' + key + '}'
                        if placeholder in template:
                            personalized = personalized.replace(placeholder, str(value))
            
            return personalized
            
        except Exception as e:
            # If personalization fails, return original template
            return template
    
    def create_email_message(
        self,
        to_email: str,
        subject: str,
        body: str,
        to_name: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
        **template_vars
    ) -> EmailMessage:
        """
        Create an email message with personalization.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body template
            to_name: Recipient name
            from_email: Sender email (defaults to configured)
            from_name: Sender name (defaults to configured)
            reply_to: Reply-to email address
            **template_vars: Additional template variables
            
        Returns:
            EmailMessage object
            
        Raises:
            EmailValidationError: If email addresses are invalid
        """
        # Validate recipient email
        if not self.validate_email_address(to_email):
            raise EmailValidationError(f"Invalid recipient email: {to_email}")
        
        # Set defaults
        from_email = from_email or self.default_from_email
        from_name = from_name or self.default_from_name
        
        # Validate sender email
        if from_email and not self.validate_email_address(from_email):
            raise EmailValidationError(f"Invalid sender email: {from_email}")
        
        # Personalize subject and body
        personalized_subject = self.personalize_message(subject, to_name, **template_vars)
        personalized_body = self.personalize_message(body, to_name, **template_vars)
        
        return EmailMessage(
            to=EmailAddress(email=to_email, name=to_name),
            subject=personalized_subject,
            body=personalized_body,
            from_email=EmailAddress(email=from_email, name=from_name) if from_email else None,
            reply_to=EmailAddress.from_string(reply_to) if reply_to else None
        )
    
    def send_email(self, message: EmailMessage, retry_count: int = 0) -> EmailResult:
        """
        Send a single email message.
        
        Args:
            message: EmailMessage to send
            retry_count: Current retry attempt
            
        Returns:
            EmailResult with send status and details
        """
        start_time = datetime.utcnow()
        
        # Mock mode for testing
        if self.mock_mode:
            return EmailResult(
                success=True,
                recipient=message.to.email,
                message_id=f"mock_{int(start_time.timestamp())}",
                smtp_response="250 OK (Mock Mode)",
                sent_at=start_time,
                retry_count=retry_count
            )
        
        try:
            # Create SMTP connection
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=30)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)
                if self.use_tls:
                    server.starttls()
            
            # Authenticate
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            
            # Create MIME message
            mime_msg = MIMEText(message.body, 'plain', 'utf-8')
            mime_msg['Subject'] = message.subject
            mime_msg['From'] = str(message.from_email) if message.from_email else self.default_from_email
            mime_msg['To'] = str(message.to)
            
            if message.reply_to:
                mime_msg['Reply-To'] = str(message.reply_to)
            
            # Add additional headers
            if message.additional_headers:
                for key, value in message.additional_headers.items():
                    mime_msg[key] = value
            
            # Send email
            smtp_response = server.send_message(mime_msg)
            server.quit()
            
            # Extract message ID from response if available
            message_id = f"email_{int(start_time.timestamp())}_{hash(message.to.email)}"
            
            return EmailResult(
                success=True,
                recipient=message.to.email,
                message_id=message_id,
                smtp_response=str(smtp_response) if smtp_response else "250 OK",
                sent_at=datetime.utcnow(),
                retry_count=retry_count
            )
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP authentication failed: {e}"
            return EmailResult(
                success=False,
                recipient=message.to.email,
                error_message=error_msg,
                error_code="AUTH_FAILED",
                retry_count=retry_count
            )
            
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"Recipient refused: {e}"
            return EmailResult(
                success=False,
                recipient=message.to.email,
                error_message=error_msg,
                error_code="RECIPIENT_REFUSED",
                retry_count=retry_count
            )
            
        except smtplib.SMTPSenderRefused as e:
            error_msg = f"Sender refused: {e}"
            return EmailResult(
                success=False,
                recipient=message.to.email,
                error_message=error_msg,
                error_code="SENDER_REFUSED",
                retry_count=retry_count
            )
            
        except smtplib.SMTPDataError as e:
            error_msg = f"SMTP data error: {e}"
            return EmailResult(
                success=False,
                recipient=message.to.email,
                error_message=error_msg,
                error_code="DATA_ERROR",
                retry_count=retry_count
            )
            
        except smtplib.SMTPConnectError as e:
            error_msg = f"SMTP connection failed: {e}"
            return EmailResult(
                success=False,
                recipient=message.to.email,
                error_message=error_msg,
                error_code="CONNECTION_FAILED",
                retry_count=retry_count
            )
            
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {e}"
            return EmailResult(
                success=False,
                recipient=message.to.email,
                error_message=error_msg,
                error_code="SMTP_ERROR",
                retry_count=retry_count
            )
            
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            return EmailResult(
                success=False,
                recipient=message.to.email,
                error_message=error_msg,
                error_code="UNKNOWN_ERROR",
                retry_count=retry_count
            )
    
    def send_email_with_retry(self, message: EmailMessage) -> EmailResult:
        """
        Send email with automatic retry on failure.
        
        Args:
            message: EmailMessage to send
            
        Returns:
            EmailResult with final send status
        """
        last_result = None
        
        for attempt in range(self.max_retry_attempts):
            result = self.send_email(message, retry_count=attempt)
            
            if result.success:
                return result
            
            last_result = result
            
            # Don't retry for certain error types
            if result.error_code in ['AUTH_FAILED', 'SENDER_REFUSED', 'RECIPIENT_REFUSED']:
                break
            
            # Wait before retry (except on last attempt)
            if attempt < self.max_retry_attempts - 1:
                import time
                time.sleep(self.retry_delay)
        
        return last_result or EmailResult(
            success=False,
            recipient=message.to.email,
            error_message="Failed after maximum retry attempts",
            error_code="MAX_RETRIES_EXCEEDED"
        )
    

    
    async def send_email_async(self, message: EmailMessage) -> EmailResult:
        """
        Send email asynchronously using aiosmtplib.
        
        Args:
            message: EmailMessage to send
            
        Returns:
            EmailResult with send status
        """
        start_time = datetime.utcnow()
        
        # Mock mode for testing
        if self.mock_mode:
            return EmailResult(
                success=True,
                recipient=message.to.email,
                message_id=f"async_mock_{int(start_time.timestamp())}",
                smtp_response="250 OK (Async Mock Mode)",
                sent_at=start_time
            )
        
        try:
            # Create MIME message
            mime_msg = MIMEText(message.body, 'plain', 'utf-8')
            mime_msg['Subject'] = message.subject
            mime_msg['From'] = str(message.from_email) if message.from_email else self.default_from_email
            mime_msg['To'] = str(message.to)
            
            if message.reply_to:
                mime_msg['Reply-To'] = str(message.reply_to)
            
            # Send via aiosmtplib
            await aiosmtplib.send(
                mime_msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                use_tls=self.use_tls,
                start_tls=self.use_tls and not self.use_ssl
            )
            
            message_id = f"async_email_{int(start_time.timestamp())}_{hash(message.to.email)}"
            
            return EmailResult(
                success=True,
                recipient=message.to.email,
                message_id=message_id,
                smtp_response="250 OK (Async)",
                sent_at=datetime.utcnow()
            )
            
        except Exception as e:
            return EmailResult(
                success=False,
                recipient=message.to.email,
                error_message=f"Async send error: {e}",
                error_code="ASYNC_SEND_ERROR"
            )
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get email service connection information.
        
        Returns:
            Dictionary with connection details
        """
        return {
            'smtp_host': self.smtp_host,
            'smtp_port': self.smtp_port,
            'use_tls': self.use_tls,
            'use_ssl': self.use_ssl,
            'default_from_email': self.default_from_email,
            'default_from_name': self.default_from_name,
            'mock_mode': self.mock_mode,
            'rate_limit': self.rate_limit,
            'max_retry_attempts': self.max_retry_attempts,
            'retry_delay': self.retry_delay
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform email service health check.
        
        Returns:
            Dictionary with health check results
        """
        try:
            connection_ok = self.test_connection()
            config = self.get_connection_info()
            
            return {
                'status': 'healthy' if connection_ok else 'unhealthy',
                'connection': connection_ok,
                'config': config,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'connection': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


# Convenience functions for common use cases
def create_email_service() -> EmailService:
    """Create email service with default configuration from environment."""
    return EmailService()


def send_simple_email(
    to_email: str,
    subject: str,
    body: str,
    to_name: Optional[str] = None,
    **template_vars
) -> EmailResult:
    """
    Send a simple email with default configuration.
    
    Args:
        to_email: Recipient email
        subject: Email subject
        body: Email body
        to_name: Recipient name
        **template_vars: Template variables
        
    Returns:
        EmailResult
    """
    service = create_email_service()
    message = service.create_email_message(
        to_email=to_email,
        subject=subject,
        body=body,
        to_name=to_name,
        **template_vars
    )
    return service.send_email_with_retry(message)