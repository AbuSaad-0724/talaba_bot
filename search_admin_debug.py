#!/usr/bin/env python3
"""
Admin Search Debug Tool
Searches for admin-related functions and handlers in the codebase
"""

import os
import re

def search_admin_functions():
    """Search for all admin-related functions"""
    print("🔍 Searching for Admin Functions...\n")
    
    admin_files = [
        'handlers/admin.py',
        'database.py',
        'main.py'
    ]
    
    admin_patterns = [
        r'@router\.(message|callback_query).*admin',
        r'def admin_\w+',
        r'AdminStates\.\w+',
        r'ADMIN_ID'
    ]
    
    results = {}
    
    for file_path in admin_files:
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
        file_results = []
        for i, line in enumerate(lines, 1):
            for pattern in admin_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    file_results.append((i, line.strip()))
                    break
        
        if file_results:
            results[file_path] = file_results
    
    # Print results
    for file_path, matches in results.items():
        print(f"📁 {file_path}")
        print("=" * 60)
        for line_num, line in matches[:10]:  # Show first 10
            print(f"  Line {line_num}: {line[:70]}")
        if len(matches) > 10:
            print(f"  ... and {len(matches) - 10} more")
        print()
    
    print(f"\n✅ Total files searched: {len(admin_files)}")
    print(f"✅ Files with matches: {len(results)}")
    print(f"✅ Total matches: {sum(len(m) for m in results.values())}")

if __name__ == "__main__":
    search_admin_functions()
