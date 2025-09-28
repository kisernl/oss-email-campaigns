#!/usr/bin/env python3
"""
Reset stuck campaigns utility script.
This can be run manually or scheduled to automatically fix campaigns stuck in 'sending' status.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import SessionLocal
from app.models import Campaign, CampaignStatus

def reset_stuck_campaigns(max_age_minutes=30):
    """
    Reset campaigns stuck in 'sending' status for more than max_age_minutes.
    
    Args:
        max_age_minutes: How long a campaign can be in 'sending' status before being reset
    """
    db = SessionLocal()
    
    try:
        # Calculate cutoff time
        cutoff_time = datetime.utcnow() - timedelta(minutes=max_age_minutes)
        
        # Find campaigns stuck in 'sending' status with no emails sent for more than max_age_minutes
        stuck_campaigns = db.query(Campaign).filter(
            Campaign.status == CampaignStatus.SENDING,
            Campaign.emails_sent == 0,
            Campaign.started_at < cutoff_time
        ).all()
        
        print(f"Checking for campaigns stuck in 'sending' status for more than {max_age_minutes} minutes...")
        print(f"Found {len(stuck_campaigns)} stuck campaigns:")
        
        for campaign in stuck_campaigns:
            age_minutes = (datetime.utcnow() - campaign.started_at).total_seconds() / 60
            print(f"\nCampaign ID {campaign.id}: '{campaign.name}'")
            print(f"  Status: {campaign.status}")
            print(f"  Started at: {campaign.started_at}")
            print(f"  Age: {age_minutes:.1f} minutes")
            print(f"  Emails sent: {campaign.emails_sent}/{campaign.total_recipients}")
            
            # Reset to draft status
            campaign.status = CampaignStatus.DRAFT
            campaign.started_at = None
            campaign.completed_at = None
            campaign.error_message = f"Campaign was automatically reset after being stuck in 'sending' status for {age_minutes:.1f} minutes"
            campaign.updated_at = datetime.utcnow()
            
            print(f"  → Reset to DRAFT status")
        
        if stuck_campaigns:
            db.commit()
            print(f"\n✅ Successfully reset {len(stuck_campaigns)} stuck campaigns to DRAFT status")
            return len(stuck_campaigns)
        else:
            print("No stuck campaigns found.")
            return 0
            
    except Exception as e:
        print(f"❌ Error resetting stuck campaigns: {e}")
        db.rollback()
        return -1
    finally:
        db.close()

def main():
    """Main function with command line argument support."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Reset campaigns stuck in sending status')
    parser.add_argument('--max-age', type=int, default=30, 
                        help='Maximum age in minutes before resetting (default: 30)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be reset without actually doing it')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        # TODO: Implement dry run logic
    
    result = reset_stuck_campaigns(args.max_age)
    
    if result > 0:
        print(f"\n🔧 FIXED: {result} campaigns were reset and can now be sent again")
    elif result == 0:
        print(f"\n✅ OK: No stuck campaigns found")
    else:
        print(f"\n❌ ERROR: Failed to check/reset campaigns")
        sys.exit(1)

if __name__ == "__main__":
    main()