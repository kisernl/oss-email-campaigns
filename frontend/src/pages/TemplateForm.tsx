/**
 * Template Form Page
 * Form interface for creating and editing email templates
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { createTemplate, updateTemplate, getTemplate, getErrorMessage } from '../services/api';
import { EmailTemplateCreate, EmailTemplateUpdate, EmailTemplateResponse } from '../types';

interface FormData {
  name: string;
  description: string;
  subject: string;
  message: string;
  variables: string;
}

interface FormErrors {
  name?: string;
  subject?: string;
  message?: string;
  general?: string;
}

const TemplateForm: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEditing = !!id;
  
  // Form state
  const [formData, setFormData] = useState<FormData>({
    name: '',
    description: '',
    subject: '',
    message: '',
    variables: ''
  });
  
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Load template data for editing
  useEffect(() => {
    if (isEditing && id) {
      loadTemplate(parseInt(id));
    }
  }, [isEditing, id]);

  const loadTemplate = async (templateId: number) => {
    setIsLoading(true);
    try {
      const template = await getTemplate(templateId);
      setFormData({
        name: template.name,
        description: template.description || '',
        subject: template.subject,
        message: template.message,
        variables: template.variables || ''
      });
    } catch (error) {
      setErrors({ 
        general: `Failed to load template: ${getErrorMessage(error)}` 
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle form input changes
  const handleInputChange = (field: keyof FormData, value: string) => {
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
      newErrors.name = 'Template name is required';
    }
    
    if (!formData.subject.trim()) {
      newErrors.subject = 'Email subject is required';
    }
    
    if (!formData.message.trim()) {
      newErrors.message = 'Email message is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Extract variables from subject and message
  const extractVariables = (text: string): string[] => {
    const matches = text.match(/\{\{([^}]+)\}\}/g);
    if (!matches) return [];
    
    const variables = matches.map(match => match.slice(2, -2).trim());
    return Array.from(new Set(variables)); // Remove duplicates
  };

  const getDetectedVariables = (): string[] => {
    const subjectVars = extractVariables(formData.subject);
    const messageVars = extractVariables(formData.message);
    const allVars = subjectVars.concat(messageVars);
    return Array.from(new Set(allVars));
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
      const templateData: EmailTemplateCreate | EmailTemplateUpdate = {
        name: formData.name.trim(),
        description: formData.description.trim() || undefined,
        subject: formData.subject.trim(),
        message: formData.message.trim(),
        variables: formData.variables.trim() || undefined
      };
      
      if (isEditing && id) {
        await updateTemplate(parseInt(id), templateData as EmailTemplateUpdate);
        navigate('/templates', { 
          state: { 
            message: `Template "${templateData.name}" updated successfully!`
          }
        });
      } else {
        await createTemplate(templateData as EmailTemplateCreate);
        navigate('/templates', { 
          state: { 
            message: `Template "${templateData.name}" created successfully!`
          }
        });
      }
      
    } catch (error) {
      setErrors({ 
        general: getErrorMessage(error)
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const detectedVariables = getDetectedVariables();

  if (isLoading) {
    return (
      <div style={{ 
        maxWidth: '80ch', 
        margin: '0 auto', 
        padding: 'calc(var(--line-height) * 2) 2ch' 
      }}>
        <div className="card">
          <p style={{ margin: 0, textAlign: 'center', color: 'var(--text-muted)' }}>
            loading template...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      maxWidth: '80ch', 
      margin: '0 auto', 
      padding: 'calc(var(--line-height) * 2) 2ch' 
    }}>
      {/* Header */}
      <div className="card">
        <h1>{isEditing ? 'Edit Template' : 'Create New Template'}</h1>
        <p>
          {isEditing 
            ? 'modify your reusable email template with template variables'
            : 'design a reusable email template with template variables like {{name}} and {{company}}'
          }
        </p>
      </div>

      {/* Main Form */}
      <form onSubmit={handleSubmit}>
        <div className="card">
          <h2>Template Details</h2>
          
          {/* General Error */}
          {errors.general && (
            <div className="error-message" style={{ marginBottom: 'var(--line-height)' }}>
              {errors.general}
            </div>
          )}
          
          {/* Template Name */}
          <div style={{ marginBottom: 'var(--line-height)' }}>
            <label className="label-field">template_name *</label>
            <input 
              type="text" 
              className={`input-field ${errors.name ? 'error' : ''}`}
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              placeholder="welcome_email_template"
              maxLength={255}
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
              placeholder="optional description of this template"
              rows={3}
              maxLength={500}
            />
          </div>
        </div>

        {/* Email Content */}
        <div className="card">
          <h2>Email Content</h2>
          
          {/* Subject */}
          <div style={{ marginBottom: 'var(--line-height)' }}>
            <label className="label-field">email_subject *</label>
            <input 
              type="text" 
              className={`input-field ${errors.subject ? 'error' : ''}`}
              value={formData.subject}
              onChange={(e) => handleInputChange('subject', e.target.value)}
              placeholder="Welcome to {{company}}, {{name}}!"
              maxLength={500}
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
              placeholder="Hi {{name}},&#10;&#10;Welcome to {{company}}! We're excited to have you on board.&#10;&#10;Best regards,&#10;The {{company}} Team"
              rows={12}
              maxLength={5000}
            />
            {errors.message && <div className="field-error">{errors.message}</div>}
          </div>

          {/* Variables Section */}
          <div style={{ marginBottom: 'var(--line-height)' }}>
            <label className="label-field">template_variables</label>
            <input 
              type="text" 
              className="input-field"
              value={formData.variables}
              onChange={(e) => handleInputChange('variables', e.target.value)}
              placeholder="name,company,email"
            />
            <div style={{ 
              fontSize: '0.875rem', 
              color: 'var(--text-muted)', 
              marginTop: 'calc(var(--line-height) / 4)' 
            }}>
              comma-separated list of variables (optional - will be auto-detected)
            </div>
          </div>

          {/* Detected Variables */}
          {detectedVariables.length > 0 && (
            <div style={{ marginBottom: 'var(--line-height)' }}>
              <label className="label-field">detected_variables</label>
              <div className="code-block" style={{ padding: 'calc(var(--line-height) / 2) 1ch' }}>
                {detectedVariables.join(', ')}
              </div>
              <div style={{ 
                fontSize: '0.875rem', 
                color: 'var(--text-muted)', 
                marginTop: 'calc(var(--line-height) / 4)' 
              }}>
                automatically detected from your subject and message
              </div>
            </div>
          )}
        </div>

        {/* Form Actions */}
        <div className="card">
          <div style={{ 
            display: 'flex', 
            gap: '2ch', 
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <Link to="/templates" className="btn-secondary">
              ← back_to_templates
            </Link>
            
            <div style={{ display: 'flex', gap: '1ch' }}>
              <button 
                type="submit" 
                className="btn-primary"
                disabled={isSubmitting}
              >
                {isSubmitting 
                  ? (isEditing ? 'updating...' : 'creating...') 
                  : (isEditing ? 'update_template' : 'create_template')
                }
              </button>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};

export default TemplateForm;