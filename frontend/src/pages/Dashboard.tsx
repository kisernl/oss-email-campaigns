/**
 * Dashboard Page
 * Overview and statistics for email campaigns
 */

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { healthCheck, getCampaigns } from '../services/api';
import { CampaignSummary } from '../types';

const Dashboard: React.FC = () => {
  const [campaigns, setCampaigns] = useState<CampaignSummary[]>([]);
  const [isHealthy, setIsHealthy] = useState<boolean>(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Check health status
        const health = await healthCheck();
        setIsHealthy(health.status === 'healthy');
        
        // Get recent campaigns
        const campaignData = await getCampaigns({ limit: 5 });
        setCampaigns(campaignData);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        setIsHealthy(false);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div style={{ 
        maxWidth: '80ch', 
        margin: '0 auto', 
        padding: 'calc(var(--line-height) * 2) 2ch' 
      }}>
        <div className="card">
          <div>loading_dashboard...</div>
        </div>
      </div>
    );
  }

  const totalCampaigns = campaigns.length;
  const totalSent = campaigns.reduce((sum, c) => sum + c.emails_sent, 0);
  const avgSuccessRate = campaigns.length > 0 
    ? campaigns.reduce((sum, c) => sum + c.success_rate, 0) / campaigns.length 
    : 0;

  return (
    <div style={{ 
      maxWidth: '80ch', 
      margin: '0 auto', 
      padding: 'calc(var(--line-height) * 2) 2ch' 
    }}>
      {/* Page Header */}
      <div className="card">
        <h1>Dashboard</h1>
        <p>
          Email campaign overview and system status.
          Monitor your campaigns and track performance metrics.
        </p>
        
        <div className="grid-mono mt-auto" style={{ marginTop: 'var(--line-height)' }}>
          <Link to="/create" className="btn-primary">+ new_campaign</Link>
          <Link to="/campaigns" className="btn-secondary mt-0">view_all</Link>
        </div>
      </div>

      {/* System Status */}
      <div className="card">
        <h2>System Status</h2>
        <div className="grid-mono">
          <div>
            <div style={{ color: 'var(--text-color-alt)', fontSize: '0.875rem' }}>
              backend_status
            </div>
            <div style={{ 
              fontSize: '1.25rem', 
              fontWeight: 'var(--font-weight-medium)',
              color: isHealthy ? 'var(--text-color)' : 'var(--text-color-alt)'
            }}>
              {isHealthy ? 'healthy' : 'offline'}
            </div>
          </div>
          <div>
            <div style={{ color: 'var(--text-color-alt)', fontSize: '0.875rem' }}>
              api_version
            </div>
            <div style={{ fontSize: '1.25rem', fontWeight: 'var(--font-weight-medium)' }}>
              v1.0.0
            </div>
          </div>
          <div>
            <div style={{ color: 'var(--text-color-alt)', fontSize: '0.875rem' }}>
              environment
            </div>
            <div style={{ fontSize: '1.25rem', fontWeight: 'var(--font-weight-medium)' }}>
              development
            </div>
          </div>
        </div>
      </div>

      {/* Campaign Statistics */}
      <div className="card">
        <h2>Campaign Statistics</h2>
        <div className="grid-mono">
          <div>
            <div style={{ color: 'var(--text-color-alt)', fontSize: '0.875rem' }}>
              total_campaigns
            </div>
            <div style={{ 
              fontSize: '2rem', 
              fontWeight: 'var(--font-weight-bold)', 
              lineHeight: '2.4rem' 
            }}>
              {totalCampaigns}
            </div>
          </div>
          <div>
            <div style={{ color: 'var(--text-color-alt)', fontSize: '0.875rem' }}>
              emails_sent
            </div>
            <div style={{ 
              fontSize: '2rem', 
              fontWeight: 'var(--font-weight-bold)', 
              lineHeight: '2.4rem' 
            }}>
              {totalSent}
            </div>
          </div>
          <div>
            <div style={{ color: 'var(--text-color-alt)', fontSize: '0.875rem' }}>
              avg_success_rate
            </div>
            <div style={{ 
              fontSize: '2rem', 
              fontWeight: 'var(--font-weight-bold)', 
              lineHeight: '2.4rem' 
            }}>
              {avgSuccessRate.toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      {/* Recent Campaigns */}
      <div className="card">
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: 'var(--line-height)'
        }}>
          <h2 style={{ margin: 0 }}>Recent Campaigns</h2>
          <Link to="/campaigns" className="nav-mono">view_all →</Link>
        </div>

        {campaigns.length === 0 ? (
          <div style={{ 
            color: 'var(--text-color-alt)', 
            textAlign: 'center',
            padding: 'calc(var(--line-height) * 2) 0'
          }}>
            no_campaigns_found
            <br />
            <Link to="/create" style={{ color: 'var(--text-color)' }}>
              create_your_first_campaign →
            </Link>
          </div>
        ) : (
          <table className="table-mono">
            <thead>
              <tr>
                <th>name</th>
                <th>status</th>
                <th>recipients</th>
                <th>sent</th>
                <th>success_rate</th>
              </tr>
            </thead>
            <tbody>
              {campaigns.map((campaign) => (
                <tr key={campaign.id}>
                  <td>
                    <Link to={`/campaigns/${campaign.id}`} style={{ 
                      color: 'var(--text-color)',
                      textDecoration: 'none'
                    }}>
                      {campaign.name}
                    </Link>
                  </td>
                  <td>
                    <span className="status-indicator">
                      {campaign.status}
                    </span>
                  </td>
                  <td>{campaign.total_recipients}</td>
                  <td>{campaign.emails_sent}</td>
                  <td>{campaign.success_rate.toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* ASCII Art Footer */}
      <div className="card">
        <h3>System Map</h3>
        <div className="code-block">
{`┌─────────────────────────────────────┐
│           CAMPAIGN FLOW             │
├─────────────────────────────────────┤
│ sheets → validate → campaign → send │
│   ↓         ↓          ↓        ↓   │
│ preview   access    create   emails │
└─────────────────────────────────────┘`}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;