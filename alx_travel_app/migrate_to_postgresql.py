#!/usr/bin/env python3
"""
Migration script to help transition from SQLite to PostgreSQL
This script can be used to migrate existing data if needed
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airbnb_clone.settings')
    django.setup()

def backup_sqlite_data():
    """Create a backup of SQLite data"""
    if os.path.exists('db.sqlite3'):
        import shutil
        backup_name = f'db_backup_{int(time.time())}.sqlite3'
        shutil.copy2('db.sqlite3', backup_name)
        print(f"SQLite database backed up as {backup_name}")
        return backup_name
    return None

def migrate_to_postgresql():
    """Migrate from SQLite to PostgreSQL"""
    print("PostgreSQL Migration Helper")
    print("=" * 40)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print(".env file not found!")
        print("Please create .env file with PostgreSQL credentials")
        return False
    
    # Setup Django
    setup_django()
    
    # Backup existing data
    backup_file = backup_sqlite_data()
    
    print("\nMigration Steps:")
    print("1. Environment file checked")
    print("2. SQLite backup created" if backup_file else "No SQLite data to backup")
    print("3. Running migrations...")
    
    try:
        # Run migrations
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("4. Migrations completed successfully!")
        print("Migration to PostgreSQL completed!")
        
        if backup_file:
            print(f"\nYour SQLite backup is saved as: {backup_file}")
            print("You can delete it once you've verified everything works correctly.")
        
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    import time
    migrate_to_postgresql() 