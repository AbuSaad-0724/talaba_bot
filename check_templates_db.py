#!/usr/bin/env python3
"""
Template Database Checker
Checks if templates table exists and shows all templates
"""

from database import get_conn, get_all_templates, get_template_categories

def check_templates():
    print("🔍 Checking Templates Database...\n")
    
    # Check if table exists
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='templates'")
    table_exists = c.fetchone()
    
    if not table_exists:
        print("❌ Templates table does not exist!")
        conn.close()
        return
    
    print("✅ Templates table exists\n")
    
    # Get all templates
    templates = get_all_templates()
    
    if not templates:
        print("⚠️  No templates found in database")
        conn.close()
        return
    
    print(f"📊 Total Templates: {len(templates)}\n")
    
    # Get categories
    categories = get_template_categories()
    print(f"📁 Categories: {', '.join(categories)}\n")
    
    # Show all templates
    print("📋 Templates List:")
    print("-" * 60)
    for tid, name, category, file_path in templates:
        print(f"ID: {tid}")
        print(f"  Name: {name}")
        print(f"  Category: {category}")
        print(f"  Path: {file_path}")
        print("-" * 60)
    
    conn.close()

if __name__ == "__main__":
    check_templates()
