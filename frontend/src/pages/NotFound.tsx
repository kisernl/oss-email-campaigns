/**
 * 404 Not Found Page
 * Monospace-styled error page
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const NotFound: React.FC = () => {
  const location = useLocation();

  return (
    <div style={{ 
      maxWidth: '80ch', 
      margin: '0 auto', 
      padding: 'calc(var(--line-height) * 4) 2ch',
      textAlign: 'center'
    }}>
      <div className="card">
        <div className="code-block">
{`HTTP/1.1 404 Not Found
Content-Type: text/plain
Location: ${location.pathname}

┌─────────────────────────────────────┐
│              ERROR 404              │
│         PAGE NOT FOUND              │
└─────────────────────────────────────┘`}
        </div>
        
        <h1>Route Not Found</h1>
        <p>
          The requested path <code>{location.pathname}</code> does not exist
          in the email campaign application routing table.
        </p>
        
        <div style={{ marginTop: 'calc(var(--line-height) * 2)' }}>
          <h3>Available Routes:</h3>
          <ul style={{ 
            listStyle: 'none', 
            padding: 0,
            margin: 'var(--line-height) 0',
            textAlign: 'left',
            display: 'inline-block'
          }}>
            <li><Link to="/" style={{ color: 'var(--text-color)' }}>/ → dashboard</Link></li>
            <li><Link to="/campaigns" style={{ color: 'var(--text-color)' }}>/campaigns → campaign_list</Link></li>
            <li><Link to="/create" style={{ color: 'var(--text-color)' }}>/create → new_campaign</Link></li>
            <li><Link to="/sheets" style={{ color: 'var(--text-color)' }}>/sheets → google_sheets</Link></li>
            <li><Link to="/settings" style={{ color: 'var(--text-color)' }}>/settings → configuration</Link></li>
          </ul>
        </div>
        
        <div className="grid-mono" style={{ marginTop: 'calc(var(--line-height) * 2)' }}>
          <Link to="/" className="btn-primary">← dashboard</Link>
          <Link to="/campaigns" className="btn-secondary">campaigns</Link>
        </div>
      </div>
    </div>
  );
};

export default NotFound;