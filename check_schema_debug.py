#!/usr/bin/env python3
"""
Database Schema Checker
Verifies database tables and their structure
"""

import sqlite3
from config import DB_PATH

def check_schema():
    """Check database schema and table structures"""
    print("🔍 Checking Database Schema...\n")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"📊 Database: {DB_PATH}")
        print(f"📁 Total Tables: {len(tables)}\n")
        print("=" * 70)
        
        # Check each table
        for (table_name,) in tables:
            print(f"\n📋 Table: {table_name}")
            print("-" * 70)
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print(f"Columns ({len(columns)}):")
            for col_id, name, col_type, not_null, default, pk in columns:
                null_str = "NOT NULL" if not_null else "NULL"
                pk_str = "PRIMARY KEY" if pk else ""
                default_str = f"DEFAULT {default}" if default else ""
                print(f"  • {name:20} {col_type:15} {null_str:10} {pk_str:15} {default_str}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\nRows: {count}")
            
            # Show sample data for small tables
            if count > 0 and count <= 5:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                if rows:
                    print("\nSample Data:")
                    for row in rows:
                        print(f"  {row}")
        
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ Schema check completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_schema()
