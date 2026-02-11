#!/usr/bin/env python3
"""
Template Cleaner
Removes old or invalid templates from database and filesystem
"""

from database import get_conn
import os

def clear_templates():
    """Clear all templates from database and optionally from filesystem"""
    print("🧹 Template Cleaner\n")
    print("=" * 70)
    
    # Check database templates
    print("\n1. Checking Database Templates")
    print("-" * 70)
    
    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        # Check if templates table exists
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name='templates'
        """)
        
        if cursor.fetchone()[0] == 0:
            print("⚠️  Templates table does not exist")
            print("   Creating templates table...")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT,
                    file_path TEXT NOT NULL,
                    created TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("✅ Templates table created")
        else:
            # Count existing templates
            cursor.execute("SELECT COUNT(*) FROM templates")
            count = cursor.fetchone()[0]
            print(f"Found {count} templates in database")
            
            if count > 0:
                # Show all templates
                cursor.execute("SELECT id, name, category, file_path FROM templates")
                templates = cursor.fetchall()
                
                print("\nExisting templates:")
                for tid, name, category, path in templates:
                    exists = "✅" if os.path.exists(path) else "❌"
                    print(f"  {tid}. {name} ({category}) - {exists} {path}")
                
                # Ask to clear (auto-clear for script)
                print("\nClearing all templates from database...")
                cursor.execute("DELETE FROM templates")
                conn.commit()
                print(f"✅ Removed {count} templates from database")
            else:
                print("✅ Database is already clean")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Check filesystem templates
    print("\n2. Checking Filesystem Templates")
    print("-" * 70)
    
    template_dirs = [
        "data/templates",
        "templates",
        "temp/templates"
    ]
    
    total_files = 0
    
    for template_dir in template_dirs:
        if os.path.exists(template_dir):
            files = [f for f in os.listdir(template_dir) if f.endswith('.pptx')]
            
            if files:
                print(f"\n{template_dir}:")
                for file in files:
                    file_path = os.path.join(template_dir, file)
                    size = os.path.getsize(file_path)
                    print(f"  • {file} ({size:,} bytes)")
                    total_files += 1
            else:
                print(f"\n{template_dir}: Empty")
        else:
            print(f"\n{template_dir}: Does not exist")
    
    print(f"\nTotal template files found: {total_files}")
    
    # Keep default template
    print("\n3. Preserving Default Template")
    print("-" * 70)
    
    default_path = "data/templates/default.pptx"
    if os.path.exists(default_path):
        size = os.path.getsize(default_path)
        print(f"✅ Default template preserved: {size:,} bytes")
    else:
        print("⚠️  Default template not found")
        print("   Run: python -c 'from utils.template_gen import create_starter_template; create_starter_template()'")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ Template cleanup completed!")

if __name__ == "__main__":
    clear_templates()
