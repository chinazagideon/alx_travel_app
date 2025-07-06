#!/usr/bin/env python3
"""
Database setup script for Airbnb Clone
This script helps set up PostgreSQL database and user
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from decouple import config

def create_database():
    """Create PostgreSQL database and user"""
    
    # Get database configuration from environment
    db_name = config('DB_NAME', default='airbnb_clone')
    db_user = config('DB_USER', default='postgres')
    db_password = config('DB_PASSWORD', default='')
    db_host = config('DB_HOST', default='localhost')
    db_port = config('DB_PORT', default='5432')
    
    try:
        # Connect to PostgreSQL server (to postgres database)
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{db_name}'...")
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Database '{db_name}' created successfully!")
        else:
            print(f"Database '{db_name}' already exists.")
        
        cursor.close()
        conn.close()
        
        # Test connection to the new database
        test_conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        test_conn.close()
        print(f"Successfully connected to database '{db_name}'!")
        
    except psycopg2.Error as e:
        print(f"Error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure PostgreSQL is installed and running")
        print("2. Check your database credentials in .env file")
        print("3. Ensure the postgres user has permission to create databases")
        print("4. Try connecting manually: psql -U postgres -h localhost")

def check_postgresql_connection():
    """Check if PostgreSQL is accessible"""
    try:
        conn = psycopg2.connect(
            host=config('DB_HOST', default='localhost'),
            port=config('DB_PORT', default='5432'),
            user=config('DB_USER', default='postgres'),
            password=config('DB_PASSWORD', default=''),
            database='postgres'
        )
        conn.close()
        print("✓ PostgreSQL connection successful!")
        return True
    except psycopg2.Error as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Airbnb Clone - Database Setup")
    print("=" * 40)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  .env file not found!")
        print("Please create a .env file based on env_template.txt")
        print("Example:")
        print("cp env_template.txt .env")
        print("Then edit .env with your actual database credentials")
        exit(1)
    
    # Test PostgreSQL connection
    if check_postgresql_connection():
        create_database()
        print("\n✅ Database setup completed!")
        print("\nNext steps:")
        print("1. Run migrations: python3 manage.py migrate")
        print("2. Create superuser: python3 manage.py createsuperuser")
        print("3. Start the server: python3 manage.py runserver")
    else:
        print("\n❌ Please fix PostgreSQL connection issues before proceeding") 