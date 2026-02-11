#!/usr/bin/env python3
"""
Comprehensive Bot Audit
Checks all aspects of the bot for issues
"""

import os
import re
from database import get_conn, get_detailed_stats
from utils.texts import TEXTS, get_all_translations

def check_localization():
    """Check localization completeness"""
    print("🌐 LOKALIZATSIYA TEKSHIRUVI")
    print("=" * 70)
    
    # All keys that should exist
    required_keys = [
        # Buttons
        'btn_test', 'btn_referat', 'btn_library', 'btn_ppt',
        'btn_deadline', 'btn_tutor', 'btn_my_deadlines', 'btn_solver',
        'btn_quiz', 'btn_checker', 'btn_lang', 'btn_flashcards',
        'btn_invite', 'btn_file_konspekt', 'btn_free_resources',
        'btn_photo_konspekt', 'btn_channels', 'btn_news', 'btn_grants',
        'btn_about', 'btn_premium', 'btn_admin', 'btn_dashboard',
        'btn_clear_chat', 'btn_cancel', 'btn_back',
        'btn_1month', 'btn_3months', 'btn_6months',
        
        # Messages
        'welcome', 'main_menu', 'premium_info', 'referat_topic',
        'test_topic', 'ppt_topic', 'tutor_welcome', 'cancel', 'back',
        'settings', 'lang_select', 'about_text', 'payment_info',
        'payment_pending', 'payment_approved', 'payment_rejected',
        'enter_test_subject', 'enter_referat_topic', 'enter_ppt_topic',
        'premium_required'
    ]
    
    missing_count = 0
    
    for lang in TEXTS.keys():
        print(f"\n{lang.upper()} Tili:")
        print("-" * 70)
        
        missing_in_lang = []
        for key in required_keys:
            if key not in TEXTS[lang]:
                missing_in_lang.append(key)
                missing_count += 1
        
        if missing_in_lang:
            print(f"❌ Yo'q kalitlar ({len(missing_in_lang)}):")
            for key in missing_in_lang[:10]:  # Show first 10
                print(f"   • {key}")
            if len(missing_in_lang) > 10:
                print(f"   ... va yana {len(missing_in_lang) - 10} ta")
        else:
            print(f"✅ Barcha kalitlar mavjud ({len(required_keys)} ta)")
    
    print(f"\n{'=' * 70}")
    print(f"JAMI YO'Q KALITLAR: {missing_count}")
    
    return missing_count == 0

def check_database():
    """Check database structure and indexes"""
    print("\n\n💾 DATABASE TEKSHIRUVI")
    print("=" * 70)
    
    conn = get_conn()
    cursor = conn.cursor()
    
    # Check indexes
    print("\n1. Indekslar:")
    print("-" * 70)
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index' AND name NOT LIKE 'sqlite_%'
    """)
    indexes = cursor.fetchall()
    
    if indexes:
        print(f"✅ Topildi: {len(indexes)} ta indeks")
        for (name,) in indexes:
            print(f"   • {name}")
    else:
        print("❌ Indekslar topilmadi!")
        print("   Tavsiya: users(tg_id), deadlines(tg_id), payments(user_id)")
    
    # Check tables
    print("\n2. Jadvallar:")
    print("-" * 70)
    
    required_tables = [
        'users', 'deadlines', 'payments', 'books', 'settings',
        'referrals', 'quiz_questions', 'quiz_answers'
    ]
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    for table in required_tables:
        if table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✅ {table}: {count} rows")
        else:
            print(f"❌ {table}: YO'Q")
    
    # Check for event_log
    print("\n3. Event Log:")
    print("-" * 70)
    if 'event_log' in tables:
        print("✅ event_log jadvali mavjud")
    else:
        print("❌ event_log jadvali yo'q (statistika uchun kerak)")
    
    conn.close()
    
    return len(indexes) > 0

def check_error_handling():
    """Check error handling in code"""
    print("\n\n⚠️  ERROR HANDLING TEKSHIRUVI")
    print("=" * 70)
    
    files_to_check = [
        'handlers/common.py',
        'handlers/student_tools.py',
        'handlers/konspekt.py',
        'handlers/admin.py',
        'services/gemini_service.py'
    ]
    
    total_bare_except = 0
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find bare except blocks
        bare_except = len(re.findall(r'except\s*:', content))
        total_bare_except += bare_except
        
        if bare_except > 0:
            print(f"⚠️  {file_path}: {bare_except} ta 'except:' blok")
    
    print(f"\n{'=' * 70}")
    if total_bare_except > 0:
        print(f"❌ JAMI: {total_bare_except} ta yomon error handler")
        print("   Tavsiya: 'except Exception as e:' ishlatish")
    else:
        print("✅ Error handling yaxshi")
    
    return total_bare_except == 0

def check_premium_checks():
    """Check if premium features are properly protected"""
    print("\n\n💎 PREMIUM TEKSHIRUVI")
    print("=" * 70)
    
    files_to_check = {
        'handlers/student_tools.py': ['referat', 'presentation', 'test'],
        'handlers/premium/ai_tutor.py': ['tutor'],
        'handlers/premium/homework_solver.py': ['solver'],
        'handlers/premium/essay_checker.py': ['checker'],
        'handlers/premium/flashcards.py': ['flashcards']
    }
    
    issues = []
    
    for file_path, features in files_to_check.items():
        if not os.path.exists(file_path):
            issues.append(f"{file_path} topilmadi")
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_premium_check = 'is_premium' in content
        
        if has_premium_check:
            print(f"✅ {file_path}: Premium tekshiruvi bor")
        else:
            print(f"❌ {file_path}: Premium tekshiruvi YO'Q")
            issues.append(file_path)
    
    print(f"\n{'=' * 70}")
    if issues:
        print(f"❌ {len(issues)} ta fayl muammo bilan")
    else:
        print("✅ Barcha premium funksiyalar himoyalangan")
    
    return len(issues) == 0

def check_file_cleanup():
    """Check temp directory"""
    print("\n\n🗑️  FILE CLEANUP TEKSHIRUVI")
    print("=" * 70)
    
    temp_dir = "temp"
    
    if not os.path.exists(temp_dir):
        print(f"⚠️  {temp_dir} papkasi yo'q")
        return True
    
    files = os.listdir(temp_dir)
    
    if not files:
        print(f"✅ {temp_dir} papkasi bo'sh")
        return True
    
    total_size = 0
    for file in files:
        file_path = os.path.join(temp_dir, file)
        if os.path.isfile(file_path):
            total_size += os.path.getsize(file_path)
    
    print(f"⚠️  {len(files)} ta fayl topildi")
    print(f"   Jami hajm: {total_size / 1024:.2f} KB")
    print("   Tavsiya: Auto-cleanup mexanizmi qo'shish")
    
    return len(files) == 0

def check_security():
    """Check security issues"""
    print("\n\n🔒 XAVFSIZLIK TEKSHIRUVI")
    print("=" * 70)
    
    issues = []
    
    # Check for SQL injection
    print("\n1. SQL Injection Himoyasi:")
    print("-" * 70)
    
    db_file = 'database.py'
    if os.path.exists(db_file):
        with open(db_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for string formatting in SQL
        dangerous_patterns = [
            r'f".*SELECT.*{',
            r'f".*INSERT.*{',
            r'f".*UPDATE.*{',
            r'%.*SELECT',
            r'%.*INSERT',
            r'%.*UPDATE'
        ]
        
        found_issues = False
        for pattern in dangerous_patterns:
            if re.search(pattern, content):
                found_issues = True
                break
        
        if found_issues:
            print("⚠️  Potensial SQL injection xavfi topildi")
            issues.append("SQL injection")
        else:
            print("✅ SQL injection himoyasi yaxshi")
    
    # Check file upload validation
    print("\n2. File Upload Validation:")
    print("-" * 70)
    
    konspekt_file = 'handlers/konspekt.py'
    if os.path.exists(konspekt_file):
        with open(konspekt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_size_check = 'file_size' in content or 'size' in content
        has_type_check = 'endswith' in content or 'content_type' in content
        
        if has_type_check:
            print("✅ File type validation mavjud")
        else:
            print("⚠️  File type validation yo'q")
            issues.append("File type validation")
        
        if has_size_check:
            print("✅ File size validation mavjud")
        else:
            print("⚠️  File size validation yo'q")
            issues.append("File size validation")
    
    print(f"\n{'=' * 70}")
    if issues:
        print(f"⚠️  {len(issues)} ta xavfsizlik muammosi")
    else:
        print("✅ Xavfsizlik yaxshi")
    
    return len(issues) == 0

def generate_summary():
    """Generate audit summary"""
    print("\n\n" + "=" * 70)
    print("📊 AUDIT XULOSASI")
    print("=" * 70)
    
    results = {
        'Lokalizatsiya': check_localization(),
        'Database': check_database(),
        'Error Handling': check_error_handling(),
        'Premium Checks': check_premium_checks(),
        'File Cleanup': check_file_cleanup(),
        'Security': check_security()
    }
    
    print("\n\nNATIJALAR:")
    print("-" * 70)
    
    passed = 0
    total = len(results)
    
    for category, result in results.items():
        status = "✅ OK" if result else "❌ MUAMMO"
        print(f"{category:20s}: {status}")
        if result:
            passed += 1
    
    print(f"\n{'=' * 70}")
    print(f"JAMI: {passed}/{total} ({passed*100//total}%)")
    
    if passed == total:
        print("🟢 MUKAMMAL - Barcha tekshiruvlar o'tdi!")
    elif passed >= total * 0.7:
        print("🟡 YAXSHI - Ba'zi muammolar bor")
    else:
        print("🔴 YOMON - Ko'p muammolar topildi")

if __name__ == "__main__":
    print("🔍 TALABA BOT - KENG QAMROVLI AUDIT\n")
    generate_summary()
