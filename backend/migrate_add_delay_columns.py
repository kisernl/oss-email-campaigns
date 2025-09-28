#!/usr/bin/env python3
"""
Migration script to add email delay configuration columns to campaigns table.

Adds:
- use_delay: Boolean column for enabling/disabling delay
- delay_min_minutes: Integer column for minimum delay in minutes (default 4)
- delay_max_minutes: Integer column for maximum delay in minutes (default 7)
"""

import sqlite3
import sys
import os

def migrate_database():
    """Add delay configuration columns to campaigns table."""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), 'email_campaigns.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    conn = None
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking current table schema...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(campaigns)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = ['use_delay', 'delay_min_minutes', 'delay_max_minutes']
        missing_columns = [col for col in new_columns if col not in columns]
        
        if not missing_columns:
            print("✅ All delay columns already exist in the database")
            return True
        
        print(f"📝 Adding missing columns: {missing_columns}")
        
        # Add missing columns with default values
        if 'use_delay' in missing_columns:
            cursor.execute("ALTER TABLE campaigns ADD COLUMN use_delay BOOLEAN DEFAULT 0")
            print("✅ Added use_delay column")
        
        if 'delay_min_minutes' in missing_columns:
            cursor.execute("ALTER TABLE campaigns ADD COLUMN delay_min_minutes INTEGER DEFAULT 4")
            print("✅ Added delay_min_minutes column")
        
        if 'delay_max_minutes' in missing_columns:
            cursor.execute("ALTER TABLE campaigns ADD COLUMN delay_max_minutes INTEGER DEFAULT 7")
            print("✅ Added delay_max_minutes column")
        
        # Commit changes
        conn.commit()
        
        print("🎉 Migration completed successfully!")
        
        # Verify columns were added
        cursor.execute("PRAGMA table_info(campaigns)")
        columns_after = [column[1] for column in cursor.fetchall()]
        
        print(f"📊 Campaign table now has {len(columns_after)} columns:")
        for col in sorted(columns_after):
            print(f"   - {col}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 Starting database migration for email delay features...")
    success = migrate_database()
    sys.exit(0 if success else 1)