import sys
import os

# Add the app directory to the path
sys.path.append('app')

from app.utils.supabase_client import supabase

def run_marketplace_migration():
    """Run the marketplace database migration"""
    
    # Read the SQL migration file
    try:
        with open('create_marketplace_tables.sql', 'r') as file:
            sql_commands = file.read()
        
        print("📋 Running marketplace database migration...")
        
        # Split SQL commands by semicolon and execute each one
        commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
        
        for i, command in enumerate(commands, 1):
            if command:
                print(f"  {i}/{len(commands)}: Executing SQL command...")
                try:
                    # Execute the SQL command
                    result = supabase.rpc('exec_sql', {'sql': command}).execute()
                    print(f"    ✅ Command executed successfully")
                except Exception as e:
                    print(f"    ⚠️  Command may have failed (this is normal for some commands): {str(e)[:100]}...")
        
        print("🎉 Marketplace migration completed!")
        
        # Verify tables were created
        print("\n🔍 Verifying tables...")
        
        tables_to_check = ['products', 'tier_pricing', 'orders', 'product_categories']
        for table in tables_to_check:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f"  ✅ {table} table exists")
            except Exception as e:
                print(f"  ❌ {table} table not found: {str(e)[:100]}...")
        
    except FileNotFoundError:
        print("❌ Migration file 'create_marketplace_tables.sql' not found!")
        print("Please make sure the file exists in the current directory.")
    except Exception as e:
        print(f"❌ Error running migration: {e}")

if __name__ == "__main__":
    run_marketplace_migration() 