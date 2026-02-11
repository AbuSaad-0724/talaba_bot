#!/usr/bin/env python3
"""
Payment Text Fixer
Fixes payment-related localization issues
"""

from utils.texts import TEXTS, get_text
from database import get_user_language

def fix_payment_texts():
    """Check and fix payment localization"""
    print("💰 Checking Payment Localization...\n")
    
    # Required payment keys
    payment_keys = [
        'payment_info',
        'payment_pending',
        'payment_approved',
        'payment_rejected',
        'payment_proof_prompt',
        'payment_card_prompt',
        'payment_amount_prompt',
        'btn_1month',
        'btn_3months',
        'btn_6months',
        'premium_plans',
        'premium_required'
    ]
    
    print("Checking required keys in all languages:")
    print("=" * 70)
    
    missing_keys = {lang: [] for lang in TEXTS.keys()}
    
    for lang in TEXTS.keys():
        print(f"\n{lang.upper()} Language:")
        print("-" * 70)
        
        for key in payment_keys:
            if key in TEXTS[lang]:
                print(f"✅ {key}")
            else:
                print(f"❌ {key} - MISSING")
                missing_keys[lang].append(key)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    total_missing = sum(len(keys) for keys in missing_keys.values())
    
    if total_missing == 0:
        print("✅ All payment texts are properly localized!")
    else:
        print(f"⚠️  Found {total_missing} missing translations:")
        for lang, keys in missing_keys.items():
            if keys:
                print(f"\n{lang.upper()}:")
                for key in keys:
                    print(f"  • {key}")
    
    # Test payment info generation
    print("\n" + "=" * 70)
    print("Testing Payment Info Generation")
    print("=" * 70)
    
    for lang in ['uz', 'ru', 'en']:
        print(f"\n{lang.upper()}:")
        print("-" * 70)
        
        # Simulate payment info
        if 'payment_info' in TEXTS[lang]:
            info = TEXTS[lang]['payment_info']
            print(info[:200] + "..." if len(info) > 200 else info)
        else:
            print("❌ payment_info not found")

if __name__ == "__main__":
    fix_payment_texts()
