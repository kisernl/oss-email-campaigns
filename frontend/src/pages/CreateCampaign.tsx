/**
 * Create Campaign Page
 * Form interface for creating new email campaigns with Google Sheets integration
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import apiClient, { getTemplates, getTemplate } from '../services/api';
import { CampaignCreate, GoogleSheetPreview, EmailTemplateSummary, EmailTemplateResponse } from '../types';

interface FormData {
  name: string;
  description: string;
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

interface FormErrors {
  name?: string;
  subject?: string;
  message?: string;
  google_sheet_id?: string;
  delay_range?: string;
  general?: string;
}

const CreateCampaign: React.FC = () => {
  const navigate = useNavigate();
  
  // Load templates on component mount
  useEffect(() => {
    loadTemplates();
  }, []);
  
  // Form state
  const [formData, setFormData] = useState<FormData>({
    name: '',
    description: '',
    subject: '',
    message: '',
    google_sheet_id: '',
    google_sheet_range: 'A:Z',
    send_immediately: false,
    use_delay: false,
    delay_min_minutes: 4,
    delay_max_minutes: 7,
    
    // Business hours defaults
    respect_business_hours: false,
    business_hours_start: 7,
    business_hours_end: 17,
    business_days_only: true,
    timezone: 'UTC'
  });
  
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Google Sheets preview state
  const [sheetPreview, setSheetPreview] = useState<GoogleSheetPreview | null>(null);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  
  // Template state
  const [templates, setTemplates] = useState<EmailTemplateSummary[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(null);
  const [isLoadingTemplates, setIsLoadingTemplates] = useState(false);

  // Load templates
  const loadTemplates = async () => {
    setIsLoadingTemplates(true);
    try {
      const templatesData = await getTemplates();
      setTemplates(templatesData);
    } catch (error) {
      console.error('Failed to load templates:', error);
    } finally {
      setIsLoadingTemplates(false);
    }
  };

  // Handle template selection
  const handleTemplateSelect = async (templateId: number | null) => {
    setSelectedTemplateId(templateId);
    
    if (templateId === null) {
      // Clear template selection but keep current values
      return;
    }
    
    try {
      const template = await getTemplate(templateId);
      
      // Pre-fill subject and message from template
      setFormData(prev => ({
        ...prev,
        subject: template.subject,
        message: template.message
      }));
      
      // Clear any existing errors for these fields
      setErrors(prev => ({
        ...prev,
        subject: undefined,
        message: undefined
      }));
      
    } catch (error) {
      console.error('Failed to load template:', error);
    }
  };

  // Handle form input changes
  const handleInputChange = (field: keyof FormData, value: string | boolean | number) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear field-specific errors when user types
    if (errors[field as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  // Validate form
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Campaign name is required';
    }
    
    if (!formData.subject.trim()) {
      newErrors.subject = 'Email subject is required';
    }
    
    if (!formData.message.trim()) {
      newErrors.message = 'Email message is required';
    }
    
    if (!formData.google_sheet_id.trim()) {
      newErrors.google_sheet_id = 'Google Sheet ID is required';
    }
    
    // Validate delay configuration
    if (formData.use_delay) {
      if (formData.delay_min_minutes < 1 || formData.delay_min_minutes > 60) {
        newErrors.delay_range = 'Minimum delay must be between 1 and 60 minutes';
      } else if (formData.delay_max_minutes < 1 || formData.delay_max_minutes > 60) {
        newErrors.delay_range = 'Maximum delay must be between 1 and 60 minutes';
      } else if (formData.delay_max_minutes < formData.delay_min_minutes) {
        newErrors.delay_range = 'Maximum delay must be greater than or equal to minimum delay';
      }
    }
    
    // Validate business hours configuration
    if (formData.respect_business_hours) {
      if (formData.business_hours_start < 0 || formData.business_hours_start > 23) {
        newErrors.delay_range = 'Business hours start must be between 0 and 23';
      } else if (formData.business_hours_end < 1 || formData.business_hours_end > 24) {
        newErrors.delay_range = 'Business hours end must be between 1 and 24';
      } else if (formData.business_hours_end <= formData.business_hours_start) {
        newErrors.delay_range = 'Business hours end must be greater than start';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Load Google Sheets preview
  const loadSheetPreview = async () => {
    if (!formData.google_sheet_id.trim()) {
      setPreviewError('Please enter a Google Sheet ID first');
      return;
    }

    setIsLoadingPreview(true);
    setPreviewError(null);
    
    try {
      const preview = await apiClient.previewGoogleSheet(
        formData.google_sheet_id,
        { sheet_range: formData.google_sheet_range }
      );
      setSheetPreview(preview);
      setShowPreview(true);
    } catch (error: any) {
      setPreviewError(error.message || 'Failed to load sheet preview');
      setSheetPreview(null);
    } finally {
      setIsLoadingPreview(false);
    }
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    setErrors({});
    
    try {
      const campaignData: CampaignCreate = {
        name: formData.name.trim(),
        description: formData.description.trim() || null,
        subject: formData.subject.trim(),
        message: formData.message.trim(),
        google_sheet_id: formData.google_sheet_id.trim(),
        google_sheet_range: formData.google_sheet_range.trim(),
        send_immediately: formData.send_immediately,
        use_delay: formData.use_delay,
        delay_min_minutes: formData.delay_min_minutes,
        delay_max_minutes: formData.delay_max_minutes,
        
        // Business hours configuration
        respect_business_hours: formData.respect_business_hours,
        business_hours_start: formData.business_hours_start,
        business_hours_end: formData.business_hours_end,
        business_days_only: formData.business_days_only,
        timezone: formData.timezone
      };
      
      const campaign = await apiClient.createCampaign(campaignData);
      
      // Navigate to campaigns list or campaign detail
      navigate('/campaigns', { 
        state: { 
          message: `Campaign "${campaign.name}" created successfully!`,
          campaignId: campaign.id
        }
      });
      
    } catch (error: any) {
      setErrors({ 
        general: error.message || 'Failed to create campaign. Please try again.' 
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ 
      maxWidth: '80ch', 
      margin: '0 auto', 
      padding: 'calc(var(--line-height) * 2) 2ch' 
    }}>
      {/* Header */}
      <div className="card">
        <h1>Create New Campaign</h1>
        <p>
          Design and configure your email campaign with Google Sheets integration.
          Follow the monospace workflow for data-focused campaign creation.
        </p>
      </div>

      {/* Main Form */}
      <form onSubmit={handleSubmit}>
        <div className="card">
          <h2>Campaign Details</h2>
          
          {/* General Error */}
          {errors.general && (
            <div className="error-message" style={{ marginBottom: 'var(--line-height)' }}>
              {errors.general}
            </div>
          )}
          
          {/* Campaign Name */}
          <div style={{ marginBottom: 'var(--line-height)' }}>
            <label className="label-field">campaign_name *</label>
            <input 
              type="text" 
              className={`input-field ${errors.name ? 'error' : ''}`}
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              placeholder="enter_campaign_name"
              maxLength={100}
            />
            {errors.name && <div className="field-error">{errors.name}</div>}
          </div>
          
          {/* Description */}
          <div style={{ marginBottom: 'var(--line-height)' }}>
            <label className="label-field">description</label>
            <textarea 
              className="input-field"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              placeholder="optional_campaign_description"
              rows={3}
              maxLength={500}
            />
          </div>
        </div>

        {/* Email Content */}
        <div className="card">
          <h2>Email Content</h2>
          
          {/* Template Selection */}
          <div style={{ marginBottom: 'var(--line-height)' }}>
            <label className="label-field">use_template (optional)</label>
            <select 
              className="input-field"
              value={selectedTemplateId || ''}
              onChange={(e) => handleTemplateSelect(e.target.value ? parseInt(e.target.value) : null)}
              disabled={isLoadingTemplates}
            >
              <option value="">Select a template (or create from scratch)</option>
              {templates.map(template => (
                <option key={template.id} value={template.id}>
                  {template.name} ({template.variables_count || 0} variables)
                </option>
              ))}
            </select>
            {isLoadingTemplates && (
              <div style={{ fontSize: '0.875rem', color: 'var(--text-color-alt)', marginTop: '0.25rem' }}>
                Loading templates...
              </div>
            )}
            {templates.length === 0 && !isLoadingTemplates && (
              <div style={{ fontSize: '0.875rem', color: 'var(--text-color-alt)', marginTop: '0.25rem' }}>
                No templates available. <Link to="/templates/create">Create your first template</Link>
              </div>
            )}
          </div>
          
          {/* Subject */}
          <div style={{ marginBottom: 'var(--line-height)' }}>
            <label className="label-field">email_subject *</label>
            <input 
              type="text" 
              className={`input-field ${errors.subject ? 'error' : ''}`}
              value={formData.subject}
              onChange={(e) => handleInputChange('subject', e.target.value)}
              placeholder="Hello {{name}}, welcome to..."
              maxLength={200}
            />
            {errors.subject && <div className="field-error">{errors.subject}</div>}
          </div>
          
          {/* Message */}
          <div style={{ marginBottom: 'var(--line-height)' }}>
            <label className="label-field">email_message *</label>
            <textarea 
              className={`input-field ${errors.message ? 'error' : ''}`}
              value={formData.message}
              onChange={(e) => handleInputChange('message', e.target.value)}
              placeholder="Hi {{name}},&#10;&#10;Your personalized message here...&#10;&#10;Best regards,&#10;Your Team"
              rows={8}
              maxLength={5000}
            />
            {errors.message && <div className="field-error">{errors.message}</div>}
          </div>
        </div>

        {/* Google Sheets Integration */}
        <div className="card">
          <h2>Google Sheets Integration</h2>
          
          {/* Sheet ID */}
          <div style={{ marginBottom: 'var(--line-height)' }}>
            <label className="label-field">google_sheet_id *</label>
            <input 
              type="text" 
              className={`input-field ${errors.google_sheet_id ? 'error' : ''}`}
              value={formData.google_sheet_id}
              onChange={(e) => handleInputChange('google_sheet_id', e.target.value)}
              placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            />
            {errors.google_sheet_id && <div className="field-error">{errors.google_sheet_id}</div>}
          </div>
          
          {/* Sheet Range */}
          <div style={{ marginBottom: 'var(--line-height)' }}>
            <label className="label-field">sheet_range</label>
            <input 
              type="text" 
              className="input-field"
              value={formData.google_sheet_range}
              onChange={(e) => handleInputChange('google_sheet_range', e.target.value)}
              placeholder="A:Z"
            />
          </div>
          
          {/* Preview Button */}
          <div style={{ marginBottom: 'var(--line-height)' }}>
            <button 
              type="button"
              className="btn-secondary"
              onClick={loadSheetPreview}
              disabled={isLoadingPreview || !formData.google_sheet_id.trim()}
            >
              {isLoadingPreview ? 'Loading...' : 'Preview Sheet Data'}
            </button>
          </div>
          
          {/* Preview Error */}
          {previewError && (
            <div className="error-message" style={{ marginBottom: 'var(--line-height)' }}>
              {previewError}
            </div>
          )}
          
          {/* Sheet Preview */}
          {showPreview && sheetPreview && (
            <div style={{ marginTop: 'var(--line-height)' }}>
              <h3>Sheet Preview</h3>
              <div className="code-block">
{`sheet_name: ${sheetPreview.sheet_name || 'Unknown'}
total_rows: ${sheetPreview.total_rows}
valid_emails: ${sheetPreview.valid_emails}
invalid_emails: ${sheetPreview.invalid_emails}
duplicate_emails: ${sheetPreview.duplicate_emails}

headers: [${sheetPreview.headers.join(', ')}]

sample_data:
${sheetPreview.sample_data.slice(0, 5).map(row => row.join(' | ')).join('\n')}`}
              </div>
            </div>
          )}
        </div>

        {/* Send Options */}
        <div className="card flex flex-col">
          <h2>Send Options</h2>
          
          <div style={{ marginBottom: 'var(--line-height)' }} className="items-center text-center">
            <label className="checkbox-field">
              <input 
                type="checkbox"
                checked={formData.send_immediately}
                onChange={(e) => handleInputChange('send_immediately', e.target.checked)}
              />
              <span>send_immediately (campaign will start sending as soon as created)</span>
            </label>
          </div>
          
          {!formData.send_immediately && (
            <p style={{ 
              color: 'var(--text-muted)', 
              fontSize: '0.9rem',
              fontStyle: 'italic',
              marginBottom: 'var(--line-height)'
            }}>
              Campaign will be saved as draft and can be sent later from the campaigns page.
            </p>
          )}
          
          {/* Email Delay Configuration */}
          <div style={{ marginBottom: 'var(--line-height)' }}>
            <label className="checkbox-field">
              <input 
                type="checkbox"
                checked={formData.use_delay}
                onChange={(e) => handleInputChange('use_delay', e.target.checked)}
              />
              <span>use_delay (add random delay between emails)</span>
            </label>
          </div>
          
          {formData.use_delay && (
            <div>
              <div className="code-block" style={{ marginBottom: 'var(--line-height)' }}>
{`delay_configuration:
  purpose: prevent_spam_detection
  type: random_delay_between_emails
  range: ${formData.delay_min_minutes}-${formData.delay_max_minutes} minutes`}
              </div>
              
              <div className="grid-mono" style={{ marginBottom: 'var(--line-height)' }}>
                <div>
                  <label className="label-field">min_delay (minutes)</label>
                  <input 
                    type="number"
                    className="input-field"
                    value={formData.delay_min_minutes}
                    onChange={(e) => handleInputChange('delay_min_minutes', parseInt(e.target.value) || 1)}
                    min="1"
                    max="60"
                  />
                </div>
                <div>
                  <label className="label-field">max_delay (minutes)</label>
                  <input 
                    type="number"
                    className="input-field"
                    value={formData.delay_max_minutes}
                    onChange={(e) => handleInputChange('delay_max_minutes', parseInt(e.target.value) || 1)}
                    min="1"
                    max="60"
                  />
                </div>
              </div>
              
              {errors.delay_range && (
                <div className="field-error" style={{ marginBottom: 'calc(var(--line-height) / 2)' }}>
                  {errors.delay_range}
                </div>
              )}
              
              <p style={{ 
                color: 'var(--text-muted)', 
                fontSize: '0.9rem',
                fontStyle: 'italic' 
              }}>
                A random delay between {formData.delay_min_minutes} and {formData.delay_max_minutes} minutes will be applied between each email to avoid spam detection.
              </p>
            </div>
          )}
        </div>

        {/* Business Hours Configuration */}
        <div className="card">
          <h2>Business Hours Restriction</h2>
          
          {/* Enable business hours restriction */}
          <div style={{ marginBottom: 'var(--line-height)' }}>
            <label className="checkbox-field">
              <input 
                type="checkbox"
                checked={formData.respect_business_hours}
                onChange={(e) => handleInputChange('respect_business_hours', e.target.checked)}
              />
              <span>respect_business_hours (only send emails during business hours)</span>
            </label>
          </div>
          
          {formData.respect_business_hours && (
            <div>
              <div className="code-block" style={{ marginBottom: 'var(--line-height)' }}>
{`business_hours_config:
  schedule: ${formData.business_hours_start}:00 - ${formData.business_hours_end}:00
  days: ${formData.business_days_only ? 'monday_to_friday' : 'all_days'}
  timezone: ${formData.timezone}
  
behavior:
  - emails will only be sent during business hours
  - if outside business hours, sending will be delayed
  - campaign can be cancelled during waiting period`}
              </div>
              
              <div className="grid-mono" style={{ marginBottom: 'var(--line-height)' }}>
                <div>
                  <label className="label-field">start_hour (24h format)</label>
                  <input 
                    type="number"
                    className="input-field"
                    value={formData.business_hours_start}
                    onChange={(e) => handleInputChange('business_hours_start', parseInt(e.target.value) || 0)}
                    min="0"
                    max="23"
                  />
                </div>
                <div>
                  <label className="label-field">end_hour (24h format)</label>
                  <input 
                    type="number"
                    className="input-field"
                    value={formData.business_hours_end}
                    onChange={(e) => handleInputChange('business_hours_end', parseInt(e.target.value) || 1)}
                    min="1"
                    max="24"
                  />
                </div>
              </div>
              
              <div style={{ marginBottom: 'var(--line-height)' }}>
                <label className="checkbox-field">
                  <input 
                    type="checkbox"
                    checked={formData.business_days_only}
                    onChange={(e) => handleInputChange('business_days_only', e.target.checked)}
                  />
                  <span>business_days_only (Monday-Friday only)</span>
                </label>
              </div>
              
              <div style={{ marginBottom: 'var(--line-height)' }}>
                <label className="label-field">timezone</label>
                <select 
                  className="input-field"
                  value={formData.timezone}
                  onChange={(e) => handleInputChange('timezone', e.target.value)}
                >
                  <option value="UTC">UTC</option>
                  <option value="US/Eastern">US/Eastern</option>
                  <option value="US/Central">US/Central</option>
                  <option value="US/Mountain">US/Mountain</option>
                  <option value="US/Pacific">US/Pacific</option>
                  <option value="Europe/London">Europe/London</option>
                  <option value="Europe/Paris">Europe/Paris</option>
                  <option value="Asia/Tokyo">Asia/Tokyo</option>
                  <option value="Australia/Sydney">Australia/Sydney</option>
                </select>
              </div>
              
              <p style={{ 
                color: 'var(--text-muted)', 
                fontSize: '0.9rem',
                fontStyle: 'italic' 
              }}>
                Emails will only be sent between {formData.business_hours_start}:00 and {formData.business_hours_end}:00 
                {formData.business_days_only ? ' on Monday-Friday' : ' every day'} in {formData.timezone} timezone.
                If started outside business hours, the campaign will wait until the next business period.
              </p>
            </div>
          )}
        </div>

        {/* Form Actions */}
        <div className="card">
          <div className="grid-mono">
            <button 
              type="submit" 
              className="btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Creating...' : 'Create Campaign'}
            </button>
            <Link to="/campaigns" className="btn-secondary">
              ← Back to Campaigns
            </Link>
          </div>
        </div>
      </form>

      {/* Template Variables Help */}
      <div className="card">
        <h3>Template Variables</h3>
        <div className="code-block">
{`Available template variables:
{{name}}    - Recipient name from sheet
{{email}}   - Recipient email address
{{custom}}  - Any custom column from sheet

Example usage:
Subject: "Hello {{name}}, special offer!"
Message: "Hi {{name}}, check this out..."`}
        </div>
      </div>
    </div>
  );
};

export default CreateCampaign;