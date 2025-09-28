/**
 * API Service Layer for Email Campaign App
 * Provides type-safe communication with FastAPI backend
 */

import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import {
  CampaignResponse,
  CampaignSummary,
  CampaignCreate,
  CampaignUpdate,
  CampaignSendRequest,
  EmailSendResponse,
  GoogleSheetPreview,
  HealthCheck,
  ErrorResponse,
  SuccessResponse,
  CampaignListParams,
  EmailSendListParams,
  ApiError,
  ApiConfig,
  ApiResponse,
  CampaignStats,
  GoogleSheetPreviewRequest,
  EmailTemplateCreate,
  EmailTemplateUpdate,
  EmailTemplateResponse,
  EmailTemplateSummary,
  TemplateListParams
} from '../types';

// ============================================================================
// API CONFIGURATION
// ============================================================================

const DEFAULT_CONFIG: ApiConfig = {
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  }
};

// ============================================================================
// AXIOS INSTANCE SETUP
// ============================================================================

class ApiClient {
  private client: AxiosInstance;

  constructor(config: Partial<ApiConfig> = {}) {
    const finalConfig = { ...DEFAULT_CONFIG, ...config };
    
    this.client = axios.create({
      baseURL: finalConfig.baseURL,
      timeout: finalConfig.timeout,
      headers: finalConfig.headers,
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add timestamp for debugging
        (config as any).metadata = { startTime: new Date() };
        
        // Log requests in development
        if (process.env.NODE_ENV === 'development') {
          console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, {
            params: config.params,
            data: config.data
          });
        }
        
        return config;
      },
      (error) => {
        console.error('[API] Request error:', error);
        return Promise.reject(this.createApiError(error));
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        // Log response time in development
        if (process.env.NODE_ENV === 'development') {
          const startTime = (response.config as any).metadata?.startTime;
          const duration = startTime ? new Date().getTime() - startTime.getTime() : 0;
          console.log(`[API] ${response.status} ${response.config.url} (${duration}ms)`);
        }
        
        return response;
      },
      (error: AxiosError) => {
        // Enhanced error logging
        if (process.env.NODE_ENV === 'development') {
          console.error('[API] Response error:', {
            status: error.response?.status,
            statusText: error.response?.statusText,
            url: error.config?.url,
            data: error.response?.data
          });
        }
        
        return Promise.reject(this.createApiError(error));
      }
    );
  }

  private createApiError(error: AxiosError): ApiError {
    const apiError = new Error(error.message) as ApiError;
    apiError.name = 'ApiError';
    apiError.status = error.response?.status;
    apiError.response = error.response ? {
      data: error.response.data as ErrorResponse,
      status: error.response.status,
      statusText: error.response.statusText
    } : undefined;
    
    return apiError;
  }

  // ============================================================================
  // HEALTH CHECK METHODS
  // ============================================================================

  async healthCheck(): Promise<HealthCheck> {
    const response = await this.client.get<HealthCheck>('/api/health');
    return response.data;
  }

  async databaseHealth(): Promise<Record<string, any>> {
    const response = await this.client.get('/api/health/database');
    return response.data;
  }

  async emailHealth(): Promise<Record<string, any>> {
    const response = await this.client.get('/api/health/email');
    return response.data;
  }

  // ============================================================================
  // CAMPAIGN METHODS
  // ============================================================================

  async createCampaign(campaign: CampaignCreate): Promise<CampaignResponse> {
    const response = await this.client.post<CampaignResponse>('/api/campaigns/', campaign);
    return response.data;
  }

  async getCampaigns(params: CampaignListParams = {}): Promise<CampaignSummary[]> {
    const response = await this.client.get<CampaignSummary[]>('/api/campaigns/', { params });
    return response.data;
  }

  async getCampaign(id: number): Promise<CampaignResponse> {
    const response = await this.client.get<CampaignResponse>(`/api/campaigns/${id}`);
    return response.data;
  }

  async updateCampaign(id: number, updates: CampaignUpdate): Promise<CampaignResponse> {
    const response = await this.client.put<CampaignResponse>(`/api/campaigns/${id}`, updates);
    return response.data;
  }

  async deleteCampaign(id: number): Promise<SuccessResponse> {
    const response = await this.client.delete<SuccessResponse>(`/api/campaigns/${id}`);
    return response.data;
  }

  async sendCampaign(id: number, request: CampaignSendRequest = {}): Promise<SuccessResponse> {
    const response = await this.client.post<SuccessResponse>(`/api/campaigns/${id}/send`, request);
    return response.data;
  }

  async stopCampaign(id: number): Promise<SuccessResponse> {
    const response = await this.client.post<SuccessResponse>(`/api/campaigns/${id}/stop`);
    return response.data;
  }

  async getCampaignEmails(id: number, params: EmailSendListParams = {}): Promise<EmailSendResponse[]> {
    const response = await this.client.get<EmailSendResponse[]>(`/api/campaigns/${id}/emails`, { params });
    return response.data;
  }

  // ============================================================================
  // GOOGLE SHEETS METHODS
  // ============================================================================

  async previewGoogleSheet(
    sheetId: string, 
    options: Omit<GoogleSheetPreviewRequest, 'sheet_id'> = {}
  ): Promise<GoogleSheetPreview> {
    const params = {
      sheet_range: options.sheet_range || 'A:Z',
      max_rows: options.max_rows || 10
    };
    
    const response = await this.client.get<GoogleSheetPreview>(
      `/api/sheets/${sheetId}/preview`, 
      { params }
    );
    return response.data;
  }

  async validateGoogleSheet(sheetId: string): Promise<SuccessResponse> {
    const response = await this.client.post<SuccessResponse>(`/api/sheets/${sheetId}/validate`);
    return response.data;
  }

  // ============================================================================
  // TEMPLATE METHODS
  // ============================================================================

  async createTemplate(template: EmailTemplateCreate): Promise<EmailTemplateResponse> {
    const response = await this.client.post<EmailTemplateResponse>('/api/templates/', template);
    return response.data;
  }

  async getTemplates(params: TemplateListParams = {}): Promise<EmailTemplateSummary[]> {
    const response = await this.client.get<EmailTemplateSummary[]>('/api/templates/', { params });
    return response.data;
  }

  async getTemplate(id: number): Promise<EmailTemplateResponse> {
    const response = await this.client.get<EmailTemplateResponse>(`/api/templates/${id}`);
    return response.data;
  }

  async updateTemplate(id: number, updates: EmailTemplateUpdate): Promise<EmailTemplateResponse> {
    const response = await this.client.put<EmailTemplateResponse>(`/api/templates/${id}`, updates);
    return response.data;
  }

  async deleteTemplate(id: number): Promise<SuccessResponse> {
    const response = await this.client.delete<SuccessResponse>(`/api/templates/${id}`);
    return response.data;
  }

  // ============================================================================
  // UTILITY METHODS
  // ============================================================================

  async getRootInfo(): Promise<Record<string, any>> {
    const response = await this.client.get('/');
    return response.data;
  }

  // Get the underlying axios instance for advanced usage
  getClient(): AxiosInstance {
    return this.client;
  }

  // Update base configuration
  updateConfig(config: Partial<ApiConfig>): void {
    if (config.baseURL) {
      this.client.defaults.baseURL = config.baseURL;
    }
    if (config.timeout) {
      this.client.defaults.timeout = config.timeout;
    }
    if (config.headers) {
      this.client.defaults.headers = { ...this.client.defaults.headers, ...config.headers };
    }
  }
}

// ============================================================================
// SINGLETON INSTANCE
// ============================================================================

const apiClient = new ApiClient();

// ============================================================================
// CONVENIENCE FUNCTIONS
// ============================================================================

// Health & Status
export const healthCheck = () => apiClient.healthCheck();
export const databaseHealth = () => apiClient.databaseHealth();
export const emailHealth = () => apiClient.emailHealth();

// Campaigns
export const createCampaign = (campaign: CampaignCreate) => apiClient.createCampaign(campaign);
export const getCampaigns = (params?: CampaignListParams) => apiClient.getCampaigns(params);
export const getCampaign = (id: number) => apiClient.getCampaign(id);
export const updateCampaign = (id: number, updates: CampaignUpdate) => apiClient.updateCampaign(id, updates);
export const deleteCampaign = (id: number) => apiClient.deleteCampaign(id);
export const sendCampaign = (id: number, request?: CampaignSendRequest) => apiClient.sendCampaign(id, request);
export const stopCampaign = (id: number) => apiClient.stopCampaign(id);
export const getCampaignEmails = (id: number, params?: EmailSendListParams) => apiClient.getCampaignEmails(id, params);

// Google Sheets
export const previewGoogleSheet = (sheetId: string, options?: Omit<GoogleSheetPreviewRequest, 'sheet_id'>) => 
  apiClient.previewGoogleSheet(sheetId, options);
export const validateGoogleSheet = (sheetId: string) => apiClient.validateGoogleSheet(sheetId);

// Templates
export const createTemplate = (template: EmailTemplateCreate) => apiClient.createTemplate(template);
export const getTemplates = (params?: TemplateListParams) => apiClient.getTemplates(params);
export const getTemplate = (id: number) => apiClient.getTemplate(id);
export const updateTemplate = (id: number, updates: EmailTemplateUpdate) => apiClient.updateTemplate(id, updates);
export const deleteTemplate = (id: number) => apiClient.deleteTemplate(id);

// Utility
export const getRootInfo = () => apiClient.getRootInfo();

// ============================================================================
// ERROR HANDLING UTILITIES
// ============================================================================

export const isApiError = (error: any): error is ApiError => {
  return error && error.name === 'ApiError';
};

export const getErrorMessage = (error: unknown): string => {
  if (isApiError(error)) {
    // Try to get detailed error message from response
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.response?.data?.error) {
      return error.response.data.error;
    }
    return error.message;
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unknown error occurred';
};

export const getErrorStatus = (error: unknown): number | undefined => {
  if (isApiError(error)) {
    return error.status;
  }
  return undefined;
};

// ============================================================================
// EXPORTS
// ============================================================================

export default apiClient;
export { ApiClient };
export type { ApiError, ApiResponse, ApiConfig };