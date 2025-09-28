/**
 * Navigation Component
 * Minimalist monospace navigation header for Email Campaign App
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';

interface NavItem {
  path: string;
  label: string;
  description?: string;
}

const navigationItems: NavItem[] = [
  // {
  //   path: '/',
  //   label: 'dashboard',
  //   description: 'Overview and statistics'
  // },
  {
    path: '/campaigns',
    label: 'campaigns',
    description: 'Manage email campaigns'
  },
  {
    path: '/create',
    label: 'create',
    description: 'New email campaign'
  },
  {
    path: '/templates',
    label: 'templates',
    description: 'Reusable email templates'
  },
  {
    path: '/sheets',
    label: 'sheets',
    description: 'Google Sheets integration'
  },
  {
    path: '/settings',
    label: 'settings',
    description: 'Configuration and preferences'
  }
];

const Navigation: React.FC = () => {
  const location = useLocation();

  const isActiveRoute = (path: string): boolean => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <header className="main-header">
      <div className="header-container">
        {/* Brand/Logo */}
        <div className="header-brand">
          <Link to="/" className="brand-link">
            oss email campaigns
          </Link>
        </div>

        {/* Navigation */}
        <nav className="header-nav">
          {navigationItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-link ${isActiveRoute(item.path) ? 'nav-link-active' : ''}`}
              title={item.description}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
};

export default Navigation;