/**
 * Templates Page
 * Manage email templates with CRUD operations
 */

import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { getTemplates, deleteTemplate, getErrorMessage } from '../services/api';
import { EmailTemplateSummary } from '../types';

interface LocationState {
  message?: string;
  templateId?: number;
}

const Templates: React.FC = () => {
  const location = useLocation();
  const locationState = location.state as LocationState;
  
  // State management
  const [templates, setTemplates] = useState<EmailTemplateSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [deletingIds, setDeletingIds] = useState<Set<number>>(new Set());

  // Load templates on component mount
  useEffect(() => {
    loadTemplates();
    
    // Show success message if navigated from template creation/edit
    if (locationState?.message) {
      setSuccessMessage(locationState.message);
      // Clear message after 5 seconds
      setTimeout(() => setSuccessMessage(null), 5000);
    }
  }, [locationState]);

  const loadTemplates = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const templatesData = await getTemplates();
      setTemplates(templatesData);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteTemplate = async (id: number, name: string) => {
    if (!window.confirm(`Are you sure you want to delete the template "${name}"?`)) {
      return;
    }

    setDeletingIds(prev => new Set(prev.add(id)));
    
    try {
      await deleteTemplate(id);
      setSuccessMessage(`Template "${name}" deleted successfully`);
      setTimeout(() => setSuccessMessage(null), 5000);
      await loadTemplates(); // Reload the list
    } catch (err) {
      setError(getErrorMessage(err));
      setTimeout(() => setError(null), 5000);
    } finally {
      setDeletingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(id);
        return newSet;
      });
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

  const formatVariablesCount = (count?: number) => {
    if (count === undefined || count === null) return '0 variables';
    if (count === 0) return 'No variables';
    if (count === 1) return '1 variable';
    return `${count} variables`;
  };

  return (
    <div style={{ 
      maxWidth: '120ch', 
      margin: '0 auto', 
      padding: 'calc(var(--line-height) * 2) 2ch' 
    }}>
      {/* Header */}
      <div className="card">
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: 'var(--line-height)'
        }}>
          <div>
            <h1 style={{ margin: 0 }}>Templates</h1>
            <p style={{ margin: 'calc(var(--line-height) / 2) 0 0 0', color: 'var(--text-muted)' }}>
              manage reusable email templates ({templates.length} total)
            </p>
          </div>
          <Link to="/templates/create" className="btn-primary">+ new_template</Link>
        </div>
      </div>

      {/* Success Message */}
      {successMessage && (
        <div className="card" style={{ backgroundColor: 'rgba(0, 128, 0, 0.1)', borderColor: '#008000' }}>
          <p style={{ margin: 0, color: '#008000', fontWeight: 'var(--font-weight-medium)' }}>
            {successMessage}
          </p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="card">
          <p style={{ margin: 0, textAlign: 'center', color: 'var(--text-muted)' }}>
            loading templates...
          </p>
        </div>
      )}

      {/* Templates List */}
      {!isLoading && (
        <>
          {templates.length === 0 ? (
            <div className="card" style={{ textAlign: 'center' }}>
              <h2>no templates found</h2>
              <p style={{ color: 'var(--text-muted)' }}>
                create your first email template to get started with reusable content.
              </p>
              <Link to="/templates/create" className="btn-primary">+ create_first_template</Link>
            </div>
          ) : (
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(40ch, 1fr))', 
              gap: 'var(--line-height)' 
            }}>
              {templates.map((template) => (
                <div key={template.id} className="card mt-0" style={{ position: 'relative' }}>
                  {/* Template Header */}
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'flex-start',
                    marginBottom: 'var(--line-height)',
                    gap: '2ch'
                  }}>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <h3 style={{ 
                        margin: 0, 
                        fontSize: '1rem', 
                        fontWeight: 'var(--font-weight-bold)',
                        textTransform: 'none',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }}>
                        {template.name}
                      </h3>
                      {template.description && (
                        <p style={{ 
                          margin: 'calc(var(--line-height) / 4) 0 0 0', 
                          color: 'var(--text-muted)',
                          fontSize: '0.875rem'
                        }}>
                          {template.description}
                        </p>
                      )}
                    </div>
                    
                    {/* Actions */}
                    <div style={{ display: 'flex', gap: '0.5ch', flexShrink: 0 }}>
                      <Link 
                        to={`/templates/${template.id}`}
                        className="btn-secondary"
                        style={{ 
                          fontSize: '0.75rem', 
                          padding: 'calc(var(--line-height) / 4) 0.75ch',
                          textDecoration: 'none'
                        }}
                      >
                        view
                      </Link>
                      <Link 
                        to={`/templates/${template.id}/edit`}
                        className="btn-secondary mt-0"
                        style={{ 
                          fontSize: '0.75rem', 
                          padding: 'calc(var(--line-height) / 4) 0.75ch',
                          textDecoration: 'none'
                        }}
                      >
                        edit
                      </Link>
                      <button
                        onClick={() => handleDeleteTemplate(template.id, template.name)}
                        disabled={deletingIds.has(template.id)}
                        className="btn-secondary"
                        style={{ 
                          fontSize: '0.75rem', 
                          padding: 'calc(var(--line-height) / 4) 0.75ch',
                          color: '#ff0000',
                          borderColor: '#ff0000'
                        }}
                      >
                        {deletingIds.has(template.id) ? '...' : 'del'}
                      </button>
                    </div>
                  </div>

                  {/* Template Metadata */}
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    fontSize: '0.875rem',
                    color: 'var(--text-muted)'
                  }}>
                    <span>
                      {formatVariablesCount(template.variables_count)}
                    </span>
                    <span>
                      {formatDate(template.created_at)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Templates;