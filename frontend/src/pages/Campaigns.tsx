/**
 * Campaigns Page
 * Manage email campaigns with filtering, sorting, and campaign list display
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import apiClient from '../services/api';
import { CampaignSummary, CampaignStatus } from '../types';
import CampaignList from '../components/CampaignList';

interface LocationState {
  message?: string;
  campaignId?: number;
}

const Campaigns: React.FC = () => {
  const location = useLocation();
  const locationState = location.state as LocationState;
  
  // State management
  const [campaigns, setCampaigns] = useState<CampaignSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<CampaignStatus | 'all'>('all');
  const [sortBy, setSortBy] = useState<'created_at' | 'name' | 'status'>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const [completionNotifications, setCompletionNotifications] = useState<string[]>([]);
  const previousCampaignsRef = useRef<CampaignSummary[]>([]);
  const [showAllCampaigns, setShowAllCampaigns] = useState(false);
  const [visibleCampaigns, setVisibleCampaigns] = useState<CampaignSummary[]>([]);
  const loadCampaigns = useCallback(async (isAutoRefresh = false) => {
    if (!isAutoRefresh) {
      setIsLoading(true);
    }
    setError(null);
    
    try {
      const campaignsData = await apiClient.getCampaigns({
        status_filter: filterStatus === 'all' ? undefined : filterStatus,
        sort_by: sortBy,
        sort_order: sortOrder
      });
      
      // Check for newly completed campaigns
      if (isAutoRefresh && previousCampaignsRef.current.length > 0) {
        const newlyCompleted = campaignsData.filter(campaign => {
          const previous = previousCampaignsRef.current.find(p => p.id === campaign.id);
          return previous && 
                 previous.status === 'sending' && 
                 (campaign.status === 'completed' || campaign.status === 'failed' || campaign.status === 'cancelled');
        });
        
        newlyCompleted.forEach(campaign => {
          const message = campaign.status === 'completed' 
            ? `Campaign "${campaign.name}" completed! ${campaign.emails_sent}/${campaign.total_recipients} emails sent.`
            : campaign.status === 'failed'
            ? `Campaign "${campaign.name}" failed to complete.`
            : `Campaign "${campaign.name}" was cancelled.`;
          
          setCompletionNotifications(prev => [...prev, message]);
          
          // Remove notification after 10 seconds
          setTimeout(() => {
            setCompletionNotifications(prev => prev.filter(msg => msg !== message));
          }, 10000);
        });
      }
      
      previousCampaignsRef.current = campaignsData;
      setCampaigns(campaignsData);
      
      // Apply pagination - show first 10 by default
      const displayCampaigns = showAllCampaigns ? campaignsData : campaignsData.slice(0, 10);
      setVisibleCampaigns(displayCampaigns);
      
      setLastRefresh(new Date());
    } catch (error: any) {
      setError(error.message || 'Failed to load campaigns');
    } finally {
      if (!isAutoRefresh) {
        setIsLoading(false);
      }
    }
  }, [filterStatus, sortBy, sortOrder]);

  // Load campaigns on component mount
  useEffect(() => {
    loadCampaigns();
    
    // Show success message if navigated from campaign creation
    if (locationState?.message) {
      setSuccessMessage(locationState.message);
      // Clear message after 5 seconds
      setTimeout(() => setSuccessMessage(null), 5000);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [locationState]); // loadCampaigns excluded to prevent infinite loops

  // Manual refresh function
  const handleManualRefresh = () => {
    loadCampaigns(false);
  };

  // Update visible campaigns when showAllCampaigns changes
  useEffect(() => {
    const displayCampaigns = showAllCampaigns ? campaigns : campaigns.slice(0, 10);
    setVisibleCampaigns(displayCampaigns);
  }, [campaigns, showAllCampaigns]);

  // Reload campaigns when filters change
  useEffect(() => {
    setShowAllCampaigns(false); // Reset pagination when filters change
    loadCampaigns();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterStatus, sortBy, sortOrder]); // loadCampaigns excluded to prevent infinite loops

  // Handle campaign sending
  const handleSendCampaign = async (campaignId: number) => {
    try {
      await apiClient.sendCampaign(campaignId, { send_immediately: true });
      await loadCampaigns(); // Refresh the list
    } catch (error: any) {
      setError(`Failed to send campaign: ${error.message}`);
    }
  };

  // Handle campaign stopping
  const handleStopCampaign = async (campaignId: number, campaignName: string) => {
    if (!window.confirm(`Are you sure you want to stop campaign "${campaignName}"? This will halt email sending immediately.`)) {
      return;
    }
    
    try {
      await apiClient.stopCampaign(campaignId);
      await loadCampaigns(); // Refresh the list
      setSuccessMessage(`Campaign "${campaignName}" stopped successfully`);
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (error: any) {
      setError(`Failed to stop campaign: ${error.message}`);
    }
  };

  // Handle campaign deletion
  const handleDeleteCampaign = async (campaignId: number, campaignName: string) => {
    if (!window.confirm(`Are you sure you want to delete campaign "${campaignName}"?`)) {
      return;
    }
    
    try {
      await apiClient.deleteCampaign(campaignId);
      await loadCampaigns(); // Refresh the list
      setSuccessMessage(`Campaign "${campaignName}" deleted successfully`);
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (error: any) {
      setError(`Failed to delete campaign: ${error.message}`);
    }
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
            <h1 style={{ margin: 0 }}>Campaigns</h1>
            <p style={{ margin: 'calc(var(--line-height) / 2) 0 0 0', color: 'var(--text-muted)' }}>
              manage your email campaigns (showing {visibleCampaigns.length} of {campaigns.length} total)
              {lastRefresh && (
                <span style={{ marginLeft: '1ch', fontSize: '0.875rem' }}>
                  • last updated: {lastRefresh.toLocaleTimeString()}
                </span>
              )}
            </p>
          </div>
          <div style={{ display: 'flex', gap: '1ch', alignItems: 'center' }}>
            {/* <button 
              onClick={handleManualRefresh}
              className="btn-secondary"
              disabled={isLoading}
              style={{ fontSize: '0.875rem' }}
            >
              {isLoading ? 'refreshing...' : 'refresh_now'}
            </button> */}
            <Link to="/create" className="btn-primary">+ new_campaign</Link>
          </div>
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

      {/* Completion Notifications */}
      {completionNotifications.map((notification, index) => (
        <div 
          key={index}
          className="card" 
          style={{ 
            backgroundColor: 'rgba(0, 128, 0, 0.1)', 
            borderColor: '#008000',
            animation: 'slideIn 0.3s ease-out'
          }}
        >
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center' 
          }}>
            <p style={{ margin: 0, color: '#008000', fontWeight: 'var(--font-weight-medium)' }}>
              🎉 {notification}
            </p>
            <button 
              onClick={() => setCompletionNotifications(prev => prev.filter((_, i) => i !== index))}
              style={{ 
                background: 'none', 
                border: 'none', 
                color: '#008000', 
                cursor: 'pointer',
                fontSize: '1.2rem',
                padding: '0 0.5ch'
              }}
            >
              ×
            </button>
          </div>
        </div>
      ))}

      {/* Filters and Sorting */}
      <div className="card">
        <h2>Filters & Sorting</h2>
        <div className="filters-grid mt-0">
          <div className="filter-column">
            <label className="label-field">status</label>
            <select 
              className="input-field"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value as CampaignStatus | 'all')}
            >
              <option value="all">all</option>
              <option value="draft">draft</option>
              <option value="scheduled">scheduled</option>
              <option value="sending">sending</option>
              <option value="completed">completed</option>
              <option value="failed">failed</option>
              <option value="cancelled">cancelled</option>
            </select>
          </div>
          
          <div className="filter-column mt-0">
            <label className="label-field">sort_by</label>
            <select 
              className="input-field"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'created_at' | 'name' | 'status')}
            >
              <option value="created_at">created_date</option>
              <option value="name">name</option>
              <option value="status">status</option>
            </select>
          </div>
          
          <div className="filter-column mt-0">
            <label className="label-field">order</label>
            <select 
              className="input-field"
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value as 'asc' | 'desc')}
            >
              <option value="desc">desc</option>
              <option value="asc">asc</option>
            </select>
          </div>
        </div>
      </div>

      {/* Campaign List Component */}
      <CampaignList
        campaigns={visibleCampaigns}
        isLoading={isLoading}
        error={error}
        onSendCampaign={handleSendCampaign}
        onStopCampaign={handleStopCampaign}
        onDeleteCampaign={handleDeleteCampaign}
        onRefresh={handleManualRefresh}
      />

      {/* Show More Button */}
      {!showAllCampaigns && campaigns.length > 10 && (
        <div className="card" style={{ textAlign: 'center' }}>
          <p style={{ 
            margin: '0 0 var(--line-height) 0', 
            color: 'var(--text-muted)',
            fontSize: '0.875rem'
          }}>
            showing most recent {visibleCampaigns.length} campaigns
          </p>
          <button 
            onClick={() => setShowAllCampaigns(true)}
            className="btn-secondary"
            style={{ margin: '0 auto' }}
          >
            show_all_campaigns ({campaigns.length - 10} older)
          </button>
        </div>
      )}

      {/* Show Less Button */}
      {showAllCampaigns && campaigns.length > 10 && (
        <div className="card" style={{ textAlign: 'center' }}>
          <p style={{ 
            margin: '0 0 var(--line-height) 0', 
            color: 'var(--text-muted)',
            fontSize: '0.875rem'
          }}>
            showing all {campaigns.length} campaigns
          </p>
          <button 
            onClick={() => setShowAllCampaigns(false)}
            className="btn-secondary"
            style={{ margin: '0 auto' }}
          >
            show_recent_only (hide {campaigns.length - 10} older)
          </button>
        </div>
      )}

      {/* Quick Actions */}
      <div className="card">
        <h2>Quick Actions</h2>
        <div className="grid-mono">
          <Link to="/create" className="btn-primary mt-0">+ Create Campaign</Link>
          <Link to="/" className="btn-secondary mt-0">← Back to Dashboard</Link>
          <button 
            className="btn-secondary mt-0"
            onClick={() => loadCampaigns(false)}
            disabled={isLoading}
          >
            {isLoading ? 'Loading...' : 'Refresh List'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Campaigns;