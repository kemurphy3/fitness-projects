#!/usr/bin/env python3
"""
Initialize the PostgreSQL database with the schema.
Run this script to create all tables and initial data.
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

def create_database():
    """Create the database if it doesn't exist"""
    # Parse the database URL
    db_url = settings.database_url
    # Extract database name and connection parameters
    if "postgresql://" in db_url:
        parts = db_url.replace("postgresql://", "").split("/")
        db_name = parts[-1].split("?")[0]
        base_url = "postgresql://" + "/".join(parts[:-1]) + "/postgres"
    else:
        print("Invalid database URL format")
        return False
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(base_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Database '{db_name}' created successfully")
        else:
            print(f"Database '{db_name}' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def run_schema():
    """Run the schema.sql file to create tables"""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    
    if not os.path.exists(schema_path):
        print(f"Schema file not found: {schema_path}")
        return False
    
    try:
        conn = psycopg2.connect(settings.database_url)
        cursor = conn.cursor()
        
        # Read and execute schema
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        cursor.execute(schema_sql)
        conn.commit()
        
        print("Schema created successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error running schema: {e}")
        return False

def main():
    """Main initialization function"""
    print("Initializing Women's Soccer Readiness Database...")
    
    # Create database
    if not create_database():
        print("Failed to create database")
        sys.exit(1)
    
    # Run schema
    if not run_schema():
        print("Failed to create schema")
        sys.exit(1)
    
    print("\nDatabase initialized successfully!")
    print(f"Connection string: {settings.database_url}")
    print("\nNext steps:")
    print("1. Run the synthetic data generator to populate test data")
    print("2. Start the FastAPI server with: uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()