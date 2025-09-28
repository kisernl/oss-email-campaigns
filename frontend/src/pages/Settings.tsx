/**
 * Settings Page
 * Configuration and preferences
 */

import React from 'react';
import { Link } from 'react-router-dom';

const Settings: React.FC = () => {
  return (
    <div style={{ 
      maxWidth: '80ch', 
      margin: '0 auto', 
      padding: 'calc(var(--line-height) * 2) 2ch' 
    }}>
      <div className="card">
        <h1>Settings</h1>
        <p>
          Configure application preferences, API settings, and email service options.
          Manage your email campaign environment.
        </p>
      </div>

      <div className="card">
        <h2>Email Configuration</h2>
        <p>
          SMTP settings and email service configuration for campaign delivery.
        </p>
        
        <div style={{ marginTop: 'calc(var(--line-height) * 2)' }}>
          <div style={{ marginBottom: 'var(--line-height)' }}>
            <label className="label-field">smtp_host</label>
            <input 
              type="text" 
              className="input-field" 
              value="mail.spacemail.com"
              disabled
            />
          </div>
          
          <div style={{ marginBottom: 'var(--line-height)' }}>
            <label className="label-field">smtp_port</label>
            <input 
              type="text" 
              className="input-field" 
              value="465"
              disabled
            />
          </div>
          
          <div style={{ marginBottom: 'var(--line-height)' }}>
            <label className="label-field">from_email</label>
            <input 
              type="email" 
              className="input-field" 
              value="noah@mayflycreative.co"
              disabled
            />
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Google Sheets API</h2>
        <p>
          Service account configuration for Google Sheets integration.
        </p>
        
        <div style={{ marginTop: 'calc(var(--line-height) * 2)' }}>
          <div style={{ marginBottom: 'var(--line-height)' }}>
            <label className="label-field">service_account</label>
            <input 
              type="text" 
              className="input-field" 
              value="lead-gen-agent@ai-lead-gen-471213.iam.gserviceaccount.com"
              disabled
            />
          </div>
          
          <div style={{ marginBottom: 'var(--line-height)' }}>
            <span className="status-indicator">authenticated</span>
            <span style={{ marginLeft: '2ch', color: 'var(--text-color-alt)' }}>
              Credentials verified and active
            </span>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Application Settings</h2>
        <p>
          General preferences and application behavior configuration.
        </p>
        
        <table className="table-mono" style={{ marginTop: 'calc(var(--line-height) * 2)' }}>
          <thead>
            <tr>
              <th>setting</th>
              <th>value</th>
              <th>description</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>api_url</td>
              <td>http://localhost:8000</td>
              <td>Backend API endpoint</td>
            </tr>
            <tr>
              <td>environment</td>
              <td>development</td>
              <td>Application environment</td>
            </tr>
            <tr>
              <td>version</td>
              <td>v1.0.0</td>
              <td>Application version</td>
            </tr>
            <tr>
              <td>mock_mode</td>
              <td>true</td>
              <td>Email mock mode status</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="card">
        <h2>System Information</h2>
        <div className="code-block">
{`System Environment:
┌─────────────────────────────────────┐
│ Frontend: React 19.1.1 + TypeScript │
│ Backend:  FastAPI + SQLAlchemy      │
│ Database: SQLite (development)      │
│ Email:    SpaceMail SMTP            │
│ Sheets:   Google Sheets API v4      │
└─────────────────────────────────────┘

Component Status:
• Frontend    [ACTIVE]
• Backend     [ACTIVE] 
• Database    [CONNECTED]
• Email       [ACTIVE]
• Sheets API  [AUTHENTICATED]`}
        </div>
        
        <div className="grid-mono" style={{ marginTop: 'var(--line-height)' }}>
          <button className="btn-secondary" disabled>Export Settings</button>
          <Link to="/" className="btn-secondary">← Dashboard</Link>
        </div>
      </div>
    </div>
  );
};

export default Settings;