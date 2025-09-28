#!/usr/bin/env python3
"""
Fix stuck campaigns that are in 'sending' status but haven't processed emails.
This script resets stuck campaigns to 'draft' status so they can be sent again.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import SessionLocal
from app.models import Campaign, CampaignStatus
from datetime import datetime

def fix_stuck_campaigns():
    """Fix campaigns stuck in 'sending' status."""
    db = SessionLocal()
    
    try:
        # Find campaigns stuck in 'sending' status with no emails sent
        stuck_campaigns = db.query(Campaign).filter(
            Campaign.status == CampaignStatus.SENDING,
            Campaign.emails_sent == 0
        ).all()
        
        print(f"Found {len(stuck_campaigns)} stuck campaigns:")
        
        for campaign in stuck_campaigns:
            print(f"\nCampaign ID {campaign.id}: '{campaign.name}'")
            print(f"  Status: {campaign.status}")
            print(f"  Started at: {campaign.started_at}")
            print(f"  Emails sent: {campaign.emails_sent}")
            print(f"  Total recipients: {campaign.total_recipients}")
            
            # Reset to draft status
            campaign.status = CampaignStatus.DRAFT
            campaign.started_at = None
            campaign.completed_at = None
            campaign.error_message = "Campaign was reset from stuck 'sending' status"
            campaign.updated_at = datetime.utcnow()
            
            print(f"  → Reset to DRAFT status")
        
        if stuck_campaigns:
            db.commit()
            print(f"\n✅ Successfully reset {len(stuck_campaigns)} stuck campaigns to DRAFT status")
            print("You can now send these campaigns again from the frontend.")
        else:
            print("No stuck campaigns found.")
            
    except Exception as e:
        print(f"❌ Error fixing stuck campaigns: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_stuck_campaigns()