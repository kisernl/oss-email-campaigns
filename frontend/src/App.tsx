import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Components
import Navigation from './components/Navigation';

// Pages
import Dashboard from './pages/Dashboard';
import Campaigns from './pages/Campaigns';
import CreateCampaign from './pages/CreateCampaign';
import Templates from './pages/Templates';
import TemplateForm from './pages/TemplateForm';
import TemplateView from './pages/TemplateView';
import Sheets from './pages/Sheets';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';

function App() {
  return (
    <Router>
      <div style={{ 
        background: 'var(--background-color)', 
        color: 'var(--text-color)', 
        minHeight: '100vh',
        fontFamily: 'var(--font-family)'
      }}>
        {/* Navigation Header */}
        <Navigation />

        {/* Main Content Area */}
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/campaigns" element={<Campaigns />} />
            <Route path="/campaigns/:id" element={<Campaigns />} />
            <Route path="/create" element={<CreateCampaign />} />
            <Route path="/templates" element={<Templates />} />
            <Route path="/templates/create" element={<TemplateForm />} />
            <Route path="/templates/:id" element={<TemplateView />} />
            <Route path="/templates/:id/edit" element={<TemplateForm />} />
            <Route path="/sheets" element={<Sheets />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer style={{
          borderTop: 'var(--border-thickness) solid var(--border-color)',
          padding: 'var(--line-height) 2ch',
          marginTop: 'calc(var(--line-height) * 4)',
          background: 'var(--background-color-alt)'
        }}>
          <div style={{
            maxWidth: '120ch',
            margin: '0 auto',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            fontSize: '0.875rem',
            color: 'var(--text-color-alt)'
          }}>
            <div className="my-4">
              oss_email_campaign v0.0.1
            </div>
            <div className="my-4">
              github.com/kisernl
            </div>
            <div className="my-4">
              design inspired by{' '}
              <a 
                href="https://owickstrom.github.io/the-monospace-web/" 
                target="_blank" 
                rel="noopener noreferrer"
                style={{ color: 'var(--text-color-alt)', textDecoration: 'none' }}
              >
                the-monospace-web
              </a>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
