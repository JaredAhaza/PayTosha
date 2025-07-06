#!/usr/bin/env python3
"""
Database migration script to add location columns to context_profiles table
"""

import os
from app.utils.supabase_client import supabase

def run_migration():
    """Run the migration to add location columns"""
    
    # Read the migration SQL
    with open('add_location_columns_simple.sql', 'r') as f:
        migration_sql = f.read()
    
    try:
        print("🔄 Running database migration...")
        
        # Execute the migration
        result = supabase.rpc('exec_sql', {'sql': migration_sql}).execute()
        
        print("✅ Migration completed successfully!")
        print("📊 Added location columns to context_profiles table")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        print("\n🔧 Alternative: Run the SQL manually in your Supabase dashboard")
        print("📝 Copy and paste the contents of 'add_location_columns_simple.sql'")

def check_table_structure():
    """Check the current structure of context_profiles table"""
    try:
        print("🔍 Checking current table structure...")
        
        # Get table info
        result = supabase.table("context_profiles").select("*").limit(1).execute()
        
        if result.data:
            columns = list(result.data[0].keys())
            print(f"📋 Current columns: {', '.join(columns)}")
            
            # Check for location columns
            location_columns = ['country', 'region', 'city', 'timezone', 'coordinates', 'ip_address', 'time_of_day', 'day_of_week', 'is_weekend']
            missing_columns = [col for col in location_columns if col not in columns]
            
            if missing_columns:
                print(f"⚠️ Missing location columns: {', '.join(missing_columns)}")
                return False
            else:
                print("✅ All location columns exist!")
                return True
        else:
            print("ℹ️ Table is empty")
            return False
            
    except Exception as e:
        print(f"❌ Error checking table structure: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 PayTosha Database Migration Tool")
    print("=" * 40)
    
    # Check current structure
    has_columns = check_table_structure()
    
    if not has_columns:
        print("\n🔄 Running migration...")
        run_migration()
        
        # Check again after migration
        print("\n🔍 Verifying migration...")
        check_table_structure()
    else:
        print("\n✅ No migration needed - all columns already exist!") 