#!/usr/bin/env python3
"""
Database migration: Add business hours columns to campaigns table.

This migration adds the following columns to the campaigns table:
- respect_business_hours: Boolean flag to enable/disable business hours restriction
- business_hours_start: Start hour in 24-hour format (default: 7 AM)
- business_hours_end: End hour in 24-hour format (default: 5 PM)
- business_days_only: Boolean flag for Monday-Friday only (default: True)
- timezone: Timezone string for business hours (default: UTC)
"""

import sqlite3
import sys
from pathlib import Path

# Database file path
DB_PATH = Path(__file__).parent / "email_campaigns.db"

def run_migration():
    """Execute the business hours migration."""
    print("🚀 Starting database migration for business hours...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(campaigns)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = [
            "respect_business_hours",
            "business_hours_start", 
            "business_hours_end",
            "business_days_only",
            "timezone"
        ]
        
        existing_new_columns = [col for col in new_columns if col in columns]
        if existing_new_columns:
            print(f"⚠️ Some business hours columns already exist: {existing_new_columns}")
            print("🔄 Skipping migration...")
            return True
        
        print("📝 Adding business hours columns to campaigns table...")
        
        # Add new columns with default values
        cursor.execute("""
            ALTER TABLE campaigns 
            ADD COLUMN respect_business_hours BOOLEAN DEFAULT 0
        """)
        
        cursor.execute("""
            ALTER TABLE campaigns 
            ADD COLUMN business_hours_start INTEGER DEFAULT 7
        """)
        
        cursor.execute("""
            ALTER TABLE campaigns 
            ADD COLUMN business_hours_end INTEGER DEFAULT 17
        """)
        
        cursor.execute("""
            ALTER TABLE campaigns 
            ADD COLUMN business_days_only BOOLEAN DEFAULT 1
        """)
        
        cursor.execute("""
            ALTER TABLE campaigns 
            ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC'
        """)
        
        # Commit changes
        conn.commit()
        
        # Verify columns were added
        cursor.execute("PRAGMA table_info(campaigns)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        
        print("✅ Business hours columns added successfully!")
        print("📊 Updated table structure:")
        
        business_hour_columns = [col for col in updated_columns if col in new_columns]
        for col in business_hour_columns:
            print(f"   - {col}")
        
        # Close connection
        conn.close()
        
        print("🎉 Migration completed successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)