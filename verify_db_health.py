#!/usr/bin/env python3
"""
Database Health Verifier
Comprehensive database health check
"""

from database import get_conn, get_detailed_stats
import os
from datetime import datetime

def verify_db_health():
    """Perform comprehensive database health check"""
    print("🏥 Database Health Check\n")
    print("=" * 70)
    
    health_score = 0
    max_score = 10
    
    # Check 1: Database file exists
    print("\n1. Database File Existence")
    print("-" * 70)
    from config import DB_PATH
    if os.path.exists(DB_PATH):
        size = os.path.getsize(DB_PATH)
        print(f"✅ Database file exists: {DB_PATH}")
        print(f"   Size: {size:,} bytes ({size/1024:.2f} KB)")
        health_score += 1
    else:
        print(f"❌ Database file not found: {DB_PATH}")
    
    # Check 2: Connection test
    print("\n2. Database Connection")
    print("-" * 70)
    try:
        conn = get_conn()
        print("✅ Connection successful")
        health_score += 1
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Check 3: Table count
    print("\n3. Table Structure")
    print("-" * 70)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        table_count = cursor.fetchone()[0]
        
        if table_count >= 15:
            print(f"✅ Found {table_count} tables (expected ~17)")
            health_score += 1
        else:
            print(f"⚠️  Only {table_count} tables found (expected ~17)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Check 4: Critical tables
    print("\n4. Critical Tables Check")
    print("-" * 70)
    critical_tables = ['users', 'payments', 'deadlines', 'books', 'settings']
    missing_tables = []
    
    for table in critical_tables:
        cursor.execute(f"""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table,))
        
        if cursor.fetchone()[0] == 1:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✅ {table}: {count} rows")
        else:
            print(f"❌ {table}: MISSING")
            missing_tables.append(table)
    
    if not missing_tables:
        health_score += 2
    elif len(missing_tables) <= 1:
        health_score += 1
    
    # Check 5: Data integrity
    print("\n5. Data Integrity")
    print("-" * 70)
    try:
        stats = get_detailed_stats()
        total_users = stats.get('total', 0)
        
        if total_users > 0:
            print(f"✅ Users table has data: {total_users} users")
            health_score += 1
        else:
            print("⚠️  Users table is empty")
        
        # Check for orphaned records
        cursor.execute("""
            SELECT COUNT(*) FROM deadlines d
            LEFT JOIN users u ON d.tg_id = u.tg_id
            WHERE u.tg_id IS NULL
        """)
        orphaned = cursor.fetchone()[0]
        
        if orphaned == 0:
            print("✅ No orphaned deadline records")
            health_score += 1
        else:
            print(f"⚠️  Found {orphaned} orphaned deadline records")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Check 6: Index efficiency
    print("\n6. Database Indexes")
    print("-" * 70)
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
        """)
        index_count = cursor.fetchone()[0]
        
        if index_count > 0:
            print(f"✅ Found {index_count} custom indexes")
            health_score += 1
        else:
            print("⚠️  No custom indexes found (performance may be slow)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Check 7: Database size vs record count
    print("\n7. Database Efficiency")
    print("-" * 70)
    try:
        cursor.execute("SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()")
        db_size = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(cnt) FROM (SELECT COUNT(*) as cnt FROM users UNION ALL SELECT COUNT(*) FROM deadlines UNION ALL SELECT COUNT(*) FROM payments)")
        total_records = cursor.fetchone()[0] or 0
        
        if total_records > 0:
            bytes_per_record = db_size / total_records
            print(f"✅ Database efficiency: {bytes_per_record:.0f} bytes/record")
            if bytes_per_record < 10000:  # Less than 10KB per record is good
                health_score += 1
        else:
            print("⚠️  No records to analyze")
    except Exception as e:
        print(f"⚠️  Could not calculate efficiency: {e}")
    
    # Check 8: Recent activity
    print("\n8. Recent Activity")
    print("-" * 70)
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE created >= datetime('now', '-7 days')
        """)
        recent_users = cursor.fetchone()[0]
        
        if recent_users > 0:
            print(f"✅ {recent_users} new users in last 7 days")
            health_score += 1
        else:
            print("⚠️  No new users in last 7 days")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    conn.close()
    
    # Final score
    print("\n" + "=" * 70)
    print(f"HEALTH SCORE: {health_score}/{max_score}")
    print("=" * 70)
    
    if health_score >= 9:
        print("🟢 EXCELLENT - Database is in perfect health")
    elif health_score >= 7:
        print("🟡 GOOD - Database is healthy with minor issues")
    elif health_score >= 5:
        print("🟠 FAIR - Database needs attention")
    else:
        print("🔴 POOR - Database has serious issues")
    
    print()

if __name__ == "__main__":
    verify_db_health()
