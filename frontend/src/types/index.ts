/**
 * TypeScript types for Email Campaign API
 * Matches backend Pydantic schemas for type safety
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum CampaignStatus {
  DRAFT = 'draft',
  SCHEDULED = 'scheduled',
  SENDING = 'sending',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export enum EmailStatus {
  PENDING = 'pending',
  SENT = 'sent',
  FAILED = 'failed',
  BOUNCED = 'bounced',
  SKIPPED = 'skipped'
}

// ============================================================================
// CAMPAIGN TYPES
// ============================================================================

export interface CampaignBase {
  name: string;
  description?: string | null;
  subject: string;
  message: string;
  google_sheet_id: string;
  google_sheet_range: string;
  send_immediately: boolean;
  use_delay: boolean;
  delay_min_minutes: number;
  delay_max_minutes: number;
  
  // Business hours configuration
  respect_business_hours: boolean;
  business_hours_start: number;
  business_hours_end: number;
  business_days_only: boolean;
  timezone: string;
}

export interface CampaignCreate extends CampaignBase {}

export interface CampaignUpdate {
  name?: string;
  description?: string | null;
  subject?: string;
  message?: string;
  google_sheet_id?: string;
  google_sheet_range?: string;
  send_immediately?: boolean;
  use_delay?: boolean;
  delay_min_minutes?: number;
  delay_max_minutes?: number;
  
  // Business hours configuration
  respect_business_hours?: boolean;
  business_hours_start?: number;
  business_hours_end?: number;
  business_days_only?: boolean;
  timezone?: string;
  
  status?: CampaignStatus;
}

export interface CampaignResponse extends CampaignBase {
  id: number;
  status: CampaignStatus;
  total_recipients: number;
  emails_sent: number;
  emails_failed: number;
  emails_pending: number;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
  scheduled_at?: string | null; // ISO datetime string
  started_at?: string | null; // ISO datetime string
  completed_at?: string | null; // ISO datetime string
  error_message?: string | null;
  error_count: number;
  // Computed fields
  success_rate?: number | null;
  failure_rate?: number | null;
  is_active?: boolean | null;
  is_completed?: boolean | null;
}

export interface CampaignSummary {
  id: number;
  name: string;
  status: CampaignStatus;
  total_recipients: number;
  emails_sent: number;
  emails_failed: number;
  success_rate: number;
  created_at: string; // ISO datetime string
  completed_at?: string | null; // ISO datetime string
}

export interface CampaignSendRequest {
  send_immediately?: boolean;
  test_mode?: boolean;
}

// ============================================================================
// EMAIL SEND TYPES
// ============================================================================

export interface EmailSendBase {
  recipient_email: string;
  recipient_name?: string | null;
  personalized_subject: string;
  personalized_message: string;
}

export interface EmailSendCreate extends EmailSendBase {
  campaign_id: number;
  sheet_row_number?: number | null;
}

export interface EmailSendUpdate {
  status?: EmailStatus;
  error_message?: string | null;
  smtp_response?: string | null;
  marked_as_sent_in_sheet?: boolean;
}

export interface EmailSendResponse extends EmailSendBase {
  id: number;
  campaign_id: number;
  status: EmailStatus;
  send_attempts: number;
  max_send_attempts: number;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
  sent_at?: string | null; // ISO datetime string
  error_message?: string | null;
  smtp_response?: string | null;
  sheet_row_number?: number | null;
  marked_as_sent_in_sheet: boolean;
}

// ============================================================================
// GOOGLE SHEETS TYPES
// ============================================================================

export interface GoogleSheetPreview {
  sheet_id: string;
  sheet_name?: string | null;
  total_rows: number;
  email_column?: string | null;
  name_column?: string | null;
  headers: string[];
  sample_data: string[][];
  valid_emails: number;
  invalid_emails: number;
  duplicate_emails: number;
}

export interface GoogleSheetEmailRow {
  row_number: number;
  email: string;
  name?: string | null;
  additional_data?: Record<string, any> | null;
}

export interface GoogleSheetPreviewRequest {
  sheet_id: string;
  sheet_range?: string;
  max_rows?: number;
}

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

export interface HealthCheck {
  status: string;
  timestamp: string; // ISO datetime string
  version: string;
  database: Record<string, any>;
  environment: string;
}

export interface ErrorResponse {
  error: string;
  detail?: string | null;
  timestamp: string; // ISO datetime string
}

export interface SuccessResponse {
  message: string;
  data?: Record<string, any> | null;
  timestamp: string; // ISO datetime string
}

// ============================================================================
// PAGINATION TYPES
// ============================================================================

export interface PaginationParams {
  page?: number;
  size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// ============================================================================
// FILTER TYPES
// ============================================================================

export interface CampaignFilter {
  status?: CampaignStatus;
  google_sheet_id?: string;
  created_after?: string; // ISO datetime string
  created_before?: string; // ISO datetime string
  name_contains?: string;
}

export interface CampaignListParams extends PaginationParams {
  skip?: number;
  limit?: number;
  status_filter?: string;
}

export interface EmailSendListParams extends PaginationParams {
  skip?: number;
  limit?: number;
  status_filter?: string;
}

// ============================================================================
// STATISTICS TYPES
// ============================================================================

export interface CampaignStats {
  total_campaigns: number;
  active_campaigns: number;
  completed_campaigns: number;
  failed_campaigns: number;
  total_emails_sent: number;
  total_recipients: number;
  overall_success_rate: number;
  recent_campaigns: CampaignSummary[];
}

// ============================================================================
// API CLIENT TYPES
// ============================================================================

export interface ApiConfig {
  baseURL: string;
  timeout?: number;
  headers?: Record<string, string>;
}

export interface ApiError extends Error {
  status?: number;
  response?: {
    data?: ErrorResponse;
    status: number;
    statusText: string;
  };
}

// ============================================================================
// REQUEST/RESPONSE HELPERS
// ============================================================================

export type ApiResponse<T> = {
  data: T;
  status: number;
  statusText: string;
};

export type ApiMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

export interface RequestConfig {
  params?: Record<string, any>;
  headers?: Record<string, string>;
  timeout?: number;
}

// ============================================================================
// VALIDATION HELPERS
// ============================================================================

export interface ValidationError {
  field: string;
  message: string;
  value?: any;
}

export interface FormErrors {
  [key: string]: string | string[];
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export type Partial<T> = {
  [P in keyof T]?: T[P];
};

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

// Campaign creation with required fields made explicit
export type CampaignCreateRequest = RequiredFields<CampaignCreate, 'name' | 'subject' | 'message' | 'google_sheet_id'>;

// Campaign update with all fields optional
export type CampaignUpdateRequest = Partial<CampaignBase> & {
  status?: CampaignStatus;
};

// ============================================================================
// EMAIL TEMPLATE TYPES
// ============================================================================

export interface EmailTemplateBase {
  name: string;
  description?: string;
  subject: string;
  message: string;
  variables?: string;
}

export interface EmailTemplateCreate extends EmailTemplateBase {}

export interface EmailTemplateUpdate {
  name?: string;
  description?: string;
  subject?: string;
  message?: string;
  variables?: string;
}

export interface EmailTemplateResponse extends EmailTemplateBase {
  id: number;
  created_at: string;
  updated_at: string;
  variables_list?: string[];
}

export interface EmailTemplateSummary {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  variables_count?: number;
}

export interface TemplateListParams {
  skip?: number;
  limit?: number;
}