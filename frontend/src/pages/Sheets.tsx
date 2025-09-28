/**
 * Google Sheets Page
 * Google Sheets integration and management
 */

import React from 'react';
import { Link } from 'react-router-dom';

const Sheets: React.FC = () => {
  return (
    <div style={{ 
      maxWidth: '80ch', 
      margin: '0 auto', 
      padding: 'calc(var(--line-height) * 2) 2ch' 
    }}>
      <div className="card">
        <h1>Google Sheets Integration</h1>
        <p>
          Manage Google Sheets connections and preview email recipient data.
          Validate sheet access and format before creating campaigns.
        </p>
      </div>

      <div className="card">
        <h2>Sheet Validation Tool</h2>
        <p>
          Test Google Sheets access and preview email data format.
          This tool will validate sheet permissions and detect email columns.
        </p>
        
        <div style={{ marginTop: 'calc(var(--line-height) * 2)' }}>
          <label className="label-field">google_sheet_id</label>
          <input 
            type="text" 
            className="input-field" 
            placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
            disabled
          />
        </div>
        
        <div style={{ marginTop: 'var(--line-height)' }}>
          <label className="label-field">sheet_range</label>
          <input 
            type="text" 
            className="input-field" 
            placeholder="A:Z"
            disabled
          />
        </div>

        <div className="grid-mono" style={{ marginTop: 'var(--line-height)' }}>
          <button className="btn-primary" disabled>Preview Sheet</button>
          <button className="btn-secondary" disabled>Validate Access</button>
        </div>
      </div>

      <div className="card">
        <h2>Sheet Requirements</h2>
        <p>
          Your Google Sheet must meet these requirements for successful integration:
        </p>
        
        <div style={{ marginTop: 'calc(var(--line-height) * 2)' }}>
          <h3>Required Columns:</h3>
          <table className="table-mono">
            <thead>
              <tr>
                <th>column_type</th>
                <th>accepted_names</th>
                <th>required</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>email</td>
                <td>email, email_address, e-mail</td>
                <td>yes</td>
              </tr>
              <tr>
                <td>name</td>
                <td>name, first_name, full_name</td>
                <td>no</td>
              </tr>
              <tr>
                <td>custom</td>
                <td>any_other_column</td>
                <td>no</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div style={{ marginTop: 'calc(var(--line-height) * 2)' }}>
          <h3>Permissions:</h3>
          <ul style={{ 
            listStyle: 'none', 
            padding: '0 0 0 2ch',
            margin: 'var(--line-height) 0'
          }}>
            <li>• Sheet must be shared with service account</li>
            <li>• Read access is sufficient</li>
            <li>• Public sheets are also supported</li>
          </ul>
        </div>
      </div>

      <div className="card">
        <h3>Sample Sheet Format</h3>
        <div className="code-block">
{`A          B             C
email      name          company
────────────────────────────────
user@ex.co John Doe      Acme Inc
jane@co.io Jane Smith    Tech Co
bob@org.co Bob Johnson   Startup`}
        </div>
        
        <div className="grid-mono" style={{ marginTop: 'var(--line-height)' }}>
          <Link to="/create" className="btn-primary">Create Campaign</Link>
          <Link to="/" className="btn-secondary">← Dashboard</Link>
        </div>
      </div>
    </div>
  );
};

export default Sheets;