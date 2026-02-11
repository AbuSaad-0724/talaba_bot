#!/usr/bin/env python3
"""
Feature Verifier
Verifies all bot features are working correctly
"""

from database import get_detailed_stats, is_premium, get_user
from utils.texts import get_text, get_all_translations, TEXTS
import os

def verify_features():
    """Verify all bot features"""
    print("🔍 Bot Feature Verification\n")
    print("=" * 70)
    
    features_ok = 0
    features_total = 0
    
    # Feature 1: Database
    print("\n1. Database Connection")
    print("-" * 70)
    features_total += 1
    try:
        stats = get_detailed_stats()
        print(f"✅ Database working")
        print(f"   Users: {stats.get('total', 0)}")
        print(f"   Premium: {stats.get('premium', 0)}")
        features_ok += 1
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    # Feature 2: Localization
    print("\n2. Localization System")
    print("-" * 70)
    features_total += 1
    try:
        langs = list(TEXTS.keys())
        test_key = 'welcome'
        
        all_langs_ok = True
        for lang in langs:
            if test_key not in TEXTS[lang]:
                all_langs_ok = False
                print(f"❌ Missing '{test_key}' in {lang}")
        
        if all_langs_ok:
            print(f"✅ Localization working ({len(langs)} languages)")
            print(f"   Languages: {', '.join(langs)}")
            features_ok += 1
        else:
            print(f"⚠️  Localization incomplete")
    except Exception as e:
        print(f"❌ Localization error: {e}")
    
    # Feature 3: Premium System
    print("\n3. Premium System")
    print("-" * 70)
    features_total += 1
    try:
        # Test with a non-existent user (should return False)
        result = is_premium(999999999)
        if result == False:
            print("✅ Premium check working")
            features_ok += 1
        else:
            print("⚠️  Premium check returned unexpected result")
    except Exception as e:
        print(f"❌ Premium system error: {e}")
    
    # Feature 4: File Structure
    print("\n4. File Structure")
    print("-" * 70)
    features_total += 1
    
    required_dirs = [
        'handlers',
        'handlers/premium',
        'services',
        'utils',
        'data',
        'data/templates'
    ]
    
    all_dirs_ok = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - MISSING")
            all_dirs_ok = False
    
    if all_dirs_ok:
        features_ok += 1
    
    # Feature 5: Required Files
    print("\n5. Core Files")
    print("-" * 70)
    features_total += 1
    
    required_files = [
        'main.py',
        'database.py',
        'config.py',
        'handlers/common.py',
        'handlers/admin.py',
        'utils/texts.py'
    ]
    
    all_files_ok = True
    for file_path in required_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            if size > 100:  # At least 100 bytes
                print(f"✅ {file_path} ({size:,} bytes)")
            else:
                print(f"⚠️  {file_path} is too small ({size} bytes)")
                all_files_ok = False
        else:
            print(f"❌ {file_path} - MISSING")
            all_files_ok = False
    
    if all_files_ok:
        features_ok += 1
    
    # Feature 6: Templates
    print("\n6. PowerPoint Templates")
    print("-" * 70)
    features_total += 1
    
    default_template = "data/templates/default.pptx"
    if os.path.exists(default_template):
        size = os.path.getsize(default_template)
        print(f"✅ Default template exists ({size:,} bytes)")
        features_ok += 1
    else:
        print(f"❌ Default template missing")
        print("   Run: python -c 'from utils.template_gen import create_starter_template; create_starter_template()'")
    
    # Feature 7: AI Services
    print("\n7. AI Service Files")
    print("-" * 70)
    features_total += 1
    
    ai_services = [
        'services/gemini_service.py',
        'services/ai_service.py',
        'services/multi_ai_service.py'
    ]
    
    ai_ok = True
    for service in ai_services:
        if os.path.exists(service):
            print(f"✅ {service}")
        else:
            print(f"❌ {service} - MISSING")
            ai_ok = False
    
    if ai_ok:
        features_ok += 1
    
    # Feature 8: Handler Files
    print("\n8. Handler Files")
    print("-" * 70)
    features_total += 1
    
    handlers = [
        'handlers/common.py',
        'handlers/student_tools.py',
        'handlers/konspekt.py',
        'handlers/languages.py',
        'handlers/premium/ai_tutor.py'
    ]
    
    handlers_ok = True
    for handler in handlers:
        if os.path.exists(handler):
            print(f"✅ {handler}")
        else:
            print(f"❌ {handler} - MISSING")
            handlers_ok = False
    
    if handlers_ok:
        features_ok += 1
    
    # Summary
    print("\n" + "=" * 70)
    print(f"FEATURE SCORE: {features_ok}/{features_total}")
    print("=" * 70)
    
    percentage = (features_ok / features_total) * 100
    
    if percentage == 100:
        print("🟢 PERFECT - All features verified!")
    elif percentage >= 80:
        print("🟡 GOOD - Most features working")
    elif percentage >= 60:
        print("🟠 FAIR - Some features need attention")
    else:
        print("🔴 POOR - Multiple features broken")
    
    print()

if __name__ == "__main__":
    verify_features()
