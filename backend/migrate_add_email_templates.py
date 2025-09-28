#!/usr/bin/env python3
"""
Migration script to add email_templates table.

Creates the email_templates table for storing reusable email templates
that can be used when creating campaigns.
"""

import sqlite3
import sys
import os

def migrate_database():
    """Add email_templates table to the database."""
    
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
        
        print("🔍 Checking if email_templates table exists...")
        
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='email_templates'
        """)
        
        if cursor.fetchone():
            print("✅ email_templates table already exists")
            return True
        
        print("📝 Creating email_templates table...")
        
        # Create email_templates table
        cursor.execute("""
            CREATE TABLE email_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                subject VARCHAR(500) NOT NULL,
                message TEXT NOT NULL,
                variables TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX idx_email_templates_name ON email_templates(name)")
        cursor.execute("CREATE INDEX idx_email_templates_created_at ON email_templates(created_at)")
        
        # Create a trigger to update updated_at timestamp
        cursor.execute("""
            CREATE TRIGGER update_email_templates_updated_at 
            AFTER UPDATE ON email_templates
            BEGIN
                UPDATE email_templates 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END
        """)
        
        # Insert some sample templates
        print("📋 Adding sample email templates...")
        
        sample_templates = [
            (
                "Welcome Email",
                "Welcome new users to your service",
                "Welcome to {{company}}, {{name}}!",
                "Hi {{name}},\n\nWelcome to {{company}}! We're excited to have you on board.\n\nYour account is now active and you can start exploring our features.\n\nIf you have any questions, feel free to reach out to us at {{support_email}}.\n\nBest regards,\nThe {{company}} Team",
                "name,company,support_email"
            ),
            (
                "Follow-up Email", 
                "Follow up with potential customers",
                "Following up on your interest in {{product}}",
                "Hi {{name}},\n\nI wanted to follow up on your recent interest in {{product}}.\n\nBased on your {{company}} profile, I think {{product}} could be a great fit for your needs.\n\nWould you be available for a quick 15-minute call this week to discuss how we can help?\n\nBest regards,\n{{sender_name}}",
                "name,product,company,sender_name"
            ),
            (
                "Newsletter Template",
                "Monthly newsletter template",
                "{{month}} Newsletter - {{company}} Updates",
                "Hi {{name}},\n\nHere's what's new at {{company}} this {{month}}:\n\n• {{update_1}}\n• {{update_2}}\n• {{update_3}}\n\nThanks for being part of our community!\n\nBest,\nThe {{company}} Team",
                "name,company,month,update_1,update_2,update_3"
            )
        ]
        
        cursor.executemany("""
            INSERT INTO email_templates (name, description, subject, message, variables)
            VALUES (?, ?, ?, ?, ?)
        """, sample_templates)
        
        # Commit changes
        conn.commit()
        
        print("🎉 Migration completed successfully!")
        
        # Verify table was created
        cursor.execute("SELECT COUNT(*) FROM email_templates")
        template_count = cursor.fetchone()[0]
        
        print(f"📊 email_templates table created with {template_count} sample templates")
        
        # Show table structure
        cursor.execute("PRAGMA table_info(email_templates)")
        columns = cursor.fetchall()
        
        print("📋 Table structure:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
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
    print("🚀 Starting database migration for email templates...")
    success = migrate_database()
    sys.exit(0 if success else 1)