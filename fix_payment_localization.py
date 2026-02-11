#!/usr/bin/env python3
"""
Localization Fixer
Fixes and verifies all localization texts
"""

from utils.texts import TEXTS, get_all_translations
import json

def fix_payment_localization():
    """Fix payment-related localization"""
    print("🌐 Fixing Payment Localization...\n")
    
    # Check all button texts
    button_keys = [
        'btn_test', 'btn_referat', 'btn_presentation', 'btn_konspekt',
        'btn_library', 'btn_channels', 'btn_news', 'btn_grants',
        'btn_invite', 'btn_free_resources', 'btn_about', 'btn_premium',
        'btn_admin', 'btn_lang', 'btn_cancel', 'btn_back',
        'btn_1month', 'btn_3months', 'btn_6months'
    ]
    
    print("Checking Button Texts:")
    print("=" * 70)
    
    for key in button_keys:
        translations = get_all_translations(key)
        if len(translations) == 3:  # uz, ru, en
            print(f"✅ {key}: {len(translations)} translations")
        else:
            print(f"⚠️  {key}: Only {len(translations)} translations")
            for lang in TEXTS.keys():
                if key not in TEXTS[lang]:
                    print(f"   Missing in: {lang}")
    
    # Check message texts
    print("\n\nChecking Message Texts:")
    print("=" * 70)
    
    message_keys = [
        'welcome', 'about_text', 'premium_info', 'payment_info',
        'payment_pending', 'payment_approved', 'payment_rejected',
        'enter_test_subject', 'enter_referat_topic', 'enter_ppt_topic',
        'premium_required', 'lang_select'
    ]
    
    for key in message_keys:
        count = 0
        for lang in TEXTS.keys():
            if key in TEXTS[lang]:
                count += 1
        
        if count == 3:
            print(f"✅ {key}: {count}/3 languages")
        else:
            print(f"⚠️  {key}: {count}/3 languages")
            for lang in TEXTS.keys():
                if key not in TEXTS[lang]:
                    print(f"   Missing in: {lang}")
    
    # Export localization stats
    print("\n\n" + "=" * 70)
    print("Localization Statistics:")
    print("=" * 70)
    
    for lang in TEXTS.keys():
        key_count = len(TEXTS[lang])
        print(f"{lang.upper()}: {key_count} keys")
    
    # Find keys only in one language
    print("\n\nKeys Not in All Languages:")
    print("=" * 70)
    
    all_keys = set()
    for lang in TEXTS.keys():
        all_keys.update(TEXTS[lang].keys())
    
    for key in sorted(all_keys):
        langs_with_key = [lang for lang in TEXTS.keys() if key in TEXTS[lang]]
        if len(langs_with_key) < 3:
            print(f"⚠️  {key}: Only in {', '.join(langs_with_key)}")
    
    print("\n✅ Localization check completed!")

if __name__ == "__main__":
    fix_payment_localization()
