#!/usr/bin/env python3
"""
Import Debug Tool v2
Advanced import analyzer with dependency graph
"""

import os
import re
import ast
from collections import defaultdict

def analyze_imports():
    """Analyze all imports in the project"""
    print("🔍 Analyzing Project Imports...\n")
    
    imports_map = defaultdict(list)
    files_analyzed = 0
    
    # Walk through project
    for root, dirs, files in os.walk('.'):
        # Skip venv and cache
        if 'venv' in root or '__pycache__' in root or '.git' in root:
            continue
            
        for file in files:
            if not file.endswith('.py'):
                continue
                
            file_path = os.path.join(root, file)
            files_analyzed += 1
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse imports
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports_map[file_path].append(f"import {alias.name}")
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        for alias in node.names:
                            imports_map[file_path].append(f"from {module} import {alias.name}")
            
            except Exception as e:
                print(f"⚠️  Error parsing {file_path}: {e}")
    
    # Print results
    print(f"📊 Analysis Results:")
    print("=" * 70)
    print(f"Files analyzed: {files_analyzed}")
    print(f"Files with imports: {len(imports_map)}\n")
    
    # Show files with most imports
    sorted_files = sorted(imports_map.items(), key=lambda x: len(x[1]), reverse=True)
    
    print("📁 Top 10 Files by Import Count:")
    print("-" * 70)
    for file_path, imports in sorted_files[:10]:
        print(f"\n{file_path} ({len(imports)} imports)")
        for imp in imports[:5]:
            print(f"  • {imp}")
        if len(imports) > 5:
            print(f"  ... and {len(imports) - 5} more")
    
    # Find circular imports
    print("\n\n🔄 Checking for Circular Imports:")
    print("-" * 70)
    
    local_imports = defaultdict(set)
    for file_path, imports in imports_map.items():
        for imp in imports:
            if 'from .' in imp or 'from handlers' in imp or 'from services' in imp or 'from utils' in imp:
                module = imp.split('import')[0].replace('from', '').strip()
                local_imports[file_path].add(module)
    
    # Simple circular detection
    circular_found = False
    for file_a, imports_a in local_imports.items():
        for file_b, imports_b in local_imports.items():
            if file_a != file_b:
                # Check if A imports B and B imports A
                if any(file_b.replace('./', '').replace('.py', '') in imp for imp in imports_a):
                    if any(file_a.replace('./', '').replace('.py', '') in imp for imp in imports_b):
                        print(f"⚠️  Potential circular: {file_a} ↔ {file_b}")
                        circular_found = True
    
    if not circular_found:
        print("✅ No obvious circular imports detected")
    
    # Find missing imports
    print("\n\n❌ Checking for Missing Modules:")
    print("-" * 70)
    
    standard_libs = {'os', 'sys', 'datetime', 'asyncio', 'logging', 're', 'json', 'sqlite3'}
    external_libs = {'aiogram', 'google', 'docx', 'pptx', 'PIL', 'matplotlib', 'pytz'}
    
    all_imports = set()
    for imports in imports_map.values():
        for imp in imports:
            module = imp.split()[1].split('.')[0]
            all_imports.add(module)
    
    unknown = all_imports - standard_libs - external_libs - {'handlers', 'services', 'utils', 'database', 'config'}
    
    if unknown:
        print("⚠️  Unknown/Custom modules:")
        for mod in sorted(unknown):
            print(f"  • {mod}")
    else:
        print("✅ All imports recognized")

if __name__ == "__main__":
    analyze_imports()
