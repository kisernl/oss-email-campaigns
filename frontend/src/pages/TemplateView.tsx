/**
 * Template View Page
 * Read-only view of a single email template
 */

import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { getTemplate, deleteTemplate, getErrorMessage } from '../services/api';
import { EmailTemplateResponse } from '../types';

const TemplateView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [template, setTemplate] = useState<EmailTemplateResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (id) {
      loadTemplate(parseInt(id));
    }
  }, [id]);

  const loadTemplate = async (templateId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const templateData = await getTemplate(templateId);
      setTemplate(templateData);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!template) return;
    
    if (!window.confirm(`Are you sure you want to delete the template "${template.name}"?`)) {
      return;
    }

    setIsDeleting(true);
    
    try {
      await deleteTemplate(template.id);
      navigate('/templates', { 
        state: { 
          message: `Template "${template.name}" deleted successfully` 
        }
      });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsDeleting(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

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

  if (error || !template) {
    return (
      <div style={{ 
        maxWidth: '80ch', 
        margin: '0 auto', 
        padding: 'calc(var(--line-height) * 2) 2ch' 
      }}>
        <div className="error-message">
          {error || 'Template not found'}
        </div>
        <div className="card">
          <Link to="/templates" className="btn-secondary">← back_to_templates</Link>
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
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'flex-start',
          marginBottom: 'var(--line-height)',
          gap: '2ch'
        }}>
          <div style={{ flex: 1 }}>
            <h1 style={{ margin: 0 }}>{template.name}</h1>
            {template.description && (
              <p style={{ margin: 'calc(var(--line-height) / 2) 0 0 0', color: 'var(--text-muted)' }}>
                {template.description}
              </p>
            )}
          </div>
          
          <div style={{ display: 'flex', gap: '1ch', flexShrink: 0 }}>
            <Link 
              to={`/templates/${template.id}/edit`}
              className="btn-secondary"
            >
              edit_template
            </Link>
            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className="btn-secondary"
              style={{ 
                color: '#ff0000',
                borderColor: '#ff0000'
              }}
            >
              {isDeleting ? 'deleting...' : 'delete'}
            </button>
          </div>
        </div>
      </div>

      {/* Template Metadata */}
      <div className="card">
        <h2>Template Information</h2>
        
        <div style={{ marginBottom: 'var(--line-height)' }}>
          <label className="label-field">created</label>
          <div className="code-block">
            {formatDate(template.created_at)}
          </div>
        </div>

        <div style={{ marginBottom: 'var(--line-height)' }}>
          <label className="label-field">last_updated</label>
          <div className="code-block">
            {formatDate(template.updated_at)}
          </div>
        </div>

        {template.variables_list && template.variables_list.length > 0 && (
          <div style={{ marginBottom: 'var(--line-height)' }}>
            <label className="label-field">variables ({template.variables_list.length})</label>
            <div className="code-block">
              {template.variables_list.join(', ')}
            </div>
          </div>
        )}
      </div>

      {/* Email Content */}
      <div className="card">
        <h2>Email Content</h2>
        
        <div style={{ marginBottom: 'var(--line-height)' }}>
          <label className="label-field">subject</label>
          <div className="code-block">
            {template.subject}
          </div>
        </div>
        
        <div style={{ marginBottom: 'var(--line-height)' }}>
          <label className="label-field">message</label>
          <div className="code-block" style={{ whiteSpace: 'pre-wrap' }}>
            {template.message}
          </div>
        </div>
      </div>

      {/* Actions */}
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
            <Link to="/create" className="btn-primary">
              use_in_campaign
            </Link>
            <Link 
              to={`/templates/${template.id}/edit`}
              className="btn-primary"
            >
              edit_template
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TemplateView;