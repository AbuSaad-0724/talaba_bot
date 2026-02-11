#!/usr/bin/env python3
"""
Group Link Updater
Updates and manages group/channel links in the database
"""

from database import get_conn, get_setting, set_setting

def update_group_links():
    """Update group and channel links"""
    print("🔗 Group Link Updater\n")
    print("=" * 70)
    
    # Default links
    default_links = {
        'main_channel': '@TalabaServis',
        'support_group': '@TalabaServisSupport',
        'news_channel': '@UniversityNewsUz',
        'library_channel': '@OnlineKutubxona',
    }
    
    conn = get_conn()
    
    # Check current settings
    print("\n1. Current Settings")
    print("-" * 70)
    
    for key, default_value in default_links.items():
        current = get_setting(key, default_value)
        print(f"{key}: {current}")
    
    # Update settings
    print("\n2. Updating Settings")
    print("-" * 70)
    
    for key, value in default_links.items():
        try:
            set_setting(key, value)
            print(f"✅ Updated {key} = {value}")
        except Exception as e:
            print(f"❌ Failed to update {key}: {e}")
    
    # Verify updates
    print("\n3. Verification")
    print("-" * 70)
    
    all_updated = True
    for key, expected_value in default_links.items():
        actual = get_setting(key)
        if actual == expected_value:
            print(f"✅ {key}: {actual}")
        else:
            print(f"❌ {key}: Expected '{expected_value}', got '{actual}'")
            all_updated = False
    
    # Show all settings
    print("\n4. All Bot Settings")
    print("-" * 70)
    
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings ORDER BY key")
    settings = cursor.fetchall()
    
    if settings:
        for key, value in settings:
            print(f"  {key} = {value}")
    else:
        print("  No settings found")
    
    conn.close()
    
    print("\n" + "=" * 70)
    if all_updated:
        print("✅ All group links updated successfully!")
    else:
        print("⚠️  Some links failed to update")

if __name__ == "__main__":
    update_group_links()
