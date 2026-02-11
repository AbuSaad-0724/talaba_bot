#!/usr/bin/env python3
"""
Import Debug Tool
Simple import checker for the project
"""

import os
import re

def check_imports():
    """Check all imports in Python files"""
    print("🔍 Checking Project Imports...\n")
    
    python_files = []
    
    # Find all Python files
    for root, dirs, files in os.walk('.'):
        # Skip venv and cache
        if 'venv' in root or '__pycache__' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files\n")
    
    # Check each file
    import_errors = []
    import_stats = {
        'aiogram': 0,
        'database': 0,
        'handlers': 0,
        'services': 0,
        'utils': 0,
        'config': 0
    }
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find imports
            imports = re.findall(r'^(?:from|import)\s+(\S+)', content, re.MULTILINE)
            
            for imp in imports:
                base_module = imp.split('.')[0]
                if base_module in import_stats:
                    import_stats[base_module] += 1
                    
        except Exception as e:
            import_errors.append((file_path, str(e)))
    
    # Print statistics
    print("📊 Import Statistics:")
    print("=" * 50)
    for module, count in sorted(import_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"{module:15} : {count:3} imports")
    
    if import_errors:
        print("\n\n❌ Files with errors:")
        for file_path, error in import_errors:
            print(f"  {file_path}: {error}")
    else:
        print("\n\n✅ All files checked successfully!")

if __name__ == "__main__":
    check_imports()
