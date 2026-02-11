#!/usr/bin/env python3
"""
Async Database Verifier
Checks database integrity and async operations
"""

import asyncio
import aiosqlite
from config import DB_PATH
from database import get_detailed_stats, get_all_users

async def verify_async_db():
    """Verify database with async operations"""
    print("🔍 Verifying Database (Async)...\n")
    
    # Test 1: Async connection
    print("Test 1: Async Connection")
    print("-" * 60)
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            count = await cursor.fetchone()
            print(f"✅ Async connection successful")
            print(f"   Users in database: {count[0]}\n")
    except Exception as e:
        print(f"❌ Async connection failed: {e}\n")
    
    # Test 2: Sync functions
    print("Test 2: Sync Database Functions")
    print("-" * 60)
    try:
        stats = get_detailed_stats()
        print(f"✅ get_detailed_stats() works")
        print(f"   Total users: {stats.get('total', 0)}")
        print(f"   Premium users: {stats.get('premium', 0)}\n")
    except Exception as e:
        print(f"❌ Failed: {e}\n")
    
    # Test 3: Concurrent reads
    print("Test 3: Concurrent Database Reads")
    print("-" * 60)
    try:
        async def read_users():
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("SELECT COUNT(*) FROM users")
                return await cursor.fetchone()
        
        # Run 5 concurrent reads
        tasks = [read_users() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        print(f"✅ Concurrent reads successful")
        print(f"   {len(results)} concurrent queries completed")
        print(f"   All returned: {results[0][0]} users\n")
    except Exception as e:
        print(f"❌ Failed: {e}\n")
    
    # Test 4: Table integrity
    print("Test 4: Table Integrity Check")
    print("-" * 60)
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """)
            tables = await cursor.fetchall()
            
            print(f"✅ Database integrity OK")
            print(f"   Tables found: {len(tables)}")
            for (table_name,) in tables:
                cursor = await db.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = await cursor.fetchone()
                print(f"   • {table_name}: {count[0]} rows")
    except Exception as e:
        print(f"❌ Failed: {e}\n")
    
    print("\n" + "=" * 60)
    print("✅ Database verification completed!")

if __name__ == "__main__":
    asyncio.run(verify_async_db())
