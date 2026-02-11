#!/usr/bin/env python3
"""
List Templates Debug Tool
Shows all available PowerPoint templates in the database
"""

from database import get_all_templates, get_template_categories, get_conn
import os

def list_templates():
    """List all templates in database and filesystem"""
    print("🔍 Listing PowerPoint Templates...\n")
    
    # Check database templates
    print("📊 Database Templates:")
    print("=" * 70)
    
    try:
        templates = get_all_templates()
        
        if not templates:
            print("⚠️  No templates found in database\n")
        else:
            print(f"Total templates: {len(templates)}\n")
            
            # Group by category
            categories = get_template_categories()
            print(f"Categories: {', '.join(categories)}\n")
            
            for tid, name, category, file_path in templates:
                exists = "✅" if os.path.exists(file_path) else "❌"
                size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                
                print(f"ID: {tid}")
                print(f"  Name: {name}")
                print(f"  Category: {category}")
                print(f"  Path: {file_path}")
                print(f"  File exists: {exists}")
                if size > 0:
                    print(f"  Size: {size:,} bytes")
                print("-" * 70)
    
    except Exception as e:
        print(f"❌ Database error: {e}\n")
    
    # Check filesystem templates
    print("\n📁 Filesystem Templates:")
    print("=" * 70)
    
    template_dirs = [
        "data/templates",
        "templates",
        "temp/templates"
    ]
    
    found_files = []
    for template_dir in template_dirs:
        if os.path.exists(template_dir):
            for file in os.listdir(template_dir):
                if file.endswith('.pptx'):
                    file_path = os.path.join(template_dir, file)
                    size = os.path.getsize(file_path)
                    found_files.append((file_path, size))
    
    if found_files:
        print(f"Found {len(found_files)} template files:\n")
        for file_path, size in found_files:
            print(f"📄 {file_path}")
            print(f"   Size: {size:,} bytes")
            print()
    else:
        print("⚠️  No template files found in filesystem\n")
    
    # Check default template
    print("\n🎨 Default Template:")
    print("=" * 70)
    
    default_path = "data/templates/default.pptx"
    if os.path.exists(default_path):
        size = os.path.getsize(default_path)
        print(f"✅ Default template exists")
        print(f"   Path: {default_path}")
        print(f"   Size: {size:,} bytes")
    else:
        print(f"❌ Default template not found at: {default_path}")
        print("   Run: python -c 'from utils.template_gen import create_starter_template; create_starter_template()'")
    
    print("\n" + "=" * 70)
    print("✅ Template listing completed!")

if __name__ == "__main__":
    list_templates()
