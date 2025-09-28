/**
 * CampaignList Component
 * Clean grid layout displaying campaign cards with monospace typography
 * Includes status indicators, progress bars, and campaign statistics
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { CampaignSummary, CampaignStatus } from '../types';

interface CampaignListProps {
  campaigns: CampaignSummary[];
  isLoading?: boolean;
  error?: string | null;
  onSendCampaign?: (campaignId: number) => void;
  onStopCampaign?: (campaignId: number, campaignName: string) => void;
  onDeleteCampaign?: (campaignId: number, campaignName: string) => void;
  onRefresh?: () => void;
}

const CampaignList: React.FC<CampaignListProps> = ({
  campaigns,
  isLoading = false,
  error = null,
  onSendCampaign,
  onStopCampaign,
  onDeleteCampaign,
  onRefresh
}) => {

  // Format date for display
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  // Calculate progress percentage
  const getProgressPercentage = (campaign: CampaignSummary): number => {
    if (campaign.total_recipients === 0) return 0;
    return Math.round((campaign.emails_sent / campaign.total_recipients) * 100);
  };

  // Get status display info with styling
  const getStatusDisplay = (status: CampaignStatus): { text: string; className: string } => {
    switch (status) {
      case CampaignStatus.DRAFT:
        return { text: 'draft', className: 'status-draft' };
      case CampaignStatus.SCHEDULED:
        return { text: 'scheduled', className: 'status-scheduled' };
      case CampaignStatus.SENDING:
        return { text: 'sending', className: 'status-sending' };
      case CampaignStatus.COMPLETED:
        return { text: 'completed', className: 'status-completed' };
      case CampaignStatus.FAILED:
        return { text: 'failed', className: 'status-failed' };
      case CampaignStatus.CANCELLED:
        return { text: 'cancelled', className: 'status-cancelled' };
      default:
        return { text: status, className: 'status-default' };
    }
  };

  // Get progress bar color based on status
  const getProgressColor = (status: CampaignStatus): string => {
    switch (status) {
      case CampaignStatus.COMPLETED:
        return '#008000'; // Green
      case CampaignStatus.FAILED:
        return '#ff0000'; // Red
      case CampaignStatus.SENDING:
        return '#007bff'; // Blue
      case CampaignStatus.CANCELLED:
        return '#ffa500'; // Orange
      default:
        return '#666666'; // Gray
    }
  };

  // Handle campaign actions
  const handleSendCampaign = (campaignId: number) => {
    if (onSendCampaign) {
      onSendCampaign(campaignId);
    }
  };

  const handleStopCampaign = (campaignId: number, campaignName: string) => {
    if (onStopCampaign) {
      onStopCampaign(campaignId, campaignName);
    }
  };

  const handleDeleteCampaign = (campaignId: number, campaignName: string) => {
    if (onDeleteCampaign) {
      onDeleteCampaign(campaignId, campaignName);
    }
  };

  // Error Display
  if (error) {
    return (
      <div className="card">
        <div className="error-message">
          {error}
        </div>
        {onRefresh && (
          <button 
            className="btn-secondary"
            onClick={onRefresh}
            style={{ marginTop: 'var(--line-height)' }}
          >
            Try Again
          </button>
        )}
      </div>
    );
  }

  // Loading State
  if (isLoading) {
    return (
      <div className="card">
        <div style={{ 
          textAlign: 'center', 
          padding: 'calc(var(--line-height) * 2)',
          color: 'var(--text-muted)'
        }}>
          <div className="code-block">
{`loading campaigns...
please wait...

[░░░░░░░░░░] 0%`}
          </div>
        </div>
      </div>
    );
  }

  // Empty State
  if (campaigns.length === 0) {
    return (
      <div className="card">
        <h2>No Campaigns Found</h2>
        <div className="code-block">
{`status: empty
campaigns: 0
message: no_campaigns_match_filters

suggestions:
- create_new_campaign
- adjust_filters
- check_backend_connection`}
        </div>
        <div className="grid-mono" style={{ marginTop: 'calc(var(--line-height) * 2)' }}>
          <Link to="/create" className="btn-primary">+ Create Campaign</Link>
          {onRefresh && (
            <button className="btn-secondary" onClick={onRefresh}>
              Refresh List
            </button>
          )}
        </div>
      </div>
    );
  }

  // Campaign Grid Layout
  return (
    <div style={{ 
      display: 'grid',
      gap: 'calc(var(--line-height) * 2)',
      gridTemplateColumns: 'repeat(auto-fit, minmax(60ch, 1fr))'
    }}>
      {campaigns.map((campaign) => {
        const statusDisplay = getStatusDisplay(campaign.status);
        const progressPercentage = getProgressPercentage(campaign);
        const progressColor = getProgressColor(campaign.status);
        
        return (
          <div key={campaign.id} className="campaign-card">
            {/* Campaign Header */}
            <div className="campaign-header">
              <div className="campaign-title">
                <h3>{campaign.name}</h3>
                <div className="campaign-meta">
                  id: {campaign.id} | created: {formatDate(campaign.created_at)}
                </div>
              </div>
              <div className={`status-indicator ${statusDisplay.className}`}>
                {statusDisplay.text}
              </div>
            </div>

             {/* Campaign Statistics */}
            <div className="campaign-stats">
              <div className="code-block">
{`recipients: ${campaign.total_recipients}
emails_sent: ${campaign.emails_sent}${campaign.emails_failed > 0 ? `
emails_failed: ${campaign.emails_failed}` : ''}
success_rate: ${campaign.success_rate.toFixed(1)}%${campaign.status === 'sending' ? `
status: actively sending emails...` : ''}${campaign.completed_at ? `
completed: ${formatDate(campaign.completed_at)}` : ''}`}
              </div>
            </div>

            {/* Progress Bar */}
            {campaign.total_recipients > 0 && (
              <div className="progress-container">
                <div className="progress-label">
                  progress: {campaign.emails_sent}/{campaign.total_recipients} ({progressPercentage}%)
                  {campaign.status === 'sending' && (
                    <span style={{ color: '#008000', marginLeft: '1ch' }}>
                      • sending now...
                    </span>
                  )}
                  {campaign.status === 'completed' && campaign.emails_sent === campaign.total_recipients && (
                    <span style={{ color: '#008000', marginLeft: '1ch' }}>
                      • all emails sent ✓
                    </span>
                  )}
                  {campaign.status === 'cancelled' && (
                    <span style={{ color: '#ff6600', marginLeft: '1ch' }}>
                      • stopped by user
                    </span>
                  )}
                  {campaign.status === 'failed' && (
                    <span style={{ color: '#ff0000', marginLeft: '1ch' }}>
                      • sending failed
                    </span>
                  )}
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{
                      width: `${progressPercentage}%`,
                      backgroundColor: progressColor,
                      animation: campaign.status === 'sending' ? 'pulse 2s infinite' : 'none'
                    }}
                  />
                </div>
              </div>
            )}

            {/* Campaign Actions */}
            <div className="campaign-actions">
              <div className="grid-mono">
                {/* Send Button - only for draft campaigns */}
                {campaign.status === CampaignStatus.DRAFT && onSendCampaign && (
                  <button 
                    className="btn-primary"
                    onClick={() => handleSendCampaign(campaign.id)}
                  >
                    Send Now
                  </button>
                )}
                
                {/* Stop Button - only for sending campaigns */}
                {campaign.status === CampaignStatus.SENDING && onStopCampaign && (
                  <button 
                    className="btn-stop"
                    onClick={() => handleStopCampaign(campaign.id, campaign.name)}
                  >
                    Stop Campaign
                  </button>
                )}
                
                {/* Refresh Button - only for active campaigns */}
                {(campaign.status === CampaignStatus.SENDING || campaign.status === CampaignStatus.SCHEDULED) && onRefresh && (
                  <button 
                    className="btn-secondary"
                    onClick={onRefresh}
                    style={{ fontSize: '0.875rem' }}
                  >
                    Refresh Status
                  </button>
                )}
                
                {/* Delete Button - only for draft campaigns */}
                {campaign.status === CampaignStatus.DRAFT && onDeleteCampaign && (
                  <button 
                    className="btn-delete"
                    onClick={() => handleDeleteCampaign(campaign.id, campaign.name)}
                  >
                    Delete
                  </button>
                )}
              </div>
            </div>


          </div>
        );
      })}
    </div>
  );
};

export default CampaignList;