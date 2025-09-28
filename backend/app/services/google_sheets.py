"""
Google Sheets service for Email Campaign App.

Provides functionality to read email addresses from Google Sheets,
validate sheet access, and mark emails as sent.
"""

import os
import re
import json
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

import httpx
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email_validator import validate_email, EmailNotValidError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class EmailRow:
    """Represents an email row from Google Sheets."""
    row_number: int
    email: str
    name: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None
    is_valid: bool = True
    validation_error: Optional[str] = None


@dataclass
class SheetInfo:
    """Represents Google Sheets information."""
    sheet_id: str
    sheet_name: Optional[str] = None
    total_rows: int = 0
    headers: Optional[List[str]] = None
    email_column: Optional[str] = None
    name_column: Optional[str] = None
    valid_emails: int = 0
    invalid_emails: int = 0
    duplicate_emails: int = 0


class GoogleSheetsError(Exception):
    """Base exception for Google Sheets operations."""
    pass


class GoogleSheetsAuthError(GoogleSheetsError):
    """Authentication error for Google Sheets."""
    pass


class GoogleSheetsAccessError(GoogleSheetsError):
    """Access error for Google Sheets."""
    pass


class GoogleSheetsValidationError(GoogleSheetsError):
    """Validation error for Google Sheets data."""
    pass


class GoogleSheetsService:
    """
    Google Sheets service class for email campaign management.
    
    Handles authentication, reading email addresses, validating data,
    and updating sheets with email send status.
    """
    
    # Google Sheets API scope
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    # Common email column names to detect automatically
    EMAIL_COLUMN_NAMES = [
        'email', 'email address', 'e-mail', 'mail', 
        'email_address', 'user_email', 'contact_email'
    ]
    
    # Common name column names to detect automatically
    NAME_COLUMN_NAMES = [
        'name', 'full name', 'first name', 'firstname', 
        'last name', 'lastname', 'full_name', 'contact_name',
        'recipient', 'recipient_name', 'user_name', 'username'
    ]
    
    # Status column name for marking emails as sent
    STATUS_COLUMN_NAME = 'Email Status'
    SENT_STATUS_VALUE = 'Sent'
    
    def __init__(self, credentials_file: Optional[str] = None):
        """
        Initialize Google Sheets service.
        
        Args:
            credentials_file: Path to Google service account credentials file
        """
        self.credentials_file = credentials_file or os.getenv(
            'GOOGLE_CREDENTIALS_FILE', 
            'credentials.json'
        )
        self._service = None
        self._credentials = None
        
    def _get_credentials(self) -> Credentials:
        """
        Get Google service account credentials.
        
        Returns:
            Google service account credentials
            
        Raises:
            GoogleSheetsAuthError: If credentials cannot be loaded
        """
        if self._credentials:
            return self._credentials
            
        try:
            # Try to load from file first
            if os.path.exists(self.credentials_file):
                self._credentials = Credentials.from_service_account_file(
                    self.credentials_file, 
                    scopes=self.SCOPES
                )
            else:
                # Try to load from environment variable
                credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
                if credentials_json:
                    credentials_info = json.loads(credentials_json)
                    self._credentials = Credentials.from_service_account_info(
                        credentials_info,
                        scopes=self.SCOPES
                    )
                else:
                    raise GoogleSheetsAuthError(
                        f"Google credentials not found. Expected file: {self.credentials_file} "
                        "or environment variable: GOOGLE_CREDENTIALS_JSON"
                    )
                    
            return self._credentials
            
        except json.JSONDecodeError as e:
            raise GoogleSheetsAuthError(f"Invalid JSON in credentials: {e}")
        except Exception as e:
            raise GoogleSheetsAuthError(f"Failed to load Google credentials: {e}")
    
    def _get_service(self):
        """
        Get Google Sheets API service.
        
        Returns:
            Google Sheets API service instance
            
        Raises:
            GoogleSheetsAuthError: If service cannot be created
        """
        if self._service:
            return self._service
            
        try:
            credentials = self._get_credentials()
            self._service = build('sheets', 'v4', credentials=credentials)
            return self._service
            
        except Exception as e:
            raise GoogleSheetsAuthError(f"Failed to create Google Sheets service: {e}")
    
    def validate_sheet_id(self, sheet_id: str) -> bool:
        """
        Validate Google Sheets ID format.
        
        Args:
            sheet_id: Google Sheets ID
            
        Returns:
            True if valid format, False otherwise
        """
        if not sheet_id or len(sheet_id) < 10:
            return False
            
        # Google Sheets IDs are typically 44 characters, alphanumeric with hyphens and underscores
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, sheet_id))
    
    def test_sheet_access(self, sheet_id: str) -> bool:
        """
        Test if we can access a Google Sheet.
        
        Args:
            sheet_id: Google Sheets ID
            
        Returns:
            True if accessible, False otherwise
        """
        try:
            service = self._get_service()
            # Try to get sheet metadata
            service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            return True
            
        except HttpError as e:
            if e.resp.status == 404:
                return False  # Sheet not found
            elif e.resp.status == 403:
                return False  # No permission
            else:
                return False  # Other errors
        except Exception:
            return False
    
    def get_sheet_info(self, sheet_id: str, sheet_range: str = "A:Z") -> SheetInfo:
        """
        Get information about a Google Sheet.
        
        Args:
            sheet_id: Google Sheets ID
            sheet_range: Range to analyze (default: A:Z)
            
        Returns:
            SheetInfo object with sheet metadata
            
        Raises:
            GoogleSheetsAccessError: If sheet cannot be accessed
            GoogleSheetsValidationError: If sheet data is invalid
        """
        if not self.validate_sheet_id(sheet_id):
            raise GoogleSheetsValidationError(f"Invalid Google Sheets ID format: {sheet_id}")
        
        try:
            service = self._get_service()
            
            # Get sheet metadata
            sheet_metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            sheet_name = sheet_metadata.get('properties', {}).get('title', 'Unknown')
            
            # Get sheet data
            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=sheet_range
            ).execute()
            
            values = result.get('values', [])
            if not values:
                raise GoogleSheetsValidationError("Sheet is empty or has no data")
            
            headers = values[0] if values else []
            total_rows = len(values)
            
            # Detect email and name columns
            email_column = self._detect_email_column(headers)
            name_column = self._detect_name_column(headers)
            
            # Analyze email data
            email_stats = self._analyze_email_data(values, email_column)
            
            return SheetInfo(
                sheet_id=sheet_id,
                sheet_name=sheet_name,
                total_rows=total_rows,
                headers=headers,
                email_column=email_column,
                name_column=name_column,
                valid_emails=email_stats['valid'],
                invalid_emails=email_stats['invalid'],
                duplicate_emails=email_stats['duplicates']
            )
            
        except HttpError as e:
            if e.resp.status == 404:
                raise GoogleSheetsAccessError(f"Sheet not found: {sheet_id}")
            elif e.resp.status == 403:
                raise GoogleSheetsAccessError(f"No permission to access sheet: {sheet_id}")
            else:
                raise GoogleSheetsAccessError(f"Failed to access sheet: {e}")
        except GoogleSheetsError:
            raise  # Re-raise our custom exceptions
        except Exception as e:
            raise GoogleSheetsAccessError(f"Unexpected error accessing sheet: {e}")
    
    def read_email_addresses(self, sheet_id: str, sheet_range: str = "A:Z") -> List[EmailRow]:
        """
        Read email addresses from a Google Sheet.
        
        Args:
            sheet_id: Google Sheets ID
            sheet_range: Range to read (default: A:Z)
            
        Returns:
            List of EmailRow objects
            
        Raises:
            GoogleSheetsAccessError: If sheet cannot be accessed
            GoogleSheetsValidationError: If sheet data is invalid
        """
        try:
            service = self._get_service()
            
            # Get sheet data
            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=sheet_range
            ).execute()
            
            values = result.get('values', [])
            if not values:
                raise GoogleSheetsValidationError("Sheet is empty or has no data")
            
            headers = values[0] if values else []
            data_rows = values[1:] if len(values) > 1 else []
            
            # Detect email and name columns
            email_column_index = self._get_column_index(headers, self.EMAIL_COLUMN_NAMES)
            name_column_index = self._get_column_index(headers, self.NAME_COLUMN_NAMES)
            
            if email_column_index is None:
                raise GoogleSheetsValidationError(
                    f"No email column found. Expected one of: {', '.join(self.EMAIL_COLUMN_NAMES)}"
                )
            
            email_rows = []
            seen_emails = set()
            
            for row_index, row in enumerate(data_rows, start=2):  # Start at row 2 (skip header)
                # Get email address
                email = row[email_column_index].strip() if email_column_index < len(row) else ""
                
                if not email:
                    continue  # Skip empty email cells
                
                # Get name if available
                name = None
                if name_column_index is not None and name_column_index < len(row):
                    name = row[name_column_index].strip() or None
                
                # Validate email
                is_valid = True
                validation_error = None
                
                try:
                    validated_email = validate_email(email)
                    email = validated_email.email  # Normalized email
                except EmailNotValidError as e:
                    is_valid = False
                    validation_error = str(e)
                
                # Check for duplicates
                if email.lower() in seen_emails:
                    is_valid = False
                    validation_error = "Duplicate email address"
                else:
                    seen_emails.add(email.lower())
                
                # Collect additional data
                additional_data = {}
                for col_index, header in enumerate(headers):
                    if col_index < len(row) and col_index not in [email_column_index, name_column_index]:
                        additional_data[header] = row[col_index]
                
                email_row = EmailRow(
                    row_number=row_index,
                    email=email,
                    name=name,
                    additional_data=additional_data if additional_data else None,
                    is_valid=is_valid,
                    validation_error=validation_error
                )
                
                email_rows.append(email_row)
            
            if not email_rows:
                raise GoogleSheetsValidationError("No email addresses found in sheet")
            
            return email_rows
            
        except HttpError as e:
            if e.resp.status == 404:
                raise GoogleSheetsAccessError(f"Sheet not found: {sheet_id}")
            elif e.resp.status == 403:
                raise GoogleSheetsAccessError(f"No permission to access sheet: {sheet_id}")
            else:
                raise GoogleSheetsAccessError(f"Failed to read sheet: {e}")
        except GoogleSheetsError:
            raise  # Re-raise our custom exceptions
        except Exception as e:
            raise GoogleSheetsAccessError(f"Unexpected error reading sheet: {e}")
    
    def mark_emails_as_sent(
        self, 
        sheet_id: str, 
        email_rows: List[EmailRow], 
        status_column: Optional[str] = None
    ) -> bool:
        """
        Mark emails as sent in the Google Sheet.
        
        Args:
            sheet_id: Google Sheets ID
            email_rows: List of EmailRow objects to mark as sent
            status_column: Column name for status (default: 'Email Status')
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            GoogleSheetsAccessError: If sheet cannot be accessed
        """
        if not email_rows:
            return True  # Nothing to update
        
        status_col = status_column or self.STATUS_COLUMN_NAME
        
        try:
            service = self._get_service()
            
            # First, ensure the status column exists
            self._ensure_status_column(service, sheet_id, status_col)
            
            # Get current headers to find status column index
            headers_result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range="1:1"
            ).execute()
            
            headers = headers_result.get('values', [[]])[0]
            status_column_index = None
            
            for i, header in enumerate(headers):
                if header.lower() == status_col.lower():
                    status_column_index = i
                    break
            
            if status_column_index is None:
                raise GoogleSheetsAccessError(f"Status column '{status_col}' not found")
            
            # Prepare batch update
            updates = []
            for email_row in email_rows:
                if email_row.is_valid and email_row.row_number:
                    # Convert column index to letter (A, B, C, etc.)
                    col_letter = self._column_index_to_letter(status_column_index)
                    cell_range = f"{col_letter}{email_row.row_number}"
                    
                    updates.append({
                        'range': cell_range,
                        'values': [[self.SENT_STATUS_VALUE]]
                    })
            
            if updates:
                # Batch update all status cells
                batch_update_request = {
                    'valueInputOption': 'RAW',
                    'data': updates
                }
                
                service.spreadsheets().values().batchUpdate(
                    spreadsheetId=sheet_id,
                    body=batch_update_request
                ).execute()
            
            return True
            
        except HttpError as e:
            if e.resp.status == 404:
                raise GoogleSheetsAccessError(f"Sheet not found: {sheet_id}")
            elif e.resp.status == 403:
                raise GoogleSheetsAccessError(f"No permission to modify sheet: {sheet_id}")
            else:
                raise GoogleSheetsAccessError(f"Failed to update sheet: {e}")
        except Exception as e:
            raise GoogleSheetsAccessError(f"Unexpected error updating sheet: {e}")
    
    def _detect_email_column(self, headers: List[str]) -> Optional[str]:
        """Detect email column from headers."""
        for header in headers:
            if header.lower().strip() in [name.lower() for name in self.EMAIL_COLUMN_NAMES]:
                return header
        return None
    
    def _detect_name_column(self, headers: List[str]) -> Optional[str]:
        """Detect name column from headers."""
        for header in headers:
            if header.lower().strip() in [name.lower() for name in self.NAME_COLUMN_NAMES]:
                return header
        return None
    
    def _get_column_index(self, headers: List[str], column_names: List[str]) -> Optional[int]:
        """Get column index for given column names."""
        for i, header in enumerate(headers):
            if header.lower().strip() in [name.lower() for name in column_names]:
                return i
        return None
    
    def _analyze_email_data(self, values: List[List[str]], email_column: Optional[str]) -> Dict[str, int]:
        """Analyze email data for statistics."""
        if not email_column or not values:
            return {'valid': 0, 'invalid': 0, 'duplicates': 0}
        
        headers = values[0] if values else []
        email_column_index = self._get_column_index(headers, [email_column])
        
        if email_column_index is None:
            return {'valid': 0, 'invalid': 0, 'duplicates': 0}
        
        seen_emails = set()
        valid_count = 0
        invalid_count = 0
        duplicate_count = 0
        
        for row in values[1:]:  # Skip header
            if email_column_index < len(row):
                email = row[email_column_index].strip()
                if email:
                    try:
                        validated_email = validate_email(email)
                        normalized_email = validated_email.email.lower()
                        
                        if normalized_email in seen_emails:
                            duplicate_count += 1
                        else:
                            seen_emails.add(normalized_email)
                            valid_count += 1
                    except EmailNotValidError:
                        invalid_count += 1
        
        return {'valid': valid_count, 'invalid': invalid_count, 'duplicates': duplicate_count}
    
    def _ensure_status_column(self, service, sheet_id: str, status_column: str):
        """Ensure status column exists in the sheet."""
        try:
            # Get current headers
            headers_result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range="1:1"
            ).execute()
            
            headers = headers_result.get('values', [[]])[0]
            
            # Check if status column already exists
            for header in headers:
                if header.lower() == status_column.lower():
                    return  # Column already exists
            
            # Add status column
            headers_len = len(headers) if headers else 0
            next_col_letter = self._column_index_to_letter(headers_len)
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"{next_col_letter}1",
                valueInputOption='RAW',
                body={'values': [[status_column]]}
            ).execute()
            
        except Exception as e:
            # If we can't add the column, it's not critical
            pass
    
    def _column_index_to_letter(self, index: int) -> str:
        """Convert column index to letter (0 -> A, 1 -> B, etc.)."""
        result = ""
        while index >= 0:
            result = chr(index % 26 + ord('A')) + result
            index = index // 26 - 1
        return result
    
    def get_preview_data(self, sheet_id: str, sheet_range: str = "A:Z", max_rows: int = 10) -> Dict:
        """
        Get preview data for a Google Sheet.
        
        Args:
            sheet_id: Google Sheets ID
            sheet_range: Range to preview
            max_rows: Maximum number of rows to return
            
        Returns:
            Dictionary with preview data
        """
        try:
            sheet_info = self.get_sheet_info(sheet_id, sheet_range)
            email_rows = self.read_email_addresses(sheet_id, sheet_range)
            
            # Get sample data (first few rows)
            service = self._get_service()
            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=f"A1:{self._column_index_to_letter(len(sheet_info.headers or [])-1)}{max_rows+1}"
            ).execute()
            
            sample_data = result.get('values', [])
            
            return {
                'sheet_id': sheet_id,
                'sheet_name': sheet_info.sheet_name,
                'total_rows': sheet_info.total_rows,
                'headers': sheet_info.headers,
                'email_column': sheet_info.email_column,
                'name_column': sheet_info.name_column,
                'valid_emails': sheet_info.valid_emails,
                'invalid_emails': sheet_info.invalid_emails,
                'duplicate_emails': sheet_info.duplicate_emails,
                'sample_data': sample_data
            }
            
        except Exception as e:
            raise GoogleSheetsAccessError(f"Failed to get sheet preview: {e}")